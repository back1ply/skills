# Release patterns

Reference files for releasing a uv_build package named `mylib` from GitHub with a static version. Rename `mylib` everywhere, including the PyPI URL. Item IDs point to [checklist.md](checklist.md).

Both workflows below pass `zizmor --persona pedantic` (1.32.0) and `actionlint` with no findings, and the release workflow's gate steps were run on a scratch repo (sources.md, P1). They have not been run on GitHub itself; do a TestPyPI dry run first.

## Contents

- One-time setup (GitHub and PyPI)
- release.yml
- zizmor.yml
- dependabot.yml
- CHANGELOG.md shape
- RELEASING.md
- Variant: version from git tags

## One-time setup (GitHub and PyPI)

1. **PyPI trusted publisher:** project (or a pending publisher for a new name, PUB-08) → Publishing → GitHub: owner, repo, workflow `release.yml`, environment `pypi` (PUB-01).
2. **Environment `pypi`:** Settings → Environments → `pypi`: required reviewer (you, even if solo), admin bypass off, deployment rule "Selected branches and tags" with tag pattern `v*` (GATE-06, TRIG-06).
3. **Tag ruleset:** Settings → Rules → Rulesets → new tag ruleset targeting `v*`: restrict creation, update, and deletion; block force pushes; bypass list = maintainers (TRIG-05).
4. **Actions settings:** require actions pinned to a full-length SHA (SEC-06).
5. **No PyPI tokens:** remove any `PYPI_*` secret and revoke old tokens on PyPI (SEC-05).

Verify with:

```
gh api repos/O/R/environments/pypi --jq '{rules: .protection_rules, admins_bypass: .can_admins_bypass}'
gh api repos/O/R/environments/pypi/deployment-branch-policies --jq '.branch_policies[] | {name, type}'
gh api repos/O/R/rulesets --jq '.[] | select(.target == "tag") | {id, name, enforcement}'
gh secret list; gh secret list --env pypi
```

## release.yml

```yaml
# .github/workflows/release.yml
name: release

on:
  push:
    tags: ["v*"]                         # the only publish trigger (TRIG-01); push one tag at a time (TRIG-03)

permissions: {}                          # each job asks for what it needs (SEC-01)

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false              # never cancel a publish midway (GATE-08)

jobs:
  test:                                  # tests on the exact tagged commit (GATE-01)
    name: Test the tagged commit
    runs-on: ubuntu-latest
    permissions:
      contents: read                     # read the repo
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false     # SEC-02
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          enable-cache: false            # no cache in the release path (SEC-03)
      - run: uv run --locked pytest

  build:                                 # build once; later jobs reuse these files (GATE-03)
    name: Build and check
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read                     # read the repo
    env:
      TAG: ${{ github.ref_name }}        # passed through env, never inlined into run: (SEC-09)
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
          fetch-depth: 0                 # full history, for the main-branch check (and VCS versions, VER-04)
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          enable-cache: false
      - name: Tagged commit is on main (TRIG-07)
        run: git merge-base --is-ancestor "$GITHUB_SHA" origin/main
      - name: Version matches tag (GATE-02)
        run: test "${TAG#v}" = "$(uv version --short)"
      - name: Changelog has this version (CHG-01)
        run: grep -qE "^## \[?${TAG#v}\]?( |$)" CHANGELOG.md
      - run: uv build
      - name: Check the artifacts (GATE-04, GATE-05, VER-05)
        run: |
          uvx twine check --strict dist/*
          ls dist
          test "$(find dist -name '*.tar.gz' | wc -l)" -eq 1
          if compgen -G 'dist/*+*' > /dev/null; then echo "local version part in a filename"; exit 1; fi
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: dist
          path: dist/
          if-no-files-found: error

  pypi:                                  # trusted publishing, attestations on by default (shared: CLI CI-03)
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi                         # required reviewer, tags v* only (GATE-06, TRIG-06)
      url: https://pypi.org/p/mylib
    permissions:
      id-token: write                    # only this job can mint the PyPI token (SEC-01)
    steps:
      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@7245906fb61fa33a13554f9d5fb856fe61758086 # v1.14.3

  github-release:                        # only after PyPI succeeded (GATE-07)
    name: GitHub release
    needs: pypi
    runs-on: ubuntu-latest
    permissions:
      contents: write                    # create the release and upload assets
    env:
      TAG: ${{ github.ref_name }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: dist
          path: dist/
      - name: Create the GitHub release from the changelog section (CHG-07, POST-01)
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          version="${TAG#v}"
          awk -v v="$version" '
            $0 ~ "^## \\[?" v "\\]?( |$)" { on = 1; next }
            on && /^## / { exit }
            on { print }
          ' CHANGELOG.md > notes.md
          flags=()
          case "$version" in *a[0-9]*|*b[0-9]*|*rc[0-9]*) flags=(--prerelease --latest=false) ;; esac
          gh release create "$TAG" dist/* --verify-tag --title "$TAG" --notes-file notes.md "${flags[@]}"
```

The job chain is test → build → PyPI → GitHub release, so nothing is published from an untested commit (GATE-01), every later job reuses the one build (GATE-03), and the GitHub release only appears if PyPI accepted the upload (GATE-07). `TAG` reaches shell code through `env:`, never through `${{ }}` inside `run:` (SEC-09). For the first release, add a TestPyPI job before `pypi` with `repository-url: https://test.pypi.org/legacy/` and its own environment (shared: CLI CI-03).

## zizmor.yml

```yaml
# .github/workflows/zizmor.yml
name: zizmor

on:
  push:
    branches: [main]
  pull_request:

permissions: {}

concurrency:
  group: zizmor-${{ github.ref }}
  cancel-in-progress: true

jobs:
  zizmor:
    name: Audit workflows
    runs-on: ubuntu-latest
    permissions:
      contents: read                     # read the workflow files
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
        with:
          enable-cache: false
      - run: uvx zizmor@1.32.0 --format=github .github/
```

Pin the zizmor version and bump it deliberately; a new release can add audits that fail CI (SEC-08).

## dependabot.yml

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7                    # let new action releases age before adopting them (SEC-07)
```

Review SHA-bump PRs; don't auto-merge them.

## CHANGELOG.md shape

The release workflow looks for a heading `## [V]` or `## V` (CHG-01) and copies everything up to the next `## ` into the GitHub release notes (CHG-07).

```markdown
# Changelog

## [Unreleased]

## [1.2.0] - 2026-11-18
### Added
- `normalize_names()` keeps input order.
### Deprecated
- `canon()`: use `normalize()`; removed in 2.0.
```

## RELEASING.md

```markdown
# Releasing

1. On a branch: `uv version --bump minor` (or `patch`, `major`; pre-release: `--bump minor --bump rc`).
   This also updates `uv.lock`. Commit both.
2. Move the `Unreleased` entries in CHANGELOG.md under `## [X.Y.Z] - YYYY-MM-DD`, and edit them for users:
   impact, migration steps, deprecations. Leave an empty `## [Unreleased]` above.
3. Open a PR, let CI pass, merge to main.
4. Tag the merge commit on main and push that one tag:
   `git switch main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
   (never `git push --tags`: more than three tags in one push trigger no workflow).
5. Approve the `pypi` deployment in the Actions run.
6. Check: `uv run --no-project --with "mylib==X.Y.Z" --refresh-package mylib -- python -c "import mylib"`
   and `uvx pypi-attestations verify pypi --repository https://github.com/O/R <wheel URL from PyPI>`.

## If something goes wrong

- Workflow failed before PyPI: fix on main, delete the unpublished tag locally and remotely only if nothing was uploaded, retag.
- Uploaded but broken: yank X.Y.Z on PyPI with a reason, release X.Y.(Z+1). Never re-upload or move the tag.
- Compromised release: delete the malicious files, rotate secrets, review trusted publishers and maintainers, publish an advisory.
```

Steps 1–3 put the version bump through review and CI before the tag exists (VER-03). The workflow then refuses a tag that doesn't match `pyproject.toml` (GATE-02).

## Variant: version from git tags

Only with hatchling or setuptools; `uv_build` needs a static version (VER-02).

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "mylib"
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"
```

Changes to the release workflow for this variant:
- Every checkout that builds uses `fetch-depth: 0`; a shallow clone silently builds `0.1.devN+g<hash>` (VER-04).
- Replace the "Version matches tag" step with a filename check after `uv build`: `compgen -G "dist/*-${TAG#v}.tar.gz"` (GATE-02). The local-version check stays (VER-05).
- Drop `uv version --bump` from RELEASING.md: the tag is the version.
