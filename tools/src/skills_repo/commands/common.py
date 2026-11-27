"""What every subcommand shares: the --root option, loading the repo, one-line errors."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skills_repo.model import Repo, RepoNotFound, find_root


def parser(command: str, description: str, epilog: str = "") -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=f"repo {command}",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,  # keep epilog examples on their lines
    )
    p.add_argument(
        "--root",
        type=Path,
        help="repo root (default: the nearest folder above here with .claude-plugin/marketplace.json)",
    )
    return p


def load_repo(args: argparse.Namespace) -> Repo:
    """Raises RepoNotFound with a message naming the fix."""
    root = args.root if args.root else find_root(Path.cwd())
    if not (root / ".claude-plugin" / "marketplace.json").is_file():
        raise RepoNotFound(f"{root} has no .claude-plugin/marketplace.json")
    return Repo.load(root)


def fail(message: str, *, as_json: bool = False, code: str = "failed") -> int:
    """One line on stderr (one JSON object under --json); returns exit code 1."""
    if as_json:
        json.dump({"error": {"code": code, "message": message}}, sys.stderr)
        sys.stderr.write("\n")
    else:
        print(f"error: {message}", file=sys.stderr)
    return 1
