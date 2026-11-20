#!/usr/bin/env python3
"""Deterministic grader for the skill-curator seeded-audit task.

Checks that /workspace/project/skills-audit.md names each planted problem next to
a matching keyword, does not flag the healthy skill, and that no skill was changed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

PROJECT = Path(os.environ.get("GRADER_PROJECT", "/workspace/project"))
SEED_HASHES = Path(os.environ.get("GRADER_SEED_HASHES", "/opt/seed-skills.sha256"))
REWARD_JSON = Path(os.environ.get("HARBOR_REWARD_JSON", "/logs/verifier/reward.json"))
REWARD_TXT = Path(os.environ.get("HARBOR_REWARD_TXT", "/logs/verifier/reward.txt"))
WINDOW = 3  # lines either side of a mention that count as "next to"

# check name -> (skills that must appear together, keyword pattern)
FINDINGS = {
    "duplicate_found": (("pdf-extract", "pdf-reader"), r"duplicat|overlap|redundan|same purpose|merge"),
    "conflict_found": (("format-tabs", "format-spaces"), r"conflict|contradict|incompatib|opposite"),
    "missing_description_found": (("release-notes",), r"description|frontmatter|front matter|metadata|invalid|malformed"),
    "missing_script_found": (("db-migrate",), r"migrate\.sh|missing|does not exist|doesn't exist|not found|no such|absent"),
}
FALSE_ALARM = r"duplicat|conflict|broken|invalid|missing"


def result(ok: bool, reason: str) -> dict:
    return {"score": 1.0 if ok else 0.0, "reason": reason}


def windows(lines: list[str], name: str):
    for i, line in enumerate(lines):
        if name in line:
            yield "\n".join(lines[max(0, i - WINDOW): i + WINDOW + 1]).lower()


def finding_present(lines: list[str], names: tuple[str, ...], pattern: str) -> bool:
    return any(
        all(other in window for other in names) and re.search(pattern, window)
        for window in windows(lines, names[0])
    )


def healthy_skill_not_flagged(lines: list[str]) -> dict:
    flagged = [
        line.strip()
        for line in lines
        if "commit-helper" in line and re.search(FALSE_ALARM, line.lower()) and not re.search(r"no issue|healthy|keep|fine|ok\b", line.lower())
    ]
    return result(not flagged, f"flagged lines: {flagged[:2]}" if flagged else "not flagged")


def skills_unchanged() -> dict:
    if not SEED_HASHES.exists():
        return result(False, "seed hash file missing")
    expected = SEED_HASHES.read_text(encoding="utf-8").splitlines()
    actual = []
    for path in sorted((PROJECT / "team-skills").rglob("*")):
        if path.is_file():
            actual.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path}")
    expected_digests = sorted(line.split()[0] for line in expected)
    actual_digests = sorted(line.split()[0] for line in actual)
    return result(expected_digests == actual_digests, "unchanged" if expected_digests == actual_digests else "skill files changed")


def grade() -> dict:
    report = PROJECT / "skills-audit.md"
    if not report.exists():
        results = {name: result(False, "skills-audit.md not written") for name in FINDINGS}
        results["healthy_not_flagged"] = result(False, "no report")
    else:
        lines = report.read_text(encoding="utf-8", errors="replace").splitlines()
        results = {
            name: result(finding_present(lines, names, pattern), f"{' + '.join(names)} with /{pattern}/")
            for name, (names, pattern) in FINDINGS.items()
        }
        results["healthy_not_flagged"] = healthy_skill_not_flagged(lines)
    results["skills_unchanged"] = skills_unchanged()
    return results


def write(results: dict) -> None:
    score = round(sum(r["score"] for r in results.values()) / len(results), 4)
    reward = {"overall": score, "custom_metrics": {k: v["score"] for k, v in results.items()}, "details": results}
    REWARD_JSON.parent.mkdir(parents=True, exist_ok=True)
    REWARD_JSON.write_text(json.dumps(reward, indent=2), encoding="utf-8")
    REWARD_TXT.write_text(str(score), encoding="utf-8")


if __name__ == "__main__":
    write(grade())
