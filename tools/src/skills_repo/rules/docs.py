"""DOC: files generated from other files are up to date.

Both rules can fix themselves: `repo check --fix` (or `repo readme` / `repo sync`) rewrites them.
"""

from __future__ import annotations

from collections.abc import Iterator

from skills_repo import config
from skills_repo.core import readme, shared_rules
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule


def rebuild_readme(repo: Repo) -> None:
    readme.write(repo, readme.render(repo))


def sync_shared_rules(repo: Repo) -> None:
    if shared_rules.present(repo.root) == (True, True):
        shared_rules.write(shared_rules.stale_files(repo.root))


@rule("DOC001", "README.md matches its template and the marketplace", fix=rebuild_readme)
def readme_current(repo: Repo) -> Iterator[Finding]:
    try:
        expected = readme.render(repo)
    except readme.TemplateError as exc:
        yield Finding(config.README_TEMPLATE, "DOC001", str(exc))
        return
    if readme.current(repo) != expected:
        yield Finding(config.README, "DOC001", "out of date; run `repo check --fix`")


@rule(
    "DOC002", "python-cli-packaging's shared rows match agent-friendly-cli", fix=sync_shared_rules
)
def shared_rules_current(repo: Repo) -> Iterator[Finding]:
    source, copy = shared_rules.present(repo.root)
    if not (source or copy):
        return  # the feature is absent (fixture repos)
    if not (source and copy):
        missing = config.SHARED_COPY if source else config.SHARED_SOURCE
        yield Finding(missing, "DOC002", "missing; shared CLI rules need both skills")
        return
    for path, _ in shared_rules.stale_files(repo.root):
        yield Finding(repo.rel(path), "DOC002", "out of date; run `repo check --fix`")
