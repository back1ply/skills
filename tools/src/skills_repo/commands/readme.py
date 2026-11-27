"""repo readme: rebuild README.md from tools/readme_template.md and the marketplace."""

from __future__ import annotations

from skills_repo import config
from skills_repo.commands.common import fail, load_repo, parser
from skills_repo.core import readme
from skills_repo.model import RepoNotFound


def build_parser():
    p = parser(
        "readme", f"Rebuild {config.README} from {config.README_TEMPLATE} and the marketplace."
    )
    p.add_argument(
        "--check", action="store_true", help="exit 1 if README.md is out of date; write nothing"
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = load_repo(args)
        text = readme.render(repo)
    except (RepoNotFound, readme.TemplateError) as exc:
        return fail(str(exc))
    if args.check:
        if readme.current(repo) != text:
            return fail(f"{config.README} is out of date; run `repo readme`")
        print(f"ok {config.README} is up to date")
        return 0
    readme.write(repo, text)
    print(f"ok {len(repo.entries)} plugins -> {config.README}")
    return 0
