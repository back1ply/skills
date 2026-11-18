---
name: agent-friendly-cli
description: Designs, converts, and audits command-line tools in any language (Go, Rust, Node/TypeScript, Python) so AI agents such as Claude Code, Codex, and Cursor can call them reliably from a shell while they stay good for humans - stdout/stderr split, exit 2 for usage errors, --json, no prompts without a TTY, quiet closed pipes, bounded output, and actionable errors. Includes the framework defaults that break this (cobra, urfave/cli, commander, yargs, oclif, Rust println!) and tested reference CLIs. Use when building or reviewing a CLI that agents or scripts call, or when an agent misreads a tool's output or exit codes.
---

# Agent-friendly CLI

An agent calls your CLI with no terminal, stdin closed or at EOF, and reads back the exit code plus a truncated mix of stdout and stderr. Claude Code shows any non-zero exit as a failure and returns only about 10,000 characters of a failed command. Most popular CLI frameworks don't meet this contract out of the box: cobra, urfave/cli, commander, and yargs exit 1 on usage errors; urfave prints help to stdout on an error; Rust's `println!` panics when the reader closes the pipe. The checklist has 70 items with stable IDs (`CLI-03`, `OUT-06`) in [references/checklist.md](references/checklist.md). Cite those IDs in every finding.

Python CLIs: use `python-cli-packaging`, which covers this contract plus packaging. This skill is the language-neutral version, with per-framework fixes.

| Mode | When | Ends with |
|---|---|---|
| **Audit** | Review an existing CLI | Findings covering every MUST and SHOULD item |
| **Convert** | Fix an existing CLI so agents can use it | Every MUST passes `scripts/cli_contract.py` and the usage-error loop |
| **Build** | New CLI | Same, starting from the reference CLI for the language |

## Safety

Behavioural checks run the tool for real. Read how it parses arguments before sending `--help` or an unknown flag: a hand-parsed CLI may treat them as data and run its action. Run anything that writes, deletes, or calls a paid or remote API only against a test target or with `--dry-run`.

## Audit

1. **Inventory.** Language, parser framework and version, every command, how `main` exits, where output is written, any prompts, env vars read, and existing tests.
2. **Look up the framework's traps** in the per-language table in [references/patterns.md](references/patterns.md). Most audit findings are a known default left unfixed.
3. **Run the contract script** from this skill's directory against the built binary:
   ```
   python <skill-dir>/scripts/cli_contract.py --cmd "<binary>" --sub <each-sub> --run "<safe args>" --json-run "<args> --json" --pipe-run "<args printing over 64 KB>"
   ```
   Then the usage-error loop from patterns.md (unknown subcommand, extra positional, bad value, missing argument). On Windows set `PYTHONUTF8=0` and quote paths with spaces inside `--cmd`.
4. **Read the code** for what scripts can't see: secrets in flags or output (CFG-03, ERR-04), prompts without a flag bypass (AGT-07), env detection changing behaviour (AGT-15), exits outside `main` (EXIT-04).
5. **Report.** Fails (MUST first) as `ID | evidence | fix`; not checked as `ID | reason | what would check it`; n/a grouped by cause, one line each; passes one line each. Done when every MUST and SHOULD ID appears in exactly one list.

## Convert and build

1. **Single exit point first** (EXIT-04, OUT-05): Go `func main() { os.Exit(run()) }`, Rust `fn main() -> ExitCode`, Node `process.exitCode`. Everything else hangs off this.
2. **Fix the parser defaults** from the patterns.md code for your framework: usage errors exit 2 with a short stderr message, help on stdout, unknown flags and extra positionals rejected (CLI-02, CLI-03, CLI-04, CLI-07).
3. **Streams:** data on stdout, everything else on stderr; color and progress only on a TTY with `NO_COLOR` unset; quiet exit on a closed pipe (OUT-01 to OUT-06).
4. **Agent contract:** `--json` on data commands, no prompts without a TTY and a flag for every prompt, bounded default output with `--limit`, one-line actionable errors (AGT-01, AGT-06, AGT-07, AGT-11, ERR-01, ERR-02).
5. **Exit-code table** documented in `--help` or the README; "no results" exits 0 (EXIT-02, EXIT-03).
6. **Contract tests** in CI that run the built binary and assert exit code, stdout, and stderr separately (TST-01, TST-02).
7. **Verify** with audit step 3.

## The MUST items

**Parsing:** CLI-01 real parser · CLI-02 `--help` on stdout, exit 0, every command · CLI-03 usage errors exit 2, stderr only · CLI-06 `--version` on stdout · CLI-07 unknown flags and extra positionals rejected.
**Streams:** OUT-01 data on stdout, the rest on stderr · OUT-02 no ANSI unless stdout is a TTY and `NO_COLOR` is unset (never decide from `TERM`) · OUT-03 progress only on a TTY · OUT-04 pager only on a TTY · OUT-05 no output lost at exit.
**Exit codes:** EXIT-01 any failure is non-zero · EXIT-02 one documented table (0, 1, 2 = usage, 3–125 for branchable failures) · EXIT-03 exit 1 only for real failures.
**Agents:** AGT-01 `--json` gives exactly one JSON document · AGT-06 never wait for input without a TTY · AGT-07 a flag for every prompt, plus `--no-input` · AGT-15 env detection never bypasses safety.
**Errors and secrets:** ERR-01 one-line errors, no stack traces · ERR-02 errors name the input and the fix · ERR-04, CFG-04 secrets never in output · CFG-03 secrets never as flag values.
**Testing:** TST-01 contract tests run the built binary and check exit code, stdout, and stderr separately.

## Defaults for disputed choices

Both sides are in [references/disputes.md](references/disputes.md).

- **JSON:** explicit `--json`, never switched on by "stdout isn't a TTY" (Codex can run commands in a PTY).
- **Help:** text help; an optional `commands --json` listing for machines.
- **Exit 2:** usage errors only, whatever the framework does by default.
- **Suggestions:** "did you mean" in the error text, never auto-run.
- **Large results:** one JSON document with `--limit` and paging; NDJSON only for event streams.
- **No arguments:** help on stdout, exit 0, for multi-command tools.
- **Destructive actions without a TTY:** require `--yes`; never auto-confirm from an env var.
- **Discovery:** name the CLI in the docs agents read; a skill is optional; MCP only when a CLI can't serve the need.

## References

- [references/checklist.md](references/checklist.md): all 70 items with severity, modes, verification, per-framework notes, and sources.
- [references/patterns.md](references/patterns.md): the per-language contract table and complete reference CLIs in Go (cobra), Rust (clap), and Node (commander).
- [references/disputes.md](references/disputes.md): debated choices with both sides.
- [references/sources.md](references/sources.md): 49 sources, research experiments, and the reference CLI tests.
- `scripts/cli_contract.py`: language-neutral behavioural checks (help, version, usage errors, no-TTY hang, ANSI, crashes, JSON, closed pipe). Run `--help` for options.
