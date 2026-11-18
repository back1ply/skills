# Patterns

How to meet the contract in each language, then one complete reference CLI per language. The three CLIs implement the same tool (`demo list [--limit N] [--json]`, `demo show FILE`) and each passes all 15 checks of `scripts/cli_contract.py`, plus the usage-error cases in sources.md (P1). Item IDs point to [checklist.md](checklist.md).

## Contents

- Per-language contract table
- Go (cobra)
- Rust (clap)
- Node (commander)
- Other frameworks
- Checking any CLI

## Per-language contract table

| Contract point | Go | Rust | Node / TypeScript | Python |
|---|---|---|---|---|
| Parser | cobra (+ pflag), urfave/cli v3, stdlib `flag` | clap 4 (derive) | commander 15, yargs 18, oclif (`@oclif/core` 5) | py skill: argparse/click/typer |
| Usage error → exit 2, stderr only | `flag`: by default [S5]. **cobra**: `SilenceUsage`, `SilenceErrors`, `SetFlagErrorFunc` → usageErr, wrap `Args` validators, and treat a message prefixed `unknown command` as usage; `main` maps to 2 (E2). **urfave v3**: `OnUsageError` → `cli.Exit(msg, 2)`; the default prints help to stdout and exits 1 (E4) | by default: `Cli::parse()` → `Error::exit` [S6, E8] | **commander**: `exitOverride()` + `CommanderError` → `process.exitCode = 2` (E10). **yargs**: `.strict().fail((msg, err) => …)` with `process.exit(2)` for `!err`, and wrap handlers in try/catch (E11). **oclif**: 2 by default, but `this.error` is also 2, so pass `{exit:1}` [S19] | argparse: by default (python-cli-packaging CLI-08) |
| Help → stdout, exit 0 | cobra yes [S1]. **`flag` prints to stderr** (E7). urfave yes (E4) | yes; `-h` short vs `--help` long [S7] | commander, yargs yes (E10, E11) | argparse yes |
| Suggestions | cobra built in [S1]; urfave `Suggest` [S2] | built in (E8) | commander default [S17]; yargs `.recommendCommands()` | argparse 3.14+ `suggest_on_error` (py CLI-09) |
| TTY check | `golang.org/x/term.IsTerminal(int(f.Fd()))`; go-isatty also has `IsCygwinTerminal` | `std::io::IsTerminal` (1.70+) [S12] | `process.stdout.isTTY === true` (it is `undefined` when piped, E12) [S16] | `sys.stdout.isatty()` |
| Color / NO_COLOR | manual: isatty && `NO_COLOR` empty && `TERM != dumb` | anstream/clap automatic [S8]; `colorchoice-clap` adds `--color` | commander `useColor()` [S17]; `tty.getColorDepth` [S16]; `util.styleText` checks the stream (E12) | py OUT-04 |
| Closed pipe | Unix: SIGPIPE kills quietly [S4]. Windows: check write errors (not `syscall.EPIPE`, E6) | `println!` panics (E9). Use `writeln!` on a locked `BufWriter` and treat `ErrorKind::BrokenPipe` as success (E9 snippet below) | `process.stdout.on('error', e => { if (e.code === 'EPIPE') process.exit(0); throw e; })` (E12) | catch `BrokenPipeError` (py OUT-08) |
| Exit plumbing and flush | `func main() { os.Exit(run()) }`; never `os.Exit` with live defers [S3, E5] | `fn main() -> ExitCode`; avoid `process::exit` [S10] | set `process.exitCode`; avoid `process.exit()` with pending writes [S15] | `raise SystemExit(main())` |
| Expected-error output | return errors up; print `error: %v` once in `main` | print `error: {e}` and return `ExitCode::FAILURE`; don't return `Err` from `main` (Debug output, E8) | top-level try/catch → `console.error('error: ' + e.message)` | py ERR-01 |
| Completion | cobra auto `completion` + `__complete` (E3) | `clap_complete` | commander/yargs: yargs `.completion()`; oclif plugin | click/typer built in |
| Contract test | `os/exec` + `ExitCode()`; testscript [S22] | assert_cmd [S13] + trycmd/snapbox [S14] | execa `reject:false` [S20] + vitest / `node:test` | pytest + subprocess (py TST-04) |
| Any language | bats `run -N --separate-stderr` [S21] | | | |

## Go (cobra)

`go.mod` requires (tested versions):

```
github.com/spf13/cobra v1.10.2
golang.org/x/term v0.48.0
```

```go
// demo: a cobra CLI that follows the agent contract.
package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"golang.org/x/term"
)

const version = "1.0.0"

// usageErr marks errors that must exit 2 (CLI-03).
type usageErr struct{ error }

func (u usageErr) Unwrap() error { return u.error }

func usage(c *cobra.Command, err error) error {
	return usageErr{fmt.Errorf("%w\nRun '%s --help' for usage.", err, c.CommandPath())}
}

// usageArgs turns cobra's positional-argument errors into usage errors.
func usageArgs(check cobra.PositionalArgs) cobra.PositionalArgs {
	return func(c *cobra.Command, args []string) error {
		if err := check(c, args); err != nil {
			return usage(c, err)
		}
		return nil
	}
}

// stdoutWriter records write failures so a closed pipe ends quietly (OUT-06).
type stdoutWriter struct{ failed bool }

func (w *stdoutWriter) Write(p []byte) (int, error) {
	n, err := os.Stdout.Write(p)
	if err != nil {
		w.failed = true
	}
	return n, err
}

// color only on a terminal, never when NO_COLOR is set; TERM alone proves nothing (OUT-02).
func color(f *os.File) bool {
	return term.IsTerminal(int(f.Fd())) && os.Getenv("NO_COLOR") == "" && os.Getenv("TERM") != "dumb"
}

type item struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

func newRoot(out io.Writer) *cobra.Command {
	root := &cobra.Command{
		Use:           "demo",
		Short:         "Demo CLI that follows the agent contract",
		Example:       "  demo list --limit 5 --json\n  demo show notes.txt",
		Version:       version,
		SilenceUsage:  true, // no usage dump on runtime errors (CLI-04)
		SilenceErrors: true, // main prints errors once
	}
	root.SetFlagErrorFunc(usage)

	var limit int
	var asJSON bool
	list := &cobra.Command{
		Use:     "list",
		Short:   "List items",
		Example: "  demo list --limit 5 --json",
		Args:    usageArgs(cobra.NoArgs),
		RunE: func(_ *cobra.Command, _ []string) error {
			if asJSON {
				items := make([]item, limit)
				for i := range items {
					items[i] = item{ID: i, Name: fmt.Sprintf("item-%d", i)}
				}
				return json.NewEncoder(out).Encode(items) // one JSON document (AGT-01)
			}
			prefix := "item"
			if color(os.Stdout) {
				prefix = "\x1b[32mitem\x1b[0m"
			}
			for i := range limit {
				if _, err := fmt.Fprintf(out, "%s-%d\n", prefix, i); err != nil {
					return err
				}
			}
			return nil
		},
	}
	list.Flags().IntVar(&limit, "limit", 10, "maximum number of items")
	list.Flags().BoolVar(&asJSON, "json", false, "print one JSON document")

	show := &cobra.Command{
		Use:   "show FILE",
		Short: "Print a file",
		Args:  usageArgs(cobra.ExactArgs(1)),
		RunE: func(_ *cobra.Command, args []string) error {
			data, err := os.ReadFile(args[0])
			if err != nil {
				return fmt.Errorf("cannot read %s: %w; pass an existing file", args[0], errors.Unwrap(err))
			}
			_, err = out.Write(data)
			return err
		},
	}
	root.AddCommand(list, show)
	return root
}

// run returns the exit code; every defer runs before main exits (OUT-05, EXIT-04).
func run() int {
	sw := &stdoutWriter{}
	out := bufio.NewWriter(sw)
	err := newRoot(out).Execute()
	if ferr := out.Flush(); err == nil {
		err = ferr
	}
	switch {
	case sw.failed:
		return 0 // reader closed the pipe (head, grep -m1): not an error
	case err == nil:
		return 0
	}
	fmt.Fprintln(os.Stderr, "error:", err)
	var u usageErr
	if errors.As(err, &u) || strings.HasPrefix(err.Error(), "unknown command") {
		return 2
	}
	return 1
}

func main() { os.Exit(run()) }
```

What the defaults get wrong and this code fixes: the common template `os.Exit(1)` makes usage errors exit 1 and dumps the full usage on every error (`SilenceUsage`); `SetFlagErrorFunc` covers only flag parsing, so positional-argument errors go through `usageArgs` and unknown commands are matched by their message; `os.Exit` would skip a deferred flush, so `run()` returns the code and `main` only exits; on Windows a closed pipe is a write error rather than SIGPIPE, so `stdoutWriter` records it and the tool exits 0 quietly.

## Rust (clap)

```toml
[package]
name = "demo"
version = "1.0.0"
edition = "2024"

[dependencies]
clap = { version = "4", features = ["derive"] }
```

```rust
//! demo: a clap CLI that follows the agent contract.
use clap::{CommandFactory, Parser, Subcommand};
use std::io::{self, BufWriter, ErrorKind, IsTerminal, Write};
use std::path::PathBuf;
use std::process::ExitCode;

/// Demo CLI that follows the agent contract
#[derive(Parser)]
#[command(
    name = "demo",
    version,
    after_help = "Examples:\n  demo list --limit 5 --json\n  demo show notes.txt"
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// List items
    List {
        /// Maximum number of items
        #[arg(long, default_value_t = 10)]
        limit: usize,
        /// Print one JSON document
        #[arg(long)]
        json: bool,
    },
    /// Print a file
    Show { file: PathBuf },
}

/// Color only on a terminal, never when NO_COLOR is set; TERM alone proves nothing (OUT-02).
fn color() -> bool {
    io::stdout().is_terminal()
        && std::env::var_os("NO_COLOR").is_none_or(|v| v.is_empty())
        && std::env::var("TERM").map_or(true, |t| t != "dumb")
}

fn run(cli: Cli) -> io::Result<()> {
    let mut out = BufWriter::new(io::stdout().lock()); // writeln! returns errors; println! panics on a closed pipe
    let Some(command) = cli.command else {
        // Bare `demo` is a discovery step: help on stdout, exit 0 (CLI-05).
        write!(out, "{}", Cli::command().render_help())?;
        return out.flush();
    };
    match command {
        Command::List { limit, json } => {
            if json {
                let items: Vec<String> = (0..limit)
                    .map(|i| format!(r#"{{"id":{i},"name":"item-{i}"}}"#))
                    .collect();
                writeln!(out, "[{}]", items.join(","))?; // one JSON document (AGT-01)
            } else {
                let prefix = if color() {
                    "\x1b[32mitem\x1b[0m"
                } else {
                    "item"
                };
                for i in 0..limit {
                    writeln!(out, "{prefix}-{i}")?;
                }
            }
        }
        Command::Show { file } => {
            let text = std::fs::read_to_string(&file).map_err(|e| {
                io::Error::new(
                    e.kind(),
                    format!("cannot read {}: {e}; pass an existing file", file.display()),
                )
            })?;
            out.write_all(text.as_bytes())?;
        }
    }
    out.flush()
}

fn main() -> ExitCode {
    let cli = Cli::parse(); // usage errors: stderr, exit 2; --help/--version: stdout, exit 0
    match run(cli) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) if e.kind() == ErrorKind::BrokenPipe => ExitCode::SUCCESS, // reader closed the pipe (OUT-06)
        Err(e) => {
            eprintln!("error: {e}"); // Display, not the Debug dump `main -> Result` would print (ERR-01)
            ExitCode::FAILURE
        }
    }
}
```

clap already exits 2 on usage errors with stderr-only output, prints help and version on stdout, and suggests near-miss subcommands. What this code adds: `writeln!` on a `BufWriter` instead of `println!` (which panics on a closed pipe, exit 101), `BrokenPipe` mapped to success, errors printed with Display instead of the Debug dump that `main -> Result` prints, and an explicit `flush()` so a write error isn't swallowed when the `BufWriter` drops.

## Node (commander)

`package.json` needs `"type": "module"` and `commander` (tested with 15.1.0).

```js
#!/usr/bin/env node
// demo: a commander CLI that follows the agent contract.
import { readFileSync } from 'node:fs';
import { Command, CommanderError, InvalidArgumentError } from 'commander';

// A reader that closes the pipe early (head, grep -m1) is not an error (OUT-06).
process.stdout.on('error', (e) => {
  if (e.code === 'EPIPE') process.exit(0);
  throw e;
});

// isTTY is undefined, not false, when piped; TERM alone proves nothing (OUT-02).
const color = process.stdout.isTTY === true && !process.env.NO_COLOR && process.env.TERM !== 'dumb';

function parseLimit(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < 0) throw new InvalidArgumentError('expected a non-negative integer, e.g. --limit 5');
  return n;
}

const program = new Command('demo')
  .description('Demo CLI that follows the agent contract')
  .version('1.0.0')
  .exitOverride() // throw instead of exiting, so usage errors can become exit 2
  .addHelpText('after', '\nExamples:\n  demo list --limit 5 --json\n  demo show notes.txt');

program
  .command('list')
  .description('List items')
  .option('--limit <n>', 'maximum number of items', parseLimit, 10)
  .option('--json', 'print one JSON document')
  .action(({ limit, json }) => {
    const ids = Array.from({ length: limit }, (_, i) => i);
    if (json) {
      process.stdout.write(`${JSON.stringify(ids.map((i) => ({ id: i, name: `item-${i}` })))}\n`); // AGT-01
      return;
    }
    const prefix = color ? '\x1b[32mitem\x1b[0m' : 'item';
    process.stdout.write(ids.map((i) => `${prefix}-${i}\n`).join(''));
  });

program
  .command('show')
  .description('Print a file')
  .argument('<file>')
  .action((file) => {
    let text;
    try {
      text = readFileSync(file, 'utf8');
    } catch (e) {
      throw new Error(`cannot read ${file}: ${e.code}; pass an existing file`);
    }
    process.stdout.write(text);
  });

try {
  if (process.argv.length <= 2) {
    program.outputHelp(); // bare `demo` is a discovery step: help on stdout, exit 0 (CLI-05)
  } else {
    await program.parseAsync();
  }
} catch (e) {
  if (e instanceof CommanderError) {
    process.exitCode = e.exitCode === 0 ? 0 : 2; // help/version: 0; any parse error: 2 (CLI-03)
  } else {
    console.error(`error: ${e.message}`); // one line, no stack (ERR-01)
    process.exitCode = 1;
  }
}
// No process.exit() here: it can cut off piped stdout on POSIX (OUT-05).
```

commander exits 1 on usage errors by default, and Node crashes with an unhandled `EPIPE` when the reader closes the pipe. `exitOverride()` plus the `CommanderError` mapping gives exit 2 for parse errors and 0 for help and version; handler errors become one `error:` line with exit 1. `process.exitCode` instead of `process.exit()` keeps piped output from being cut off on POSIX.

## Other frameworks

- **urfave/cli v3:** prints the help to stdout on a usage error and accepts extra positionals silently. Return `cli.Exit(msg, 2)` from `OnUsageError`, and validate positional counts in each action:

```go
OnUsageError: func(ctx context.Context, c *cli.Command, err error, sub bool) error {
	return cli.Exit(fmt.Sprintf("error: %v\nRun 'demo --help' for usage.", err), 2)
},
```

- **Go `flag`:** exits 2 on usage errors already, but `-h` prints to stderr; set `flag.Usage` to write to stdout when help was asked for.
- **yargs:** needs `.strict()`, `.demandCommand(1)`, and `.fail((msg, err) => ...)` that exits 2 for parse errors; a synchronous throw inside a handler bypasses `.fail`, so wrap handlers in try/catch.
- **oclif:** usage errors already exit 2, but `this.error()` also exits 2, so pass `{exit: 1}` for runtime failures.
- **Python:** see the `python-cli-packaging` skill.

## Checking any CLI

```
python <skill-dir>/scripts/cli_contract.py --cmd "./demo" --sub list --sub show \
  --run "list" --run "show missing.txt" --json-run "list --json" --pipe-run "list --limit 200000"
```

Add the usage errors the script doesn't send, and check each exits 2 with empty stdout:

```
for args in "lsit" "list extra" "list --limit x" "show"; do
  ./demo $args >out.txt 2>err.txt </dev/null; echo "[$args] rc=$? stdout=$(wc -c <out.txt)B"
done
```

On Windows run it with `PYTHONUTF8=0`, quote paths with spaces inside `--cmd`, and use `--cmd "node demo.mjs"` for Node scripts.
