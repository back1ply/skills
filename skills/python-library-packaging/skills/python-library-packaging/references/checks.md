# Command blocks

Copy-paste commands for audit steps 2 and 3. Set `PKG` to the shipped package directory and `NAME` to its import name first. All blocks were run on Windows (Git Bash) against the example library in patterns.md with uv 0.13.9, ruff 0.17, and pyright 1.1.414, unless marked "not run".

```
PKG=src/mylib        # flat layout: PKG=mylib
NAME=mylib
```

**Metadata and build** (META-01, META-03, REL-01, REL-02, TYP-01)

```
uvx 'validate-pyproject[all]' pyproject.toml
uv build                                              # use --no-sources if [tool.uv.sources] exists (DEP-11)
uvx twine check --strict dist/*
uvx check-wheel-contents dist/*.whl
python -c "import zipfile,glob; print([n for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist() if 'py.typed' in n or 'licenses' in n or '/tests/' in n])"
grep -nE 'requires-python.*<' pyproject.toml          # must find nothing (DEP-03)
rg -n '"[^"]*(<[^=]|~=)' pyproject.toml               # each cap needs a comment (DEP-02); the uv_build cap in [build-system] is expected
```

An old uv can fail to build a wheel from a newer `uv_build` sdist (`malformed pax extension`). Update uv, or run the current one with `uvx uv@latest build`.

**Public API** (API-01 to API-06)

```
rg --files-without-match '^__all__' $PKG -g '*.py' -g '!_*.py'     # public modules missing __all__
ruff check --select F401 $PKG/__init__.py                         # plain re-exports
fd -e py --exclude '_*' . $PKG                                    # modules that count as public
```

**Library behaviour and typing source checks** (BEH, PY-07, DOC-01)

```
ruff check --select LOG015,T20,E722,BLE001,S110,D1 $PKG
ruff check --preview --select PLW1514 $PKG                        # preview rule: needs --preview
rg -n 'basicConfig|logging\.config|StreamHandler|FileHandler|addHandler' $PKG
rg -n '\b(sys\.exit|os\._exit|exit\(|quit\()' $PKG
rg -n 'sys\.(stdout|stderr)\.write' $PKG
rg -n '__file__' $PKG
rg -n 'warnings\.warn\(' $PKG                                     # each needs stacklevel= (DEPR-02)
rg -n 'os\.chdir|os\.environ\[.*\]\s*=|setlocale|setrecursionlimit|warnings\.simplefilter' $PKG
uvx deptry $PKG                                                   # undeclared imports (DEP-10)
```

**Fresh install from the wheel** (TST-03, DEP-07)

Run from a directory outside the repo. `REPO` is the repo path in `F:/...` form on Windows.

```
uv venv wheel-env
VIRTUAL_ENV=wheel-env uv pip install "$REPO"/dist/*.whl
wheel-env/Scripts/python -c "import $NAME; print($NAME.__all__)"   # Linux/macOS: wheel-env/bin/python
```

Import every public subpackage and call one function that reads bundled data. Without the extras installed, `import $NAME` must still succeed.

**Type completeness** (TYP-03, TYP-05)

In the same wheel environment:

```
VIRTUAL_ENV=wheel-env uv pip install pyright
PATH="$PWD/wheel-env/Scripts:$PATH" VIRTUAL_ENV=wheel-env pyright --verifytypes $NAME --ignoreexternal --outputjson | jq '.typeCompleteness | {score: .completenessScore, counts: .exportedSymbolCounts}'
```

`score` is a fraction (1 = complete). Add `--verbose` without `--outputjson` to list each symbol with an unknown type.

**Dependency bounds** (DEP-04, DEP-05)

Neither command changes `uv.lock` (checked by hashing it before and after).

```
uv run --isolated --resolution lowest-direct --python <floor> pytest
uv run --isolated --resolution highest --python <newest> pytest
```

**Import cost and side effects** (BEH-09, BEH-10)

```
python -X importtime -c "import $NAME" 2>&1 | sort -t'|' -k2 -n | tail
```

Run it once with the network disabled: an import that hangs or fails is doing I/O at import time.

**API breaks and repo checks** (API-08, META-06), not run

```
uvx griffe check $NAME --search src -a <last-tag>
uvx 'sp-repo-review[cli]' .
```
