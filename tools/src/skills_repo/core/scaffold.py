"""Create a new plugin: skills/<name>/, its plugin.json, its SKILL.md, and a marketplace entry."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from skills_repo import config
from skills_repo.model import Repo, parse_frontmatter

NAME_RE = re.compile(config.NAME_PATTERN)
STUB = """---
name: {name}
description: >-
  {description}
---

# {name}

TODO: the instructions. Keep this file under 500 lines; move detail to references/.
"""


@dataclass
class NewPlugin:
    name: str
    category: str
    description: str  # catalog line: what it does, then "Use when ..."
    summary: str = ""  # plugin.json line; defaults to description up to " Use "
    keywords: list[str] = field(default_factory=list)
    source: Path | None = None  # an existing SKILL.md to copy in

    @property
    def manifest_description(self) -> str:
        return self.summary or self.description.split(" Use ")[0].rstrip(".")


def _name_problems(repo: Repo, name: str) -> list[str]:
    listed = {e.get("name") for e in repo.entries}
    skills = {s.folder for s in repo.skills}
    valid = len(name) <= config.NAME_MAX and bool(NAME_RE.match(name))
    reserved = name.startswith(config.RESERVED_PREFIXES) or name in (
        config.RESERVED_NAMES | config.PRIVATE_DIRS
    )
    rules = (
        (not valid, f"name {name!r}: use 1-{config.NAME_MAX} chars of a-z, 0-9 and single hyphens"),
        (reserved, f"name {name!r} is reserved"),
        (repo.path(f"{config.PLUGINS_DIR}/{name}").exists(), f"skills/{name}/ already exists"),
        (name in listed, f"marketplace.json already lists {name!r}"),
        (name in skills, f"a skill named {name!r} already exists (skills.sh keeps only the first)"),
    )
    return [message for fails, message in rules if fails]


def _source_problems(plan: NewPlugin) -> list[str]:
    if plan.source is None:
        return []
    if not plan.source.is_file():
        return [f"--from {plan.source}: no such file"]
    fm, error = parse_frontmatter(plan.source.read_text(encoding="utf-8"))
    if fm is None:
        return [f"--from {plan.source}: {error}"]
    if fm.get("name") != plan.name:
        return [
            f"--from {plan.source}: frontmatter name is {fm.get('name')!r}, expected {plan.name!r}"
        ]
    return []


def problems(repo: Repo, plan: NewPlugin) -> list[str]:
    """Everything that stops the plugin from being created; nothing is written if any."""
    found = _name_problems(repo, plan.name) + _source_problems(plan)
    if plan.category not in config.CATEGORIES:
        found.append(f"category {plan.category!r} is not one of {', '.join(config.CATEGORIES)}")
    return found


def _write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )


def create(repo: Repo, plan: NewPlugin) -> Path:
    """Write the plugin and its marketplace entry; return the new SKILL.md path."""
    plugin = repo.path(f"{config.PLUGINS_DIR}/{plan.name}")
    skill_dir = plugin / "skills" / plan.name
    skill_dir.mkdir(parents=True)
    (plugin / ".claude-plugin").mkdir()
    manifest = {
        "name": plan.name,
        "description": plan.manifest_description,
        "author": {"name": "back1ply"},
        "homepage": config.REPO_URL,
        "repository": config.REPO_URL,
        "license": "MIT",
        "keywords": plan.keywords,
    }
    _write_json(plugin / ".claude-plugin" / "plugin.json", manifest)
    skill = skill_dir / "SKILL.md"
    if plan.source:
        shutil.copyfile(plan.source, skill)
    else:
        stub = STUB.format(name=plan.name, description=plan.description)
        skill.write_text(stub, encoding="utf-8", newline="\n")
    repo.marketplace["plugins"].append(
        {
            "name": plan.name,
            "description": plan.description,
            "source": f"./{config.PLUGINS_DIR}/{plan.name}",
            "license": "MIT",
            "keywords": plan.keywords,
            "category": plan.category,
        }
    )
    _write_json(repo.path(config.MARKETPLACE), repo.marketplace)
    return skill
