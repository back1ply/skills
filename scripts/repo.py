"""Shared helpers for the repo scripts: paths, manifests, and SKILL.md frontmatter.

Layout this repo follows (both Claude Code and skills.sh read it):

    .claude-plugin/marketplace.json          one entry per plugin
    skills/<plugin>/.claude-plugin/plugin.json
    skills/<plugin>/skills/<skill>/SKILL.md
    skills/plugins/                          unpublished, gitignored, never checked
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = ROOT / "skills"
PRIVATE = {"plugins"}  # skills/plugins/ holds unpublished plugins

# Agent Skills spec (agentskills.io/specification): 1-64 chars, a-z 0-9 and single hyphens.
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_marketplace() -> dict:
    return load_json(MARKETPLACE)


def plugin_dirs() -> list[Path]:
    """Published plugin folders: every skills/<plugin>/ except private and hidden ones."""
    return sorted(
        p
        for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and p.name not in PRIVATE and not p.name.startswith(".")
    )


def skill_files(plugin: Path | None = None) -> list[Path]:
    """SKILL.md files of one plugin, or of every published plugin."""
    roots = [plugin] if plugin else plugin_dirs()
    return sorted(f for r in roots for f in r.glob("skills/*/SKILL.md"))


def read_frontmatter(path: Path) -> tuple[dict | None, str]:
    """Return (frontmatter, error). The opening --- must be the first line of the file."""
    import yaml  # callers declare pyyaml in their PEP 723 block

    text = path.read_text(encoding="utf-8")
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


def report(problems: list[str], ok_message: str) -> int:
    """Print problems to stderr and return 1, or print the ok line and return 0."""
    import sys

    if problems:
        print(*problems, sep="\n", file=sys.stderr)
        print(f"{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print(ok_message)
    return 0


REPO_URL = "https://github.com/back1ply/skills"
