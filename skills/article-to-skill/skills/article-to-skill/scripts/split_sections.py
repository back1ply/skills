# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Split a fetched article into section files with a citation link on each.

Usage: uv run split_sections.py data/articles/<id>.json [--level 2] [--window 1500] [--min-words 80]
  -> data/sections/<id>/info.md + NN-<slug>.md

Splits at headings of --level (## by default; falls back to ### if there are none, then to
--window-word parts). A section over 2x --window words is split again at the next heading level. Sections shorter than --min-words are merged into the one before.
Each section starts with `Cite: <url>#<anchor>`: the page's own heading id when known, else a
text fragment (#:~:text=...) that Chrome, Edge and Safari scroll to.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

from article_ids import slugify

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MD_INLINE = re.compile(r"[*_`]|\[([^\]]*)\]\([^)]*\)")


def plain(text: str) -> str:
    return " ".join(MD_INLINE.sub(lambda m: m.group(1) or "", text).split())


def cite(url: str, heading: str, anchors: dict[str, str]) -> str:
    if not heading:
        return url
    if hid := anchors.get(heading):
        return f"{url}#{hid}"
    return f"{url}#:~:text={quote(heading, safe='')}"


def split_at(lines: list[str], level: int) -> list[tuple[str, list[str]]]:
    """[(heading, lines)] split at headings of exactly `level`; text before the first is '' (intro)."""
    parts: list[tuple[str, list[str]]] = [("", [])]
    for line in lines:
        m = HEADING.match(line)
        if m and len(m.group(1)) == level:
            parts.append((plain(m.group(2)), [line]))
        else:
            parts[-1][1].append(line)
    return [(h, body) for h, body in parts if h or "".join(body).strip()]


def split_window(lines: list[str], window: int) -> list[tuple[str, list[str]]]:
    parts, current, words = [], [], 0
    for line in lines:
        current.append(line)
        words += len(line.split())
        if words >= window and not line.strip():
            parts.append(("", current))
            current, words = [], 0
    if current:
        parts.append(("", current))
    return parts


def merge_small(parts: list[tuple[str, list[str]]], min_words: int) -> list[tuple[str, list[str]]]:
    merged: list[tuple[str, list[str]]] = []
    for heading, body in parts:
        small = (lambda lines: len(" ".join(lines).split()) < min_words)
        if merged and (small(merged[-1][1]) or small(body)):
            prev_heading, prev_body = merged.pop()
            heading, body = prev_heading or heading, prev_body + body
        merged.append((heading, body))
    return merged


def split_large(parts: list[tuple[str, list[str]]], level: int, window: int, min_words: int) -> list[tuple[str, list[str]]]:
    """Split sections longer than 2x --window again at the next heading level."""
    out = []
    for heading, body in parts:
        sub = split_at(body, level + 1) if len(" ".join(body).split()) > 2 * window else []
        if sum(1 for h, _ in sub if h) >= 2:
            first_heading, first_body = sub[0]
            out += merge_small([(first_heading or heading, first_body), *sub[1:]], min_words)
        else:
            out.append((heading, body))
    return out


def sections(text: str, level: int, window: int, min_words: int) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    for lvl in (level, level + 1):
        parts = split_at(lines, lvl)
        if sum(1 for h, _ in parts if h) >= 2:
            return split_large(merge_small(parts, min_words), lvl, window, min_words)
    return split_window(lines, window)


def info_md(rec: dict, parts: list[tuple[str, str, int]]) -> str:
    domains = sorted({re.sub(r"^https?://([^/]+).*", r"\1", u) for u in rec.get("links", [])})
    lines = [
        f"# {rec.get('title') or '?'}", "",
        f"- URL: {rec['url']}", f"- Author: {rec.get('author') or '?'}", f"- Site: {rec.get('sitename') or '?'}",
        f"- Date: {rec.get('date') or '?'}", f"- Words: {rec['word_count']}", f"- Source: {rec.get('source')}",
        f"- Description: {rec.get('description') or ''}", "", "## Sections", "",
        *[f"- `{name}` ({words} words): {link}" for name, link, words in parts],
        "", "## Linked domains", "", *[f"- {d}" for d in domains],
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("article", type=Path)
    parser.add_argument("--level", type=int, default=2)
    parser.add_argument("--window", type=int, default=1500)
    parser.add_argument("--min-words", type=int, default=80)
    args = parser.parse_args()

    if not args.article.exists():
        sys.exit(f"error: {args.article} not found")
    rec = json.loads(args.article.read_text(encoding="utf-8"))
    url, anchors = rec.get("final_url") or rec["url"], rec.get("anchors", {})
    out = Path("data/sections") / rec["id"]
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.md"):
        old.unlink()

    index = []
    for n, (heading, body) in enumerate(sections(rec["text"], args.level, args.window, args.min_words)):
        name = f"{n:02d}-{slugify(heading or ('intro' if n == 0 else f'part-{n}'), 40)}.md"
        link = cite(url, heading, anchors)
        text = "\n".join(body).strip()
        (out / name).write_text(f"Cite: {link}\n\n{text}\n", encoding="utf-8")
        index.append((name, link, len(text.split())))
    (out / "info.md").write_text(info_md(rec, index), encoding="utf-8")
    print(f"ok {out}: {len(index)} sections")


if __name__ == "__main__":
    main()
