"""repo sync: copy agent-friendly-cli's shared rows and contract script into python-cli-packaging."""

from __future__ import annotations

from skills_repo import config
from skills_repo.commands.common import fail, load_repo, parser
from skills_repo.core import shared_rules
from skills_repo.model import RepoNotFound


def build_parser():
    p = parser(
        "sync", f"Copy shared CLI rules from {config.SHARED_SOURCE} into {config.SHARED_COPY}."
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any copied file is out of date; write nothing",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = load_repo(args)
    except RepoNotFound as exc:
        return fail(str(exc))
    if shared_rules.present(repo.root) != (True, True):
        return fail(f"shared rules need both {config.SHARED_SOURCE} and {config.SHARED_COPY}")
    stale = shared_rules.stale_files(repo.root)
    if args.check:
        if stale:
            names = ", ".join(repo.rel(p) for p, _ in stale)
            return fail(f"out of date (run `repo sync`): {names}")
        print("ok shared CLI rules are in sync")
        return 0
    shared_rules.write(stale)
    print(f"ok updated {len(stale)} file(s)")
    return 0
