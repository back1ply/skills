# /// script
# requires-python = ">=3.12"
# dependencies = ["yt-dlp"]
# ///
"""List the videos in a playlist, channel, or single-video URL (metadata only, nothing downloaded).

Usage: uv run list_videos.py <url> [--out FILE] [--limit N] [--min-seconds N] [--no-shorts]
       uv run list_videos.py --search "raft consensus" [--limit 10]

Writes a TSV (video_id, duration_seconds, short, title, url) that fetch_video.py --list reads.
Default out: data/lists/<playlist or channel id>.tsv
Channel URLs (@handle) list the channel's regular videos; add /shorts or /streams for those tabs.
Shorts have no duration in flat listings, so --min-seconds keeps them unless --no-shorts is set.
"""

import argparse
import csv
import io
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError


def flat_listing(url: str) -> dict:
    opts: Any = {"extract_flat": "in_playlist", "skip_download": True, "quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return dict(ydl.extract_info(url, download=False))


def iter_videos(info: dict) -> Iterator[dict]:
    """Yield video entries, descending into nested playlists (channel tabs)."""
    if info.get("_type") not in ("playlist", "multi_video"):
        yield info
        return
    for entry in filter(None, info.get("entries") or []):
        yield from expand(entry)


def expand(entry: dict) -> Iterator[dict]:
    """A channel tab arrives either already expanded or as a link to list."""
    if "entries" in entry:
        yield from iter_videos(entry)
    elif entry.get("_type") == "playlist" or entry.get("ie_key") == "YoutubeTab":
        yield from iter_videos(flat_listing(entry.get("url") or entry["webpage_url"]))
    else:
        yield entry


def is_short(entry: dict) -> bool:
    return "/shorts/" in (entry.get("url") or "")


def keep(entry: dict, min_seconds: int, no_shorts: bool) -> bool:
    if no_shorts and is_short(entry):
        return False
    duration = entry.get("duration")
    return duration is None or duration >= min_seconds


def default_out(info: dict) -> Path:
    name = info.get("id") or info.get("channel_id") or "videos"
    if str(name).startswith("ytsearch") or " " in str(name):
        name = "search-" + (info.get("title") or "results")
    return Path("data/lists") / f"{re.sub(r'[^\w-]+', '_', str(name))}.tsv"


def write_tsv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["video_id", "duration_seconds", "short", "title", "url"])
        for r in rows:
            duration = "" if r.get("duration") is None else int(r["duration"])
            short = "yes" if is_short(r) else ""
            writer.writerow([r["id"], duration, short, r.get("title") or "", f"https://www.youtube.com/watch?v={r['id']}"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="video, playlist or channel URL (or the query, with --search)")
    parser.add_argument("--search", action="store_true", help="treat the argument as a YouTube search query")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--limit", type=int, default=0, help="keep only the first N videos (0 = all)")
    parser.add_argument("--min-seconds", type=int, default=0, help="drop videos shorter than this")
    parser.add_argument("--no-shorts", action="store_true", help="drop YouTube Shorts")
    return parser.parse_args()


def select(info: dict, args: argparse.Namespace) -> tuple[list[dict], int]:
    """Unique videos after filters and --limit, plus the count before filtering."""
    rows = list({e["id"]: e for e in iter_videos(info) if e.get("id")}.values())
    kept = [e for e in rows if keep(e, args.min_seconds, args.no_shorts)]
    return kept[: args.limit] if args.limit else kept, len(rows)


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    url = f"ytsearch{args.limit or 10}:{args.url}" if args.search else args.url
    try:
        info = flat_listing(url)
    except DownloadError as exc:
        sys.exit(f"error: cannot list {args.url}: {exc}")

    rows, total = select(info, args)
    if not rows:
        sys.exit(f"error: no videos left in {args.url} ({total} before filters)")
    out = args.out or default_out(info)
    write_tsv(rows, out)
    title = info.get("title") or info.get("channel") or args.url
    print(f"ok {len(rows)} of {total} videos | {title} -> {out}")


if __name__ == "__main__":
    main()
