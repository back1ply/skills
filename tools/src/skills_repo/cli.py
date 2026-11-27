"""`repo`: the root command. It picks a subcommand and hands it the rest of the arguments."""

from __future__ import annotations

import argparse
import errno
import importlib
import importlib.metadata
import os
import sys

# Lazy "module:function" map, so a subcommand's imports load only when it runs.
COMMANDS = {
    "check": ("skills_repo.commands.check:main", "run the rules (default: every default rule)"),
    "rules": ("skills_repo.commands.rules:main", "list every rule with its ID"),
    "new": ("skills_repo.commands.new:main", "scaffold a plugin and its marketplace entry"),
    "readme": ("skills_repo.commands.readme:main", "rebuild README.md from its template"),
    "sync": ("skills_repo.commands.sync:main", "copy shared CLI rules into python-cli-packaging"),
}
EPILOG = """exit codes: 0 ok, 1 problems found or a command failed, 2 usage error
Run 'repo COMMAND --help' for a command's options."""


def configure_streams() -> None:
    """Windows pipes default to cp1252, so non-ASCII paths or messages would crash."""
    if os.environ.get("PYTHONIOENCODING"):
        return
    for stream, errors in ((sys.stdout, "strict"), (sys.stderr, "backslashreplace")):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors=errors)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo",
        description="Checks and chores for the back1ply/skills marketplace.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=importlib.metadata.version("skills-repo")
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    for name, (_, help_text) in COMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)
    return parser


def dispatch(argv: list[str] | None) -> int:
    args, rest = build_parser().parse_known_args(argv)
    module_name, _, func_name = COMMANDS[args.command][0].partition(":")
    return getattr(importlib.import_module(module_name), func_name)(rest)


def stdout_closed(exc: OSError) -> bool:
    """The reader closed the pipe (`| head`). Windows raises EINVAL, not EPIPE."""
    if isinstance(exc, BrokenPipeError):
        return True
    return sys.platform == "win32" and exc.errno == errno.EINVAL and exc.filename is None


def main(argv: list[str] | None = None) -> int:
    configure_streams()
    try:
        code = dispatch(argv)
        sys.stdout.flush()
        return code
    except OSError as exc:
        if not stdout_closed(exc):
            raise
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
