# /// script
# requires-python = ">=3.12"
# dependencies = ["yt-dlp", "youtube-transcript-api"]
# ///
"""Fetch YouTube videos' metadata and transcripts (text only, never the video).

Usage: uv run fetch_video.py <video_id_or_url>... [--list FILE.tsv] [--out data/raw]
                             [--lang en,es] [--via auto|api|ytdlp] [--delay 3] [--refresh]
                             [--translate [FROM]]

Writes <out>/<video_id>.json per video: metadata plus "segments" as [start_seconds, text] pairs.
Cached files are skipped unless --refresh. Prints one ok/error line per video; a failed video does
not stop the rest, but the exit code is 1 if any failed.
--list reads the first column of a list_videos.py TSV.
Transcript order (--via auto): youtube-transcript-api, then yt-dlp subtitles. YouTube blocks bulk
requests, so --delay waits between network fetches. If both methods are blocked, set
YTDLP_COOKIES_BROWSER=chrome (or firefox, edge) so yt-dlp uses your browser's cookies.
Some uploads have caption tracks only in other languages. The error then lists them; --translate
fetches YouTube's machine translation into the first --lang (from FROM, or the first track found),
recorded as transcript_source "translated from <code>". Translated wording drifts: fine for ideas
and timestamps, not for exact quotes or names.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

URL = re.compile(r"https?://[^\s)\]>\"'<]+")
VIA_NAMES = {"api": "youtube-transcript-api", "ytdlp": "yt-dlp"}
REPO_HOSTS = ("github.com", "gitlab.com", "codeberg.org", "replit.com", "bitbucket.org")


def parse_video_id(arg: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})", arg)
    if match:
        return match.group(1)
    if re.fullmatch(r"[\w-]{11}", arg):
        return arg
    raise ValueError(f"cannot find a video id in {arg!r} (playlists and channels: use list_videos.py)")


def read_list(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    return [r[0] for r in rows if r and r[0] != "video_id" and not r[0].startswith("#")]


def ydl_opts() -> Any:
    # no_warnings hides yt-dlp's JS-challenge notices; they only affect video formats, which we never download.
    opts: Any = {"skip_download": True, "quiet": True, "no_warnings": True}
    if browser := os.environ.get("YTDLP_COOKIES_BROWSER"):
        opts["cookiesfrombrowser"] = (browser,)
    return opts


def fetch_info(video_id: str) -> dict:
    with yt_dlp.YoutubeDL(ydl_opts()) as ydl:
        return dict(ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False))


def find_links(description: str) -> list[str]:
    urls = (u.rstrip(".,;") for u in URL.findall(description))
    return list(dict.fromkeys(urls))


def is_repo(url: str) -> bool:
    host = re.sub(r"^https?://(?:www\.)?", "", url).split("/")[0].lower()
    return host in REPO_HOSTS


def metadata(info: dict) -> dict:
    upload = info.get("upload_date") or ""
    description = info.get("description") or ""
    links = find_links(description)
    return {
        "title": info.get("title"),
        "channel": info.get("channel"),
        "channel_id": info.get("channel_id"),
        "published_date": f"{upload[:4]}-{upload[4:6]}-{upload[6:]}" if upload else None,
        "duration_seconds": info.get("duration"),
        "media_type": info.get("media_type"),  # "short" for YouTube Shorts
        "repo_urls": [u for u in links if is_repo(u)],
        "links": links,
        "chapters": [
            {"start_seconds": int(c["start_time"]), "title": c["title"]}
            for c in info.get("chapters") or []
        ],
        "description": description,
    }


def via_api(video_id: str, langs: list[str], translate: str | None = None) -> tuple[list[dict], str, str]:
    """Return (segments, source, lang) from youtube-transcript-api. Manual captions beat generated.

    With translate set, a video with no track in langs is machine-translated into langs[0].
    """
    transcripts = YouTubeTranscriptApi().list(video_id)
    source = None
    try:
        transcript = transcripts.find_manually_created_transcript(langs)
    except Exception:  # noqa: BLE001 - library raises several types; fall back to generated captions
        try:
            transcript = transcripts.find_generated_transcript(langs)
        except Exception:  # noqa: BLE001 - no track in langs; maybe translatable
            transcript, source = translated(transcripts, langs[0], translate)
    segments = [
        {"start": round(s.start, 1), "text": s.text.replace("\n", " ").strip()}
        for s in transcript.fetch()
        if s.text.strip()
    ]
    source = source or ("generated" if transcript.is_generated else "manual")
    return segments, source, transcript.language_code


def translated(transcripts: Any, target: str, translate: str | None) -> tuple[Any, str]:
    """Pick a translatable track and translate it to target, or raise listing what exists."""
    tracks = sorted(transcripts, key=lambda t: t.is_generated)  # manual tracks first
    codes = ",".join(t.language_code for t in tracks) or "none"
    usable = [t for t in tracks if t.is_translatable and (translate in (None, "auto") or t.language_code == translate)]
    if translate is None or not usable:
        hint = "rerun with --translate, or --lang <code> and read it as is" if any(t.is_translatable for t in tracks) else "rerun with --lang <code>"
        raise LookupError(f"no {target} track; available: {codes} ({hint})")
    source = usable[0]
    return source.translate(target), f"translated from {source.language_code}"


def json3_segments(data: dict) -> list[dict]:
    segments = []
    for event in data.get("events", []):
        text = "".join(seg.get("utf8", "") for seg in event.get("segs") or []).replace("\n", " ").strip()
        if text:
            segments.append({"start": round(event.get("tStartMs", 0) / 1000, 1), "text": text})
    return segments


def find_track(tracks: dict, lang: str) -> dict | None:
    # "en" also matches regional/original variants such as "en-US" or "en-orig".
    key = next((k for k in tracks if k == lang or k.startswith(f"{lang}-")), None)
    fmt = next((f for f in tracks.get(key, []) if f.get("ext") == "json3"), None) if key else None
    return {"key": key, **fmt} if fmt else None


def via_ytdlp(info: dict, langs: list[str]) -> tuple[list[dict], str, str]:
    """Return (segments, source, lang) from yt-dlp's subtitle tracks (json3 format)."""
    for source, tracks in (("manual", info.get("subtitles") or {}), ("generated", info.get("automatic_captions") or {})):
        for lang in langs:
            track = find_track(tracks, lang)
            if not track:
                continue
            with yt_dlp.YoutubeDL(ydl_opts()) as ydl:
                data = json.loads(ydl.urlopen(track["url"]).read().decode("utf-8"))
            if segments := json3_segments(data):
                return segments, source, str(track["key"])
    raise LookupError(f"no subtitles in {langs} via yt-dlp")


def first_line(exc: Exception) -> str:
    text = str(exc).strip()
    return f"{type(exc).__name__}: {text.splitlines()[0] if text else ''}"


def fetch_transcript(
    video_id: str, info: dict, langs: list[str], via: str, translate: str | None = None
) -> tuple[list[dict], str, str, str]:
    """Try each method in order; return (segments, source, lang, method) or raise with every error."""
    methods = [("youtube-transcript-api", lambda: via_api(video_id, langs, translate)), ("yt-dlp", lambda: via_ytdlp(info, langs))]
    if via != "auto":
        methods = [m for m in methods if m[0] == VIA_NAMES[via]]
    errors = []
    for name, method in methods:
        try:
            return (*method(), name)
        except Exception as exc:  # noqa: BLE001 - blocked IP, no captions, etc.; try the next method
            errors.append(f"{name}: {first_line(exc)}")
    raise LookupError(f"no transcript in {langs}. " + " | ".join(errors))


def to_json(record: dict, segments: list[dict]) -> str:
    """Metadata pretty-printed, then the transcript stored once as [start, text] pairs, one per line.

    One segment per line keeps the file compact and makes git diffs readable.
    """
    head = json.dumps(record, ensure_ascii=False, indent=2)[:-2]  # drop the closing "\n}"
    lines = ",\n".join("    " + json.dumps([s["start"], s["text"]], ensure_ascii=False) for s in segments)
    return f'{head},\n  "segments": [\n{lines}\n  ]\n}}\n'


def fetch_one(video_id: str, args: argparse.Namespace) -> str:
    """Fetch and save one video. Returns the ok line; raises on failure."""
    info = fetch_info(video_id)
    record = {"video_id": video_id, **metadata(info)}
    segments, record["transcript_source"], record["language"], record["fetched_via"] = fetch_transcript(
        video_id, info, args.langs, args.via, args.translate
    )
    out_path = args.out / f"{video_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(to_json(record, segments), encoding="utf-8")
    words = sum(len(s["text"].split()) for s in segments)
    return (f"ok {video_id} | {record['title']} | {record['channel']} | {record['published_date']} | {words} words "
            f"({record['transcript_source']}, {record['language']}, via {record['fetched_via']}) -> {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("videos", nargs="*", help="video ids or URLs")
    parser.add_argument("--list", type=Path, help="TSV from list_videos.py (first column = video id)")
    parser.add_argument("--out", type=Path, default=Path("data/raw"))
    parser.add_argument("--lang", default="en", help="comma-separated language codes, in priority order")
    parser.add_argument("--via", choices=["auto", "api", "ytdlp"], default="auto")
    parser.add_argument("--delay", type=float, default=3.0, help="seconds to wait between network fetches")
    parser.add_argument("--refresh", action="store_true", help="re-fetch even if the JSON already exists")
    parser.add_argument("--translate", nargs="?", const="auto", metavar="FROM",
                        help="if no track in --lang exists, machine-translate one (optionally from FROM) into it")
    args = parser.parse_args()
    args.langs = [code.strip() for code in args.lang.split(",") if code.strip()]
    if not args.videos and not args.list:
        parser.error("give video ids/URLs or --list FILE")
    return args


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    inputs = args.videos + (read_list(args.list) if args.list else [])
    failed = 0
    fetched = 0
    for item in dict.fromkeys(inputs):
        try:
            video_id = parse_video_id(item)
            if (args.out / f"{video_id}.json").exists() and not args.refresh:
                print(f"ok {video_id} | cached -> {args.out / f'{video_id}.json'} (use --refresh to re-fetch)")
                continue
            if fetched:
                time.sleep(args.delay)
            fetched += 1
            print(fetch_one(video_id, args), flush=True)
        except Exception as exc:  # noqa: BLE001 - one bad video must not stop the batch
            failed += 1
            print(f"error: {item}: {first_line(exc)}", flush=True)
    if failed:
        sys.exit(f"FAIL {failed} of {len(inputs)} videos had errors")


if __name__ == "__main__":
    main()
