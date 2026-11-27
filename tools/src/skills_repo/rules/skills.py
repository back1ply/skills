"""SKL: every SKILL.md against the Agent Skills spec (skills.sh) and Claude Code's skill rules.

Sources: agentskills.io/specification (name, description, compatibility, metadata, 500 lines),
the Claude Code skills docs (frontmatter on line 1, extra fields, 1,536-char listing), and
vercel-labs/skills (duplicate names: only the first is kept; three folder levels deep).
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Iterator

from skills_repo import config
from skills_repo.findings import ERROR, NOTE, Finding
from skills_repo.model import Repo, Skill
from skills_repo.rules import rule

NAME_RE = re.compile(config.NAME_PATTERN)


def _parsed(repo: Repo) -> Iterator[tuple[Skill, dict]]:
    """Skills whose frontmatter parsed; SKL001 reports the rest."""
    for skill in repo.skills:
        if skill.frontmatter is not None:
            yield skill, skill.frontmatter


@rule("SKL001", "frontmatter is valid YAML starting on line 1")
def frontmatter_parses(repo: Repo) -> Iterator[Finding]:
    for skill in repo.skills:
        if skill.frontmatter is None:
            yield Finding(repo.rel(skill.path), "SKL001", skill.frontmatter_error)


Check = Callable[[Skill, dict], str | None]


def _each(repo: Repo, rule_id: str, check: Check, severity: str = ERROR) -> Iterator[Finding]:
    """Run a per-skill check on every parsed skill; it returns a message or None."""
    for skill, fm in _parsed(repo):
        message = check(skill, fm)
        if message:
            yield Finding(repo.rel(skill.path), rule_id, message, severity)


def _valid_name(name: object) -> bool:
    return isinstance(name, str) and len(name) <= config.NAME_MAX and bool(NAME_RE.match(name))


def _bad_name(skill: Skill, fm: dict) -> str | None:
    if _valid_name(fm.get("name")):
        return None
    return f"name {fm.get('name')!r}: use 1-{config.NAME_MAX} chars of a-z, 0-9 and single hyphens"


def _folder_mismatch(skill: Skill, fm: dict) -> str | None:
    if fm.get("name") == skill.folder:
        return None
    return f"name {fm.get('name')!r} does not match its folder {skill.folder!r}"


def _bad_description(skill: Skill, fm: dict) -> str | None:
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        return "description is missing or empty"
    if len(desc) > config.DESCRIPTION_MAX:
        return f"description is {len(desc)} chars (max {config.DESCRIPTION_MAX})"
    return None


def _listing_too_long(skill: Skill, fm: dict) -> str | None:
    when, desc = fm.get("when_to_use"), fm.get("description")
    total = (len(desc) if isinstance(desc, str) else 0) + len(str(when or ""))
    if when and total > config.LISTING_MAX:
        return f"description + when_to_use exceed {config.LISTING_MAX} chars"
    return None


def _bad_compatibility(skill: Skill, fm: dict) -> str | None:
    compat = fm.get("compatibility")
    valid = compat is None or (
        isinstance(compat, str) and 0 < len(compat) <= config.COMPATIBILITY_MAX
    )
    return (
        None if valid else f"compatibility must be a string of 1-{config.COMPATIBILITY_MAX} chars"
    )


def _bad_metadata(skill: Skill, fm: dict) -> str | None:
    meta = fm.get("metadata")
    if meta is None:
        return None
    if not isinstance(meta, dict):
        return "metadata must be a mapping"
    bad = [str(k) for k, v in meta.items() if not isinstance(v, str)]
    return f"metadata values must be strings; quote: {', '.join(bad)}" if bad else None


def _unknown_fields(skill: Skill, fm: dict) -> str | None:
    unknown = sorted(set(fm) - config.SPEC_FIELDS - config.CLAUDE_FIELDS)
    return f"unknown frontmatter field(s): {', '.join(unknown)}" if unknown else None


def _claude_only(skill: Skill, fm: dict) -> str | None:
    fields = sorted(set(fm) & config.CLAUDE_FIELDS)
    return f"Claude-only field(s): {', '.join(fields)}" if fields else None


@rule("SKL002", "name is 1-64 chars of a-z, 0-9 and single hyphens")
def name_format(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL002", _bad_name)


@rule("SKL003", "name matches the skill's folder")
def name_matches_folder(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL003", _folder_mismatch)


@rule("SKL004", "description is present and at most 1024 chars")
def description_length(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL004", _bad_description)


@rule("SKL005", "description + when_to_use fit Claude Code's 1,536-char listing")
def listing_length(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL005", _listing_too_long)


@rule("SKL006", "compatibility, if set, is 1-500 chars")
def compatibility_length(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL006", _bad_compatibility)


@rule("SKL007", "metadata maps strings to strings")
def metadata_strings(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL007", _bad_metadata)


@rule("SKL008", "no frontmatter field that neither spec defines")
def known_fields(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL008", _unknown_fields)


@rule("SKL009", "SKILL.md is under 500 lines")
def skill_length(repo: Repo) -> Iterator[Finding]:
    for skill in repo.skills:
        lines = skill.text.count("\n") + 1
        if lines > config.SKILL_LINES_MAX:
            message = f"{lines} lines (keep SKILL.md under {config.SKILL_LINES_MAX}; move detail to references/)"
            yield Finding(repo.rel(skill.path), "SKL009", message)


def _owners(repo: Repo) -> dict[str, list[str]]:
    """Skill name -> the SKILL.md paths that declare it."""
    owners: dict[str, list[str]] = defaultdict(list)
    for skill in (s for s in repo.skills if s.name):
        owners[skill.name].append(repo.rel(skill.path))
    return owners


@rule("SKL010", "skill names are unique across the repo")
def unique_names(repo: Repo) -> Iterator[Finding]:
    for name, paths in ((n, p) for n, p in _owners(repo).items() if len(p) > 1):
        message = f"skill name {name!r} is used {len(paths)} times (skills.sh keeps only the first)"
        yield from (Finding(p, "SKL010", message) for p in paths)


@rule("SKL011", "every SKILL.md is at skills/<plugin>/skills/<skill>/")
def skill_location(repo: Repo) -> Iterator[Finding]:
    plugins_dir = repo.path(config.PLUGINS_DIR)
    expected = {s.path.resolve() for s in repo.skills}
    published = (
        p
        for p in sorted(plugins_dir.rglob("SKILL.md"))
        if p.relative_to(plugins_dir).parts[0] not in config.PRIVATE_DIRS
    )
    message = "not at skills/<plugin>/skills/<skill>/SKILL.md, so neither tool loads it"
    for path in (p for p in published if p.resolve() not in expected):
        yield Finding(repo.rel(path), "SKL011", message)


@rule("SKL100", "note: Claude-only frontmatter fields, which other agents ignore")
def claude_only_fields(repo: Repo) -> Iterator[Finding]:
    return _each(repo, "SKL100", _claude_only, NOTE)
