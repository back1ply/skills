# Automated checks and anti-patterns

On Windows, the `script`, `${PIPESTATUS}`, `timeout --preserve-status`, and `/tmp` lines below are Linux-only. Use `scripts/cli_contract.py` for the behavioural checks instead.

Commands are unescaped and can be copied as-is. The packaging, dependency, and lint/CI blocks were run against a sample project (Windows, uv 0.11) and work as written. Not run: the CLI-contract bash block (Linux-only; use `scripts/cli_contract.py` on Windows), the startup-time block, `actionlint`, and `hyperfine` (separate installs). `pyproject-fmt --check` fails on any file it would reformat; run `pyproject-fmt pyproject.toml` to apply the formatting. Replace `tool`, `pkg`, `<repo>`, and `<wheel>` with real values. Run behavioural checks against a test target only (see Safety in SKILL.md).

**Packaging and metadata**

```
uvx 'validate-pyproject[all]' pyproject.toml        schema
uvx pyproject-fmt --check pyproject.toml            formatting
uvx 'sp-repo-review[cli]' .                         PY/PP/GH repo checks
uv build
uvx twine check --strict dist/*
uvx check-wheel-contents dist/*.whl
python -c "import zipfile,glob;print({n.split('/')[0] for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist()})"   # top-level names: reject tools/utils/common
```

**Entry points and fresh install**

```
uv run python -c "import tomllib,importlib;[getattr(importlib.import_module(m),f) for m,f in (v.split(':') for v in tomllib.load(open('pyproject.toml','rb'))['project']['scripts'].values())]"
cd /tmp && uvx --from <repo>/dist/<wheel>.whl tool --help && uvx --from <repo>/dist/<wheel>.whl tool --version
python -m pkg --help
```

**Dependencies and supply chain**

```
uv lock --check
uv sync --locked
uv audit --locked                                     # preview
UV_MALWARE_CHECK=1 uv sync --locked                 opt-in malware check
uv export --format requirements.txt --no-hashes | diff - requirements.txt   # only if requirements.txt is kept
grep -n "exclude-newer" pyproject.toml
curl -s https://pypi.org/pypi/<pkg>/<ver>/json | jq -r '.urls[0].upload_time'   # age of a locked version
# Lowest-bound check rewrites uv.lock, so run it in a scratch copy:
cp -r . /tmp/lowcheck && cd /tmp/lowcheck && uv sync --resolution lowest-direct && uv run pytest   # dev deps need lower bounds
```

**Lint, tests, CI**

```
uv run ruff check . && uv run ruff format --check .
uv run --with pytest-console-scripts pytest --script-launch-mode=subprocess
uv run --with cogapp cog --check README.md   # uv run, so cog's code can call the installed tool             help text in README is current
uvx zizmor .github/workflows/                      
actionlint
```

**CLI contract (bash; run against a safe target)**

```
for s in sub1 sub2 sub3; do tool "$s" --help >/dev/null || echo "FAIL help $s"; done
tool --definitely-bogus >o 2>e; rc=$?; [ "$rc" -eq 2 ] && [ ! -s o ] && [ -s e ] && echo PASS || echo "FAIL usage rc=$rc"
timeout 10 tool list </dev/null >/dev/null; rc=$?; [ "$rc" -ne 124 ] && echo PASS || echo "FAIL hangs without TTY"
tool list --json | python -c "import json,sys;json.load(sys.stdin)" && echo PASS
tool list | grep -q $'\x1b\[' && echo "FAIL ansi in pipe" || echo PASS
NO_COLOR=1 script -qc "tool list" /dev/null | grep -q $'\x1b\[' && echo "FAIL NO_COLOR" || echo PASS   # util-linux script
timeout 10 tool list | cat >/dev/null; [ "${PIPESTATUS[0]}" -ne 124 ] && echo PASS || echo "FAIL pager/hang"
(tool list 2>e) | head -1 >/dev/null; grep -q Traceback e && echo "FAIL brokenpipe" || echo PASS     # needs >64 KB of output
timeout --preserve-status -s INT 2 tool longcmd 2>e; echo "rc=$? (want 130)"; grep -q Traceback e && echo "FAIL traceback on Ctrl-C"
tool cmd /nonexistent 2>&1 | grep -q Traceback && echo "FAIL traceback" || echo PASS
```

**Startup time**

```
python -X importtime -c "import pkg.cli" 2>&1 | sort -t'|' -k2 -n | tail -5
hyperfine 'tool --help'
```

**Code smells (ripgrep)**

```
rg -n 'sys\.path\.(insert|append)' src/
rg -n 'subprocess.*sys\.executable' src/
rg -n 'input\(|getpass|confirm\(|prompt\(' src/
rg -n 'basicConfig\(.*stdout|StreamHandler\(sys\.stdout' src/
rg -n 'show_locals' src/
rg -n '__file__|os\.getcwd\(\)|Path\.cwd\(\)' src/
rg -n 'sys\.exit|raise SystemExit' src/
rg -n 'CLAUDECODE|AGENT|CODEX' src/
```

## Anti-patterns to look for in AI-written or migrated CLIs

1. **A generic top-level package** (`tools/`, `utils/`, `scripts/`, `cli/`). Installed packages with the same name overwrite each other. W005 does not catch `tools` [S40].
2. **requirements.txt deleted without a replacement install path** for pip users [S12].
3. **An arbitrary `requires-python`**, copied from the dev machine and not tested in CI, or capped with `<4` [S22].
4. **Locking a release that is a few days old** of a security-sensitive dependency with no cooldown and no note [S9, S49].
5. **Errors printed to stdout**, for example `console.print("[red]Error...")` with a default Rich Console, which breaks `--json` and pipes. One of the skills reviewed shows exactly this pattern [S29, S16].
6. **Rich, colors, or spinners used unconditionally**, so ANSI escapes reach pipes and agent context and waste tokens [S30, S16].
7. **`sys.exit()` scattered through library functions**, or `main` returning a string, which makes Python print it and exit 1 [S4].
8. **Calling sibling scripts through `subprocess.run([sys.executable, "other.py"])`** instead of importing them [S4].
9. **`sys.path.insert(0, ...)` hacks** left over from the script era [S2].
10. **`input()` or `confirm()` with no isatty guard and no bypass flag**, which hangs agents and CI [S16, S30].
11. **`except Exception: print(e)` that then exits 0** [S16].
12. **A `--json` mode that prints a log or banner line before the JSON**, or prints a Python `repr` instead of JSON [S30].
13. **The version hardcoded in two places** (`pyproject.toml` and `__version__`) that drift apart [S17].
14. **Dev tools in `[project.optional-dependencies]` or runtime `dependencies`**. Outdated skills still teach this [S26, S24].
15. **Only in-process CliRunner tests**, so the installed entry point and packaged data are never exercised [S21, S44, S45].
16. **Lazy `module:function` dispatch maps that no test resolves**, where a typo only shows at runtime.
17. **Data files located relative to the working directory or `__file__`**, which work from the repo and break after install [S21].
18. **`logging.basicConfig(stream=sys.stdout)`** or debug prints left in [S16].
19. **Boxed tables as the only output format** [S17].
20. **A `--dry-run` that still writes**, for example a cache, a lockfile, or a log in the working directory.
21. **Assuming `uv.lock` protects end users** of `uv tool install` or pipx [S14].
22. **Typer older than 0.23 with pretty tracebacks**, which print locals including tokens [S46].
23. **Accepting `--password VALUE` or `--token VALUE` flags** [S16].
24. **Copying the "50 ms startup" or "always auto-JSON when piped" rules** from generic skills without checking them [S31, S30].
