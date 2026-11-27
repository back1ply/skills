"""MAN: this repo's manifest rules. Each one comes from a past fix commit:

- MAN001 "fix: remove version field from all plugin.json files": a version pins installs until
  it changes, so updates stop reaching users.
- MAN003 "remove email from all plugin.json author fields".
- MAN004 "change repository field from object to string", "point repo URLs at back1ply/skills".
- MAN002, MAN006: `claude plugin validate` warns when author or license is missing.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

from skills_repo import config
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule

Check = Callable[[dict], str | None]
VERSION_PINS = "remove `version` (it pins installs and stops updates)"
REPOSITORY = f"`repository` must be the string {config.REPO_URL!r}"


def _each_manifest(repo: Repo, rule_id: str, check: Check) -> Iterator[Finding]:
    """Run a check on every plugin.json (REG001 reports missing ones); it returns a message or None."""
    for plugin in (p for p in repo.plugins if p.manifest is not None):
        message = check(plugin.manifest or {})
        if message:
            yield Finding(repo.rel(plugin.manifest_path), rule_id, message)


def _each_entry(repo: Repo, rule_id: str, check: Check) -> Iterator[Finding]:
    """Run a check on every marketplace entry; it returns a message or None."""
    for entry in repo.entries:
        message = check(entry)
        if message:
            yield Finding(f"marketplace.json ({entry.get('name')})", rule_id, message)


def _has_version(data: dict) -> str | None:
    return VERSION_PINS if "version" in data else None


def _no_author_name(manifest: dict) -> str | None:
    author = manifest.get("author")
    return None if isinstance(author, dict) and author.get("name") else "set author.name"


def _author_email(manifest: dict) -> str | None:
    author = manifest.get("author")
    return "remove author.email" if isinstance(author, dict) and "email" in author else None


def _wrong_repository(manifest: dict) -> str | None:
    value = manifest.get("repository")
    return None if isinstance(value, str) and value.rstrip("/") == config.REPO_URL else REPOSITORY


def _repository_not_string(entry: dict) -> str | None:
    return (
        REPOSITORY if "repository" in entry and not isinstance(entry["repository"], str) else None
    )


def _homepage_not_https(manifest: dict) -> str | None:
    # homepage may credit a source site (ai-readiness does), so only the scheme is checked
    if "homepage" in manifest and not str(manifest["homepage"]).startswith("https://"):
        return "`homepage` must be an https URL"
    return None


def _no_license(manifest: dict) -> str | None:
    return None if manifest.get("license") else "set `license`"


@rule("MAN001", "no `version` in plugin.json or marketplace entries")
def no_version(repo: Repo) -> Iterator[Finding]:
    yield from _each_manifest(repo, "MAN001", _has_version)
    yield from _each_entry(repo, "MAN001", _has_version)


@rule("MAN002", "plugin.json sets author.name")
def author_name(repo: Repo) -> Iterator[Finding]:
    return _each_manifest(repo, "MAN002", _no_author_name)


@rule("MAN003", "no email in plugin.json author or marketplace owner")
def no_email(repo: Repo) -> Iterator[Finding]:
    yield from _each_manifest(repo, "MAN003", _author_email)
    if "email" in repo.marketplace.get("owner", {}):
        yield Finding("marketplace.json", "MAN003", "remove owner.email")


@rule("MAN004", "repository is the string URL of this repo")
def repository_url(repo: Repo) -> Iterator[Finding]:
    yield from _each_manifest(repo, "MAN004", _wrong_repository)
    yield from _each_entry(repo, "MAN004", _repository_not_string)


@rule("MAN005", "homepage, if set, is an https URL")
def homepage_https(repo: Repo) -> Iterator[Finding]:
    return _each_manifest(repo, "MAN005", _homepage_not_https)


@rule("MAN006", "plugin.json sets license")
def has_license(repo: Repo) -> Iterator[Finding]:
    return _each_manifest(repo, "MAN006", _no_license)
