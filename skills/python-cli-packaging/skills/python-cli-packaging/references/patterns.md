# Code patterns

Reference shapes for a packaged argparse CLI named `mytool` with import package `mytool`. Rename both. Item IDs point to [checklist.md](checklist.md).

## Layout

```
pyproject.toml
src/mytool/
    __init__.py
    __main__.py        # python -m mytool
    cli.py             # root parser and dispatch
    commands/
        __init__.py
        export.py      # one module per subcommand: build_parser() + main(argv)
    core/
        records.py     # logic with no argparse imports (LAY-03)
tests/
```

## pyproject.toml

```toml
[build-system]
requires = ["uv_build>=0.13,<0.14"]     # cap at the next minor (PKG-01); no patch pin, or exclude-newer can block it
build-backend = "uv_build"

[project]
name = "mytool"
version = "0.1.0"
description = "One line saying what mytool does"
readme = "README.md"
license = "MIT"
license-files = ["LICENSE"]             # PEP 639 (PKG-02)
requires-python = ">=3.11"              # proven: uv run --python 3.11 pytest (PKG-03)
dependencies = ["httpx>=0.27"]          # lower bounds, no == pins

[project.scripts]
mytool = "mytool.cli:main"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]            # lower bounds, so lowest-version tests work

[tool.uv]
exclude-newer = "7 days"                # dependency cooldown (DEP-05)

# Only when the package name differs from the normalized project name,
# e.g. dist "my-tool" with package "mytool" (PKG-09):
# [tool.uv.build-backend]
# module-name = "mytool"
```

## Entry point and dispatch (LAY-02, LAY-07, CLI-01, CLI-08, OUT-12)

```python
# src/mytool/cli.py
import argparse
import importlib
import importlib.metadata
import os
import sys

# Lazy "module:function" map: a subcommand's heavy imports load only when it runs.
COMMANDS = {
    "export": ("mytool.commands.export:main", "export records"),
    # one entry per module in mytool/commands/
}


def configure_streams():
    """OUT-12: Windows pipes default to cp1252, so non-ASCII output or error text crashes."""
    if os.environ.get("PYTHONIOENCODING"):   # the caller chose an encoding; keep it
        return
    for stream, errors in ((sys.stdout, "strict"), (sys.stderr, "backslashreplace")):
        if hasattr(stream, "reconfigure"):   # StringIO in tests has no reconfigure
            stream.reconfigure(encoding="utf-8", errors=errors)


def build_parser():
    parser = argparse.ArgumentParser(prog="mytool", description="What mytool does.",
                                     epilog="Run 'mytool COMMAND --help' for command options.")
    parser.add_argument("--version", action="version",
                        version=importlib.metadata.version("mytool"))
    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    for name, (_, help_text) in COMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)  # the command's own parser owns --help
    return parser


def main(argv=None):
    configure_streams()
    args, rest = build_parser().parse_known_args(argv)  # no command or unknown command: stderr, exit 2
    module_name, _, func_name = COMMANDS[args.command][0].partition(":")
    func = getattr(importlib.import_module(module_name), func_name)
    return func(rest)  # the command's parser handles its flags, --help, and unknown flags
```

The root parser only picks the command; everything after it goes to that command's own `build_parser()`, so `mytool export --help` shows export's help and `mytool export --bogus` gets export's usage error on stderr with exit 2. Root options go before the command (`mytool --version`). Printing help to stdout for an unknown flag fails CLI-08.

## A subcommand (OUT-01, ERR-01, AGT-01, AGT-03)

```python
# src/mytool/commands/export.py
import argparse
import json
import sys

from mytool.core.records import load_records


def build_parser():
    parser = argparse.ArgumentParser(prog="mytool export", description="Export records.",
                                     epilog="Example: mytool export data.json --json")
    parser.add_argument("source", help="JSON file of records")
    parser.add_argument("--json", action="store_true", help="print one JSON document")
    parser.add_argument("--limit", type=int, default=100, help="max records (default: %(default)s)")
    return parser


def fail(args, code, message):
    """One-line error on stderr; one JSON object instead under --json (AGT-03)."""
    if args.json:
        json.dump({"error": {"code": code, "message": message}}, sys.stderr)
        sys.stderr.write("\n")
    else:
        print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv=None):
    args = build_parser().parse_args(argv)  # usage errors: argparse text on stderr, exit 2
    try:
        records = load_records(args.source, limit=args.limit)
    except FileNotFoundError:
        return fail(args, "not_found", f"{args.source} not found; pass an existing JSON file")
    if args.json:
        json.dump(records, sys.stdout)
        sys.stdout.write("\n")
    else:
        for r in records:
            print(f"{r['id']}\t{r['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Data goes to stdout, every message to stderr. Expected failures print one line naming the input and the fix, then return non-zero. Under `--json` the same failure is one JSON object on stderr, so an agent can parse it; stdout stays empty.

## Exit codes (CLI-08, OUT-02, OUT-03, OUT-11, AGT-03, AGT-11)

Agent harnesses show any non-zero exit as a failure before the caller reads a word of output (Claude Code prints `Exit code N`). So non-zero must mean "something went wrong", and the detail belongs in stderr or the JSON error.

| Code | Meaning | Use it for |
|---|---|---|
| 0 | Success | The command did its job, including "no results" (print `[]` under `--json`) |
| 1 | Runtime failure | Missing file, bad data, network or auth error, partial failure. The message (or JSON `error.code`) says which |
| 2 | Usage error | Unknown flag, missing argument, bad choice. argparse does this; never reuse 2 for runtime results |
| 3–125 | Documented extras | Only for a failure class callers branch on (for example 3 = "already exists" for an idempotent create). List each in `--help` and the README |
| 126–127 | Reserved by the shell | Not executable / command not found. Never use them |
| 128+N | Killed by signal N | 130 for Ctrl-C (OUT-11). Don't use others on purpose |
| 124 | Reserved by `timeout` | Means the caller's timeout fired. Never use it |

Comparison commands are the exception agents trip on: `diff` and `grep` exit 1 for "differences found" or "no match", which a harness shows as a failure. Prefer exit 0 with the result in the output (`"identical": false` under `--json`). If you keep the `diff` convention because users expect it, use 1 for "different" and 2 for errors, and say so in `--help`.

## `__main__.py` (LAY-04)

```python
from mytool.cli import main

raise SystemExit(main())
```

## Prompts that never block agents (AGT-04, AGT-05)

```python
import getpass
import os
import sys


def get_token(token_file=None):
    if token_file:
        return open(token_file, encoding="utf-8").read().strip()
    if token := os.environ.get("MYTOOL_TOKEN"):
        return token
    if not sys.stdin.isatty():
        raise SystemExit("error: no token; pass --token-file PATH or set MYTOOL_TOKEN")
    return getpass.getpass("Token: ")
```

## Tests (TST-01, TST-02, LAY-06)

```python
import importlib

import pytest

from mytool import cli


@pytest.mark.parametrize("name", cli.COMMANDS)
def test_every_command_resolves(name):
    module_name, _, func_name = cli.COMMANDS[name][0].partition(":")
    assert callable(getattr(importlib.import_module(module_name), func_name))


def test_export_json(tmp_path, capsys):
    src = tmp_path / "data.json"
    src.write_text('[{"id": 1, "name": "a"}]')
    assert cli.main(["export", str(src), "--json"]) == 0
    out, err = capsys.readouterr()
    assert out.startswith("[") and err == ""


def test_unknown_flag_exits_2_on_stderr(capsys):
    with pytest.raises(SystemExit) as exc:   # argparse exits; main never returns
        cli.main(["export", "data.json", "--bogus"])
    assert exc.value.code == 2
    out, err = capsys.readouterr()
    assert out == "" and "--bogus" in err
```

## Fresh-install check in CI (TST-03)

```yaml
- run: uv build                          # builds the wheel from the sdist, so both are tested
- run: |
    cd "$RUNNER_TEMP"
    run() { uvx --from "$GITHUB_WORKSPACE"/dist/*.whl mytool "$@"; }
    run --help
    run --version
    for sub in export; do run "$sub" --help; done   # imports every subcommand module
    run export "$GITHUB_WORKSPACE"/tests/fixtures/data.json --json   # one real command
```

Root `--help` alone imports no subcommand module, so a missing dependency or data file would still pass.
