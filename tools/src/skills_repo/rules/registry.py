"""REG: plugin folders, plugin.json files and marketplace.json entries agree.

Catches what `claude plugin validate` does not. Descriptions are not compared: plugin.json and
the marketplace entry differ on purpose (the entry is the README catalog line).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator

from skills_repo import config
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule

MARKET = config.MARKETPLACE


@rule("REG001", "every plugin folder has .claude-plugin/plugin.json")
def has_manifest(repo: Repo) -> Iterator[Finding]:
    for plugin in repo.plugins:
        if plugin.manifest is None:
            yield Finding(repo.rel(plugin.path), "REG001", "no .claude-plugin/plugin.json")


@rule("REG002", "plugin.json name matches its folder")
def manifest_name(repo: Repo) -> Iterator[Finding]:
    for plugin in repo.plugins:
        declared = (plugin.manifest or {}).get("name", plugin.name)
        if declared != plugin.name:
            message = f"name {declared!r} does not match its folder {plugin.name!r}"
            yield Finding(repo.rel(plugin.manifest_path), "REG002", message)


@rule("REG003", "every plugin folder is registered in marketplace.json")
def registered(repo: Repo) -> Iterator[Finding]:
    for plugin in repo.plugins:
        if plugin.entry is None:
            message = f"not registered in {config.MARKETPLACE}"
            yield Finding(repo.rel(plugin.path), "REG003", message)


@rule("REG004", "every marketplace entry has a plugin folder")
def has_folder(repo: Repo) -> Iterator[Finding]:
    folders = {p.name for p in repo.plugins}
    for entry in repo.entries:
        if entry.get("name") not in folders:
            message = (
                f"{entry.get('name')!r} has no folder {config.PLUGINS_DIR}/{entry.get('name')}/"
            )
            yield Finding(MARKET, "REG004", message)


@rule("REG005", "no plugin is listed twice")
def unique_entries(repo: Repo) -> Iterator[Finding]:
    counts = Counter(e.get("name") for e in repo.entries)
    for name, count in counts.items():
        if count > 1:
            yield Finding(MARKET, "REG005", f"plugin {name!r} is listed {count} times")


@rule("REG006", "entry source is ./skills/<name>")
def entry_source(repo: Repo) -> Iterator[Finding]:
    for entry in repo.entries:
        expected = f"./{config.PLUGINS_DIR}/{entry.get('name')}"
        if entry.get("source") != expected:
            message = f"source is {entry.get('source')!r}, expected {expected!r}"
            yield Finding(MARKET, "REG006", message, subject=str(entry.get("name")))


@rule("REG007", "entry category is a README section")
def entry_category(repo: Repo) -> Iterator[Finding]:
    for entry in repo.entries:
        if entry.get("category") not in config.CATEGORIES:
            message = (
                f"category {entry.get('category')!r} is not one of {', '.join(config.CATEGORIES)}"
            )
            yield Finding(MARKET, "REG007", message, subject=str(entry.get("name")))


@rule("REG008", "entry has a description for the README catalog")
def entry_description(repo: Repo) -> Iterator[Finding]:
    for entry in repo.entries:
        if not entry.get("description"):
            yield Finding(MARKET, "REG008", "no description", subject=str(entry.get("name")))


@rule("REG009", "every plugin has at least one skill")
def has_skills(repo: Repo) -> Iterator[Finding]:
    for plugin in repo.plugins:
        if not plugin.skills:
            yield Finding(repo.rel(plugin.path), "REG009", "no skills/<skill>/SKILL.md")
