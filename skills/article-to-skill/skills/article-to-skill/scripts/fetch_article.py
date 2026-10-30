# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.27", "trafilatura>=2.0"]
# ///
"""Fetch web articles as clean Markdown plus metadata, cached in data/articles/<id>.json.

Usage:
  uv run fetch_article.py <url> [<url> ...] [--list data/lists/<name>.tsv] [--refresh] [--delay 1]
  uv run fetch_article.py --from-file page.md --url <original url>    # import a page saved elsewhere
                                                                      # (.md, .txt, .html, or Firecrawl scrape JSON)

Text only: main content is extracted with trafilatura (boilerplate, nav and comments dropped).
Each JSON holds url, final_url, title, author, date, sitename, description, fetched_at, source,
word_count, anchors (heading text -> HTML id, for citation links), links, and text (Markdown).
A page that yields fewer than --min-words words is reported as an error and not cached: it is
probably JS-rendered, paywalled or a block page. Save it with another tool (Firecrawl, a browser)
and import it with --from-file (.md, .txt, .html, or a saved Firecrawl scrape JSON, which keeps
author and date). Site navigation above the first '# ' title and footer link blocks are trimmed.
Prints one `ok` line per article; exits 1 if any failed.
"""

import argparse
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
import trafilatura
from lxml import html as lxml_html

from article_ids import article_id

OUT_DIR = Path("data/articles")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
LINK = re.compile(r"\]\((https?://[^)\s]+)\)")
MD_LINK = re.compile(r"!?\[[^\]]*\]\([^)]*\)")
FOOTER = re.compile(r"^[\[\s#*]*(written by|more from|recommended from|responses \(|about the author)\b", re.IGNORECASE)
EXTRACT_OPTS = {"include_links": True, "include_tables": True, "include_formatting": True, "favor_recall": True}


def heading_anchors(page: str) -> dict[str, str]:
    """Heading text -> id, so citations can deep-link to a section (url#id)."""
    try:
        tree = lxml_html.fromstring(page)
    except (ValueError, lxml_html.etree.ParserError):
        return {}
    anchors = {}
    for h in tree.xpath("//h1|//h2|//h3|//h4"):
        hid = h.get("id") or next((el.get("id") or el.get("name") for el in h.iter() if el.get("id") or el.get("name")), None)
        if not hid and h.getparent() is not None and h.getparent().tag == "section":
            hid = h.getparent().get("id")
        text = " ".join(h.text_content().split())
        if hid and text:
            anchors.setdefault(text, hid)
    return anchors


def extract(page: str, url: str) -> dict:
    """Main text as Markdown plus metadata from raw HTML."""
    meta = trafilatura.bare_extraction(page, url=url, with_metadata=True, **EXTRACT_OPTS)
    text = trafilatura.extract(page, url=url, output_format="markdown", **EXTRACT_OPTS) or ""
    get = (lambda k: getattr(meta, k, None)) if meta else (lambda k: None)
    return {
        "title": get("title"), "author": get("author"), "date": get("date"),
        "sitename": get("sitename"), "description": get("description"),
        "anchors": heading_anchors(page), "text": text,
    }


def trim_chrome(lines: list[str]) -> list[str]:
    """Drop site navigation above the first '# ' title and the footer after the article."""
    start = next((i for i, line in enumerate(lines) if line.startswith("# ")), None)
    if start is not None and start < len(lines) // 3:
        lines = lines[start:]
    cut = next((i for i in range(len(lines) * 2 // 3, len(lines)) if FOOTER.match(lines[i])), None)
    if cut is not None:
        lines = lines[:cut]
    while lines and len(MD_LINK.sub("", lines[-1]).split()) < 8:
        lines.pop()
    return lines


def from_markdown(text: str, meta: dict | None = None) -> dict:
    """Saved Markdown, with site navigation and footer trimmed."""
    lines = trim_chrome(text.splitlines())
    meta = meta or {}
    title = meta.get("og:title") or (lines[0][2:].strip() if lines and lines[0].startswith("# ") else None)
    date = meta.get("article:published_time") or meta.get("publishedTime")
    return {"title": title, "author": meta.get("author"), "date": date[:10] if date else None,
            "sitename": meta.get("og:site_name"), "description": meta.get("og:description"),
            "anchors": {}, "text": "\n".join(lines)}


def from_saved(content: str, suffix: str, url: str) -> tuple[dict, str]:
    """(fields, kind) for a saved page: Firecrawl scrape JSON, HTML, or Markdown/text."""
    if content.lstrip().startswith("{"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict) and isinstance(data.get("markdown"), str):
            return from_markdown(data["markdown"], data.get("metadata") or {}), "firecrawl json"
    if suffix in {".html", ".htm"} or content.lstrip().lower().startswith(("<!doctype", "<html")):
        return extract(content, url), "html"
    return from_markdown(content), "markdown"


def record(url: str, final_url: str, source: str, fields: dict) -> dict:
    text = fields["text"]
    return {
        "id": article_id(url), "url": url, "final_url": final_url, **{k: v for k, v in fields.items() if k != "text"},
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"), "source": source,
        "word_count": len(text.split()), "links": sorted(set(LINK.findall(text))), "text": text,
    }


def fetch(client: httpx.Client, url: str) -> dict:
    resp = client.get(url)
    if resp.status_code >= 400:
        raise ValueError(f"HTTP {resp.status_code}")
    ctype = resp.headers.get("content-type", "")
    if "pdf" in ctype:
        raise ValueError("this is a PDF; use book-to-skill for documents")
    return record(url, str(resp.url), "httpx+trafilatura", extract(resp.text, str(resp.url)))


def save(rec: dict, min_words: int) -> Path:
    if rec["word_count"] < min_words:
        raise ValueError(f"only {rec['word_count']} words extracted (JS-rendered, paywalled or blocked?); "
                         "save the page with Firecrawl or a browser and use --from-file")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{rec['id']}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def urls_from_list(path: Path) -> list[str]:
    rows = path.read_text(encoding="utf-8").splitlines()
    return [r.split("\t")[0] for r in rows[1:] if r.strip()]


def import_file(path: Path, url: str, min_words: int) -> None:
    if not path.exists():
        sys.exit(f"error: {path} not found")
    content = path.read_text(encoding="utf-8", errors="replace")
    fields, kind = from_saved(content, path.suffix.lower(), url)
    try:
        out = save(record(url, url, f"file:{path.name} ({kind})", fields), min_words)
    except ValueError as exc:
        sys.exit(f"error: {url}: {exc}")
    print(f"ok {out} ({fields.get('title') or '?'}, {len(fields['text'].split())} words, from {kind})")


def fetch_all(urls: list[str], args: argparse.Namespace) -> int:
    failed = 0
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en;q=0.9,*;q=0.5"}
    with httpx.Client(follow_redirects=True, timeout=30, headers=headers) as client:
        for i, url in enumerate(urls):
            cached = OUT_DIR / f"{article_id(url)}.json"
            if cached.exists() and not args.refresh:
                print(f"ok {cached} (cached)")
                continue
            if i:
                time.sleep(args.delay)
            try:
                rec = fetch(client, url)
                out = save(rec, args.min_words)
                print(f"ok {out} ({rec['title'] or '?'}, {rec['word_count']} words)")
            except (httpx.HTTPError, ValueError) as exc:
                failed += 1
                print(f"error: {url}: {exc}")
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("--list", type=Path, help="TSV from list_articles.py (first column = url)")
    parser.add_argument("--from-file", type=Path, help="import a saved page (.md/.txt/.html or Firecrawl JSON) instead of fetching")
    parser.add_argument("--url", help="original URL of --from-file")
    parser.add_argument("--refresh", action="store_true", help="refetch even if cached")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--min-words", type=int, default=150)
    args = parser.parse_args()

    if args.from_file:
        if not args.url:
            sys.exit("error: --from-file needs --url <original url>")
        import_file(args.from_file, args.url, args.min_words)
        return
    urls = args.urls + (urls_from_list(args.list) if args.list else [])
    if not urls:
        sys.exit("error: give URLs, --list or --from-file")
    failed = fetch_all(urls, args)
    if failed:
        sys.exit(f"FAIL {failed} of {len(urls)} articles")


if __name__ == "__main__":
    main()
