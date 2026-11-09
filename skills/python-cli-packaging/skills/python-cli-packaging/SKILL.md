---
name: python-cli-packaging
description: Builds, converts, and audits installable Python command-line tools that work for humans and for AI agents calling them from a shell. Use when packaging a folder of Python scripts into one CLI, starting a new Python CLI, reviewing or auditing an existing CLI repo, setting up pyproject.toml [project.scripts] entry points with uv, or making a CLI agent-friendly (--json, non-interactive, exit codes).
---

# Python CLI packaging

A packaged CLI has one installable command (`tool sub --flag`), declared in `pyproject.toml`, that behaves the same for a person at a terminal and for an agent or CI job with no TTY. The checklist has 93 items with stable IDs (`PKG-09`, `AGT-04`) in [references/checklist.md](references/checklist.md). Cite those IDs in every finding.

Pick the mode from the request:

| Mode | When | Ends with |
|---|---|---|
| **Audit** | Review, assess, or "is this good" on an existing CLI | A findings table covering every MUST and SHOULD item |
| **Convert** | Turn existing scripts into one installable CLI | Repo passes all MUSTs and the fresh-install test |
| **Build** | New CLI from scratch | Same as convert, without the migration items |

## Safety

Behavioural checks run real commands. Run read-only commands first (`--help`, `--version`, list or show). Run anything that writes, logs in, or touches a device only against a test target, a fixture file, or `--dry-run`. Clone third-party repos into a fresh empty directory and run their code only after reading what it does.

## Audit

1. **Inventory.** Read `pyproject.toml`, the entry modules, tests, CI workflows, and README. List every command and subcommand.
2. **Static checks.** Run the packaging, dependency, and ripgrep blocks in [references/checks.md](references/checks.md). Several commands there are Linux-only (`script`, `${PIPESTATUS}`, `/tmp`); on Windows use the Python script in the next step.
3. **Behavioural checks.** Install into an isolated env (`uv sync` or `uv tool install .`), then run the contract script from this skill's own directory (not the audited repo):
   ```
   python <skill-dir>/scripts/cli_contract.py --cmd "uv run tool" --sub <each-sub> --run "<safe args>" --json-run "<args> --json"
   ```
   It checks help, version, usage-error exit 2, no hang without a TTY, no ANSI in pipes, no tracebacks, and valid JSON. Then do the fresh-install test (TST-03): `uv build`, then run `uvx --from dist/<wheel>.whl tool --help` from a directory outside the repo.
4. **Report.** One table row per MUST and SHOULD item: `ID | status | evidence`. Status is `pass`, `fail`, `n/a` (with a reason), or `not checked` (with a reason). Evidence is a command plus its result, or `file:line`. List fails MUST first, then SHOULD, each with a concrete fix. Add NICE items only when they fail cheaply.

The audit is done when every MUST and SHOULD ID has a row. No item is skipped silently.

## Convert

1. **Decide whether to package (DIST-03).** One or two independent scripts with few dependencies may be better as PEP 723 scripts (`uv run --script`). Package when there are several related tools, shared code, or other users.
2. **Inventory and record.** Write down every current invocation (`python a.py X Y`), its arguments, exit codes, and how the scripts import each other. Sibling imports (`from a import x`) must become package imports.
3. **Restructure.** Use `src/<project_name>/` with a project-specific package name (PKG-09). Add `pyproject.toml` with `[project]`, `[build-system]`, `[project.scripts]`, and a `dev` dependency group. Set `requires-python` to the oldest version CI tests (PKG-03).
4. **Rewrite each tool** to `build_parser()` plus `main(argv=None) -> int`, following [references/patterns.md](references/patterns.md). Keep core logic importable without argparse. Dispatch subcommands in-process through a lazy `"module:function"` map, never through `subprocess` (LAY-07). Add `__main__.py`.
5. **Add the agent contract** from the MUST list below: streams, exit codes, `--json`, no prompts without a TTY.
6. **Tests and CI.** One `main([...])` test per subcommand (TST-01), a test that resolves every dispatch-map entry (LAY-06), the fresh-install test (TST-03), and CI with `astral-sh/setup-uv` and `uv sync --locked`.
7. **Docs.** README install paths for uv, pipx, and pip (DOC-01, DEP-04), exit codes, and a migration map from old to new invocations (DOC-05). Optionally add a `justfile` with `setup`, `test`, `lint`, and `check` recipes that wrap `uv run`.
8. **Verify** by running the audit steps 2–3 on the result.

Convert is done when every MUST passes, the fresh-install test passes from outside the repo, and each old invocation has a documented replacement.

## Build

Follow convert steps 3–8, skipping the migration map. For a new tool with several commands, click or typer are reasonable; see the defaults below.

## The MUST items

Every mode needs these. Full wording, verification, and sources are in the checklist.

**Packaging**
- PKG-01: `[build-system]` table present; without it uv ignores `[project.scripts]`.
- PKG-02: `[project]` has name, version, description, readme, requires-python, SPDX license; `LICENSE` file exists.
- PKG-03: `requires-python` floor equals the oldest Python in CI, with a written reason; no upper cap.
- PKG-09: top-level import package has a project-specific name, never `tools`, `utils`, `scripts`, `cli`, `app`, `lib`, `common`, or `src`.

**Entry points**
- LAY-01: every `[project.scripts]` target imports and resolves.
- LAY-02: `main(argv=None) -> int`; only the entry wrapper calls `sys.exit`.
- LAY-09: no `sys.path` edits in package code.

**Interface and output**
- CLI-01: a real parser (argparse, click, typer), no hand-parsed `sys.argv`.
- CLI-02: `--help` on root and every subcommand, to stdout, exit 0.
- CLI-05: `--version` to stdout, exit 0.
- CLI-08: usage errors exit 2, message on stderr, stdout empty.
- OUT-01: data on stdout; logs, progress, warnings, errors, prompts on stderr.
- OUT-02: any failure exits non-zero, including partial failure.
- OUT-04, OUT-05, OUT-06: color, spinners, and pagers only when the stream is a TTY and `NO_COLOR` is unset.

**Agents**
- AGT-01: data commands take `--json`; stdout is then exactly one JSON document.
- AGT-04: with no TTY on stdin, never wait for input; fail fast naming the flag to pass.
- AGT-05: every prompt has a flag equivalent (`--yes`, `--no-input`, a value flag).
- AGT-10: errors name the bad input and the fix.

**Errors and secrets**
- ERR-01: expected failures print one line on stderr, no traceback.
- ERR-04: tracebacks never include local variables (Typer: `pretty_exceptions_show_locals=False`).
- CFG-03: secrets come from a file, stdin, env var, or keyring, never a flag value.
- CFG-04: secrets never appear in output, logs, JSON, or errors.

**Dependencies, tests, distribution**
- DEP-02: `uv lock --check` passes when a lockfile exists.
- DEP-04 (convert): if `requirements.txt` is removed, the README documents `pip install .` or `pipx install`.
- TST-01: each subcommand has a test asserting exit code, stdout, and stderr separately.
- TST-03: wheel installs into a clean env and `tool --help` runs from outside the repo.
- DOC-01: README shows install commands for each supported path and the command name.
- DIST-01: `uv tool install .` and `pipx install .` put the command on PATH.

## Defaults for disputed choices

Reasoning and both sides are in [references/disputes.md](references/disputes.md).

- **Parser:** keep argparse when converting argparse scripts. New multi-command tools may use click or typer, which add roughly 100–200 ms of import time; keep heavy imports lazy (CLI-10).
- **Layout:** src. Flat is acceptable only when the fresh-install test runs in CI.
- **requirements.txt:** remove hand-written ones, document `pip install .`, generate pinned files with `uv export` when a platform needs one.
- **Lockfile:** commit `uv.lock`. It protects dev and CI only; `uv tool install`, pipx, and pip resolve fresh, so the `pyproject.toml` ranges must work alone (DEP-03).
- **New releases:** set `[tool.uv] exclude-newer = "7 days"`; justify any locked version newer than that (DEP-05).
- **Exit codes:** 0 success, 1 failure, 2 usage. Add more only for failure classes a caller would branch on, and document them.
- **JSON:** explicit `--json`, never switched on automatically by piping. In `--json` mode, errors go to stderr as JSON with a non-zero exit.
- **Prompts:** allowed when stdin and stdout are TTYs, as long as every prompt has a flag.
- **Agent env vars** (`CLAUDECODE`, `CI`): may change cosmetics only, never confirm actions.
- **CLI vs MCP:** build the CLI first, with a short usage guide for agents (DOC-06). Add an MCP server when users need OAuth, remote access, or have no shell.
- **Build backend:** `uv_build` for pure-Python tools; hatchling with hatch-vcs for git-tag versions.

## References

- [references/checklist.md](references/checklist.md): all 93 items with severity, modes, verification, and sources. Read it for an audit report or when an item ID needs detail.
- [references/checks.md](references/checks.md): copy-paste commands and the anti-pattern list. Read it in audit step 2.
- [references/disputes.md](references/disputes.md): debated choices and research gaps. Read it before overriding a default.
- [references/patterns.md](references/patterns.md): code shapes for `pyproject.toml`, the entry point, lazy dispatch, a subcommand, safe prompts, tests, and the fresh-install CI step. Read it in convert step 4 and build mode.
- [references/sources.md](references/sources.md): the 56 sources behind the checklist.
- `scripts/cli_contract.py`: cross-platform behavioural checks. Run `--help` for options.
