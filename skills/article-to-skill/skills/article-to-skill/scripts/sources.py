# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Map skills to the web articles they came from, and check each article's text is kept.

Usage: uv run sources.py [--skills skills] [--articles data/articles] [--readme README.md] [--marker articles]

Finds every SKILL.md under --skills (flat or plugin-nested layouts) and reads the links in its
"## Sources" section. Non-YouTube http(s) links there are article sources; skills with none are
not article-derived and are skipped. Prints an article -> skills table.
Warnings: an article with no <articles>/<id>.json (text not kept for re-checking).
--readme replaces the block between <!-- <marker>:start --> and <!-- <marker>:end --> with a table of
article-derived skills (skill, what it does, sources). Exits 1 if there are warnings.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from article_ids import article_id

SOURCES = re.compile(r"^## Sources\b.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
YOUTUBE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/", re.IGNORECASE)


def article_links(skill_md: Path) -> list[tuple[str, str]]:
    """(title, url) for each article linked in the SKILL.md Sources section, in order."""
    match = SOURCES.search(skill_md.read_text(encoding="utf-8"))
    if not match:
        return []
    seen, links = set(), []
    for title, url in LINK.findall(match.group(0)):
        if not YOUTUBE.match(url) and url not in seen:
            seen.add(url)
            links.append((title.replace("|", "/"), url))
    return links


def description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    first = re.split(r"(?<=\.)\s", match.group(1).strip(), maxsplit=1)[0] if match else ""
    return first.replace("|", "/")


def skills_table(skills: dict[str, tuple[Path, list[tuple[str, str]]]]) -> str:
    rows = ["| Skill | What it does | Sources |", "|---|---|---|"]
    for name, (md, links) in skills.items():
        sources = "<br>".join(f"[{t}]({u})" for t, u in links)
        rows.append(f"| `{name}` | {description(md)} | {sources} |")
    return "\n".join(rows)


def update_readme(readme: Path, table: str, marker: str) -> None:
    start, end = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    text = readme.read_text(encoding="utf-8")
    if start not in text or end not in text:
        sys.exit(f"error: {readme} has no {start} ... {end} block")
    head, rest = text.split(start, 1)
    readme.write_text(f"{head}{start}\n{table}\n{end}{rest.split(end, 1)[1]}", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills", type=Path, default=Path("skills"))
    parser.add_argument("--articles", type=Path, default=Path("data/articles"))
    parser.add_argument("--readme", type=Path)
    parser.add_argument("--marker", default="articles")
    args = parser.parse_args()

    found = sorted(args.skills.rglob("SKILL.md"))
    skills = {md.parent.name: (md, links) for md in found if (links := article_links(md))}
    by_url: dict[str, list[str]] = {}
    for name, (_, links) in skills.items():
        for _, url in links:
            by_url.setdefault(url, []).append(name)

    print("| Article | Kept as | Skills |\n|---|---|---|")
    warnings = []
    for url, names in by_url.items():
        kept = args.articles / f"{article_id(url)}.json"
        if not kept.exists():
            warnings.append(f"{url}: no {kept} (article text not kept)")
        title = json.loads(kept.read_text(encoding="utf-8")).get("title") if kept.exists() else None
        print(f"| [{title or url}]({url}) | `{kept.name if kept.exists() else '-'}` | {', '.join(names)} |")
    if args.readme:
        update_readme(args.readme, skills_table(skills), args.marker)
    for w in warnings:
        print(f"WARN {w}")
    summary = f"{len(skills)} article skills ({len(found) - len(skills)} others skipped), {len(by_url)} articles, {len(warnings)} warnings"
    if warnings:
        sys.exit(f"FAIL {summary}")
    print(f"ok {summary}" + (f" -> {args.readme}" if args.readme else ""))


if __name__ == "__main__":
    main()
