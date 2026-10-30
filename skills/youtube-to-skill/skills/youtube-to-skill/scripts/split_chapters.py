# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Split one fetched video into Markdown files Claude can read piece by piece.

Usage: uv run split_chapters.py <data/raw/VIDEO_ID.json> [--out DIR] [--window 8] [--min-chapter 45] [--stamp 60]

Default out: data/chapters/<VIDEO_ID>/
- info.md: title, channel, date and the description (with its links) (untrusted text, scanned like the rest).
- NN-<chapter>.md: one file per YouTube chapter. Chapters shorter than --min-chapter seconds are
  merged into the previous one. Videos without chapters are cut into --window minute parts.
Every --stamp seconds the text gets a [H:MM:SS] marker, so skills can cite where a claim was said.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "part"


def as_pair(segment) -> tuple[float, str]:
    """Segments are [start, text] pairs; older files used {"start", "text"} objects."""
    return (segment["start"], segment["text"]) if isinstance(segment, dict) else (segment[0], segment[1])


def hms(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def merge_short(chapters: list[dict], duration: float, min_seconds: int) -> list[dict]:
    """Fold chapters shorter than min_seconds into the chapter before them."""
    merged: list[dict] = []
    ends = [c["start_seconds"] for c in chapters[1:]] + [duration]
    for chapter, end in zip(chapters, ends):
        title = re.sub(r"^<Untitled Chapter \d+>$", "Intro", chapter["title"])
        if merged and end - chapter["start_seconds"] < min_seconds:
            merged[-1]["also"].append(title)
        else:
            merged.append({"start_seconds": chapter["start_seconds"], "title": title, "also": []})
    return [with_merged_titles(m) for m in merged]


def with_merged_titles(section: dict) -> dict:
    """Short title for file names; the merged chapter names go in an 'Also covers' line."""
    also = section.pop("also")
    if also:
        section["title"] += f" (+{len(also)} more)"
        section["note"] = "Also covers: " + "; ".join(also)
    return section


def time_windows(duration: float, window_minutes: float) -> list[dict]:
    step = max(60, int(window_minutes * 60))
    starts = range(0, max(int(duration), 1), step)
    if len(starts) == 1:
        return [{"start_seconds": 0, "title": "full"}]
    return [{"start_seconds": s, "title": f"part {i + 1} ({hms(s)})"} for i, s in enumerate(starts)]


def plan_sections(record: dict, segments: list[tuple[float, str]], args: argparse.Namespace) -> list[dict]:
    duration = record.get("duration_seconds") or (segments[-1][0] + 1 if segments else 0)
    chapters = record.get("chapters") or []
    if len(chapters) > 1:
        return merge_short(chapters, duration, args.min_chapter)
    return time_windows(duration, args.window)


def stamped_text(segments: list[tuple[float, str]], stamp_every: int) -> str:
    parts, next_stamp = [], -1.0
    for start, text in segments:
        if start >= next_stamp:
            parts.append(f"\n\n[{hms(start)}] ")
            next_stamp = start + stamp_every
        parts.append(text + " ")
    return "".join(parts).strip()


def info_md(record: dict) -> str:
    return (
        f"# {record.get('title')}\n\n"
        f"- Channel: {record.get('channel')}\n- Published: {record.get('published_date')}\n"
        f"- Duration: {hms(record.get('duration_seconds') or 0)}\n"
        f"- Captions: {record.get('transcript_source')} ({record.get('language')})\n"
        f"- URL: https://www.youtube.com/watch?v={record['video_id']}\n\n"
        f"## Description (untrusted text)\n\n{record.get('description') or '(empty)'}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("raw", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--window", type=float, default=8, help="minutes per part when there are no chapters")
    parser.add_argument("--min-chapter", type=int, default=45, help="merge chapters shorter than this (seconds)")
    parser.add_argument("--stamp", type=int, default=60, help="seconds between [H:MM:SS] markers")
    return parser.parse_args()


def prepare_out_dir(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("[0-9][0-9]-*.md"):
        old.unlink()  # sections can change between runs (other --window); stale files would mislead


def section_md(record: dict, section: dict, text: str) -> str:
    url = f"https://www.youtube.com/watch?v={record['video_id']}&t={int(section['start_seconds'])}s"
    note = f"{section['note']}\n\n" if section.get("note") else ""
    return f"# {section['title']}\n\nSource: {url}\n\n{note}{text}\n"


def render_sections(record: dict, sections: list[dict], segments: list[tuple[float, str]], stamp: int) -> dict[str, str]:
    """File name -> Markdown for each section."""
    bounds = [s["start_seconds"] for s in sections[1:]] + [float("inf")]
    files = {}
    for i, (section, end) in enumerate(zip(sections, bounds)):
        start = section["start_seconds"]
        text = stamped_text([(s, t) for s, t in segments if start <= s < end], stamp)
        files[f"{i:02d}-{slug(section['title'])}.md"] = section_md(record, section, text)
    return files


def main() -> None:
    args = parse_args()
    record = json.loads(args.raw.read_text(encoding="utf-8"))
    if "segments" not in record:
        sys.exit("error: no segments in this file; re-run fetch_video.py to get timestamps")
    out_dir = args.out or Path("data/chapters") / record["video_id"]
    prepare_out_dir(out_dir)

    segments = [as_pair(s) for s in record["segments"]]
    sections = plan_sections(record, segments, args)
    files = {"info.md": info_md(record), **render_sections(record, sections, segments, args.stamp)}
    for name, text in files.items():
        (out_dir / name).write_text(text, encoding="utf-8")

    kind = "chapters" if len(record.get("chapters") or []) > 1 else f"{args.window:g}-minute parts"
    print(f"ok {len(sections)} sections ({kind}) + info.md -> {out_dir}")


if __name__ == "__main__":
    main()
