# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Map skills to the YouTube videos they came from, and check every skill links its sources.

Usage: uv run sources.py [--skills skills] [--raw data/raw] [--readme README.md] [--marker skills]

Finds every SKILL.md under --skills (flat skills/<name>/ or nested plugin layouts like
skills/<plugin>/skills/<name>/), collects YouTube links (watch?v=, youtu.be/, shorts/) per skill,
and prints a video -> skills table. Skills with no video link are not video-derived and are skipped.
Titles, channels and dates come from <raw>/<id>.json when the transcript is kept there.
Warnings: a video-derived SKILL.md without a "## Sources" section, a video with no raw file.
--readme replaces the block between <!-- <marker>:start --> and <!-- <marker>:end --> with a table of
video-derived skills (skill, what it does, sources). Exits 1 if there are warnings.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

VIDEO_ID = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})")


def skill_videos(skill_dir: Path) -> list[str]:
    """Video ids linked from a skill's Markdown files, most-linked first."""
    counts = Counter(
        vid for f in skill_dir.rglob("*.md") for vid in VIDEO_ID.findall(f.read_text(encoding="utf-8"))
    )
    return [vid for vid, _ in counts.most_common()]


def description(skill_dir: Path) -> str:
    """First sentence of the SKILL.md description."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    first = re.split(r"(?<=\.)\s", match.group(1).strip(), maxsplit=1)[0] if match else ""
    return first.replace("|", "/")


def video_info(raw_dir: Path, vid: str) -> dict | None:
    path = raw_dir / f"{vid}.json"
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    return {k: record.get(k) for k in ("title", "channel", "published_date")}


def video_link(vid: str, info: dict | None) -> str:
    title = (info or {}).get("title") or vid
    return f"[{title.replace('|', '/')}](https://www.youtube.com/watch?v={vid})"


def skill_warnings(name: str, skill_dir: Path) -> list[str]:
    if "## Sources" not in (skill_dir / "SKILL.md").read_text(encoding="utf-8"):
        return [f"{name}: SKILL.md has no '## Sources' section"]
    return []


def video_table(by_video: dict[str, list[str]], infos: dict[str, dict | None]) -> str:
    rows = ["| Video | Channel | Date | Skills |", "|---|---|---|---|"]
    for vid, skills in by_video.items():
        info = infos[vid] or {}
        rows.append(f"| {video_link(vid, info)} | {info.get('channel') or '?'} | "
                    f"{info.get('published_date') or '?'} | {', '.join(f'`{s}`' for s in skills)} |")
    return "\n".join(rows)


def skills_table(skills: dict[str, list[str]], dirs: dict[str, Path], infos: dict[str, dict | None]) -> str:
    rows = ["| Skill | What it does | Sources |", "|---|---|---|"]
    for name, videos in skills.items():
        sources = "<br>".join(video_link(v, infos[v]) for v in videos)
        rows.append(f"| `{name}` | {description(dirs[name])} | {sources} |")
    return "\n".join(rows)


def update_readme(readme: Path, table: str, marker: str) -> None:
    START, END = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit(f"error: {readme} has no {START} ... {END} block")
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    readme.write_text(f"{head}{START}\n{table}\n{END}{tail}", encoding="utf-8")


def collect(args: argparse.Namespace) -> tuple[dict[str, list[str]], dict[str, Path], list[str], int]:
    """Per video-derived skill: linked video ids; skill folders; warnings; count of skipped skills."""
    found = {f.parent.name: f.parent for f in sorted(args.skills.rglob("SKILL.md"))}
    skills, dirs, warnings = {}, {}, []
    for name, d in found.items():
        videos = skill_videos(d)
        if not videos or name in args.ignore:
            continue
        skills[name], dirs[name] = videos, d
        warnings += skill_warnings(name, d)
    return skills, dirs, warnings, len(found) - len(skills)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills", type=Path, default=Path("skills"))
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--readme", type=Path, help="rewrite the skills table in this README")
    parser.add_argument("--marker", default="skills", help="README block name: <!-- NAME:start --> ... <!-- NAME:end -->")
    parser.add_argument("--ignore", default="youtube-to-skill", help="comma-separated skills to leave out")
    args = parser.parse_args()
    args.ignore = set(args.ignore.split(","))

    skills, dirs, warnings, skipped = collect(args)
    by_video: dict[str, list[str]] = {}
    for name, videos in skills.items():
        for vid in videos:
            by_video.setdefault(vid, []).append(name)
    infos = {vid: video_info(args.raw, vid) for vid in by_video}
    warnings += [f"{vid}: no {args.raw}/{vid}.json (transcript not kept)" for vid, info in infos.items() if info is None]

    print(video_table(by_video, infos))
    if args.readme:
        update_readme(args.readme, skills_table(skills, dirs, infos), args.marker)
    for w in warnings:
        print(f"WARN {w}")
    summary = f"{len(skills)} video skills ({skipped} others skipped), {len(by_video)} videos, {len(warnings)} warnings"
    if warnings:
        sys.exit(f"FAIL {summary}")
    print(f"ok {summary}" + (f" -> {args.readme}" if args.readme else ""))


if __name__ == "__main__":
    main()
