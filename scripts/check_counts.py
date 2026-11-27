"""Check that item counts written in prose still match the files they count.

    uv run scripts/check_counts.py

Two kinds of claim, both from past fixes ("chore(python-cli-packaging): plugin.json item count 99"):
1. A skill with references/checklist.md whose rows carry stable IDs (`| PKG-01 |`): every
   "N items" or "N-item" in its SKILL.md, plugin.json, or marketplace entry must equal the
   number of unique IDs.
2. AGENTS.md ("copies N of its checklist rows") and python-cli-packaging's checklist
   ("**Shared rows:** N items") must equal the number of shared items in scripts/sync_shared.py.
Other numbers are not checked; add a claim here when one drifts.
"""

import argparse
import re
import sys
from pathlib import Path

from repo import (
    ROOT,
    load_json,
    load_marketplace,
    plugin_dirs,
    rel,
    report,
    skill_files,
)

ID_ROW = re.compile(r"^\| *`?([A-Z]+-\d{2})`? *\|", re.MULTILINE)
ITEM_CLAIM = re.compile(r"\b(\d+)[- ]items?\b")
SHARED_CLAIMS = {
    ROOT / "AGENTS.md": re.compile(r"copies (\d+) of its checklist rows"),
    ROOT
    / "skills/python-cli-packaging/skills/python-cli-packaging/references/checklist.md": re.compile(
        r"^\*\*Shared rows:\*\* (\d+) items", re.MULTILINE
    ),
}


def checklist_ids(skill: Path) -> tuple[Path, set[str]]:
    """The skill's references/checklist.md and its stable IDs (empty if none)."""
    checklist = skill.parent / "references" / "checklist.md"
    if not checklist.exists():
        return checklist, set()
    return checklist, set(ID_ROW.findall(checklist.read_text(encoding="utf-8")))


def claim_texts(plugin: Path, skill: Path, entries: dict[str, str]) -> dict[str, str]:
    """Every text that may state the checklist's item count, keyed by where it lives."""
    texts = {rel(skill): skill.read_text(encoding="utf-8")}
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        texts[rel(manifest)] = load_json(manifest).get("description", "")
    texts[f"marketplace.json ({plugin.name})"] = entries.get(plugin.name, "")
    return texts


def wrong_claims(texts: dict[str, str], checklist: Path, count: int) -> list[str]:
    return [
        f"{where}: says {claim} items, {rel(checklist)} has {count}"
        for where, text in texts.items()
        for claim in ITEM_CLAIM.findall(text)
        if int(claim) != count
    ]


def checklist_claims(entries: dict[str, str]) -> tuple[list[str], int]:
    """Return (problems, checklists checked) for claim kind 1."""
    problems, checked = [], 0
    skills = [
        (plugin, skill) for plugin in plugin_dirs() for skill in skill_files(plugin)
    ]
    for plugin, skill in skills:
        checklist, ids = checklist_ids(skill)
        if not ids:
            continue  # no checklist, or one without stable IDs: no count claim
        checked += 1
        problems += wrong_claims(
            claim_texts(plugin, skill, entries), checklist, len(ids)
        )
    return problems, checked


def shared_rows_claim() -> list[str]:
    """Claim kind 2: prose counts of shared rows vs the SHARED map in scripts/sync_shared.py."""
    sync = (ROOT / "scripts" / "sync_shared.py").read_text(encoding="utf-8")
    block = re.search(r"^SHARED = \{(.*?)^\}", sync, re.MULTILINE | re.DOTALL)
    if not block:
        return ["scripts/sync_shared.py: no SHARED = {...} block to count"]
    shared = len(re.findall(r'^\s*"[A-Z]+-\d{2}":', block.group(1), re.MULTILINE))
    problems = []
    for path, pattern in SHARED_CLAIMS.items():
        claim = pattern.search(path.read_text(encoding="utf-8"))
        if not claim:
            problems.append(
                f"{rel(path)}: shared-row count sentence not found; update SHARED_CLAIMS"
            )
        elif int(claim.group(1)) != shared:
            problems.append(
                f"{rel(path)}: says {claim.group(1)} shared rows, scripts/sync_shared.py has {shared}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.parse_args(argv)

    entries = {
        e["name"]: e.get("description", "") for e in load_marketplace()["plugins"]
    }
    problems, checked = checklist_claims(entries)
    problems += shared_rows_claim()
    return report(
        problems,
        f"ok counts match in {checked} checklists and {len(SHARED_CLAIMS)} shared-row notes",
    )


if __name__ == "__main__":
    sys.exit(main())
