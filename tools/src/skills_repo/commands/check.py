"""repo check: run rules, optionally fix what can be fixed, and print the findings."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

from skills_repo import rules
from skills_repo.commands.common import fail, load_repo, parser
from skills_repo.findings import (
    FORMATS,
    Finding,
    errors,
    print_github,
    print_json,
    print_sarif,
    print_text,
)
from skills_repo.model import Repo, RepoNotFound

EPILOG = """examples:
  repo check                              every default rule
  repo check --select SKL,REG             two rule families
  repo check --select REF --paths a.md    one rule, findings for a.md only
  repo check --fix                        rewrite generated files (DOC), then report
  repo check --format github              GitHub Actions annotations (inline on PRs)
  repo check --format sarif > out.sarif   SARIF 2.1.0 for code-scanning tools
Opt-in rules (DSC) run only when selected. Exit 1 when any error-level finding remains."""


def build_parser():
    p = parser("check", "Run the repo's rules and print what they find.", EPILOG)
    p.add_argument(
        "--select",
        metavar="CODES",
        help="comma-separated rule IDs or prefixes (SKL, SKL003); default: every default rule",
    )
    p.add_argument(
        "--paths", nargs="+", type=Path, metavar="FILE", help="report findings for these files only"
    )
    p.add_argument(
        "--format", choices=FORMATS, default="text", help="output format (default: text)"
    )
    p.add_argument("--json", action="store_true", help="same as --format json")
    p.add_argument(
        "--fix", action="store_true", help="run the fix of every failing fixable rule first"
    )
    return p


def only_paths(repo: Repo, findings: list[Finding], paths: list[Path]) -> list[Finding]:
    """Keep findings whose path is one of `paths`, compared as repo-relative POSIX paths."""
    resolved = (p.resolve() for p in paths)
    wanted = {repo.rel(p) for p in resolved if p.is_relative_to(repo.root)}
    return [f for f in findings if f.path in wanted]


def parse_codes(select: str | None) -> list[str]:
    return [c.strip() for c in select.split(",") if c.strip()] if select else []


def apply_fixes(repo: Repo, selected: list[rules.Rule], findings: list[Finding]) -> list[str]:
    """Run each failing rule's fix once; return the IDs fixed. Messages go to stderr."""
    failing = {f.rule for f in errors(findings)}
    fixable = [r for r in selected if r.fix and r.id in failing]
    for r in fixable:
        r.fix(repo)  # type: ignore[misc]  # filtered on r.fix above
        print(f"fixed {r.id}: {r.title}", file=sys.stderr)
    return [r.id for r in fixable]


def report(repo: Repo, selected: list[rules.Rule], findings: list[Finding], fmt: str) -> None:
    ok = f"ok {len(selected)} rules on {len(repo.plugins)} plugins and {len(repo.skills)} skills"
    if fmt == "json":
        summary = {
            "rules": [r.id for r in selected],
            "plugins": len(repo.plugins),
            "skills": len(repo.skills),
        }
        print_json(findings, summary, sys.stdout)
    elif fmt == "sarif":
        version = importlib.metadata.version("skills-repo")
        print_sarif(findings, [(r.id, r.title) for r in selected], version, sys.stdout)
    elif fmt == "github":
        print_github(findings, ok, sys.stdout)
    else:
        print_text(findings, ok, sys.stdout)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fmt = "json" if args.json else args.format
    codes = parse_codes(args.select)
    selected = rules.select(codes)
    if codes and not selected:
        message = f"no rule matches {args.select!r}; run `repo rules`"
        return fail(message, as_json=fmt == "json", code="no_rule")
    try:
        repo = load_repo(args)
    except RepoNotFound as exc:
        return fail(str(exc), as_json=fmt == "json", code="no_repo")
    findings = rules.run(repo, selected)
    if args.fix and apply_fixes(repo, selected, findings):
        repo = Repo.load(repo.root)  # files changed; read them again
        findings = rules.run(repo, selected)
    if args.paths:
        findings = only_paths(repo, findings, args.paths)
    report(repo, selected, findings, fmt)
    return 1 if errors(findings) else 0
