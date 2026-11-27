"""CNT: counts written in prose still match the files they count.

Past fix: "chore(python-cli-packaging): plugin.json item count 99". Other numbers are not
checked; add a rule here when one drifts.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from skills_repo import config
from skills_repo.core import shared_rules
from skills_repo.findings import Finding
from skills_repo.model import Plugin, Repo, Skill
from skills_repo.rules import rule

ID_ROW = re.compile(r"^\| *`?([A-Z]+-\d{2})`? *\|", re.MULTILINE)
ITEM_CLAIM = re.compile(r"\b(\d+)[- ]items?\b")


def _checklist_ids(skill: Skill) -> tuple[Path, set[str]]:
    checklist = skill.path.parent / "references" / "checklist.md"
    if not checklist.is_file():
        return checklist, set()
    return checklist, set(ID_ROW.findall(checklist.read_text(encoding="utf-8")))


def _claim_texts(repo: Repo, plugin: Plugin, skill: Skill) -> dict[str, str]:
    """Every text that may state the checklist's item count, keyed by where it lives."""
    texts = {repo.rel(skill.path): skill.text}
    if plugin.manifest is not None:
        texts[repo.rel(plugin.manifest_path)] = plugin.manifest.get("description", "")
    texts[f"marketplace.json ({plugin.name})"] = (plugin.entry or {}).get("description", "")
    return texts


def _wrong_claims(texts: dict[str, str], checklist: str, count: int) -> Iterator[Finding]:
    for where, text in texts.items():
        for claim in (c for c in ITEM_CLAIM.findall(text) if int(c) != count):
            yield Finding(where, "CNT001", f"says {claim} items, {checklist} has {count}")


@rule("CNT001", "'N items' in a skill, plugin.json or entry matches its checklist's IDs")
def checklist_counts(repo: Repo) -> Iterator[Finding]:
    for plugin, skill in ((p, s) for p in repo.plugins for s in p.skills):
        checklist, ids = _checklist_ids(skill)
        if ids:  # no checklist, or one without stable IDs, makes no count claim
            texts = _claim_texts(repo, plugin, skill)
            yield from _wrong_claims(texts, repo.rel(checklist), len(ids))


@rule("CNT002", "notes on shared CLI rows match the shared-rules map")
def shared_row_counts(repo: Repo) -> Iterator[Finding]:
    source, copy = shared_rules.present(repo.root)
    if not (source or copy):
        return  # the feature is absent (fixture repos); DOC002 reports a half-present pair
    count = len(shared_rules.SHARED)
    for relative, pattern in config.SHARED_COUNT_CLAIMS.items():
        path = repo.path(relative)
        match = re.search(pattern, path.read_text(encoding="utf-8")) if path.is_file() else None
        if not match:
            yield Finding(relative, "CNT002", "shared-row count sentence not found")
        elif int(match.group(1)) != count:
            message = f"says {match.group(1)} shared rows, the shared-rules map has {count}"
            yield Finding(relative, "CNT002", message)
