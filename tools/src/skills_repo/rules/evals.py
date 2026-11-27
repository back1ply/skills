"""EVL: every skill has trigger eval cases, and every case file is one `claude plugin eval` accepts.

The cases themselves are billed model runs, so nothing here runs them; see core/evals.py and
`just trigger-evals`.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from skills_repo.core import evals
from skills_repo.findings import Finding
from skills_repo.model import Plugin, Repo, parse_frontmatter
from skills_repo.rules import rule


@rule("EVL001", "every skill has trigger-<skill> and no-trigger-<skill> eval cases")
def has_trigger_cases(repo: Repo) -> Iterator[Finding]:
    expected = (
        (plugin, skill.folder, case)
        for plugin in repo.plugins
        for skill in plugin.skills
        if skill.frontmatter is not None
        for case in evals.expected_cases(skill.folder, skill.frontmatter)
    )
    for plugin, skill, case in expected:
        if not (plugin.path / evals.EVALS_DIR / case / "prompt.md").is_file():
            message = f"no {evals.EVALS_DIR}/{case}/prompt.md for skill {skill!r}"
            yield Finding(repo.rel(plugin.path), "EVL001", message)


def _case_files(plugin: Plugin) -> Iterator[Path]:
    root = plugin.path / evals.EVALS_DIR
    for path in sorted(root.rglob("*.md")) if root.is_dir() else ():
        if "results" not in path.relative_to(root).parts:
            yield path


def _prompt_problem(fm: dict) -> str | None:
    unknown = sorted(set(fm) - evals.PROMPT_KEYS)
    return f"unknown prompt.md key(s): {', '.join(unknown)}" if unknown else None


def _grader_problem(fm: dict) -> str | None:
    kind = fm.get("type")
    if kind not in evals.GRADER_TYPES:
        return f"grader type {kind!r} is not one of {', '.join(sorted(evals.GRADER_TYPES))}"
    unknown = sorted(set(fm) - evals.TOOL_USED_KEYS) if kind == "tool_used" else []
    return f"unknown tool_used key(s): {', '.join(unknown)}" if unknown else None


def _file_problem(path: Path) -> str | None:
    fm, error = parse_frontmatter(path.read_text(encoding="utf-8"))
    if path.name == "prompt.md":
        return _prompt_problem(fm) if fm is not None else None  # a body-only prompt is valid
    if path.parent.name == "graders":
        return _grader_problem(fm) if fm is not None else error
    return None


@rule("EVL002", "eval case files use only keys and grader types `claude plugin eval` accepts")
def valid_case_files(repo: Repo) -> Iterator[Finding]:
    for path in (p for plugin in repo.plugins for p in _case_files(plugin)):
        problem = _file_problem(path)
        if problem:
            yield Finding(repo.rel(path), "EVL002", problem)
