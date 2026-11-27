"""DSC: skills.sh (`npx skills add`) finds exactly the published skills (opt-in: needs npx).

Copies the files git would publish (tracked plus new, not ignored) to a temp folder, so the
gitignored skills/plugins/ stays out, then runs `skills add <folder> --list` with a pinned CLI.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from skills_repo import config
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
LISTED = re.compile(r"^│ {4}(\S+)\s*$", re.MULTILINE)


class DiscoveryError(Exception):
    """npx is missing, or the skills CLI failed or listed nothing."""


def parse_listing(output: str) -> set[str]:
    """Skill names from `skills add --list` output (ANSI colors and box-drawing included)."""
    return set(LISTED.findall(ANSI.sub("", output)))


def _published_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root, capture_output=True, check=True,
    ).stdout  # fmt: skip
    return [f for f in out.decode("utf-8").split("\0") if f and (root / f).is_file()]


def _run_cli(folder: Path) -> str:
    npx = shutil.which("npx")
    if not npx:
        raise DiscoveryError("npx not found; install Node 22.20+ to run DSC")
    env = {**os.environ, "NO_COLOR": "1", "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1"}
    result = subprocess.run(
        [npx, "-y", config.SKILLS_CLI, "add", str(folder), "--list"],
        check=False, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=300,
    )  # fmt: skip
    output = result.stdout + result.stderr
    if result.returncode != 0 or not parse_listing(output):
        lines = [line.strip() for line in ANSI.sub("", output).splitlines() if line.strip()]
        tail = " | ".join(lines[-6:]) or "no output"
        raise DiscoveryError(
            f"{config.SKILLS_CLI} add --list failed (exit {result.returncode}) "
            f"or listed nothing; last output: {tail}"
        )
    return output


@lru_cache(maxsize=4)
def listed_skills(root: Path) -> frozenset[str]:
    with tempfile.TemporaryDirectory(prefix="skills-discovery-") as tmp:
        for relative in _published_files(root):
            target = Path(tmp, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, target)
        return frozenset(parse_listing(_run_cli(Path(tmp))))


def _found(repo: Repo) -> tuple[set[str], set[str]] | Finding:
    """(published, found by skills.sh), or a Finding when the CLI can't run."""
    try:
        found = set(listed_skills(repo.root))
    except DiscoveryError as exc:
        return Finding(config.PLUGINS_DIR, "DSC001", str(exc))
    return {s.folder for s in repo.skills}, found


@rule("DSC001", "skills.sh finds every published skill", default=False)
def finds_all(repo: Repo) -> Iterator[Finding]:
    result = _found(repo)
    if isinstance(result, Finding):
        yield result
        return
    published, found = result
    for name in sorted(published - found):
        yield Finding(config.PLUGINS_DIR, "DSC001", f"skills.sh does not find {name!r}")


@rule("DSC002", "skills.sh finds nothing outside skills/<plugin>/skills/", default=False)
def finds_nothing_else(repo: Repo) -> Iterator[Finding]:
    result = _found(repo)
    if isinstance(result, Finding):
        return  # DSC001 already reported why the CLI can't run
    published, found = result
    for name in sorted(found - published):
        message = f"skills.sh finds {name!r}, which is not under skills/<plugin>/skills/"
        yield Finding(config.PLUGINS_DIR, "DSC002", message)
