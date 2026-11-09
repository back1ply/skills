"""Black-box contract checks for any installed CLI. Stdlib only, works on Windows and POSIX.

Runs the command as a subprocess with stdin closed and stdout piped (no TTY),
the way an agent or CI calls it. Covers CLI-02, CLI-05, CLI-08, AGT-01, AGT-04,
OUT-04, and ERR-01 from references/checklist.md.

    python cli_contract.py --cmd "mytool" --sub fetch --sub dump
    python cli_contract.py --cmd "uv run mytool" --run "dump --file x.xml" --json-run "list --json"

Only pass --run / --json-run commands that are safe to execute (read-only or a
test target). The script runs them for real.

The script always sends --help, --version, and an unknown flag to the root
command, and --help to every --sub. A script that hand-parses sys.argv may treat
those as real arguments and run its action, so read its argument handling first.

Exit codes: 0 all checks passed, 1 at least one check failed, 2 usage error
or the command could not start (its root --help printed nothing and failed).
"""

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass

ANSI = "\x1b["
BOGUS_FLAG = "--definitely-not-a-real-flag-xyz"


@dataclass
class Result:
    check: str
    target: str
    ok: bool
    detail: str = ""


@dataclass
class Run:
    rc: int | None  # None means it timed out
    out: str
    err: str


def run(cmd, args, timeout):
    try:
        proc = subprocess.run(
            [*cmd, *args],
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return Run(None, "", "")
    except FileNotFoundError:
        raise SystemExit(f"error: command not found: {cmd[0]}") from None
    return Run(proc.returncode, proc.stdout, proc.stderr)


def first_err(r):
    lines = r.err.strip().splitlines()
    return f", stderr: {lines[0][:100]!r}" if lines else ""


def preflight(cmd, timeout):
    """Stop early when the command cannot start, so later checks can't pass vacuously."""
    r = run(cmd, ["--help"], timeout)
    if r.rc != 0 and not r.out.strip():
        print(
            f"error: '{shlex.join(cmd)} --help' printed nothing and exited {r.rc}{first_err(r)}. "
            "Make sure the command runs on its own (on Windows, pass paths as F:/..., not /f/...).",
            file=sys.stderr,
        )
        raise SystemExit(2)


def check_help(cmd, sub, timeout):
    args = [*sub, "--help"]
    r = run(cmd, args, timeout)
    ok = r.rc == 0 and bool(r.out.strip())
    return Result(
        "help",
        " ".join(args),
        ok,
        f"rc={r.rc}, stdout {len(r.out)} chars{first_err(r)}",
    )


def check_version(cmd, timeout):
    r = run(cmd, ["--version"], timeout)
    ok = r.rc == 0 and bool(r.out.strip())
    return Result(
        "version", "--version", ok, f"rc={r.rc}, stdout={r.out.strip()[:60]!r}"
    )


def check_usage_error(cmd, timeout):
    r = run(cmd, [BOGUS_FLAG], timeout)
    ok = r.rc == 2 and not r.out.strip() and bool(r.err.strip())
    detail = f"rc={r.rc} (want 2), stdout empty={not r.out.strip()}, stderr set={bool(r.err.strip())}"
    return Result("usage-error", BOGUS_FLAG, ok, detail)


def check_run(cmd, line, timeout):
    """No hang without a TTY, no ANSI in piped output, no traceback."""
    r = run(cmd, shlex.split(line), timeout)
    if r.rc is None:
        return [
            Result(
                "no-tty",
                line,
                False,
                f"timed out after {timeout}s (waiting for input?)",
            )
        ]
    return [
        Result("no-tty", line, True, f"rc={r.rc}{first_err(r)}"),
        Result(
            "no-ansi",
            line,
            ANSI not in r.out and ANSI not in r.err,
            "escape codes in piped output",
        ),
        Result(
            "no-traceback",
            line,
            "Traceback (most recent call last)" not in r.err,
            "traceback on stderr",
        ),
    ]


def check_json(cmd, line, timeout):
    r = run(cmd, shlex.split(line), timeout)
    try:
        json.loads(r.out)
    except json.JSONDecodeError as exc:
        return Result(
            "json", line, False, f"rc={r.rc}, stdout is not one JSON document: {exc}"
        )
    return Result("json", line, r.rc == 0, f"rc={r.rc}")


def collect(opts):
    cmd = shlex.split(opts.cmd)
    t = opts.timeout
    preflight(cmd, t)
    results = [check_help(cmd, [], t), check_version(cmd, t), check_usage_error(cmd, t)]
    results += [check_help(cmd, [s], t) for s in opts.sub]
    for line in opts.run:
        results += check_run(cmd, line, t)
    results += [check_json(cmd, line, t) for line in opts.json_run]
    return results


def report(results, as_json):
    if as_json:
        print(json.dumps([asdict(r) for r in results], indent=2))
        return
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        note = "" if r.ok and r.check != "help" else f"  ({r.detail})"
        print(f"{status}  {r.check:<13} {r.target}{note}")
    failed = sum(not r.ok for r in results)
    print(f"{len(results) - failed}/{len(results)} checks passed", file=sys.stderr)


def build_parser():
    p = argparse.ArgumentParser(
        prog="cli_contract.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--cmd", required=True, help='command to test, e.g. "mytool" or "uv run mytool"'
    )
    p.add_argument(
        "--sub",
        action="append",
        default=[],
        help="subcommand whose --help to check (repeatable)",
    )
    p.add_argument(
        "--run",
        action="append",
        default=[],
        help="safe args to run without a TTY (repeatable)",
    )
    p.add_argument(
        "--json-run",
        action="append",
        default=[],
        help="safe args whose stdout must be JSON (repeatable)",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="seconds per call (default: %(default)s)",
    )
    p.add_argument("--json", action="store_true", help="print results as JSON")
    return p


def main(argv=None):
    opts = build_parser().parse_args(argv)
    results = collect(opts)
    report(results, opts.json)
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
