# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Triage table for fetched articles: type guess, size and token estimate.

Usage: uv run catalog.py [--list data/lists/<name>.tsv] [--out data/catalog.md]
Reads data/articles/*.json (or only the articles in --list) and writes a Markdown table.
The type is a guess from the title and URL; confirm it from the text before distilling.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from article_ids import article_id

ARTICLES = Path("data/articles")
TOKENS_PER_WORD = 1.35
TYPES = [
    ("postmortem", r"postmortem|post-mortem|incident|outage|retrospective|what went wrong|lessons learned"),
    ("benchmark", r"benchmark|\bvs\.?\b|versus|compar|faster|performance of"),
    ("tutorial", r"how to|tutorial|step[- ]by[- ]step|guide to|getting started|walkthrough|build a"),
    ("interview", r"interview|q&a|conversation with|podcast|ama\b"),
    ("reference", r"/docs?/|/reference/|/api/|documentation|cheat ?sheet|spec\b"),
    ("research", r"paper|study|research|survey|findings"),
    ("list", r"^\d+ |top \d+|\d+ (ways|tips|things|lessons|mistakes)"),
]


def guess_type(title: str, url: str) -> str:
    hay = f"{title} {url}".lower()
    return next((name for name, pattern in TYPES if re.search(pattern, hay)), "essay")


def load(ids: list[str] | None) -> list[dict]:
    paths = [ARTICLES / f"{i}.json" for i in ids] if ids else sorted(ARTICLES.glob("*.json"))
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths if p.exists()]


def table(records: list[dict]) -> str:
    rows = ["| # | Title | Site | Date | Type? | Words | ~Tokens | Id |", "|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(records, 1):
        title = (r.get("title") or "?").replace("|", "/")
        tokens = int(r["word_count"] * TOKENS_PER_WORD)
        rows.append(f"| {n} | [{title}]({r['url']}) | {r.get('sitename') or '?'} | {r.get('date') or '?'} | "
                    f"{guess_type(title, r['url'])} | {r['word_count']} | {tokens:,} | `{r['id']}` |")
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", type=Path, help="only articles from this TSV")
    parser.add_argument("--out", type=Path, default=Path("data/catalog.md"))
    args = parser.parse_args()

    ids = None
    if args.list:
        rows = args.list.read_text(encoding="utf-8").splitlines()[1:]
        ids = [article_id(r.split("\t")[0]) for r in rows if r.strip()]
    records = load(ids)
    if not records:
        sys.exit(f"error: no fetched articles in {ARTICLES} (run fetch_article.py first)")
    total = int(sum(r["word_count"] for r in records) * TOKENS_PER_WORD)
    missing = len(ids) - len(records) if ids else 0
    note = f" ({missing} listed articles not fetched yet)" if missing else ""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(f"# Article catalog\n\n{table(records)}\n\nTotal: ~{total:,} tokens{note}\n", encoding="utf-8")
    print(f"ok {args.out}: {len(records)} articles, ~{total:,} tokens{note}")


if __name__ == "__main__":
    main()
