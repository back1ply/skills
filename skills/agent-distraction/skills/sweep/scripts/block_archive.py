#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block agent access to the sweep archive folder.

Reads the hook event JSON on stdin. Exits 2 (block, reason on stderr) when the
tool call touches the archive folder, else 0. `mv` / `git mv` commands are
allowed so the sweep can move files into the archive.

Archive folder: $SWEEP_ARCHIVE_DIR, default "docs/archive" (relative to the project).
"""

from __future__ import annotations

import json
import os
import re
import sys

PATH_KEYS = ("file_path", "path", "notebook_path", "pattern", "glob", "command")
MOVE_COMMAND = re.compile(r"^\s*(git\s+)?mv\s")


def archive_marker() -> str:
    raw = os.environ.get("SWEEP_ARCHIVE_DIR", "docs/archive")
    return raw.replace("\\", "/").strip("/").lower()


def touched_values(tool_input: dict) -> list[str]:
    values = (tool_input.get(key) for key in PATH_KEYS)
    return [v.replace("\\", "/").lower() for v in values if isinstance(v, str)]


def is_allowed_move(tool_input: dict) -> bool:
    command = tool_input.get("command")
    return isinstance(command, str) and bool(MOVE_COMMAND.match(command))


def blocked(event: dict) -> bool:
    tool_input = event.get("tool_input") or {}
    if is_allowed_move(tool_input):
        return False
    marker = archive_marker()
    return any(marker in value for value in touched_values(tool_input))


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never break the session on malformed input
    if not blocked(event):
        return 0
    print(
        f"Blocked: {archive_marker()}/ holds archived, outdated files that are "
        "not part of the current plan. Use the live specs and code instead.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
