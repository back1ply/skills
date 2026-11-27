# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Scaffold a new plugin: skills/<name>/, its plugin.json, its SKILL.md, and a marketplace entry.

    uv run scripts/new_plugin.py NAME --category agents --description "What it does. Use when ..."
    uv run scripts/new_plugin.py NAME --category agents --description "..." --from path/to/SKILL.md

--description is the catalog line (marketplace.json and the README): what it does, then "Use when".
--summary is the shorter plugin.json line; it defaults to --description up to " Use ".
--from copies an existing SKILL.md (its frontmatter `name` must equal NAME); without it a stub is
written for you to fill in. Nothing is written if any check fails. This does not rebuild the
README or run the checks; `just new` chains those.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

from build_readme import CATEGORIES
from repo import (
    MARKETPLACE,
    NAME_MAX,
    NAME_RE,
    PLUGINS_DIR,
    PRIVATE,
    REPO_URL,
    load_marketplace,
    read_frontmatter,
    rel,
    skill_files,
)

# Claude Code refuses plugin names with these prefixes, or equal to these words.
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_NAMES = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}
STUB = """---
name: {name}
description: >-
  {description}
---

# {name}

TODO: the instructions. Keep this file under 500 lines; move detail to references/.
"""


def is_valid_name(name: str) -> bool:
    return len(name) <= NAME_MAX and bool(NAME_RE.match(name))


def is_reserved(name: str) -> bool:
    return name.startswith(RESERVED_PREFIXES) or name in RESERVED_NAMES | PRIVATE


def name_problems(name: str, marketplace: dict) -> list[str]:
    """Spec rules first, then clashes with what the repo already has."""
    listed = {e.get("name") for e in marketplace["plugins"]}
    skills = {f.parent.name for f in skill_files()}
    rules = (
        (
            not is_valid_name(name),
            f"name {name!r}: use 1-{NAME_MAX} chars of a-z, 0-9 and single hyphens",
        ),
        (is_reserved(name), f"name {name!r} is reserved"),
        ((PLUGINS_DIR / name).exists(), f"skills/{name}/ already exists"),
        (name in listed, f"marketplace.json already lists {name!r}"),
        (
            name in skills,
            f"a skill named {name!r} already exists (skills.sh keeps only the first)",
        ),
    )
    return [message for fails, message in rules if fails]


def source_problems(source: Path | None, name: str) -> list[str]:
    if source is None:
        return []
    if not source.is_file():
        return [f"--from {source}: no such file"]
    fm, error = read_frontmatter(source)
    if fm is None:
        return [f"--from {source}: {error}"]
    if fm.get("name") != name:
        return [
            f"--from {source}: frontmatter name is {fm.get('name')!r}, expected {name!r}"
        ]
    return []


def plugin_manifest(name: str, summary: str, keywords: list[str]) -> dict:
    return {
        "name": name,
        "description": summary,
        "author": {"name": "back1ply"},
        "homepage": REPO_URL,
        "repository": REPO_URL,
        "license": "MIT",
        "keywords": keywords,
    }


def write_plugin(args: argparse.Namespace, summary: str, marketplace: dict) -> Path:
    plugin = PLUGINS_DIR / args.name
    skill_dir = plugin / "skills" / args.name
    skill_dir.mkdir(parents=True)
    (plugin / ".claude-plugin").mkdir()
    manifest = plugin_manifest(args.name, summary, args.keywords)
    (plugin / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    skill = skill_dir / "SKILL.md"
    if args.source:
        shutil.copyfile(args.source, skill)
    else:
        skill.write_text(
            STUB.format(name=args.name, description=args.description),
            encoding="utf-8",
            newline="\n",
        )
    marketplace["plugins"].append(
        {
            "name": args.name,
            "description": args.description,
            "source": f"./skills/{args.name}",
            "license": "MIT",
            "keywords": args.keywords,
            "category": args.category,
        }
    )
    MARKETPLACE.write_text(
        json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return skill


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("name", help="plugin and skill name, kebab-case")
    parser.add_argument(
        "--category",
        required=True,
        choices=list(CATEGORIES),
        help="README catalog section",
    )
    parser.add_argument(
        "--description",
        required=True,
        help='catalog line: what it does, then "Use when ..."',
    )
    parser.add_argument(
        "--summary",
        help="plugin.json description (default: --description up to ' Use ')",
    )
    parser.add_argument("--keywords", nargs="*", default=[], help="plugin keywords")
    parser.add_argument(
        "--from", dest="source", type=Path, help="existing SKILL.md to copy in"
    )
    args = parser.parse_args(argv)

    marketplace = load_marketplace()
    problems = name_problems(args.name, marketplace) + source_problems(
        args.source, args.name
    )
    if problems:
        print(*problems, sep="\n", file=sys.stderr)
        return 1
    summary = args.summary or args.description.split(" Use ")[0].rstrip(".")
    skill = write_plugin(args, summary, marketplace)
    print(
        f"ok created skills/{args.name}/ and its marketplace entry; edit {rel(skill)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
