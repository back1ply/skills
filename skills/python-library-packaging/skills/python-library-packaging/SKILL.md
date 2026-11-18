---
name: python-library-packaging
description: Builds, converts, and audits importable Python libraries that other code depends on - public API, type completeness, dependency bounds tested at both ends, Python version policy, deprecations, and library-safe logging and errors. Use when packaging reusable code as a library, extracting a library from scripts or an app, reviewing a library repo before release, adding py.typed, or setting dependency ranges for a package others install. For command-line tools use python-cli-packaging instead.
---

# Python library packaging

A library runs inside someone else's process and environment. Everything it does leaks: its dependency ranges constrain their resolver, its logging and warnings land in their output, its exceptions cross into their code, and every public name becomes a promise. The checklist has 83 items with stable IDs (`API-03`, `DEP-04`) in [references/checklist.md](references/checklist.md). Cite those IDs in every finding.

Pick the mode from the request:

| Mode | When | Ends with |
|---|---|---|
| **Audit** | Review or assess an existing library | Findings covering every MUST and SHOULD item |
| **Convert** | Extract an importable library from scripts or an app | Repo passes all MUSTs and the fresh-install import test |
| **Build** | New library from scratch | Same as convert, without the migration items |

Command-line tools follow the sister skill `python-cli-packaging`. Cutting releases (version bumps, tags, the publish workflow, yanking) follows `python-release-automation`. A project that is both (a library with a CLI) follows this skill for the importable package and the CLI skill for the command.

## Safety

Run the library's code only after reading what import does: a module with import-time side effects (BEH-09) can touch the network or files on `import`. Clone third-party repos into a fresh empty directory. Lowest-version test runs rewrite nothing when done with `uv run --isolated`, but check `git status` afterwards.

## Audit

1. **Inventory.** Read `pyproject.toml`, `__init__.py` of the top-level package, the module tree, tests, CI workflows, and README. Write down the declared public API (`__all__`) and the Python floor.
2. **Static checks.** Run the blocks in [references/checks.md](references/checks.md): metadata, public API, ruff library rules, logging and side-effect greps. Point every grep at the shipped package directory (`<pkg>`), not a guess at `src/`.
3. **Build and install.** `uv build`, then install the wheel into a clean environment outside the repo and import every public subpackage (TST-03). Measure type completeness from that install (TYP-03). Run the tests at the lowest allowed dependency versions on the floor Python (DEP-04).
4. **Report.** Spend the words on what's broken:
   - **Fails**, MUST first, then SHOULD: `ID | evidence | fix`. Evidence is a command plus its result, or `file:line`.
   - **Not checked**: `ID | reason | what would check it`.
   - **n/a**: grouped by cause, one line each ("not typed: TYP-02 to TYP-08").
   - **Passes**: one line each, `ID: evidence`. No table.

The audit is done when every MUST and SHOULD ID appears in exactly one of those four lists.

## Convert

1. **Find the library inside the code.** List the functions and classes other code should call. Everything else is private. Scripts mix three things that must be split: core logic (becomes the library), I/O and configuration (moves to the caller or a thin `_cli`/`__main__`), and process control (`sys.exit`, `print`, `input`, `argparse`), which never stays in library code (API-11, BEH-04, BEH-05).
2. **Record current behaviour.** Before rewriting, write a small script that calls the to-be-public functions on fixture inputs and saves the results. Step 8 reruns it against the library and diffs.
3. **Restructure.** `src/<pkg>/` with a project-specific name. Implementation modules start with `_` (API-05). `pyproject.toml` from [references/patterns.md](references/patterns.md): lower bounds only, no caps (DEP-01, DEP-02), dev tools in `[dependency-groups]` (DEP-08), a Python floor from the written policy (PY-01, PY-02).
4. **Declare the public API.** `__init__.py` re-exports with redundant aliases (`from ._core import parse as parse`) plus a literal `__all__` (API-01 to API-04). Options become keyword-only (API-09).
5. **Make it safe to import.** No import-time side effects (BEH-09). Logging through `getLogger(__name__)`, never configured (BEH-01, BEH-02). One base exception class, exported (BEH-06, BEH-07). Data through `importlib.resources` (BEH-11). Optional dependencies imported lazily behind extras (DEP-07).
6. **Type it, then mark it.** Annotate the public interface, check strict (TYP-04), and add `py.typed` only when `pyright --verifytypes` reports full completeness from the built wheel (TYP-01 to TYP-03).
7. **Tests and CI.** Tests import the installed package (TST-01). CI: floor and newest Python (PY-03), a lowest-direct job (DEP-04), a scheduled newest-versions job (DEP-05), the wheel import smoke test (TST-03), and the type-completeness check (TYP-03). Warnings are errors in tests (DEPR-06).
8. **Verify** with audit steps 2–3, then rerun the step 2 recording script against the library and diff.

Convert is done when every MUST passes, the wheel imports cleanly from outside the repo, the lowest-direct job passes, and the recorded behaviour matches or every difference is in the changelog.

## Build

Follow convert steps 3–8, skipping the recording script.

## The MUST items

Full wording, verification, and sources are in the checklist.

**Public API**
- API-01: every public module has a literal `__all__`; `__init__.py` re-exports exactly the supported names.
- API-02: every name in `__all__` exists.
- API-03: re-exports use `from ._x import Y as Y` or `__all__`; a plain import is private to type checkers.
- API-04: `__all__` is a static literal, never built dynamically.

**Typing** (if the library claims to be typed)
- TYP-01: `py.typed` sits in the top-level package and ships in the wheel.
- TYP-02: `py.typed` ships only once the public interface is annotated.

**Dependencies**
- DEP-01: every runtime dependency has a tested lower bound; no `==` pins.
- DEP-02: no upper caps unless a comment names a known incompatibility.
- DEP-03: `requires-python` has a floor and no cap.
- DEP-04: CI runs the tests at the lowest direct versions on the floor Python.
- DEP-08: dev tools live in `[dependency-groups]`, not extras or runtime deps.
- DEP-10: every third-party import is declared (`uvx deptry`).
- DEP-11: releases build with `uv build --no-sources` when `[tool.uv.sources]` exists.

**Python versions**
- PY-03: CI tests the floor and the newest stable Python.

**Deprecation**
- DEPR-02: a manual `warnings.warn(..., DeprecationWarning)` passes `stacklevel=2` (or `skip_file_prefixes`).

**Behaviour**
- BEH-01: modules log through `getLogger(__name__)`, never the root logger functions.
- BEH-02: the library never configures logging.
- BEH-04: no `print()` or direct `sys.stdout`/`sys.stderr` writes.
- BEH-09: importing the package has no side effects.
- BEH-11: package data loads through `importlib.resources`, never `__file__` paths.

**Metadata, tests, release**
- META-01: `[build-system]`, SPDX `license`, license file in the wheel, `readme`.
- META-04: the import name is unique and project-specific.
- TST-03: the built wheel installs into a clean env and every public subpackage imports from outside the repo.
- REL-01: `uv build` output passes `twine check --strict`.

## Defaults for disputed choices

Reasoning and both sides are in [references/disputes.md](references/disputes.md).

- **Upper caps:** none by default. A cap needs a comment naming the incompatibility. Users can add a cap you left out; they can't remove one you added.
- **Python floor:** every non-EOL CPython for general libraries; SPEC 0 for libraries in the scientific stack. Write the policy down either way.
- **Lockfile:** committing `uv.lock` is fine for reproducible CI, but it never reaches users, so the lowest and newest jobs are still required.
- **NullHandler:** don't add it by default. The logging docs call WARNING+ reaching stderr in an unconfigured app the best default. Never add any other handler.
- **Deprecation category:** `DeprecationWarning` for API removals; `FutureWarning` only for default-behaviour changes that change results for end users.
- **Versioning:** SemVer unless a written CalVer deprecation window exists.
- **`py.typed`:** top-level package only (the marker applies recursively).
- **Docs stack:** Sphinx + MyST for new libraries; existing mkdocstrings sites can stay.
- **Build backend:** `uv_build` for pure Python, capped at the next minor (it also writes PEP 794 `import-names`); hatchling when you need versions from git tags. Compiled code: see the pointer section at the end of the checklist.

## References

- [references/checklist.md](references/checklist.md): all 83 items with severity, modes, verification, and sources.
- [references/checks.md](references/checks.md): copy-paste command blocks for audit step 2 and 3.
- [references/patterns.md](references/patterns.md): `pyproject.toml`, `__init__.py`, exceptions, logging, deprecation, resources, optional extras, tests, and CI for a library. Read it in convert steps 3–7 and build mode.
- [references/disputes.md](references/disputes.md): debated choices with both sides.
- [references/sources.md](references/sources.md): the 52 sources behind the checklist.
