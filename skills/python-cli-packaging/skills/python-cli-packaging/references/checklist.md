# Python CLI checklist

94 items with stable IDs. Sources: [sources.md](sources.md). Commands in tables escape `|` as `\|`; copy runnable commands from [checks.md](checks.md) instead.

Modes: **B** build, **C** convert, **A** audit. Every item applies in audit mode unless the mode column says otherwise. The only items without A are the convert-only LAY-08, DOC-05, and DIST-03.


### 2.1 Packaging and metadata (PKG)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| PKG-01 | `pyproject.toml` has a `[build-system]` table with `requires` and `build-backend`. Without it, `[project.scripts]` does nothing under uv. | MUST | B C A | `grep -A3 '^\[build-system\]' pyproject.toml`, then `uvx 'validate-pyproject[all]' pyproject.toml` (docs) | S7, S23 (PP002), S41 |
| PKG-02 | The `[project]` table has `name`, `version` (or `dynamic`), `description`, `readme`, `requires-python`, `license` as an SPDX string, and a `LICENSE` file is present. | MUST | B C A | `validate-pyproject` passes, `ls LICENSE*`, and `uv build` succeeds | S23 (PY002, PY003, PP005), S27, S41 |
| PKG-03 | The `requires-python` floor equals the oldest Python version CI actually tests, and the reason for it is written down. It has no upper cap. | MUST | B C A | Compare `grep requires-python pyproject.toml` with the CI `python-version` matrix. `grep -E "requires-python.*<"` must find nothing. | S22, S23 (PP004), S7 |
| PKG-04 | Runtime `dependencies` use lower bounds. No exact `==` pins (exact pins belong in the lockfile). Any upper cap has a comment explaining it. | SHOULD | B C A | `python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies'])"` and look for `==` or `<` | S22 |
| PKG-05 | Dev tools (ruff, pytest, type checker) live in `[dependency-groups]` (PEP 735), not in `dependencies` or `optional-dependencies`. | SHOULD | B C A | `grep -A5 '^\[dependency-groups\]' pyproject.toml` | S24, S23 (PP006) |
| PKG-06 | The version has one source of truth. `--version` reads `importlib.metadata.version("<dist>")` or the build backend's dynamic version, not a second hardcoded string. | SHOULD | B C A | `tool --version` matches the version in `pyproject.toml`. `rg -n "__version__ = ['\"]"` finds no duplicate. | S17 (factor 3), S27 |
| PKG-07 | `uv build` produces an sdist and a wheel whose metadata passes `twine check --strict`. Run this in CI. | SHOULD (MUST if publishing) | B C A | `uv build && uvx twine check --strict dist/*` | S27, S43 |
| PKG-08 | The wheel contains only the package: no `tests/`, no `.pyc`, one top-level entry. | SHOULD | B C A | `uvx check-wheel-contents dist/*.whl` | S40 |
| PKG-09 | The top-level import package has a project-specific name. Never use a generic name such as `tools`, `utils`, `scripts`, `cli`, `app`, `lib`, `common`, or `src`, because installed packages with the same top-level name overwrite each other. | MUST | B C A | `python -c "import zipfile,glob;print({n.split('/')[0] for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist()})"`. W005 catches `cli`, `app`, `scripts`, `lib`, and `src`, but not `tools`, `utils`, or `common`, so check those by eye. | S40 (W005 rationale), S27 (naming) |
| PKG-10 | The distribution name is free on PyPI, or deliberately private. The command name is short, lowercase, and does not clash with an existing command. | SHOULD | B C A | `curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/<name>/json` returns 404. `command -v <cmd>` finds nothing before install. | S16 (naming), S27 |
| PKG-11 | Bundled data files load through `importlib.resources`, not paths built from `__file__` or the working directory. | SHOULD | B C A | `rg -n "__file__\|os\.getcwd\(\)\|Path\.cwd\(\)" src/`, then run the fresh-install smoke test (TST-03) from another directory | S21, S2 |

### 2.2 Entry points and layout (LAY)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| LAY-01 | Every command is declared in `[project.scripts]` as `pkg.module:function`, and every target can be imported and resolved. | MUST | B C A | `python -c "import tomllib,importlib;[getattr(importlib.import_module(v.split(':')[0]),v.split(':')[1]) for v in tomllib.load(open('pyproject.toml','rb'))['project']['scripts'].values()]"` inside the project environment | S3, S1, S7 |
| LAY-02 | The entry-point function has the signature `main(argv: Sequence[str] \| None = None) -> int`. It returns an int exit code or `None`, never a string. Library code does not call `sys.exit()`. | MUST | B C A | `rg -n "sys\.exit\|raise SystemExit" src/` matches only the top-level entry wrappers. Read `main`'s signature. | S3, S4 |
| LAY-03 | Core logic is separate from CLI wiring. Core functions can be imported and called without argparse or `sys.argv`, and the CLI module stays thin. | SHOULD | B C A | No module other than the CLI layer imports argparse, click, or typer. `rg -ln "argparse\|import click\|import typer" src/` | S1, S4 |
| LAY-04 | `python -m pkg` works through a minimal `__main__.py` that only imports and calls `main`. | SHOULD | B C A | `python -m pkg --help; echo $?` prints 0 | S4, S1 |
| LAY-05 | A packaged CLI uses the src layout, or the repo records why it chose flat. Either way, tests run against the installed package. | SHOULD | B C A | `ls src/`. Run the TST-03 smoke test. | S1, S2, S21, S24 (disputed: disputes.md) |
| LAY-06 | Every target in a lazy subcommand map (`{"name": "module:function"}` resolved by importlib) can be imported, and a test enforces this. A typo in the map only fails at runtime otherwise. | SHOULD (if a map is used) | B C A | A parametrized pytest that runs `importlib.import_module` and `getattr` for every map entry, plus `tool <sub> --help` for each subcommand | Derived; no source requires it. Supporting background: S3 (object-reference syntax), S17 (factor 9, lazy loading). |
| LAY-07 | Subcommands run in-process by calling functions, not through `subprocess` running `python script.py`. In-process calls keep exit codes, env, and speed, and avoid Windows interpreter mix-ups. | SHOULD | C A | `rg -n "subprocess.*(sys\.executable\|python)" src/` finds nothing for internal dispatch | S4 (same behaviour as a console script), S17 (factor 9) |
| LAY-08 | If old scripts must stay runnable on their own, that is checked from a clean shell, because relative imports break `python path/to/script.py`. Otherwise the README documents `python -m pkg.tool`. | SHOULD | C | `cd /tmp && python <repo>/src/pkg/tool.py --help` (or `python -m pkg.tool --help`) | S4, S2 |
| LAY-09 | Package code never modifies `sys.path` (`sys.path.insert` or `append` hacks). | MUST | C A | `rg -n "sys\.path\.(insert\|append)" src/` finds nothing | S21, S1. S2 mentions a `sys.path` workaround only for running an uninstalled src-layout CLI during development. It does not endorse it in shipped code. |
| LAY-10 | Related tools sit under one top-level command with subcommands. The grammar is consistent (all noun-verb or all verb-noun) and no two subcommand names are easy to confuse. | SHOULD | B C A | Read `tool --help` | S16, S17 (factor 11), S30, S37 |

### 2.3 CLI interface and help (CLI)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| CLI-01 | Arguments go through a real parser (argparse, click, or typer). No hand-parsing of `sys.argv`. | MUST | B C A | `rg -n "sys\.argv\[" src/` finds nothing outside `main(argv)` defaults | S16, S1 |
| CLI-02 | `-h` and `--help` work on the root command and every subcommand. They print to stdout, exit 0, and take priority over other arguments. | MUST | B C A | `for s in $(subcommands); do tool $s --help >/dev/null \|\| echo FAIL $s; done` | S16, S17 |
| CLI-03 | Running with no arguments shows usage or the subcommand list and performs no action. | SHOULD | B C A | `tool </dev/null; echo $?` prints usage and does nothing | S17 (factor 11), S32 (`no_args_is_help`), S16 |
| CLI-04 | Every command's help has a one-line description and at least one working example. | SHOULD | B C A | Read `tool <sub> --help` and look for an "Examples" or epilog section | S16, S17, S18, S30 |
| CLI-05 | `tool --version` prints the version to stdout and exits 0. | MUST | B C A | `tool --version; echo $?` | S17, S16, S31 |
| CLI-06 | Every flag has a long form. Single-letter flags exist only for common options. Flags use conventional names (`--json`, `--quiet`, `--verbose`, `--output`, `--dry-run`, `--force`/`--yes`, `--no-input`, `--no-color`), and names are unambiguous (`--user-id`, not `--user`). | SHOULD | B C A | Read the flag list in `--help` | S16, S17, S34 |
| CLI-07 | Flags are preferred over positional arguments. Use at most one kind of positional, such as a list of files. | SHOULD | B C A | Read the help. Two different positional types is a smell. | S17, S16, S30 |
| CLI-08 | A usage error (unknown flag, missing argument, bad choice) exits 2, prints its message on stderr, and leaves stdout empty. | MUST | B C A | `tool --bogus >o 2>e; echo $?` prints 2, `test ! -s o`, `test -s e` | S16, S37, S30 |
| CLI-09 | A mistyped subcommand or choice gets a suggestion (argparse `suggest_on_error=True` on 3.14+, built into click and typer). Suggestions never run automatically. | NICE | B C A | `tool lsit` suggests `list` | S6, S16 |
| CLI-10 | `tool --help` starts in roughly 500 ms or less. Heavy imports are deferred to the subcommand that needs them. | SHOULD | B C A | `python -X importtime -c "import pkg.cli" 2>&1 \| sort -t'\|' -k2 -n \| tail -5`, then `hyperfine 'tool --help'` | S17 (100–500 ms target), S47 |
| CLI-11 | Where a file is expected, `-` means stdin or stdout. | NICE | B C A | `echo data \| tool cmd -` | S16, S33 |

### 2.4 Output and exit codes (OUT)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| OUT-01 | Data goes to stdout. Logs, progress, warnings, errors, and prompts go to stderr. | MUST | B C A | `tool cmd 2>/dev/null` shows only data and `tool cmd >/dev/null` shows only diagnostics. `rg -n "print\(" src/` and check each one that is not data. | S16, S17, S30, S36 |
| OUT-02 | Success exits 0 and any failure exits non-zero, including partial failures. Never exit 0 after printing an error. | MUST | B C A | Trigger a known failure (missing file, bad credentials) and check that `echo $?` is not 0. `rg -n "except.*:\s*$" -A3 src/` to find swallowed errors. | S16, S3, S30 |
| OUT-03 | Exit codes are documented in the README or the `--help` epilog and stay stable. At minimum, usage error (2) is distinct from runtime failure (1). | SHOULD | B C A | `grep -i "exit code" README*` | S16, S35, S36, S37 (scheme disputed: disputes.md) |
| OUT-04 | No ANSI escape codes appear when stdout is not a TTY, when `NO_COLOR` is set to a non-empty value, when `TERM=dumb`, or with `--no-color`. | MUST | B C A | `tool cmd \| grep -c $'\x1b\['` prints 0. `NO_COLOR=1 script -qc "tool cmd" /dev/null \| grep -c $'\x1b\['` prints 0 (Linux). | S16, S17, S30, S6 |
| OUT-05 | Spinners, progress bars, and animations appear only when stderr is a TTY. | MUST | B C A | `tool longcmd 2>err.txt </dev/null; grep -c $'\r' err.txt` prints 0 | S16, S17 |
| OUT-06 | A pager is never started unless stdout is a TTY. | MUST | B C A | `timeout 10 tool cmd \| cat; echo "${PIPESTATUS[0]}"` is not 124 (bash; plain `$?` would report `cat`) | S16, S38 |
| OUT-07 | Human output is line-oriented: one record per line, no box borders. If the default is a table, a `--plain`, `--json`, or tab-separated form exists. | SHOULD | B C A | `tool list \| wc -l` equals the number of records | S17 (factor 8), S16 |
| OUT-08 | A closed pipe produces no traceback. `BrokenPipeError` is handled as the Python docs describe. | SHOULD | B C A | `(tool list 2>err.txt) \| head -1; grep -c Traceback err.txt` prints 0. The output must be larger than the pipe buffer (about 64 KB), or EPIPE never fires and the check passes falsely. | S5 |
| OUT-09 | Output is deterministic: stable sort order, no timestamps or random IDs unless asked for, ISO 8601 times instead of "3 days ago". | SHOULD | B C A | Run the same command twice and `diff` the outputs | S37, S16 (`--plain` stability) |
| OUT-10 | Commands that change state say what changed. `-q`/`--quiet` silences them. | SHOULD | B C A | Run a mutating command and look for a one-line confirmation, then check that `-q` silences it | S16, S30 |
| OUT-11 | Ctrl-C exits quickly with code 130 and a short message, not a `KeyboardInterrupt` traceback. | SHOULD | B C A | `timeout --preserve-status -s INT 2 tool longcmd 2>e; echo $?` prints 130 and `grep -c Traceback e` prints 0 (without `--preserve-status`, GNU timeout reports 124) | S16, S31 |
| OUT-12 | Output with non-ASCII text survives being piped or redirected on Windows (no `UnicodeEncodeError` from cp1252). Reconfigure stdout to UTF-8 or document `PYTHONUTF8=1`. | SHOULD | B C A | On Windows: `tool cmd-with-unicode > out.txt; echo $?` | Python Windows encoding behaviour (PEP 528/686; from knowledge, not fetched). Gap: no CLI source covers it. |

### 2.5 Agent-friendliness (AGT)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| AGT-01 | Every data-returning command has `--json` (or `--format json`). With it, stdout holds exactly one valid JSON document (or NDJSON for streams) and nothing else. | MUST | B C A | `tool cmd --json \| python -c "import json,sys;json.load(sys.stdin)"` | S16, S30, S35, S36, S37, S39 |
| AGT-02 | The JSON shape is a documented, stable contract: field names are consistent across commands, the structure is flat, and changes are additive only. | SHOULD | B C A | Schema or examples in the docs, plus the TST-04 contract test | S16 (future-proofing), S30, S37 |
| AGT-03 | Failures stay machine-detectable in `--json` mode: a non-zero exit plus a parseable error with a code and message. A `transient`/retryable hint is a plus. | SHOULD | B C A | `tool cmd --json --bad-input; echo $?` returns non-zero with a parseable error (stream: disputes.md) | S30, S36, S37 |
| AGT-04 | The tool never blocks waiting for input when stdin is not a TTY. It shows no prompt, and fails fast with a message naming the flag to pass. | MUST | B C A | `timeout 10 tool <each-cmd> </dev/null; echo $?` is never 124 | S16, S17 (factor 7), S30, S35, S36, S37 |
| AGT-05 | Every prompt or confirmation has a flag equivalent (`--yes`/`--force`, `--no-input`, or a value flag). | MUST | B C A | `rg -n "input\(\|getpass\|confirm\(\|prompt\(" src/`, then check each hit for a bypass flag and an isatty guard | S16, S17, S30, S36 |
| AGT-06 | Mutating commands offer `--dry-run`. It changes nothing and reports the planned changes (structured under `--json`). | SHOULD | B C A | Run `--dry-run` and confirm no files or remote state changed (`git status`, checksums) | S16, S30, S36, S37 |
| AGT-07 | Mutating commands are idempotent, or report "already exists" as a distinct result. Re-running after an interruption is safe. | SHOULD | B C A | Run the same create or apply command twice: the second run succeeds or returns the documented conflict code | S16 (robustness), S30, S36, S37 |
| AGT-08 | Output is bounded: list and search commands have a default limit, accept `--limit` and filters, and print a hint on truncation explaining how to get more. Field selection or `--quiet` bare values are a plus. | SHOULD | B C A | `tool list` against a large dataset prints at most N items plus a hint (on stderr) | S34, S36, S30, S39, S37 |
| AGT-09 | Mutations print the identifier or path of what they created or changed, so the next command can chain on it. | SHOULD | B C A | `tool create --json \| jq -r .id` | S30, S36, S37 |
| AGT-10 | Errors are actionable: what failed, the offending input, and the fix (valid values or the exact command to run). | MUST | B C A | Trigger 3 common errors and check each message names the input and a next step | S16, S17, S34, S36, S37 |
| AGT-11 | "No results" (exit 0, empty list or `[]`) is distinguishable from "query failed" (non-zero, error object). Carry the difference in the JSON, not in a special exit code. | SHOULD | B C A | Run a query that matches nothing (`echo $?` prints 0, `--json` prints `[]`) and one that fails (non-zero) | S48, S16 |
| AGT-12 | `--help` alone is enough for an agent to use the tool: subcommands, required vs optional arguments, defaults, an example, a mention of `--json`, and exit codes. | SHOULD | B C A | Give an agent only `tool --help` and see whether it can complete a typical task | S19, S37, S35, S36 |
| AGT-13 | If the tool detects CI or agent env vars (`CI`, `AGENT`, `CLAUDECODE`, ...), they change cosmetics only (color, pager, progress). They never auto-confirm or skip safety checks. | SHOULD (MUST NOT break if detection is implemented) | B A | `rg -n "CLAUDECODE\|AGENT\|CODEX" src/` and read what each hit changes | S38 |
| AGT-14 | Lookup commands accept several identifiers in one call (`tool show A B C --json` returns one array), so agents don't pay startup, config, and auth cost once per item. | SHOULD | B C A | `tool show <id1> <id2> --json` returns both records in one document | S48 |
| AGT-15 | Inputs are flags and positional arguments. Structured input, if offered, is an extra path that reads from a file or stdin (`--input spec.json`, `-`), never the only way and never only an inline JSON string, because shell quoting breaks it (worst on PowerShell). | SHOULD | B C A | Read `--help`: every required value has a flag. `rg -n "json.loads\(args\." src/` and check each has a flag equivalent | S57, S16 |

### 2.6 Errors and logging (ERR)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| ERR-01 | Expected failures (missing file, bad input, network, auth) show a one-line message on stderr, not a traceback. Inputs are validated before any side effect. | MUST | B C A | `tool cmd /nonexistent 2>&1 \| grep -c Traceback` prints 0 | S16, S17, S30, S31 |
| ERR-02 | Unexpected errors show a full traceback only behind `--debug`/`-v` or an env var such as `TOOL_DEBUG=1`. By default they print a short message and where to report the bug. | SHOULD | B C A | Read the top-level exception handler in `main` | S16, S17 |
| ERR-03 | Diagnostics go through `logging` to stderr, with the level set by `-v`/`-q`. `logging.basicConfig(stream=sys.stdout)` is a fail. | SHOULD | B C A | `rg -n "basicConfig\|StreamHandler\(sys\.stdout" src/` | S16 |
| ERR-04 | Tracebacks never print local variables, which can contain secrets. On Typer, require `typer>=0.23` (where locals are off by default) or set `pretty_exceptions_show_locals=False`. | MUST (Typer/Rich users) | B C A | `grep typer pyproject.toml` and `rg -n "show_locals" src/` | S46 |

### 2.7 Config, env vars, and secrets (CFG)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| CFG-01 | Config precedence is flags, then env vars, then project config, then user config, then defaults, and it is documented. | SHOULD | B C A | Read the README and the config-loading code | S16, S30, S36 |
| CFG-02 | The tool's own env vars carry its prefix (`TOOLNAME_*`) and are documented. It honors the standard ones (`NO_COLOR`, `HTTP(S)_PROXY`, `TMPDIR`, `PAGER`, `EDITOR`). | SHOULD | B C A | `rg -n "os\.environ\|getenv" src/` and compare against the docs | S16 |
| CFG-03 | Secrets are never accepted as flag values, because flags leak into `ps` output and shell history. Accept them from a file, stdin, or a keyring (env vars: disputes.md). | MUST | B C A | Read `--help` for `--password`, `--token`, `--secret`, or `--api-key` flags that take a value | S16, S30 |
| CFG-04 | Secrets never appear in output, logs, `--json`, error messages, or debug dumps. | MUST | B C A | Run with `--debug --json` and grep the output for a test token | S16, S46 |
| CFG-05 | Config, cache, and data files go to platform locations (XDG on Linux, `%LOCALAPPDATA%` on Windows, for example via `platformdirs`), never into the package directory or an unannounced spot in the working directory. | SHOULD | B C A | `rg -n "expanduser\|Path\.home\|open\(.*['\"]w" src/` | S17 (factor 12), S16 |
| CFG-06 | Network calls have a timeout that is configurable and has a sensible default. | SHOULD | B C A | `rg -n "requests\.(get\|post)\|httpx\.\|urlopen" src/` and check each call passes `timeout=` | S16 |

### 2.8 Dependencies, lockfile, and supply chain (DEP)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DEP-01 | An application repo commits `uv.lock` (or another lockfile), and CI installs with `uv sync --locked`. | SHOULD | B C A | `git ls-files uv.lock` and `grep -n "sync --locked" .github/workflows/*` | S8, S24, S25 |
| DEP-02 | The lockfile matches `pyproject.toml`. | MUST (if a lock exists) | B C A | `uv lock --check` | S8 |
| DEP-03 | The repo accepts that `uv.lock` only protects dev and CI. `uv tool install`, `pipx`, and `pip install` resolve fresh from the `pyproject.toml` ranges, so those ranges must work alone. Test the lowest direct versions. | SHOULD | B C A | In a scratch copy (it rewrites `uv.lock`): `cp -r . /tmp/lowcheck && cd /tmp/lowcheck && uv sync --resolution lowest-direct && uv run pytest` (docs). In place, finish with `git checkout uv.lock`. | S14, S15, S10 |
| DEP-04 | A pip path exists. The README documents `pip install .` or `pipx install git+URL`. If a pinned requirements file is needed, it is generated with `uv export --format requirements.txt` (or `--format pylock.toml`, the PEP 751 standard) and CI checks it is current. Never delete a requirements.txt without documenting the replacement. | SHOULD (MUST in convert mode when requirements.txt is removed) | C A | `grep -nE "pip install\|pipx install" README*`. If the file exists: `uv export --format requirements.txt --no-hashes \| diff - requirements.txt`. | S12, S28, S24, S59 (disputed: disputes.md) |
| DEP-05 | A dependency cooldown is set (`[tool.uv] exclude-newer = "7 days"`, which needs uv 0.9.17+), with exceptions listed in `exclude-newer-package`. Any locked version less than about 7 days old has a written reason, for example a security fix. | SHOULD | B C A | `grep -n exclude-newer pyproject.toml`. Check age with `curl -s https://pypi.org/pypi/<pkg>/<ver>/json \| jq -r '.urls[0].upload_time'` | S9, S49 |
| DEP-06 | CI scans dependencies for known vulnerabilities, with `uv audit --locked` (preview) or `pip-audit`. CI may also set `UV_MALWARE_CHECK=1`. | SHOULD | B C A | `grep -nE "uv audit\|pip-audit" .github/workflows/*` | S13, S24 |
| DEP-07 | Runtime dependencies are kept minimal. Small tools prefer the stdlib. No dev tool appears in runtime `dependencies`. | SHOULD | B C A | `uv tree --no-dev --depth 1` | S47, S24 |

### 2.9 Testing (TST)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| TST-01 | Every subcommand has at least one test that calls `main([...])` (or uses CliRunner) and asserts the exit code, stdout, and stderr separately. | MUST | B C A | `rg -n "main\(\[" tests/` or `CliRunner`, mapped against the subcommand list | S44, S45, S30 |
| TST-02 | Tests account for argparse raising `SystemExit` on `--help` (code 0) and on usage errors (code 2) even when `main` returns ints. They use `pytest.raises(SystemExit)` and assert `.code`. | SHOULD | B C A | `rg -n "raises\(SystemExit\)" tests/` | S52 (on errors argparse prints to stderr and exits 2, `help` "prints ... and then exits", `exit_on_error=False` documented only for argument errors), S4 |
| TST-03 | A fresh-install smoke test runs: build the wheel, install it into a clean, isolated environment, then run `tool --help` and `tool --version` from outside the repo. An editable install (`uv sync`) does not count, because it can still see files the wheel leaves out. | MUST | B C A | `uv build && cd /tmp && uvx --from <repo>/dist/<name>-<ver>-py3-none-any.whl tool --help` | S21, S2, S45 (subprocess mode), S56 |
| TST-04 | Contract tests pin the agent-facing behaviour: `--json` parses, no ANSI escapes when piped, no hang with stdin at `/dev/null`, and usage errors exit 2 with empty stdout. | SHOULD | B C A | `pytest -k contract` with subprocess-based tests (`pytest-console-scripts --script-launch-mode=subprocess`) | S30, S45 |
| TST-05 | Help text is protected against accidental interface changes, either by snapshot tests of `--help` or by docs generated from `--help` (Cog). | NICE | B C A | Look for snapshot files or `cog --check` in CI | S18, S30 |
| TST-06 | The CI matrix covers the `requires-python` floor and the newest Python, plus Windows and macOS if users run there. | SHOULD | B C A | Read the workflow `matrix:` | S22, S31 |

### 2.10 CI (CI)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| CI-01 | CI runs `astral-sh/setup-uv`, `uv sync --locked`, `ruff check`, `ruff format --check`, `pytest`, and the build checks (PKG-07, PKG-08, TST-03). Adding a type checker (ty, mypy, or pyright) is a plus. | SHOULD | B C A | Read `.github/workflows/*.yml` | S24, S8, S25 |
| CI-02 | Workflows pin actions to SHAs (or keep them updated with Dependabot) and declare least-privilege `permissions:`. Lint them with actionlint and zizmor. | SHOULD | B C A | `uvx zizmor .github/workflows/` (docs). `grep -n "permissions:" .github/workflows/*` | S25, S24, S23 (GH200, GH210, GH211) |
| CI-03 | Publishing uses PyPI Trusted Publishing (OIDC), not a long-lived API token. | SHOULD (if publishing) | B A | `grep -n "pypa/gh-action-pypi-publish\|id-token: write" .github/workflows/*` and no `PYPI_TOKEN` secret | S23 (GH105), S20, S27 |

### 2.11 Docs and README (DOC)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DOC-01 | The README gives install commands for each supported path (`uv tool install`, `pipx install`, `pip install`, from git) and the exact command name. | MUST | B C A | `grep -nE "uv tool install\|pipx install\|pip install" README*` | S17 (factors 1, 10), S1, S10 |
| DOC-02 | The README shows usage examples and the `--help` output, kept in sync (Cog or a CI check). | SHOULD | B C A | Compare the README help block with `tool --help` output | S18, S17 |
| DOC-03 | The README documents exit codes, env vars, config file locations, and the `--json` output shape. | SHOULD | B C A | grep the README for those sections | S16, S30, S37 |
| DOC-04 | There is a changelog and the project follows SemVer. Flags, subcommands, exit codes, and JSON fields count as public API: breaking changes bump the major version and first get a deprecation warning on stderr. | SHOULD | B C A | `ls CHANGELOG*`, then `git log -p` on the CLI module for renamed flags | S18, S16, S30, S31 |
| DOC-05 | Convert mode records a migration map from old invocations (`python script_a.py --x`) to new ones (`tool a --x`). Shims stay for one release if other people or scripts call the old names. | SHOULD | C | Look for a migration section in the README or CHANGELOG | S30, S16 |
| DOC-06 | Ship a short AGENTS.md section or agent skill that leads with usage: the 3–7 core tasks, which commands are safe for agents, and which ones are destructive or cost money (paid APIs, tokens), with the cheaper alternative. Keep it short; a short opinionated guide beats a long reference. | SHOULD | B C A | Look for `AGENTS.md` or `SKILL.md` and check it starts with usage, not contribution rules | S35, S19, S48, S50, S55 |

### 2.12 Distribution and install paths (DIST)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DIST-01 | `uv tool install .` and `pipx install .` install the tool into an isolated environment and put the command on PATH. | MUST | B C A | `uv tool install . && tool --version && uv tool uninstall <dist>` | S1, S10 |
| DIST-02 | `uvx --from git+https://<repo> tool --help` works, so the tool can be tried without installing it. | NICE | B C A | Run it from `/tmp` | S10 |
| DIST-03 | Convert mode decides whether packaging is warranted at all. One or two independent single-file scripts with few dependencies may be better as PEP 723 scripts (`#!/usr/bin/env -S uv run --script`, `uv lock --script`). | SHOULD | C | Count the scripts, how much code they share, and whether anyone else installs them | S11, S7, S24 |

Total: 94 items (PKG 11, LAY 10, CLI 11, OUT 12, AGT 15, ERR 4, CFG 6, DEP 7, TST 6, CI 3, DOC 6, DIST 3).
