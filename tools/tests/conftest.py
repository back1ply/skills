"""A minimal clean marketplace repo, built fresh in a temp folder for each test.

Built in code rather than committed as files, so no fake SKILL.md ever sits in the real repo
where skills.sh or Claude Code could pick it up.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from skills_repo import config
from skills_repo.core import evals, readme
from skills_repo.model import Repo

TEMPLATE = """# Skills

{{skill_count}} skills in {{plugin_count}} plugins.

{{catalog}}

<!-- video-skills:start -->
<!-- video-skills:end -->

<!-- articles:start -->
<!-- articles:end -->
"""


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_skill(path: Path, frontmatter: dict, body: str = "# Skill\n\nDo the thing.\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"---\n{yaml.safe_dump(frontmatter, sort_keys=False)}---\n\n{body}"
    path.write_text(text, encoding="utf-8")


def add_plugin(root: Path, name: str, skill: str | None = None, category: str = "agents") -> None:
    """A plugin that passes every rule: folder, plugin.json, SKILL.md, trigger cases, entry."""
    skill = skill or name
    plugin = root / config.PLUGINS_DIR / name
    write_json(
        plugin / ".claude-plugin" / "plugin.json",
        {
            "name": name,
            "description": f"{name} plugin",
            "author": {"name": "back1ply"},
            "homepage": config.REPO_URL,
            "repository": config.REPO_URL,
            "license": "MIT",
        },
    )
    write_skill(
        plugin / "skills" / skill / "SKILL.md",
        {"name": skill, "description": f"Does {skill} things. Use when testing."},
    )
    evals.write_trigger_cases(
        plugin, skill, f"Please do {skill} things.", "What time is it in Tokyo?"
    )
    market_path = root / config.MARKETPLACE
    market = read_json(market_path)
    market["plugins"].append(
        {
            "name": name,
            "description": f"{name} catalog line",
            "source": f"./{config.PLUGINS_DIR}/{name}",
            "category": category,
        }
    )
    write_json(market_path, market)


def render_readme(root: Path) -> None:
    repo = Repo.load(root)
    readme.write(repo, readme.render(repo))


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    write_json(
        root / config.MARKETPLACE, {"name": "skills", "owner": {"name": "back1ply"}, "plugins": []}
    )
    (root / config.README_TEMPLATE).parent.mkdir(parents=True)
    (root / config.README_TEMPLATE).write_text(TEMPLATE, encoding="utf-8")
    add_plugin(root, "alpha")
    render_readme(root)
    return root


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests never call npx: skills.sh 'finds' exactly the skills on disk."""
    from skills_repo.rules import discovery

    def on_disk(root: Path) -> frozenset[str]:
        return frozenset(
            p.parent.name for p in (root / config.PLUGINS_DIR).glob("*/skills/*/SKILL.md")
        )

    monkeypatch.setattr(discovery, "listed_skills", on_disk)
