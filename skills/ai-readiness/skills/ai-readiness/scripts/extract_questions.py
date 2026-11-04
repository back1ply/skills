# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Fetch the live howreadyfor.ai assessment and write each dimension's text as Markdown.

Usage: uv run scripts/extract_questions.py <out.md> [--html <saved page.html>]

One `## <slug>` section per dimension: framing, question, the five levels and each tell.
The live wording wins over the skill's cluster files; diff the two to spot drift.
"""

import argparse
import html
import re
import sys
import urllib.request

ASSESS_URL = "https://howreadyfor.ai/assess/"
USER_AGENT = "ai-readiness-skill/1.0"


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def section_text(section_html: str) -> str:
    text = re.sub(
        r"<(script|style|svg)[^>]*>.*?</\1>", " ", section_html, flags=re.DOTALL
    )
    text = re.sub(r"</(p|h2|h3|li|div|section|span)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    lines = (
        re.sub(r"\s+", " ", html.unescape(line)).strip() for line in text.splitlines()
    )
    return "\n".join(line for line in lines if line)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract the live howreadyfor.ai questions, levels and tells."
    )
    parser.add_argument("out", help="Markdown file to write")
    parser.add_argument(
        "--html", help="read a saved copy of the page instead of fetching it"
    )
    args = parser.parse_args()

    if args.html:
        with open(args.html, encoding="utf-8") as saved:
            page = saved.read()
    else:
        page = fetch(ASSESS_URL)
    declared = re.search(r'data-slugs="([^"]+)"', page)
    if not declared:
        print("error: no data-slugs list on the page; the page layout may have changed")
        return 1
    slugs = declared.group(1).split(",")
    sections = dict(
        re.findall(
            r'<section data-step="([a-z0-9-]+)"[^>]*>(.*?)</section>',
            page,
            flags=re.DOTALL,
        )
    )
    missing = [slug for slug in slugs if slug not in sections]
    if missing:
        print(f"error: declared dimensions with no section: {', '.join(missing)}")
        return 1
    dimensions = [(slug, sections[slug]) for slug in slugs]
    with open(args.out, "w", encoding="utf-8", newline="\n") as out:
        out.writelines(
            f"## {slug}\n\n{section_text(body)}\n\n" for slug, body in dimensions
        )
    print(f"ok {len(dimensions)} dimensions -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
