"""DOC: files generated from other files are up to date. `repo readme` and `repo sync` fix them."""

from __future__ import annotations

from collections.abc import Iterator

from skills_repo import config
from skills_repo.core import readme, shared_rules
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule


@rule("DOC001", "README.md matches its template and the marketplace")
def readme_current(repo: Repo) -> Iterator[Finding]:
    try:
        expected = readme.render(repo)
    except readme.TemplateError as exc:
        yield Finding(config.README_TEMPLATE, "DOC001", str(exc))
        return
    if readme.current(repo) != expected:
        yield Finding(config.README, "DOC001", "out of date; run `repo readme`")


@rule("DOC002", "python-cli-packaging's shared rows match agent-friendly-cli")
def shared_rules_current(repo: Repo) -> Iterator[Finding]:
    source, copy = shared_rules.present(repo.root)
    if not (source or copy):
        return  # the feature is absent (fixture repos)
    if not (source and copy):
        missing = config.SHARED_COPY if source else config.SHARED_SOURCE
        yield Finding(missing, "DOC002", "missing; shared CLI rules need both skills")
        return
    for path, _ in shared_rules.stale_files(repo.root):
        yield Finding(repo.rel(path), "DOC002", "out of date; run `repo sync`")
