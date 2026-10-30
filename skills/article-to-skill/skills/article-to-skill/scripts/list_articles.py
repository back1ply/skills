# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.27", "feedparser>=6", "trafilatura>=2.0"]
# ///
"""List the articles on a blog or site, from its feed, its sitemap, or the links on an index page.

Usage: uv run list_articles.py <site|feed|sitemap|index url> [--mode auto|feed|sitemap|links]
                                [--match REGEX] [--limit N] [--out FILE]
  -> data/lists/<host>.tsv with columns url, title, date (title/date blank when the source has none)

auto: the URL itself if it is a feed; else a feed advertised by the page (<link rel=alternate>)
or found at a common path (/feed, /rss.xml, /feed.atom, ...); else the site's sitemap. Feeds usually hold only the latest 10-50 posts; use --mode sitemap for
the full archive. --mode links lists same-site links on an index page (series, tag or docs pages).
--match keeps URLs matching a regex (for example '/blog/20(24|25)/').
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import feedparser
import httpx
from lxml import html as lxml_html
from trafilatura import sitemaps

from article_ids import slugify

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
FEED_TYPES = ("application/rss+xml", "application/atom+xml", "application/feed+json")
COMMON_FEEDS = ("/feed", "/feed.xml", "/rss.xml", "/atom.xml", "/feed.atom", "/index.xml", "/rss", "/blog/feed")


def from_feed(body: bytes) -> list[tuple[str, str, str]]:
    feed = feedparser.parse(body)
    return [(e.get("link", ""), e.get("title", ""), (e.get("published") or e.get("updated") or "")[:16])
            for e in feed.entries if e.get("link")]


def advertised_feed(page: str, base: str) -> str | None:
    tree = lxml_html.fromstring(page)
    for link in tree.xpath("//link[@rel='alternate'][@href]"):
        if link.get("type", "").lower() in FEED_TYPES:
            return urljoin(base, link.get("href"))
    return None


def feed_candidates(page: str, base: str) -> list[str]:
    """The feed the page advertises, else the usual feed paths at the site root."""
    if advertised := advertised_feed(page, base):
        return [advertised]
    root = f"{urlsplit(base).scheme}://{urlsplit(base).netloc}"
    return [root + path for path in COMMON_FEEDS]


def from_links(page: str, base: str) -> list[tuple[str, str, str]]:
    host = urlsplit(base).netloc
    seen, rows = set(), []
    for a in lxml_html.fromstring(page).xpath("//a[@href]"):
        url = urljoin(base, a.get("href")).split("#")[0]
        text = " ".join(a.text_content().split())
        if urlsplit(url).netloc == host and url != base and url not in seen and len(text) > 15:
            seen.add(url)
            rows.append((url, text, ""))
    return rows


def from_sitemap(url: str) -> list[tuple[str, str, str]]:
    return [(u, "", "") for u in sitemaps.sitemap_search(url)]


def discover(client: httpx.Client, url: str, mode: str) -> tuple[str, list[tuple[str, str, str]]]:
    if mode == "sitemap":
        return "sitemap", from_sitemap(url)
    resp = client.get(url)
    resp.raise_for_status()
    if mode in ("auto", "feed") and (rows := from_feed(resp.content)):
        return "feed", rows
    if mode == "links":
        return "links", from_links(resp.text, str(resp.url))
    for feed_url in feed_candidates(resp.text, str(resp.url)):
        feed = client.get(feed_url)
        if feed.status_code == 200 and (rows := from_feed(feed.content)):
            return f"feed {feed_url}", rows
    if mode == "feed":
        raise ValueError("no feed found; try --mode sitemap or --mode links")
    return "sitemap", from_sitemap(url)


def write_tsv(rows: list[tuple[str, str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    clean = (lambda s: s.replace("\t", " ").replace("\n", " ").strip())
    lines = ["url\ttitle\tdate"] + ["\t".join(clean(c) for c in row) for row in rows]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--mode", choices=["auto", "feed", "sitemap", "links"], default="auto")
    parser.add_argument("--match", help="keep URLs matching this regex")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        with httpx.Client(follow_redirects=True, timeout=30, headers=HEADERS) as client:
            how, rows = discover(client, args.url, args.mode)
    except (httpx.HTTPError, ValueError) as exc:
        sys.exit(f"error: {args.url}: {exc}")
    if args.match:
        rows = [r for r in rows if re.search(args.match, r[0])]
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        sys.exit(f"error: {args.url}: no articles found via {how}")
    out = args.out or Path("data/lists") / f"{slugify(urlsplit(args.url).netloc + urlsplit(args.url).path, 80)}.tsv"
    write_tsv(rows, out)
    print(f"ok {out}: {len(rows)} articles via {how}")


if __name__ == "__main__":
    main()
