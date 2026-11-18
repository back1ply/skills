# Python library checklist

83 items with stable IDs. Sources: [sources.md](sources.md). Commands in tables escape `|` as `\|`; copy runnable commands from [checks.md](checks.md) instead.

Modes: **B** build, **C** convert, **A** audit. `<pkg>` is the import package directory as shipped (`src/mylib`), `pkg` its import name, `dist` the distribution name. Items marked "CLI X" are shared with the `python-cli-packaging` skill and verified the same way.

## Contents

- API: Public API (API-01 to API-11)
- TYP: Typing (TYP-01 to TYP-09)
- DEP: Dependencies (DEP-01 to DEP-11)
- PY: Python versions (PY-01 to PY-07)
- DEPR: Deprecation and compatibility (DEPR-01 to DEPR-08)
- BEH: Library behaviour (BEH-01 to BEH-12)
- META: Metadata (META-01 to META-07)
- DOC: Documentation (DOC-01 to DOC-06)
- TST: Testing (TST-01 to TST-05)
- REL: Release (REL-01 to REL-07)
- Compiled extensions (pointer only)

### Public API (API)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| API-01 | Every public module declares its public API with a literal `__all__`, and the top-level `__init__.py` re-exports exactly the supported names. SemVer only means something once the public API is declared. | MUST | B C A | `rg --files-without-match '^__all__' <pkg> -g '*.py' -g '!_*.py'` lists public modules without `__all__`; read `__init__.py` | S2, S6, S7, S25 |
| API-02 | Every name in `__all__` exists. A stale entry breaks `from pkg import *` and type checkers. | MUST | B C A | `python -c "import pkg; print([n for n in pkg.__all__ if not hasattr(pkg, n)])"` prints `[]` | S2, S7 |
| API-03 | Re-exports in `__init__.py` use the redundant alias `from ._core import X as X` (plus `__all__`). A plain `from ._core import X` is private to type checkers, and ruff F401 may delete it. | MUST | B C A | `ruff check --select F401 <pkg>/__init__.py` reports nothing | S2, S3, S8 |
| API-04 | `__all__` uses a statically readable form (`= [...]`, `+= [...]`, `.append`, `.extend`). It is never built in a loop or comprehension. | MUST | B C A | `rg -n -A2 '__all__\s*[+]?=' <pkg>`: each right-hand side is a literal list or tuple | S2, S7 |
| API-05 | Implementation modules and subpackages start with an underscore (`_core.py`, `_impl/`). In a `py.typed` package every non-underscore module counts as public API. | SHOULD | B C A | `fd -e py --exclude '_*' . <pkg>` lists the public modules; each is meant to be public | S2, S3, S4 |
| API-06 | Only names in `__all__` (and submodules) are public. Imported helpers don't leak as accidental exports. | SHOULD | B C A | `python -c "import pkg; print(sorted({n for n in dir(pkg) if not n.startswith('_')} - set(pkg.__all__)))"`: every extra name is a submodule | S6, S7 |
| API-07 | Tests are not shipped inside the package (`pkg/tests/`). They bloat the wheel and count as public API in type-completeness checks. | SHOULD | B C A | `python -c "import zipfile,glob; print([n for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist() if '/tests/' in n])"` prints `[]` | S46, S38, S41 |
| API-08 | CI detects breaking API changes against the last release tag, and a break forces a major bump or a documented exception. A snapshot test of `pkg.__all__` is the minimal alternative. | SHOULD | B A | `uvx griffe check pkg --search src -a <last-tag>` in CI with `fetch-depth: 0` | S9, S25 |
| API-09 | Options are keyword-only (`def f(data, *, strict=False)`), so parameters can be added without breaking callers. Inputs take the widest type that works (`Iterable`, `Mapping`), outputs return concrete types. | SHOULD | B C A | Read public signatures for long positional parameter lists | S1 |
| API-10 | `pkg.__version__`, if offered, comes from `importlib.metadata.version("dist")`, not a second hard-coded string. Compute it lazily in a module `__getattr__`, since importing `importlib.metadata` adds tens of milliseconds to every `import pkg` (BEH-10). | SHOULD | B C A | `python -c "import pkg, importlib.metadata as m; print(pkg.__version__ == m.version('dist'))"` | CLI PKG-06 |
| API-11 | Convert mode: the importable layer holds no application code. No `argparse`, `input()`, `sys.argv`, or config-file loading; core functions take data or file-like objects and return values. A CLI, if any, lives in `_cli.py` or `__main__.py`. | SHOULD | C A | `rg -n 'argparse\|input\(\|sys\.argv' <pkg>` finds nothing outside `_cli.py`/`__main__.py` | S52, CLI LAY-03 |

### Typing (TYP)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| TYP-01 | A library that claims to be typed ships an empty `py.typed` in the top-level import package, and the file is in the wheel. Without it, type checkers ignore the inline annotations. | MUST (if typed) | B C A | `python -c "import zipfile,glob; print([n for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist() if n.endswith('py.typed')])"` lists it | S1, S5 |
| TYP-02 | `py.typed` ships only once the public interface is annotated. The marker is a promise: on an unannotated package users get `Unknown` everywhere and errors in their own code. | MUST (if typed) | B C | TYP-03 reports full completeness before the marker is added | S1 |
| TYP-03 | Type completeness is measured from the installed wheel in a clean environment, with `--ignoreexternal` so untyped dependencies don't count, and CI enforces a threshold: 100% for a new library, no regression for a converted one. The JSON score is a 0–1 fraction. | SHOULD | B A | See checks.md "Type completeness": `pyright --verifytypes pkg --ignoreexternal --outputjson` from the wheel install, read `typeCompleteness.completenessScore` | S3, S4, S46 |
| TYP-04 | Source is type-checked in strict mode (`[tool.mypy] strict = true`, or pyright `typeCheckingMode = "strict"`). | SHOULD | B C A | `grep -nE 'strict\|typeCheckingMode' pyproject.toml`, then run the checker on `<pkg>` | S39, S37 |
| TYP-05 | Public signatures don't leak `Any` or unknown types: no unannotated parameters or returns, decorators keep signatures (`ParamSpec`), generic bases have type arguments. | SHOULD | B C A | `pyright --verifytypes pkg --ignoreexternal --verbose` lists each symbol with unknown types | S1, S4 |
| TYP-06 | APIs whose return type depends on arguments use `@overload` or `Literal`. Structured results are dataclasses, `NamedTuple`, or `TypedDict`, not untyped dicts. | SHOULD | B C | `rg -n -- '-> (dict\|Dict\|Any)\b' <pkg>`, then review | S1 |
| TYP-07 | Type behaviour is tested for generic or overloaded APIs: `assert_type(...)` files run through the type checker in CI, or `--warn-unused-ignores` proves expected errors still occur. | NICE (SHOULD for generic APIs) | B A | `mypy typing_tests/` or pyright on that folder in CI | S4 |
| TYP-08 | Newer typing features on older floors come from `typing_extensions`, declared with a marker (`"typing_extensions>=4.6; python_version<'3.13'"`) and imported behind `if sys.version_info < (3, 13):`. | SHOULD | B C A | `rg -n 'typing_extensions' <pkg> pyproject.toml`: each import is version-guarded and matches the marker | S13, S1 |
| TYP-09 | Pure-Python code uses inline annotations, not `.pyi` stubs. Stubs are for extension modules; a separate stub distribution is named `<dist>-stubs`. | NICE | B C | `fd -e pyi . <pkg>` is empty for a pure-Python package | S1, S5, S35 |

### Dependencies (DEP)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DEP-01 | Every runtime dependency has a tested lower bound (`>=X.Y`) and no `==` pin. A library shares the user's environment, so a pin makes their resolve unsolvable. | MUST | B C A | `python -c "import tomllib;d=tomllib.load(open('pyproject.toml','rb'))['project'];print([x for x in d.get('dependencies',[]) if '==' in x or '>' not in x])"` prints `[]` | S10, S11, S12 |
| DEP-02 | No upper caps (`<2`, `~=`) by default. Each remaining cap has a comment naming the known incompatibility or accepted reason (framework plugin, packages released in lockstep). Exclude one bad release with `!=X.Y.Z`. | MUST | B C A | `rg -n '"[^"]*(<[^=]\|~=)' pyproject.toml`: each hit has a comment | S10, S26, S12 |
| DEP-03 | `requires-python` has a floor and no upper cap. | MUST | B C A | `grep -nE 'requires-python.*<' pyproject.toml` finds nothing | S10, S50, S37 |
| DEP-04 | CI runs the test suite at the lowest direct versions allowed by `pyproject.toml`, on the floor Python. A lower bound nobody tests is a guess. | MUST | B A | `uv run --isolated --resolution lowest-direct --python <floor> pytest` (leaves `uv.lock` untouched) | S11, S12 |
| DEP-05 | CI also tests the newest allowed versions on a schedule, resolving fresh instead of from the lock, so upstream releases break CI before they break users. | SHOULD | B A | A scheduled workflow (`on: schedule`) running `uv run --isolated --resolution highest --python <newest> pytest` | S12, S10 |
| DEP-06 | The repo accepts that `uv.lock` (or `pylock.toml`) only pins dev and CI and never reaches users. Committing it is fine; DEP-04 and DEP-05 are still required. | SHOULD | B C A | If `git ls-files uv.lock` lists it, the DEP-04 and DEP-05 jobs exist | S12, S10 |
| DEP-07 | Optional features live in `[project.optional-dependencies]` extras. Their imports happen inside the feature, and a missing extra raises `ImportError` naming the install command (`pip install "dist[plot]"`). `import pkg` works without any extra. | SHOULD | B C A | In a clean env without extras: `python -c "import pkg"` succeeds, and calling the feature names the extra | S12 |
| DEP-08 | Dev tools (pytest, ruff, type checker, docs) are in `[dependency-groups]` (PEP 735), not extras or runtime deps. | MUST | B C A | `uv tree --no-dev --depth 1` shows no dev tools | S12, S37 |
| DEP-09 | Runtime dependencies are minimal. Backports are conditional on `python_version` markers and are dropped when the floor rises. | SHOULD | B C A | `uv tree --no-dev --depth 1`; `rg -n python_version pyproject.toml` | S12, S13 |
| DEP-10 | Every third-party module the library imports is declared in `[project] dependencies` (or an extra, for optional features). | MUST | B C A | `uvx deptry <pkg>` reports no DEP001, DEP003, or DEP004 | CLI DEP-08 |
| DEP-11 | Release artifacts are built with `uv build --no-sources`, so `[tool.uv.sources]` overrides (local paths, git) can't hide a dependency that won't resolve from PyPI. | MUST (if `[tool.uv.sources]` exists) | B A | `grep -n 'tool.uv.sources' pyproject.toml`; the release job uses `--no-sources` | S36 |

### Python versions (PY)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| PY-01 | The `requires-python` floor follows a written policy (every non-EOL CPython, SPEC 0, or a stated window) in README or CONTRIBUTING, and is raised on schedule. | SHOULD | B C A | `rg -n -i 'SPEC 0\|supported python\|python version' README* CONTRIBUTING* docs/` | S14, S15 |
| PY-02 | The floor excludes end-of-life Pythons. Check https://devguide.python.org/versions/ (as of 2026-11: 3.10 is EOL, so at least 3.11; a SPEC 0 floor is 3.13). | SHOULD | B C A | Compare `grep requires-python pyproject.toml` with the devguide table | S15, S14 |
| PY-03 | The CI matrix tests the floor and the newest stable Python. Prereleases are optional (`allow-prereleases: true`). | MUST | B C A | Compare `requires-python` with the workflow `python-version` list | S51, S15 |
| PY-04 | Version-specific code uses `if sys.version_info >= (3, X):`, not `try/except ImportError`, so type checkers understand it and `ruff --select UP` removes dead branches when the floor rises. | SHOULD | B C A | `rg -n -A3 'except ImportError' <pkg>`: none switches between stdlib and a backport | S13 |
| PY-05 | Free-threaded support is a decision: either CI runs the suite on `3.14t` with `PYTHON_GIL=0` and a job `timeout-minutes`, or the docs say free-threading is untested. A `Free Threading :: N` classifier is claimed only after that, at the level that matches (1 Unstable, 2 Beta, 3 Stable, 4 Resilient). | SHOULD (MUST before claiming support) | B A | `rg -n '3\.1[45]t\|PYTHON_GIL' .github/workflows/`; `grep -n 'Free Threading' pyproject.toml` | S16, S17, S18, S21 |
| PY-06 | Mutable module-level state (caches, registries, counters) is guarded by a lock, a `ContextVar`, or `threading.local`, or replaced by copy-on-write, and thread-safety guarantees are documented. Pure Python is not race-free on free-threaded builds. | SHOULD | B C A | `rg -n '^_?[a-z_]+\s*(:.*)?=\s*(\{\|\[\|dict\(\|list\(\|set\()' <pkg>` lists globals to review | S17, S19 |
| PY-07 | Every text file operation passes `encoding=` (usually `"utf-8"`). Python 3.15 made UTF-8 mode the default, so locale-dependent code now behaves differently on 3.14 and 3.15 on Windows. | SHOULD | B C A | `ruff check --preview --select PLW1514 <pkg>` (a preview rule: without `--preview` the selection does nothing); `python -X warn_default_encoding -W error::EncodingWarning -m pytest` | S32 |

### Deprecation and compatibility (DEPR)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DEPR-01 | Deprecated public callables and classes use `@warnings.deprecated("...")` (3.13+) or `@typing_extensions.deprecated` on older floors, so users get both a runtime warning and a type-checker diagnostic. Its default `stacklevel=1` already points at the caller. | SHOULD | B A | `rg -n '@(warnings\.\|typing_extensions\.)?deprecated' <pkg>`, compared with the changelog's Deprecated entries | S22, S23, local test (Python 3.14) |
| DEPR-02 | A manual `warnings.warn(..., DeprecationWarning)` inside a function passes `stacklevel=2` (deeper if wrapped) or `skip_file_prefixes=(os.path.dirname(__file__),)`. Without it the warning points at the library's own line. | MUST | B A | `rg -n 'warnings\.warn\(' <pkg>`: each has `stacklevel=` or `skip_file_prefixes=`. Test: `w[0].filename` is the test file. | S23, local test (Python 3.14) |
| DEPR-03 | The category matches the audience: `DeprecationWarning` for API removals (developers), `FutureWarning` for default-behaviour changes end users must see. `DeprecationWarning` is hidden by default outside `__main__`. | SHOULD | B A | `rg -n 'FutureWarning\|PendingDeprecationWarning\|DeprecationWarning' <pkg>` | S23 |
| DEPR-04 | Every deprecation message names the replacement and the version or date of removal ("use parse_v2(); removed in 3.0"). | SHOULD | B A | Read each warning string | S24 |
| DEPR-05 | The removal policy is written down: deprecated in a minor release, kept at least one more minor (or N months), removed only in a major release or after the stated window. Renamed public names keep a warning shim (module `__getattr__`) for that window. | SHOULD | B A | `rg -n -i deprecat README* CONTRIBUTING* docs/`; `rg -n 'def __getattr__' <pkg>` when the changelog lists renames | S25, S24, S26 |
| DEPR-06 | The test suite turns warnings into errors (`filterwarnings = ["error"]`), with commented ignores for known upstream warnings. | SHOULD | B C A | `grep -n -A3 filterwarnings pyproject.toml` | S38, S37, S23 |
| DEPR-07 | Every deprecation has a test asserting the warning, its category, and its message. | SHOULD | B A | `rg -n 'pytest.warns\|deprecated_call' tests/` | S23 |
| DEPR-08 | The versioning scheme (SemVer, or CalVer with a compatibility window) is stated in README and changelog. Under SemVer a deprecation bumps the minor version. | SHOULD | B A | `rg -n -i 'semver\|semantic version\|calver' README* CHANGELOG*` | S25, S26, S27 |

### Library behaviour (BEH)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| BEH-01 | Each module logs through `logger = logging.getLogger(__name__)`, never the root-logger functions (`logging.info(...)`), which also call `basicConfig()` implicitly. | MUST | B C A | `ruff check --select LOG015 <pkg>` reports nothing | S28, S39 |
| BEH-02 | The library never configures logging: no `basicConfig()`, no `logging.config`, no handlers other than an optional `NullHandler`, no `setLevel` on loggers it doesn't own. NullHandler is optional: without it, WARNING+ reaches stderr in unconfigured apps, which the logging docs call the best default. | MUST | B C A | `rg -n 'basicConfig\|logging\.config\|StreamHandler\|FileHandler\|addHandler' <pkg>`: only `addHandler(logging.NullHandler())` may appear | S28 |
| BEH-03 | Logger names and what each level means are documented. | SHOULD | B A | `rg -n -i 'logger\|logging' docs/ README*` | S28 |
| BEH-04 | No `print()` and no direct writes to `sys.stdout` or `sys.stderr` in library code. Results go out as return values, diagnostics through logging or warnings. | MUST | B C A | `ruff check --select T20 <pkg>`; `rg -n 'sys\.(stdout\|stderr)\.write' <pkg>` | S39, S28 |
| BEH-05 | No `sys.exit()`, `exit()`, `quit()`, or `os._exit()` in library code. The library raises; the application decides whether to exit. | SHOULD | B C A | `rg -n '\b(sys\.exit\|os\._exit\|exit\(\|quit\()' <pkg>` finds nothing outside `__main__.py`/`_cli.py` | Practice (no primary source) |
| BEH-06 | Errors derive from one library base exception (`class MylibError(Exception)`), with subclasses designed around what callers catch. A subclass may also inherit a built-in (`class InvalidInput(MylibError, ValueError)`). Never derive from `BaseException`. | SHOULD | B C A | `rg -n 'class \w+\(.*Exception' <pkg>`: one base, no `BaseException` | S6 |
| BEH-07 | The exception classes are public API: exported in `__all__` and documented, so callers can catch them. | SHOULD | B A | `python -c "import pkg; print([n for n in pkg.__all__ if isinstance(getattr(pkg,n),type) and issubclass(getattr(pkg,n),Exception)])"` lists them | S6, S25 |
| BEH-08 | No bare `except:` and no swallowed `except Exception: pass`. Errors reach the caller with a message saying what failed and with what input. | SHOULD | B C A | `ruff check --select E722,BLE001,S110 <pkg>` reports nothing | S39, S52 |
| BEH-09 | Importing the package has no side effects: no network or file I/O, no environment reads that change behaviour, no warnings filters, no logging config, no `sys.path` changes, no signal handlers, no plugin registration. | MUST | B C A | Read every module's top level; `python -X importtime -c "import pkg"` with the network off | S31, S7, S28 |
| BEH-10 | Import time is measured and kept low. Heavy or optional dependencies are imported inside the functions that need them (or listed in `__lazy_modules__`, honoured on 3.15+ and ignored before), and `__init__.py` doesn't eagerly import every submodule. Libraries never enable the global lazy-import mode. | SHOULD | B C A | `python -X importtime -c "import pkg" 2>&1 \| sort -t'\|' -k2 -n \| tail` | S30, S7, S31 |
| BEH-11 | Package data is read with `importlib.resources.files("pkg").joinpath(...).read_text(encoding="utf-8")` (or `as_file()` when a real path is needed), never with paths built from `__file__`. | MUST | B C A | `rg -n '__file__' <pkg>`: each hit reviewed | S29, CLI PKG-11 |
| BEH-12 | Library calls don't change process-global state (warnings filters, logging levels, `os.environ`, cwd, locale, recursion limit). An unavoidable temporary change goes through a context manager that restores it. | SHOULD | B C A | `rg -n 'os\.chdir\|os\.environ\[.*\]\s*=\|setlocale\|setrecursionlimit\|warnings\.simplefilter' <pkg>` | S52, S31 |

### Metadata (META)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| META-01 | `[build-system]` (with `uv_build` capped at the next minor), `[project]` with `name`, `version`, `description`, `readme`, `requires-python`, SPDX `license`, and the license file in the wheel. No `License ::` classifiers. | MUST | B C A | `uvx 'validate-pyproject[all]' pyproject.toml`; the wheel has `.dist-info/licenses/` | CLI PKG-01, PKG-02 |
| META-02 | `[project.urls]` uses well-known labels (`Homepage`, `Source`, `Documentation`, `Issues`, `Changelog`) so PyPI shows them properly. | SHOULD | B C A | Read `[project.urls]`; labels normalise by lowercasing and dropping punctuation | S34 |
| META-03 | Classifiers are valid and true: `Development Status` matches reality, Python version classifiers match the CI matrix, `Typing :: Typed` when `py.typed` ships, a Free Threading level only per PY-05. | SHOULD | B A | `grep -n -A20 classifiers pyproject.toml`; `uv build` rejects invalid classifiers | S21, S37 |
| META-04 | The import name is unique and project-specific (never `utils`, `common`, `lib`). If dist and import names differ, the README says so in the install section, and `uv_build` gets `module-name`. | MUST | B C A | `uvx check-wheel-contents dist/*.whl` (W005); read the README | CLI PKG-09 |
| META-05 | Optional: declare `import-names = ["pkg"]` (PEP 794) so tools can map import name to distribution. Supported by uv_build 0.13 (tested: writes `Metadata-Version: 2.5` and `Import-Name`), hatchling (default since 1.32.0), and PyPI; setuptools doesn't support it yet. | NICE | B A | After the build: `unzip -p dist/*.whl '*/METADATA' \| grep -E '^(Metadata-Version\|Import-Name)'` | S33, local test (uv_build 0.13) |
| META-06 | Repo checks pass, or each failure is ignored with a reason: `sp-repo-review`, optionally `pyroma` as a second opinion. | NICE | B A | `uvx 'sp-repo-review[cli]' .` | S37, S48 |
| META-07 | Namespace packages (PEP 420) only when several distributions share one import prefix. Then no distribution ships `<ns>/__init__.py`, and `uv_build` uses a dotted `module-name`. Otherwise use a plain prefixed name. | SHOULD (if namespace) | B A | `unzip -l dist/*.whl \| grep '<ns>/__init__.py'` finds nothing | S43, S35 |

### Documentation (DOC)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| DOC-01 | Every public module, class, function, and method has a docstring. `_` modules are exempt. | SHOULD | B C A | `ruff check --select D1 <pkg>` | S1 |
| DOC-02 | One docstring convention (NumPy or Google) is chosen, enforced, and parsed by the docs renderer (Sphinx napoleon, or mkdocstrings `docstring_style`). | SHOULD | B A | `grep -n 'convention\|docstring_style\|napoleon' pyproject.toml docs/conf.py mkdocs.yml 2>/dev/null` | S40 |
| DOC-03 | The API reference is generated from docstrings and type hints (Sphinx autodoc or mkdocstrings) and covers exactly `__all__`. CI builds the docs. | SHOULD | B A | `rg -n 'autodoc\|mkdocstrings' docs/ mkdocs.yml` and a docs job in CI | S40 |
| DOC-04 | Docstring examples are doctests and CI runs them. | SHOULD | B A | `uv run pytest --doctest-modules <pkg>` | S42 |
| DOC-05 | The docs state the Python-version policy (PY-01), deprecation policy (DEPR-05), thread-safety guarantees (PY-06), and logger names (BEH-03). | SHOULD | B A | `rg -n -i 'thread\|deprecat\|logger\|supported python' docs/ README*` | S17, S28, S14 |
| DOC-06 | The README has the install line, a 5–10 line example that runs, and links to docs and changelog. | SHOULD | B C A | Run the README example in the TST-03 clean environment | S34, S27 |

### Testing (TST)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| TST-01 | Tests run against the installed package: src layout, `--import-mode=importlib`, no `__init__.py` in `tests/`. | SHOULD | B C A | `ls src/ tests/__init__.py`; `grep -n import-mode pyproject.toml` | S41, S38, S47 |
| TST-02 | pytest is strict: `strict = true` on pytest 9 (or `--strict-markers --strict-config` and `xfail_strict`), `filterwarnings = ["error"]`, `testpaths`. | SHOULD | B A | `uvx 'sp-repo-review[cli]' .` PP3xx results | S38, S37 |
| TST-03 | Fresh-install smoke test from the built wheel, outside the project: import the package and every public subpackage, and touch bundled data. An editable install doesn't count. | MUST | B C A | `uv build`, then from another directory: `uv run --no-project --with <repo>/dist/<wheel>.whl -- python -c "import pkg, pkg.sub; print(pkg.__all__)"` | S36, S47, CLI TST-03 |
| TST-04 | Libraries with shared state have multithreaded tests (`ThreadPoolExecutor` with a `threading.Barrier`) with a timeout. | NICE (SHOULD if PY-05 claims level 3+) | B A | `rg -n 'ThreadPoolExecutor\|Barrier' tests/` | S19 |
| TST-05 | Windows and macOS are in the matrix when the library touches paths, encodings, subprocesses, or the filesystem. | NICE | B A | `runs-on` in the workflow matrix | S51 |

### Release (REL)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| REL-01 | `uv build` (with `--no-sources` per DEP-11) produces an sdist and wheel whose metadata passes `twine check --strict`. Keep uv current: an old uv can fail to build a wheel from a newer `uv_build` sdist. | MUST | B C A | `uv build && uvx twine check --strict dist/*` | CLI PKG-07, S36 |
| REL-02 | Wheel contents are clean: one top-level package, no tests, no stray modules. | SHOULD | B C A | `uvx check-wheel-contents dist/*.whl` | CLI PKG-08 |
| REL-03 | Publishing uses PyPI Trusted Publishing from a separate publish job with PEP 740 attestations (`pypa/gh-action-pypi-publish`), and the first release goes to TestPyPI. | SHOULD (if publishing) | B A | Read the release workflow | CLI CI-03, S37 |
| REL-04 | A Keep a Changelog file: Unreleased section, dated versions, Deprecated and Removed sections filled whenever relevant, linked from `[project.urls] Changelog`. | SHOULD | B C A | `grep -n -E '^## \[?Unreleased' CHANGELOG*` | S27, S34 |
| REL-05 | The release flow is scripted (`uv version --bump <part>`, changelog entry, tag), and the API check (API-08) decides major vs minor. | NICE | B A | Release docs or workflow mention `uv version --bump` | S36, S9 |
| REL-06 | Workflow actions are pinned and kept current (Dependabot), with least-privilege `permissions:`. | SHOULD | B A | `uvx zizmor .github/workflows/` | CLI CI-02, S37 |
| REL-07 | A library others depend on in production has left 0.y.z (where SemVer says "anything MAY change"), and its stability statement matches the `Development Status` classifier. | NICE | A | `grep -n 'Development Status' pyproject.toml`; the current version | S25, S26, S21 |

### Compiled extensions (pointer only)

Not a checklist. If the library needs native code, everything above still applies, plus:
- **Backend:** maturin (Rust), scikit-build-core (CMake, CUDA), or meson-python. `uv_build` cannot build extensions [S35, S45].
- **Wheels:** cibuildwheel builds the platform matrix, including free-threaded wheels (`cp314t`) [S18, S45].
- **Stable ABI:** `Py_LIMITED_API` gives `abi3` wheels; Python 3.15 adds `abi3t` for free-threaded builds. Still test each supported minor version [S44].
- **Typing:** ship `.pyi` stubs next to the extension module and `py.typed` in the package [S1, S5].

Total: 83 items (API 11, TYP 9, DEP 11, PY 7, DEPR 8, BEH 12, META 7, DOC 6, TST 5, REL 7).
