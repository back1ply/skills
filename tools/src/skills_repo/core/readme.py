"""Render README.md from tools/readme_template.md and the marketplace.

- {{catalog}} becomes one table per category, from each plugin's `category` and `description`.
  Plugins with their own README.md get a link to it.
- {{plugin_count}} and {{skill_count}} are counted from the repo.
- The <!-- video-skills --> and <!-- articles --> blocks are copied from the current README,
  because the youtube-to-skill and article-to-skill sources.py scripts write them there.
"""

from __future__ import annotations

import re

from skills_repo import config
from skills_repo.model import Repo

GENERATED_BLOCKS = ("video-skills", "articles")


class TemplateError(Exception):
    """The template or the marketplace can't produce a README."""


def _row(repo: Repo, entry: dict) -> str:
    name, text = entry["name"], entry["description"]
    if repo.path(f"{config.PLUGINS_DIR}/{name}/README.md").exists():
        text += f" ([README]({config.PLUGINS_DIR}/{name}/README.md))"
    return f"| `{name}` | {text} |"


def catalog(repo: Repo) -> str:
    bad = [e.get("name") for e in repo.entries if e.get("category") not in config.CATEGORIES]
    if bad:
        raise TemplateError(f"missing or unknown category: {', '.join(map(str, bad))}")
    sections = []
    for slug, heading in config.CATEGORIES.items():
        entries = [e for e in repo.entries if e["category"] == slug]
        if entries:
            rows = [f"### {heading}", "", "| Plugin | What it does |", "|---|---|"]
            sections.append("\n".join(rows + [_row(repo, e) for e in entries]))
    return "\n\n".join(sections)


def _copy_blocks(text: str, current: str) -> str:
    for marker in GENERATED_BLOCKS:
        pattern = re.compile(rf"<!-- {marker}:start -->.*?<!-- {marker}:end -->", re.DOTALL)
        slot = pattern.search(text)
        if not slot:
            raise TemplateError(f"template has no <!-- {marker}:start/end --> block")
        old = pattern.search(current)
        if old:
            text = text[: slot.start()] + old.group(0) + text[slot.end() :]
    return text


def current(repo: Repo) -> str:
    path = repo.path(config.README)
    return path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.exists() else ""


def render(repo: Repo) -> str:
    template = repo.path(config.README_TEMPLATE)
    if not template.is_file():
        raise TemplateError(f"no template at {config.README_TEMPLATE}")
    text = template.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = text.replace("{{catalog}}", catalog(repo))
    text = text.replace("{{plugin_count}}", str(len(repo.entries)))
    text = text.replace("{{skill_count}}", str(len(repo.skills)))
    return _copy_blocks(text, current(repo))


def write(repo: Repo, text: str) -> None:
    repo.path(config.README).write_text(text, encoding="utf-8", newline="\n")
