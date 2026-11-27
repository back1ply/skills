"""Check that skills.sh (`npx skills add`) finds exactly the skills this repo publishes.

    uv run scripts/check_discovery.py

Copies the files git would publish (tracked plus new, not ignored) to a temp folder, runs
`skills add <folder> --list` with a pinned CLI version, and compares the skill names it lists
with skills/<plugin>/skills/<skill>/. The copy keeps the gitignored skills/plugins/ out, since
users installing from GitHub never see it. Needs Node (npx) and network for the first run.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from repo import ROOT, report, skill_files

SKILLS_CLI = "skills@1.5.3"  # bump deliberately; the list output format is parsed below
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
LISTED = re.compile(r"^│ {4}(\S+)\s*$", re.MULTILINE)


def published_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout  # fmt: skip
    return [f for f in out.decode("utf-8").split("\0") if f and (ROOT / f).is_file()]


def listed_skills(folder: Path) -> set[str]:
    npx = shutil.which("npx")
    if not npx:
        sys.exit("error: npx not found; install Node 22.20+ to run this check")
    env = {**os.environ, "NO_COLOR": "1", "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1"}
    result = subprocess.run(
        [npx, "-y", SKILLS_CLI, "add", str(folder), "--list"],
        check=False, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300,
    )  # fmt: skip
    text = ANSI.sub("", result.stdout + result.stderr)
    names = set(LISTED.findall(text))
    if result.returncode != 0 or not names:
        sys.exit(
            f"error: {SKILLS_CLI} add --list failed or listed nothing:\n{text[-2000:]}"
        )
    return names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.parse_args(argv)

    expected = {f.parent.name for f in skill_files()}
    with tempfile.TemporaryDirectory(prefix="skills-discovery-") as tmp:
        for rel_path in published_files():
            target = Path(tmp, rel_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel_path, target)
        found = listed_skills(Path(tmp))
    problems = [f"skills.sh does not find {n!r}" for n in sorted(expected - found)]
    problems += [
        f"skills.sh finds {n!r}, which is not under skills/<plugin>/skills/"
        for n in sorted(found - expected)
    ]
    return report(
        problems,
        f"ok skills.sh finds all {len(found)} published skills and nothing else",
    )


if __name__ == "__main__":
    sys.exit(main())
