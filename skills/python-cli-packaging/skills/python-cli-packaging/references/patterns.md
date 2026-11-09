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
requires = ["uv_build"]                 # or hatchling, setuptools
build-backend = "uv_build"

[project]
name = "mytool"
version = "0.1.0"
description = "One line saying what mytool does"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"              # oldest version CI tests; reason: tomllib
dependencies = ["httpx>=0.27"]          # lower bounds, no == pins

[project.scripts]
mytool = "mytool.cli:main"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]            # lower bounds, so lowest-version tests work

[tool.uv]
exclude-newer = "7 days"                # dependency cooldown (DEP-05)
```

## Entry point and dispatch (LAY-02, LAY-07, CLI-08)

```python
# src/mytool/cli.py
import argparse
import importlib
import importlib.metadata
import sys

# Lazy "module:function" map: a subcommand's heavy imports load only when it runs.
COMMANDS = {
    "export": ("mytool.commands.export:main", "export records"),
    # one entry per module in mytool/commands/
}


def build_parser():
    parser = argparse.ArgumentParser(prog="mytool", description="What mytool does.")
    parser.add_argument("--version", action="version",
                        version=importlib.metadata.version("mytool"))
    parser.add_argument("command", choices=COMMANDS, metavar="COMMAND",
                        help=", ".join(f"{k}: {v[1]}" for k, v in COMMANDS.items()))
    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        build_parser().print_help(sys.stderr)
        return 2
    if argv[0] not in COMMANDS:
        build_parser().parse_args(argv[:1])   # argparse prints the error to stderr and exits 2
    target, _ = COMMANDS[argv[0]]
    module_name, _, func_name = target.partition(":")
    func = getattr(importlib.import_module(module_name), func_name)
    return func(argv[1:])
```

Unknown flags and commands must reach argparse's error path, which writes to stderr and exits 2. Printing help to stdout for an unknown flag fails CLI-08.

## A subcommand (OUT-01, ERR-01, AGT-01)

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


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        records = load_records(args.source, limit=args.limit)
    except FileNotFoundError:
        print(f"error: {args.source} not found; pass an existing JSON file", file=sys.stderr)
        return 1
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

Data goes to stdout, every message to stderr. Expected failures print one line naming the input and the fix, then return non-zero.

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
- run: uv build
- run: |
    cd "$RUNNER_TEMP"
    uvx --from "$GITHUB_WORKSPACE"/dist/*.whl mytool --help
    uvx --from "$GITHUB_WORKSPACE"/dist/*.whl mytool --version
```
