"""Build README.md from scripts/readme_template.md and .claude-plugin/marketplace.json.

Usage (from the repo root):
    uv run scripts/build_readme.py           # write README.md
    uv run scripts/build_readme.py --check   # exit 1 if README.md is out of date (CI)

- {{catalog}} becomes one table per category, using each plugin's `category` and `description`.
  Plugins with their own README.md get a link to it.
- {{plugin_count}} and {{skill_count}} are counted from the repo.
- The <!-- video-skills --> and <!-- articles --> blocks are copied from the current README,
  because the youtube-to-skill and article-to-skill sources.py scripts write them there.

Fails if a plugin has no category or one not listed in CATEGORIES.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# category slug in marketplace.json -> README heading, in README order
CATEGORIES = {
    "data": "Data and BI",
    "dbt": "dbt",
    "code-quality": "Code quality and design",
    "agents": "Working with coding agents",
    "backend": "Backend, infrastructure, and security",
    "business": "Business",
    "skills": "Making and managing skills",
}
GENERATED_BLOCKS = ("video-skills", "articles")


def group_plugins(plugins: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {slug: [] for slug in CATEGORIES}
    bad = [
        f"{p['name']} ({p.get('category')})"
        for p in plugins
        if p.get("category") not in CATEGORIES
    ]
    if bad:
        sys.exit(
            f"error: missing or unknown category: {', '.join(bad)}\n       known: {', '.join(CATEGORIES)}"
        )
    for plugin in plugins:
        groups[plugin["category"]].append(plugin)
    return {slug: items for slug, items in groups.items() if items}


def catalog_row(plugin: dict) -> str:
    name = plugin["name"]
    text = plugin["description"]
    if Path("skills", name, "README.md").exists():
        text += f" ([README](skills/{name}/README.md))"
    return f"| `{name}` | {text} |"


def catalog_markdown(groups: dict[str, list[dict]]) -> str:
    sections = []
    for slug, plugins in groups.items():
        rows = [f"### {CATEGORIES[slug]}", "", "| Plugin | What it does |", "|---|---|"]
        rows += [catalog_row(p) for p in plugins]
        sections.append("\n".join(rows))
    return "\n\n".join(sections)


def count_skills(plugins: list[dict]) -> int:
    return sum(
        len(list(Path("skills", p["name"], "skills").glob("*/SKILL.md")))
        for p in plugins
    )


def copy_generated_blocks(text: str, current: str) -> str:
    for marker in GENERATED_BLOCKS:
        pattern = re.compile(
            rf"<!-- {marker}:start -->.*?<!-- {marker}:end -->", re.DOTALL
        )
        slot = pattern.search(text)
        if not slot:
            sys.exit(f"error: template has no <!-- {marker}:start/end --> block")
        old = pattern.search(current)
        if old:
            text = text[: slot.start()] + old.group(0) + text[slot.end() :]
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "--template", type=Path, default=Path("scripts/readme_template.md")
    )
    parser.add_argument(
        "--marketplace", type=Path, default=Path(".claude-plugin/marketplace.json")
    )
    parser.add_argument("--out", type=Path, default=Path("README.md"))
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the output is out of date; write nothing",
    )
    args = parser.parse_args(argv)

    plugins = json.loads(args.marketplace.read_text(encoding="utf-8"))["plugins"]
    groups = group_plugins(plugins)

    text = args.template.read_text(encoding="utf-8")
    text = text.replace("{{catalog}}", catalog_markdown(groups))
    text = text.replace("{{plugin_count}}", str(len(plugins)))
    text = text.replace("{{skill_count}}", str(count_skills(plugins)))
    current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
    text = copy_generated_blocks(text, current)

    if args.check:
        if current.replace("\r\n", "\n") != text:
            print(
                f"{args.out} is out of date: run uv run scripts/build_readme.py",
                file=sys.stderr,
            )
            return 1
        print(f"ok {args.out} is up to date")
        return 0
    args.out.write_text(text, encoding="utf-8", newline="\n")
    print(f"ok {len(plugins)} plugins in {len(groups)} categories -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
