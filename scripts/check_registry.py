"""Check that plugin folders, plugin.json files and marketplace.json entries agree.

    uv run scripts/check_registry.py

Catches what `claude plugin validate` does not: a plugin folder with no marketplace entry (or an
entry with no folder), names that differ between folder, plugin.json and entry, a `source` that
is not ./skills/<name>, a plugin with no skills, and a category the README builder doesn't know.
Descriptions are not compared: plugin.json and the marketplace entry differ on purpose.
"""

import argparse
import sys
from collections import Counter

from build_readme import CATEGORIES
from repo import load_json, load_marketplace, plugin_dirs, rel, report, skill_files


def check_entries(entries: list[dict]) -> list[str]:
    problems = []
    dupes = [n for n, c in Counter(e.get("name") for e in entries).items() if c > 1]
    problems += [
        f"marketplace.json: plugin {n!r} is listed more than once" for n in dupes
    ]
    for entry in entries:
        name = entry.get("name", "?")
        if entry.get("source") != f"./skills/{name}":
            problems.append(
                f"marketplace.json: {name}: source is {entry.get('source')!r}, expected './skills/{name}'"
            )
        if entry.get("category") not in CATEGORIES:
            problems.append(
                f"marketplace.json: {name}: category {entry.get('category')!r} is not one of {', '.join(CATEGORIES)}"
            )
        if not entry.get("description"):
            problems.append(
                f"marketplace.json: {name}: no description (the README catalog needs one)"
            )
    return problems


def check_folders(entry_names: set[str]) -> list[str]:
    problems = []
    for folder in plugin_dirs():
        manifest = folder / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            problems.append(f"{rel(folder)}: no .claude-plugin/plugin.json")
            continue
        declared = load_json(manifest).get("name")
        if declared != folder.name:
            problems.append(
                f"{rel(manifest)}: name {declared!r} does not match its folder {folder.name!r}"
            )
        if folder.name not in entry_names:
            problems.append(
                f"{rel(folder)}: not registered in .claude-plugin/marketplace.json"
            )
        if not skill_files(folder):
            problems.append(f"{rel(folder)}: no skills/<skill>/SKILL.md")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.parse_args(argv)

    entries = load_marketplace()["plugins"]
    names = {e.get("name") for e in entries}
    folders = {f.name for f in plugin_dirs()}
    problems = check_entries(entries) + check_folders(names)
    problems += [
        f"marketplace.json: {n!r} has no folder skills/{n}/"
        for n in sorted(names - folders)
    ]
    return report(
        problems,
        f"ok {len(entries)} plugins: folders, plugin.json and marketplace.json agree",
    )


if __name__ == "__main__":
    sys.exit(main())
