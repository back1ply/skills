"""Check that long reference files open with a Contents section.

    uv run scripts/lint_references.py                 # every skills/*/skills/*/references/*.md
    uv run scripts/lint_references.py FILE [FILE...]  # only these (the pre-push hook passes changed files)

Anthropic's skill authoring guidance: a reference file over 100 lines gets a table of contents at
the top, so an agent that previews only the first lines still sees everything the file covers.
Past fix: "Cite four uncited sources; add Contents to long reference files".
"""

import argparse
import re
import sys
from pathlib import Path

from repo import PLUGINS_DIR, rel, report

MAX_LINES = 100
HEAD_LINES = 30  # the Contents heading must appear this early
CONTENTS = re.compile(
    r"^#{1,6}\s+(contents|table of contents)\s*$", re.IGNORECASE | re.MULTILINE
)


def is_reference(path: Path) -> bool:
    parts = path.relative_to(PLUGINS_DIR).parts
    # <plugin>/skills/<skill>/references/<file>.md, outside the private skills/plugins/
    return (
        path.suffix == ".md"
        and len(parts) == 5
        and parts[1] == "skills"
        and parts[3] == "references"
        and parts[0] != "plugins"
    )


def check(path: Path) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) <= MAX_LINES:
        return None
    if CONTENTS.search("\n".join(lines[:HEAD_LINES])):
        return None
    return f"{rel(path)}: {len(lines)} lines and no '## Contents' in the first {HEAD_LINES} lines"


def select_files(given: list[Path]) -> list[Path]:
    """The given files that are reference files, or every reference file if none are given."""
    if not given:
        return sorted(
            p for p in PLUGINS_DIR.glob("*/skills/*/references/*.md") if is_reference(p)
        )
    resolved = [p.resolve() for p in given if p.exists()]
    return [p for p in resolved if p.is_relative_to(PLUGINS_DIR) and is_reference(p)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="files to check (default: all reference files)",
    )
    args = parser.parse_args(argv)

    files = select_files(args.files)
    problems = [msg for p in files if (msg := check(p))]
    return report(
        problems,
        f"ok {len(files)} reference files under {MAX_LINES} lines or with Contents",
    )


if __name__ == "__main__":
    sys.exit(main())
