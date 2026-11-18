# Code patterns

Reference shapes for a typed, pure-Python library with distribution and import name `mylib`. Rename both. Each block starts with its file path. Item IDs point to [checklist.md](checklist.md).

## Contents

- Layout
- pyproject.toml
- Public API: `__init__.py`
- Exceptions
- Core module: logging, data, deprecation, optional extra
- Tests
- CI workflow

## Layout

```
pyproject.toml
README.md
LICENSE
CHANGELOG.md
src/mylib/
    __init__.py        # public API: redundant-alias re-exports + __all__
    py.typed           # empty; only once the interface is annotated (TYP-02)
    _core.py           # implementation (underscore = private, API-05)
    _errors.py         # exception hierarchy
    data/defaults.json # bundled data, read with importlib.resources
tests/                 # no __init__.py (TST-01)
    test_core.py
```

## pyproject.toml

```toml
# pyproject.toml
[build-system]
requires = ["uv_build>=0.13,<0.14"]     # cap the backend at the next minor (META-01)
build-backend = "uv_build"

[project]
name = "mylib"
version = "0.1.0"
description = "Normalize Python package names"
readme = "README.md"
license = "MIT"
license-files = ["LICENSE"]
import-names = ["mylib"]                # PEP 794, optional (META-05)
requires-python = ">=3.11"              # policy: every non-EOL CPython (PY-01); no cap (DEP-03)
dependencies = [
    "packaging>=21",                    # lower bound tested by the lowest-direct job (DEP-04); no cap (DEP-02)
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.15",
    "Typing :: Typed",
]

[project.optional-dependencies]
toml = ["tomli-w>=1.0"]                 # optional feature, imported lazily (DEP-07)

[project.urls]
Homepage = "https://github.com/me/mylib"
Source = "https://github.com/me/mylib"
Issues = "https://github.com/me/mylib/issues"
Changelog = "https://github.com/me/mylib/blob/main/CHANGELOG.md"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6", "pyright>=1.1.400", "tomli-w>=1.0"]   # lower bounds, so lowest-direct works

[tool.pytest.ini_options]
addopts = ["-ra", "--import-mode=importlib", "--strict-markers", "--strict-config"]
xfail_strict = true
filterwarnings = ["error"]              # DEPR-06; with -X warn_default_encoding this also catches PY-07
testpaths = ["tests"]

[tool.ruff.lint]
extend-select = ["T20", "LOG", "E722", "BLE", "S110", "D1", "UP"]   # PLW1514 needs preview; tests catch it via EncodingWarning

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D1"]

[tool.pyright]
typeCheckingMode = "strict"             # TYP-04
```

`requires-python` floor, the CI matrix, and the version classifiers move together (PY-03, META-03).

## Public API: `__init__.py`

```python
# src/mylib/__init__.py
"""Normalize Python package names the way PyPI does."""

from ._core import canon as canon
from ._core import dump_toml as dump_toml
from ._core import load_defaults as load_defaults
from ._core import normalize as normalize
from ._core import normalize_names as normalize_names
from ._errors import InvalidNameError as InvalidNameError
from ._errors import MylibError as MylibError

__all__ = [
    "InvalidNameError",
    "MylibError",
    "canon",
    "dump_toml",
    "load_defaults",
    "normalize",
    "normalize_names",
]

def __getattr__(name: str) -> str:
    """Compute __version__ on first access; importlib.metadata is slow to import (BEH-10)."""
    if name == "__version__":
        from importlib.metadata import version

        return version("mylib")  # one source of truth (API-10)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

The redundant `X as X` form tells type checkers and ruff the import is a re-export (API-03). `__all__` is a literal list (API-04). Nothing here does I/O on import (BEH-09). `__version__` is computed on first access: importing `importlib.metadata` at the top cost about 50 ms of a 195 ms import in the tested example (Windows, Python 3.14).

## Exceptions

```python
# src/mylib/_errors.py
"""Exception hierarchy. Callers catch MylibError for anything this library raises."""


class MylibError(Exception):
    """Base class for every error mylib raises."""


class InvalidNameError(MylibError, ValueError):
    """A name contains characters a package name can't have."""
```

One base class (BEH-06), exported from `__init__.py` (BEH-07). Inheriting `ValueError` too keeps `except ValueError` callers working.

## Core module: logging, data, deprecation, optional extra

```python
# src/mylib/_core.py
"""Implementation. Public names are re-exported from mylib."""

import json
import logging
import re
import warnings
from collections.abc import Iterable, Mapping
from importlib.resources import files

from packaging.utils import canonicalize_name

from ._errors import InvalidNameError

logger = logging.getLogger(__name__)  # never logging.info(...) on the root logger (BEH-01)
_VALID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def normalize(name: str, *, strict: bool = True) -> str:
    """Return the canonical form of a package name.

    >>> normalize("My_Package")
    'my-package'
    """
    if strict and not _VALID.match(name):
        raise InvalidNameError(f"invalid package name {name!r}: use letters, digits, '.', '_' or '-'")
    result = str(canonicalize_name(name))
    logger.debug("normalized %r to %r", name, result)
    return result


def normalize_names(names: Iterable[str], *, strict: bool = True) -> list[str]:
    """Normalize several names, keeping their order."""
    return [normalize(n, strict=strict) for n in names]


def canon(name: str) -> str:
    """Deprecated alias for normalize()."""
    warnings.warn(
        "canon() is deprecated; use normalize(); removed in 1.0",  # replacement + removal (DEPR-04)
        DeprecationWarning,
        stacklevel=2,  # point at the caller's line, not this one (DEPR-02)
    )
    return normalize(name)


def load_defaults() -> dict[str, str]:
    """Return the bundled default settings."""
    text = files("mylib").joinpath("data/defaults.json").read_text(encoding="utf-8")  # BEH-11, PY-07
    data: dict[str, str] = json.loads(text)
    return data


def dump_toml(settings: Mapping[str, str]) -> str:
    """Render settings as TOML. Needs the ``toml`` extra."""
    try:
        import tomli_w  # imported here so `import mylib` works without the extra (DEP-07)
    except ImportError:
        raise ImportError('dump_toml() needs tomli-w: pip install "mylib[toml]"') from None
    return tomli_w.dumps(dict(settings))
```

On a 3.13+ floor, replace the manual warning with `@warnings.deprecated("...")` (or `@typing_extensions.deprecated` behind a version guard on older floors, TYP-08). Its default `stacklevel=1` already points at the caller, and type checkers flag every use (DEPR-01).

The library never calls `print`, `sys.exit`, or `logging.basicConfig` (BEH-02, BEH-04, BEH-05). The application decides where output goes and whether to exit.

## Tests

```python
# tests/test_core.py
import logging

import pytest

import mylib


def test_normalize():
    assert mylib.normalize("My_Package") == "my-package"


def test_errors_are_catchable_as_the_library_base():
    with pytest.raises(mylib.MylibError, match="invalid package name"):
        mylib.normalize("bad name!")


def test_invalid_name_is_still_a_value_error():
    with pytest.raises(ValueError):
        mylib.normalize("bad name!")


def test_deprecation_points_at_the_caller():  # DEPR-02, DEPR-07
    with pytest.warns(DeprecationWarning, match="use normalize") as record:
        assert mylib.canon("A_B") == "a-b"
    assert record[0].filename == __file__


def test_logs_through_the_module_logger(caplog):  # BEH-01
    with caplog.at_level(logging.DEBUG, logger="mylib"):
        mylib.normalize("x")
    assert caplog.records[0].name == "mylib._core"


def test_bundled_data_ships_with_the_package():  # BEH-11
    assert mylib.load_defaults()["index"].startswith("https://")


def test_public_api_snapshot():  # API-08 minimal form
    assert sorted(mylib.__all__) == [
        "InvalidNameError", "MylibError", "canon", "dump_toml",
        "load_defaults", "normalize", "normalize_names",
    ]
```

## CI workflow

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
  pull_request:
  schedule:
    - cron: "0 6 * * 1"                  # weekly newest-versions run (DEP-05)
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.11", "3.15"]         # floor and newest (PY-03)
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv run --python ${{ matrix.python }} pytest --doctest-modules src tests

  lowest:                                # DEP-04: the lower bounds actually work
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv run --isolated --resolution lowest-direct --python 3.11 pytest

  newest:                                # DEP-05: fresh resolve, not the lock
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv run --isolated --resolution highest --python 3.15 pytest

  wheel:                                 # TST-03, TYP-03, REL-01
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv build
      - run: uvx twine check --strict dist/*
      - run: |
          cd "$RUNNER_TEMP"
          uv venv wheel-env
          VIRTUAL_ENV=wheel-env uv pip install "$GITHUB_WORKSPACE"/dist/*.whl pyright
          wheel-env/bin/python -c "import mylib; print(mylib.load_defaults())"
          score=$(VIRTUAL_ENV=wheel-env PATH="$PWD/wheel-env/bin:$PATH" pyright --verifytypes mylib --ignoreexternal --outputjson | jq .typeCompleteness.completenessScore)
          echo "type completeness: $score"
          test "$score" = "1"
```

Pin the actions to SHAs before release (REL-06).
