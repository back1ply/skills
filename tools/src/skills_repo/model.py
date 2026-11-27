"""The repo as objects: one Repo holding its Plugins, each holding its Skills.

Load once with Repo.load(root); rules and commands read from it instead of parsing files
themselves. Every path a rule reports goes through Repo.rel(), so it is repo-relative POSIX.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import yaml

from skills_repo import config

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


class RepoNotFound(Exception):
    """No folder at or above the start has .claude-plugin/marketplace.json."""


def find_root(start: Path) -> Path:
    for folder in (start.resolve(), *start.resolve().parents):
        if (folder / config.MARKETPLACE).is_file():
            return folder
    raise RepoNotFound(f"no {config.MARKETPLACE} at or above {start}; pass --root")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, error). The opening --- must be the file's first line."""
    match = _FRONTMATTER.match(text)
    if not match:
        return None, "no YAML frontmatter starting on line 1"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"frontmatter is not valid YAML: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, ""


@dataclass
class Skill:
    path: Path  # .../skills/<plugin>/skills/<skill>/SKILL.md

    @property
    def folder(self) -> str:
        return self.path.parent.name

    @cached_property
    def text(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @cached_property
    def _parsed(self) -> tuple[dict | None, str]:
        return parse_frontmatter(self.text)

    @property
    def frontmatter(self) -> dict | None:
        return self._parsed[0]

    @property
    def frontmatter_error(self) -> str:
        return self._parsed[1]

    @property
    def name(self) -> str | None:
        name = (self.frontmatter or {}).get("name")
        return name if isinstance(name, str) else None

    @property
    def references(self) -> list[Path]:
        return sorted((self.path.parent / "references").glob("*.md"))


@dataclass
class Plugin:
    path: Path  # skills/<plugin>/
    entry: dict | None  # its marketplace.json entry, if registered

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def manifest_path(self) -> Path:
        return self.path / ".claude-plugin" / "plugin.json"

    @cached_property
    def manifest(self) -> dict | None:
        return read_json(self.manifest_path) if self.manifest_path.is_file() else None

    @cached_property
    def skills(self) -> list[Skill]:
        return [Skill(p) for p in sorted(self.path.glob("skills/*/SKILL.md"))]


@dataclass
class Repo:
    root: Path
    marketplace: dict
    plugins: list[Plugin] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path) -> Repo:
        root = root.resolve()
        marketplace = read_json(root / config.MARKETPLACE)
        entries = {e.get("name"): e for e in marketplace.get("plugins", [])}
        plugins_dir = root / config.PLUGINS_DIR
        folders = sorted(
            p
            for p in plugins_dir.iterdir()
            if p.is_dir() and p.name not in config.PRIVATE_DIRS and not p.name.startswith(".")
        )
        return cls(root, marketplace, [Plugin(p, entries.get(p.name)) for p in folders])

    @property
    def entries(self) -> list[dict]:
        return self.marketplace.get("plugins", [])

    @property
    def skills(self) -> list[Skill]:
        return [s for p in self.plugins for s in p.skills]

    def plugin(self, name: str) -> Plugin | None:
        return next((p for p in self.plugins if p.name == name), None)

    def path(self, relative: str) -> Path:
        return self.root / relative

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()
