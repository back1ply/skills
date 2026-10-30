# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Make a triage table of fetched videos, so you can pick what is worth a skill before reading transcripts.

Usage: uv run catalog.py [--raw data/raw] [--list FILE.tsv] [--out data/catalog.md]

One row per video: date, title, duration, words, chapters, captions, links to code, a guessed type,
and a rough token count. Shorts show as short/<type>. --list limits the table to the videos in a list_videos.py TSV.
The type is a keyword guess from the title and length; confirm it from the transcript.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# First match wins. Patterns look at the lower-cased title.
TYPE_RULES = [
    ("postmortem", r"postmortem|post-mortem|outage|incident|hacked|breach|failures? overnight"),
    ("benchmark", r"\bi tested\b|benchmark|\bvs\.?\b|faster|slower|max out|how many users|which .* can handle"),
    ("tutorial", r"tutorial|course|crash course|build (?:a|an|your)|how to (?:build|make|set up|install)|step by step|\b101\b"),
    ("explainer", r"explained|what is|types of|concepts|system design|understand|everything you need"),
    ("advice", r"how to|tips|mistakes|career|land|promotion|offer|interview(?:ing)?|hired|degree|ranking|watch this"),
]


def title_type(title: str) -> str | None:
    return next((name for name, pattern in TYPE_RULES if re.search(pattern, title)), None)


def looks_like_interview(record: dict, title: str) -> bool:
    return (record.get("duration_seconds") or 0) >= 40 * 60 and bool(re.search(r"\||\s-\s|with |ft\.|feat", title))


def is_short(record: dict) -> bool:
    """yt-dlp marks Shorts; older raw files lack the field, so fall back to length."""
    if record.get("media_type"):
        return record["media_type"] == "short"
    return (record.get("duration_seconds") or 0) <= 180 and not record.get("chapters")


def guess_type(record: dict) -> str:
    title = (record.get("title") or "").lower()
    short = is_short(record)
    kind = title_type(title) or ("interview" if looks_like_interview(record, title) else None)
    if short:
        return f"short/{kind}" if kind else "short"
    return kind or "other"


def segment_text(segment) -> str:
    """Segments are [start, text] pairs; older files used {"start", "text"} objects."""
    return segment["text"] if isinstance(segment, dict) else segment[1]


def words(record: dict) -> int:
    return sum(len(segment_text(s).split()) for s in record.get("segments") or [])


def tokens_k(word_count: int) -> float:
    return round(word_count * 1.35 / 1000, 1)


def duration_text(seconds: int | None) -> str:
    if not seconds:
        return "?"
    h, rest = divmod(int(seconds or 0), 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}"


def row(record: dict) -> str:
    w = words(record)
    cells = [
        record.get("published_date") or "?", f"`{record['video_id']}`", (record.get("title") or "").replace("|", "/"),
        duration_text(record.get("duration_seconds")), f"{w:,}", str(len(record.get("chapters") or [])),
        record.get("transcript_source") or "?", str(len(record.get("repo_urls") or [])),
        guess_type(record), f"~{tokens_k(w)}K",
    ]
    return "| " + " | ".join(cells) + " |"


def read_ids(list_file: Path | None) -> set[str] | None:
    if not list_file:
        return None
    with list_file.open(encoding="utf-8", newline="") as f:
        return {r[0] for r in csv.reader(f, delimiter="\t") if r and r[0] != "video_id"}


def load(raw_dir: Path, only: set[str] | None) -> list[dict]:
    paths = [p for p in sorted(raw_dir.glob("*.json")) if only is None or p.stem in only]
    records = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    return sorted(records, key=lambda r: r.get("published_date") or "", reverse=True)


def missing_note(only: set[str] | None, found: int) -> str:
    gap = len(only) - found if only else 0
    return f" ({gap} listed videos not fetched yet)" if gap > 0 else ""


HEADER = ("| Date | ID | Title | Length | Words | Chapters | Captions | Repos | Type (guess) | Tokens |\n"
          "|---|---|---|---|---|---|---|---|---|---|")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--list", type=Path, help="only videos in this list_videos.py TSV")
    parser.add_argument("--out", type=Path, default=Path("data/catalog.md"))
    args = parser.parse_args()

    only = read_ids(args.list)
    records = load(args.raw, only)
    if not records:
        sys.exit(f"error: no fetched videos in {args.raw} (filter: {args.list or 'none'})")

    total = sum(words(r) for r in records)
    missing = missing_note(only, len(records))
    body = "\n".join(row(r) for r in records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(f"# Catalog\n\n{len(records)} videos, {total:,} words{missing}\n\n{HEADER}\n{body}\n", encoding="utf-8")
    print(f"ok {len(records)} videos, {total:,} words (~{tokens_k(total)}K tokens){missing} -> {args.out}")


if __name__ == "__main__":
    main()
