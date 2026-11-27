"""Enforce this repo's manifest rules on every plugin.json and marketplace entry.

    uv run scripts/lint_manifests.py

Each rule comes from a past fix commit:
- no `version`: a version pins installs until it changes, so updates stop reaching users
  ("fix: remove version field from all plugin.json files");
- no `email` in `author` or `owner` ("remove email from all plugin.json author fields");
- `repository` is a string, not an object ("change repository field from object to string");
- `repository` points at this repo ("point repo URLs at back1ply/skills"); `homepage` may
  point elsewhere (ai-readiness credits its source site);
- `author.name` and `license` are set, so `claude plugin validate` shows no missing-metadata warning.
"""

import argparse
import sys

from repo import (
    MARKETPLACE,
    REPO_URL,
    load_json,
    load_marketplace,
    plugin_dirs,
    rel,
    report,
)


def author_problem(author: object) -> str | None:
    if not isinstance(author, dict) or not author.get("name"):
        return "set author.name"
    return "remove author.email" if "email" in author else None


def repository_problem(repo: object) -> str | None:
    if isinstance(repo, str) and repo.rstrip("/") == REPO_URL:
        return None
    return f"`repository` must be the string {REPO_URL!r}"


def homepage_problem(data: dict) -> str | None:
    # homepage may credit a source site (ai-readiness), so only the scheme is checked
    if "homepage" in data and not str(data["homepage"]).startswith("https://"):
        return "`homepage` must be an https URL"
    return None


def check_plugin_json(data: dict, where: str) -> list[str]:
    found = (
        "remove `version` (it pins installs and stops updates)"
        if "version" in data
        else None,
        author_problem(data.get("author")),
        repository_problem(data.get("repository")),
        homepage_problem(data),
        None if data.get("license") else "set `license`",
    )
    return [f"{where}: {p}" for p in found if p]


def check_marketplace(data: dict) -> list[str]:
    where = rel(MARKETPLACE)
    problems = (
        [f"{where}: remove owner.email"] if "email" in data.get("owner", {}) else []
    )
    for entry in data.get("plugins", []):
        name = entry.get("name", "?")
        if "version" in entry:
            problems.append(
                f"{where}: {name}: remove `version` (it pins installs and stops updates)"
            )
        if "repository" in entry and not isinstance(entry["repository"], str):
            problems.append(f"{where}: {name}: `repository` must be a string")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.parse_args(argv)

    manifests = [p / ".claude-plugin" / "plugin.json" for p in plugin_dirs()]
    manifests = [
        m for m in manifests if m.exists()
    ]  # check_registry reports missing ones
    problems = check_marketplace(load_marketplace())
    for manifest in manifests:
        problems += check_plugin_json(load_json(manifest), rel(manifest))
    return report(
        problems,
        f"ok {len(manifests)} plugin.json files and the marketplace follow the repo rules",
    )


if __name__ == "__main__":
    sys.exit(main())
