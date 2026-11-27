"""repo check: run rules and print their findings."""

from __future__ import annotations

import sys
from pathlib import Path

from skills_repo import rules
from skills_repo.commands.common import fail, load_repo, parser
from skills_repo.findings import Finding, errors, print_json, print_text
from skills_repo.model import Repo, RepoNotFound

EPILOG = """examples:
  repo check                              every default rule
  repo check --select SKL,REG             two rule families
  repo check --select REF --paths a.md    one rule, findings for a.md only
  repo check --json                       one JSON object on stdout
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
    p.add_argument("--json", action="store_true", help="print one JSON object")
    return p


def only_paths(repo: Repo, findings: list[Finding], paths: list[Path]) -> list[Finding]:
    """Keep findings whose path is one of `paths`, compared as repo-relative POSIX paths."""
    resolved = (p.resolve() for p in paths)
    wanted = {repo.rel(p) for p in resolved if p.is_relative_to(repo.root)}
    return [f for f in findings if f.path in wanted]


def parse_codes(select: str | None) -> list[str]:
    return [c.strip() for c in select.split(",") if c.strip()] if select else []


def report(repo: Repo, selected: list[rules.Rule], findings: list[Finding], as_json: bool) -> None:
    if as_json:
        summary = {
            "rules": [r.id for r in selected],
            "plugins": len(repo.plugins),
            "skills": len(repo.skills),
        }
        print_json(findings, summary, sys.stdout)
    else:
        ok = (
            f"ok {len(selected)} rules on {len(repo.plugins)} plugins and {len(repo.skills)} skills"
        )
        print_text(findings, ok, sys.stdout)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    codes = parse_codes(args.select)
    selected = rules.select(codes)
    if codes and not selected:
        message = f"no rule matches {args.select!r}; run `repo rules`"
        return fail(message, as_json=args.json, code="no_rule")
    try:
        repo = load_repo(args)
    except RepoNotFound as exc:
        return fail(str(exc), as_json=args.json, code="no_repo")
    findings = rules.run(repo, selected)
    if args.paths:
        findings = only_paths(repo, findings, args.paths)
    report(repo, selected, findings, args.json)
    return 1 if errors(findings) else 0
