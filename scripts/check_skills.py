# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Check every SKILL.md against the Agent Skills spec (skills.sh) and Claude Code's skill rules.

    uv run scripts/check_skills.py          # all published skills
    uv run scripts/check_skills.py --json   # machine-readable result

Rules, with sources:
- agentskills.io/specification: `name` and `description` required; name 1-64 chars of a-z, 0-9 and
  single hyphens, matching its folder; description 1-1024 chars; compatibility 1-500 chars;
  metadata maps strings to strings; SKILL.md under 500 lines.
- Claude Code skills docs: frontmatter must start on line 1; description + when_to_use are cut at
  1,536 chars in the skill listing; the Claude-only fields listed in CLAUDE_FIELDS are allowed.
- skills.sh (vercel-labs/skills): skill names must be unique (it keeps the first one it finds),
  and skills/<plugin>/skills/<skill>/SKILL.md is the deepest level it walks.
Any field that neither spec defines fails, because both tools ignore it silently.
"""

import argparse
import json
import sys
from collections import defaultdict

from repo import (
    NAME_MAX,
    NAME_RE,
    PLUGINS_DIR,
    read_frontmatter,
    rel,
    report,
    skill_files,
)

SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
CLAUDE_FIELDS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
    "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths",
    "shell",
}  # fmt: skip
DESCRIPTION_MAX = 1024
LISTING_MAX = 1536  # Claude Code: description + when_to_use
COMPATIBILITY_MAX = 500
LINES_MAX = 500


def check_name(name: object, folder: str) -> list[str]:
    if not isinstance(name, str) or not name:
        return ["`name` is missing"]
    problems = []
    if len(name) > NAME_MAX or not NAME_RE.match(name):
        problems.append(
            f"`name` {name!r}: use 1-{NAME_MAX} chars of a-z, 0-9 and single hyphens"
        )
    if name != folder:
        problems.append(f"`name` {name!r} does not match its folder {folder!r}")
    return problems


def description_problem(desc: object) -> str | None:
    if not isinstance(desc, str) or not desc.strip():
        return "`description` is missing or empty"
    if len(desc) > DESCRIPTION_MAX:
        return f"`description` is {len(desc)} chars (max {DESCRIPTION_MAX})"
    return None


def listing_problem(desc: object, when: object) -> str | None:
    total = len(desc if isinstance(desc, str) else "") + len(str(when or ""))
    if when and total > LISTING_MAX:
        return f"description + when_to_use exceed {LISTING_MAX} chars"
    return None


def compatibility_problem(compat: object) -> str | None:
    if compat is None:
        return None
    valid = isinstance(compat, str) and 0 < len(compat) <= COMPATIBILITY_MAX
    return (
        None
        if valid
        else f"`compatibility` must be a string of 1-{COMPATIBILITY_MAX} chars"
    )


def check_lengths(fm: dict) -> list[str]:
    desc = fm.get("description")
    found = (
        description_problem(desc),
        listing_problem(desc, fm.get("when_to_use")),
        compatibility_problem(fm.get("compatibility")),
    )
    return [p for p in found if p]


def metadata_problem(meta: object) -> str | None:
    if meta is None:
        return None
    if not isinstance(meta, dict):
        return "`metadata` must be a mapping"
    bad = [str(k) for k, v in meta.items() if not isinstance(v, str)]
    return (
        f"`metadata` values must be strings; quote: {', '.join(bad)}" if bad else None
    )


def check_fields(fm: dict) -> tuple[list[str], list[str]]:
    """Return (problems, notes). Notes list Claude-only fields, which skills.sh agents ignore."""
    unknown = sorted(set(fm) - SPEC_FIELDS - CLAUDE_FIELDS)
    problems = (
        [f"unknown frontmatter field(s): {', '.join(unknown)}"] if unknown else []
    )
    meta = metadata_problem(fm.get("metadata"))
    if meta:
        problems.append(meta)
    claude_only = sorted(set(fm) & CLAUDE_FIELDS)
    notes = [f"Claude-only field(s): {', '.join(claude_only)}"] if claude_only else []
    return problems, notes


def check_skill(path) -> tuple[str | None, list[str], list[str]]:
    """Return (name, problems, notes) for one SKILL.md."""
    fm, error = read_frontmatter(path)
    if fm is None:
        return None, [error], []
    problems = check_name(fm.get("name"), path.parent.name) + check_lengths(fm)
    field_problems, notes = check_fields(fm)
    problems += field_problems
    lines = path.read_text(encoding="utf-8").count("\n") + 1
    if lines > LINES_MAX:
        problems.append(
            f"{lines} lines (keep SKILL.md under {LINES_MAX}; move detail to references/)"
        )
    return fm.get("name"), problems, notes


def stray_skill_files() -> list[str]:
    """SKILL.md files outside skills/<plugin>/skills/<skill>/, which neither tool will load."""
    expected = set(skill_files())
    found = {
        p
        for p in PLUGINS_DIR.rglob("SKILL.md")
        if p.relative_to(PLUGINS_DIR).parts[0] != "plugins"
    }
    return [
        f"{rel(p)}: not at skills/<plugin>/skills/<skill>/SKILL.md"
        for p in sorted(found - expected)
    ]


def check_all(files: list) -> tuple[list[str], list[str]]:
    """Return (problems, notes) for every SKILL.md, plus stray files and duplicate names."""
    problems, notes = stray_skill_files(), []
    owners: dict[str, list[str]] = defaultdict(list)
    for path in files:
        name, found, info = check_skill(path)
        problems += [f"{rel(path)}: {p}" for p in found]
        notes += [f"{rel(path)}: {n}" for n in info]
        if name:
            owners[name].append(rel(path))
    problems += [
        f"skill name {n!r} is used by {len(p)} skills: {', '.join(p)}"
        for n, p in owners.items()
        if len(p) > 1
    ]
    return problems, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print one JSON object")
    args = parser.parse_args(argv)

    files = skill_files()
    problems, notes = check_all(files)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": not problems,
                    "skills": len(files),
                    "problems": problems,
                    "notes": notes,
                },
                indent=2,
            )
        )
        return 1 if problems else 0
    for note in notes:
        print(f"note: {note}")
    return report(
        problems, f"ok {len(files)} skills meet the Agent Skills and Claude Code rules"
    )


if __name__ == "__main__":
    sys.exit(main())
