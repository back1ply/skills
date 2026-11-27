"""repo new: scaffold a plugin. It does not rebuild the README or run checks; `just new` does."""

from __future__ import annotations

from pathlib import Path

from skills_repo import config
from skills_repo.commands.common import fail, load_repo, parser
from skills_repo.core import scaffold
from skills_repo.model import RepoNotFound

EPILOG = """example:
  repo new my-skill --category agents --description "What it does. Use when ..." --from ~/SKILL.md
Nothing is written if any check fails."""


def build_parser():
    p = parser(
        "new", "Create skills/NAME/, its plugin.json and SKILL.md, and a marketplace entry.", EPILOG
    )
    p.add_argument("name", help="plugin and skill name, kebab-case")
    p.add_argument(
        "--category", required=True, choices=list(config.CATEGORIES), help="README catalog section"
    )
    p.add_argument(
        "--description", required=True, help='catalog line: what it does, then "Use when ..."'
    )
    p.add_argument(
        "--summary",
        default="",
        help="plugin.json description (default: --description up to ' Use ')",
    )
    p.add_argument("--keywords", nargs="*", default=[], help="plugin keywords")
    p.add_argument("--from", dest="source", type=Path, help="existing SKILL.md to copy in")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = load_repo(args)
    except RepoNotFound as exc:
        return fail(str(exc))
    plan = scaffold.NewPlugin(
        args.name, args.category, args.description, args.summary, args.keywords, args.source
    )
    problems = scaffold.problems(repo, plan)
    if problems:
        return fail("; ".join(problems))
    skill = scaffold.create(repo, plan)
    print(
        f"ok created {config.PLUGINS_DIR}/{args.name}/ and its marketplace entry; edit {repo.rel(skill)}"
    )
    return 0
