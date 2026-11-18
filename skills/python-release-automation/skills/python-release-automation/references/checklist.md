# Python release checklist

63 items with stable IDs. Sources: [sources.md](sources.md) (`S` = source, `L`/`P` = local tests). Commands in tables escape `|` as `\|`; copy runnable commands from [checks.md](checks.md) instead.

Modes: **S** set up release automation, **R** run a release or recover from a bad one, **A** audit a release setup. `O/R` is the GitHub owner/repo, `dist` the distribution name, `pkg` the import name, `V` the version without the `v`. Items marked "shared" are owned by the `python-cli-packaging` or `python-library-packaging` skill.

## Contents

- VER: Version source of truth
- CHG: Changelog
- TRIG: Release trigger
- GATE: Release gates
- PUB: Publishing and recovery
- PROV: Provenance beyond PyPI attestations
- POST: Post-release
- SEC: Release workflow security

### 2.1 Version source of truth (VER)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| VER-01 | The version has exactly one source: a static `[project].version` bumped with `uv version`, **or** `dynamic = ["version"]` from git tags (hatch-vcs or setuptools-scm). No second hardcoded `__version__`. | MUST | S A | `grep -nE '^(version\|dynamic)' pyproject.toml`; `rg -n "__version__ = ['\"]"` finds nothing | shared with CLI PKG-06, library API-10; S6, S29 |
| VER-02 | With `uv_build` the version must be static. uv_build rejects `dynamic = ["version"]` (`missing field 'version'`), and `uv version` refuses dynamic projects. Tag-derived versions require hatchling + hatch-vcs or setuptools + setuptools-scm. | MUST | S A | `grep -A2 '^\[build-system\]' pyproject.toml` shows `uv_build` → `grep -n '^version = ' pyproject.toml` succeeds | S7, L1, L2 |
| VER-03 | Static versions: the bump (`uv version --bump <part>`) lands on main in a reviewed commit or PR **before** the tag, together with the updated `uv.lock` (uv locks by default). The release job never bumps. | SHOULD | S R A | `git show <tag> -- pyproject.toml uv.lock` shows the bump; `uv lock --check` passes at the tag | S6, S47 |
| VER-04 | Dynamic versions: every job that builds checks out full history and tags (`fetch-depth: 0`). A shallow clone silently builds `0.1.devN+g<hash>` with no error. | MUST (if dynamic) | S A | `rg -n 'fetch-depth' .github/workflows/` in the build job; locally: `git clone --depth 1 file://$PWD /tmp/x && cd /tmp/x && uv build` shows the bad version | S42, L4 |
| VER-05 | The uploaded version has no local part (`+g<hash>`, `+d<date>`). PyPI rejects it, so it only appears when a build runs off the tag or on a dirty tree. Gate on it rather than finding out at upload. | MUST | R A | `ls dist/ \| grep -F '+'` prints nothing | S1, S29, L4, P1 |
| VER-06 | Tags are `v` + the normalized PEP 440 version (`v1.2.0rc1`, not `v1.2.0-RC1`). PEP 440 ignores the leading `v`. uv normalizes `1.0.0-RC1` to `1.0.0rc1`. | SHOULD | S R A | `test "${TAG#v}" = "$(uv version --short)"` | S1, S29, L3 |
| VER-07 | Pre-releases use `aN`/`bN`/`rcN`. `.devN` is for TestPyPI or nightly builds, not PyPI announcements. Users only get pre-releases with `--pre` or an explicit pin. | SHOULD | R | `uv version --bump minor --bump rc --dry-run`; read the resulting version | S1, S6 |
| VER-08 | `.postN` only for changes that don't touch installed code (README, metadata). A bug fix is a new patch release. Note that `uv version --bump post` from `X.Y.Z.devN` jumps to `X.Y.Z.post1`, skipping the final release. | SHOULD | R | Diff the source tree between `vX.Y.Z` and `vX.Y.Z.postN`: only docs or metadata changed | S1, L3 |
| VER-09 | Release builds come from a clean tree. setuptools-scm appends `.dYYYYMMDD` to dirty builds, and hatchling sweeps untracked, non-ignored files (including a stray `dist/` from a previous build) into the sdist. | SHOULD | R A | `test -z "$(git status --porcelain)"` before `uv build` | S29, L4, L6 |
| VER-10 | The sdist rebuilds to the same version without git (dynamic versions read `PKG-INFO`). For git-less builds (distro packagers, archives), document `SETUPTOOLS_SCM_PRETEND_VERSION` (the per-dist variant did not work through hatch-vcs in L5). | NICE | A | `tar xzf dist/*.tar.gz -C /tmp/s && cd /tmp/s/* && uv build --wheel` gives the same version | S29, L5 |

### 2.2 Changelog (CHG)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| CHG-01 | A changelog section for exactly this version exists in the tagged commit (format: shared with library REL-04, CLI DOC-04). The release workflow fails if it is missing. | MUST | R A | `grep -nE "^## \[?$V\]?" CHANGELOG.md` at the tag | shared; S36, S47, P1 |
| CHG-02 | One changelog method is chosen and written in RELEASING/CONTRIBUTING: hand-written (Keep a Changelog), fragments (towncrier, scriv), or derived from commits (git-cliff, commitizen, PSR, release-please). Mixing methods produces duplicate or missing entries. | SHOULD | S A | `ls changelog.d newsfragments 2>/dev/null; grep -nE 'towncrier\|scriv\|git-cliff\|commitizen\|semantic_release' pyproject.toml cliff.toml` match the docs | S31, S32, S33, S34 |
| CHG-03 | Fragments: PRs run `towncrier check --compare-with origin/main` (with a skip label for trivial PRs). The release PR runs `towncrier build --version $V --yes` after reviewing `--draft`. | SHOULD (if towncrier) | S A | Read the PR workflow; `uvx towncrier build --draft --version $V` | S31 |
| CHG-04 | Commit-derived changelogs and versions need enforced Conventional Commits: squash-merge with a checked PR title, or a `commitizen` commit-msg hook. Without enforcement the output is wrong, not merely ugly. | MUST (if commit-derived) | S A | `git log --format=%s <last-tag>..HEAD \| grep -vcE '^(feat\|fix\|docs\|chore\|refactor\|perf\|test\|ci\|build\|style\|revert)(\(.+\))?!?: '` is 0 | S38, S36, S34 |
| CHG-05 | A human edits generated notes before the tag: tools emit commit subjects, but users need impact, migration steps, and deprecations. Keep the edit in the release PR. | SHOULD | R | The release PR diff for CHANGELOG.md has hand-edited lines | S36, S35 (practice) |
| CHG-06 | git-cliff `--bump` in 0.x: the default config moves `0.y` to `1.0.0` on any breaking commit (L7). Set `breaking_always_bump_major = false` and `features_always_bump_minor = false` in `cliff.toml` while in 0.x, unless 1.0 is intended. | SHOULD (if git-cliff bump) | S A | `grep -nE 'breaking_always_bump_major\|features_always_bump_minor' cliff.toml`; `uvx git-cliff --bumped-version` | S33, L7 |
| CHG-07 | The GitHub release body is the changelog section for that version (`gh release create --notes-file`), or generated notes with `.github/release.yml` categories. Not empty. | SHOULD | S R A | `gh release view v$V --json body -q .body \| head` | S14, S20, S32 |

### 2.3 Release trigger (TRIG)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| TRIG-01 | One publish trigger only: tag push (`on: push: tags: ["v*"]`) **or** `release: types: [published]`. Other triggers in the same workflow (`pull_request`, `workflow_dispatch`) may build but cannot reach the publish job (`if: github.event_name == 'release' && github.event.action == 'published'`, or `startsWith(github.ref, 'refs/tags/v')`). | MUST | S A | `yq '.on, .jobs.*.if' .github/workflows/release.yml` | S42, S28 |
| TRIG-02 | A `release` trigger uses `types: [published]`. `released` misses pre-releases, drafts fire none of `created`/`edited`/`deleted`, and a bare `on: release` fires on every type (edits included). | MUST (if release trigger) | S A | `yq '.on.release.types' .github/workflows/*.yml` is `["published"]` | S9, S42 |
| TRIG-03 | Push the release tag alone (`git push origin v$V`). GitHub creates no push events when more than three tags are pushed at once, so `git push --tags` can silently skip the release. | SHOULD | R | Release docs and scripts contain no `git push --tags` / `--follow-tags` | S9 |
| TRIG-04 | If a bot creates the tag or release with `GITHUB_TOKEN` (release-please, PSR, a bump job), no other workflow fires. Publish in the same workflow gated on the tool's output (`release_created`, `released`), or use a GitHub App token. | MUST (if bot-created tags) | S A | Find who creates tags: `rg -n 'release-please-action\|semantic-release\|git tag\|git push' .github/workflows/`; check the publish job lives in that workflow | S8, S37, S35 |
| TRIG-05 | A tag ruleset on `v*` restricts creation, update, and deletion to maintainers (bypass list) and blocks force pushes, so a collaborator cannot cut a release. | SHOULD | S A | `gh api repos/O/R/rulesets --jq '.[] \| select(.target=="tag")'`, then `gh api repos/O/R/rulesets/<id>` shows creation/update/deletion rules | S10, S24, S47 |
| TRIG-06 | The `pypi` environment's deployment rule allows only tags matching `v*` (or only `main` plus tags), so `workflow_dispatch` from a feature branch can't publish even with approval. | SHOULD | S A | `gh api repos/O/R/environments/pypi --jq .deployment_branch_policy`, then `gh api repos/O/R/environments/pypi/deployment-branch-policies` | S11 |
| TRIG-07 | The tagged commit is on main. Tags on unmerged branches publish code no reviewer approved. | SHOULD | R A | In the release job: `git fetch origin main && git merge-base --is-ancestor "$GITHUB_SHA" origin/main` | S43, S47, P1 |
| TRIG-08 | `gh release create` runs with `--verify-tag`. Without it, a typo creates a new tag from the default-branch HEAD, which may not be the tested commit. | SHOULD | R A | `rg -n 'gh release create' .github/ RELEASING* scripts/` each has `--verify-tag` | S20 |
| TRIG-09 | Choosing release-please or PSR is a deliberate trade: it needs Conventional Commits (CHG-04), write permissions for a bot, PR creation enabled for Actions, and a PAT or App to pass branch protection or to run CI on the release PR. For a solo maintainer a manual bump PR plus tag is usually simpler. | SHOULD (decision) | S | Document the choice in RELEASING.md | S35, S36, S37, S15 |

### 2.4 Release gates (GATE)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| GATE-01 | Tests pass on the exact commit being released, inside the release workflow (`needs: [test]`, or CI called as a reusable workflow with `workflow_call`). "Main was green yesterday" doesn't count. | MUST | S A | `yq '.jobs.*.needs' .github/workflows/release.yml` chains publish ← build ← test | S46, S16, S47 |
| GATE-02 | The version being built equals the tag. Static: `test "${GITHUB_REF_NAME#v}" = "$(uv version --short)"`. Dynamic: the built filenames contain `${GITHUB_REF_NAME#v}`. On mismatch the job fails before anything is uploaded. | MUST | S R A | Look for that step before the build in the release workflow | S41 (`package_version` output), S6, L3, P1 |
| GATE-03 | Build once in a job without `id-token`, upload `dist/` as an artifact, and have every later job (PyPI, TestPyPI, GitHub release assets, attestations) download that same artifact. Nothing rebuilds. | MUST | S A | Exactly one `uv build`/`python -m build`/`build-and-inspect` step across release workflows | shared with CLI CI-03; S27, S28, S48, S18 |
| GATE-04 | Artifacts are checked before publish: `twine check --strict`, wheel contents, and an install-and-smoke test of the built wheel in a clean environment. | SHOULD | S A | `uvx twine check --strict dist/*`; `uvx check-wheel-contents dist/*.whl`; smoke test per CLI TST-03 / library TST | shared with CLI PKG-07, TST-03; S41 |
| GATE-05 | `dist/` holds exactly one sdist and the expected wheels, named with the release version, before upload. A leftover file from another version makes the upload publish both. | SHOULD | R A | `ls dist/` shows `dist-$V.tar.gz` and `dist-$V-*.whl` only | S27, L6, P1 |
| GATE-06 | The publish job runs in environment `pypi` with a required reviewer and admin bypass disabled. A solo maintainer can't turn on "prevent self-review" (it would block them), but the approval click still stops an unintended trigger. | SHOULD | S A | `gh api repos/O/R/environments/pypi --jq '.protection_rules, .can_admins_bypass'` | S11, S24, S28, S44 |
| GATE-07 | The release fails closed: if the PyPI upload fails, no GitHub release is published as latest. Order: build → PyPI → GitHub release, or create the GitHub release as a draft and publish it after PyPI succeeds. | SHOULD | S A | Read job ordering: the GitHub-release job `needs:` the PyPI job | S47, S13 |
| GATE-08 | The release workflow has `concurrency: {group: release-${{ github.ref }}, cancel-in-progress: false}`, so two runs never publish at once and a running publish is never cancelled midway. | NICE | S A | `yq '.concurrency' .github/workflows/release.yml` | S35, S39 (concurrency-limits) |

### 2.5 Publishing and recovery (PUB)

Trusted publishing, PEP 740 attestations, and TestPyPI-first are shared with CLI CI-03 and library REL-03 and are not repeated.

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| PUB-01 | The job that calls `pypa/gh-action-pypi-publish` lives in a top-level workflow whose filename matches the PyPI trusted-publisher entry. Trusted publishing does not work from inside a reusable workflow. | MUST | S A | The publish job has no `on: workflow_call` parent; its file name matches the PyPI project's publisher settings | S27, S25 |
| PUB-02 | `skip-existing` is off for PyPI (on at most for TestPyPI). A rerun that "succeeds" by skipping hides a version that was already published, possibly from a different build. | SHOULD | S A | `rg -n 'skip-existing' .github/workflows/` only in a TestPyPI step | S27 |
| PUB-03 | If `uv publish` is used instead of the PyPA action, note that it uploads but never creates attestations. Prefer the PyPA action, or create `.publish.attestation` files another way. | SHOULD | S A | `rg -n 'uv publish' .github/workflows/` → check for an attestation step | S6, S27 |
| PUB-04 | Pre-releases go to PyPI as `rcN`/`bN` (installers skip them by default) with a GitHub release marked `--prerelease --latest=false`. | SHOULD | R | `gh release view v$V --json isPrerelease` is true for pre-release tags | S1, S20, S9 |
| PUB-05 | A broken release (uninstallable, breaks its compatibility promise, vulnerable) is **yanked with a reason** and followed by a fixed `X.Y.Z+1`. It is not deleted: deletion is permanent and breaks exact pins. | MUST | R | PyPI project → Manage → release → Options → Yank, with a reason; then `uv pip install 'dist==X.Y.Z'` still works with a warning | S2, S3, S4 |
| PUB-06 | A version number is spent once uploaded: never re-upload, re-tag, or move a published tag. A deleted file's name is permanently blocked ("Use a different version"). If the publish fails after the tag exists, fix forward with a new patch version. | MUST | R | `git ls-remote --tags origin v$V` matches the SHA in the PyPI release's provenance | S5, S12, S6 |
| PUB-07 | Compromise runbook, written down in advance: delete known-malicious releases (the one case for deletion), rotate every long-lived secret, revoke stray PyPI tokens, review trusted publishers and maintainers, and publish an advisory. | SHOULD | S R | RELEASING.md or SECURITY.md has an incident section | S45, S24 |
| PUB-08 | A first release reserves the name with a PyPI **pending** trusted publisher before the first upload. | NICE | S | PyPI account → Publishing → pending publisher exists for `dist` | S46, S25 |

### 2.6 Provenance beyond PyPI attestations (PROV)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| PROV-01 | After each release, check that PyPI attestations exist and verify against the repo. | SHOULD | R A | `uvx pypi-attestations verify pypi --repository https://github.com/O/R https://files.pythonhosted.org/.../dist-$V-py3-none-any.whl` | shared with CLI CI-03; S26 |
| PROV-02 | GitHub artifact attestations (`actions/attest@v4`, or `attest-build-provenance`, now a wrapper) are optional for a small public project. They are free for public repos, need Enterprise Cloud for private ones, and add verification through `gh`. If used, run them in the job that already holds `id-token` with `attestations: write` and `artifact-metadata: write`, and verify them pinned to the workflow and tag. | NICE | S R A | `rg -n 'actions/attest' .github/workflows/` with matching job permissions; after a release: `gh attestation verify dist/*.whl --repo O/R --signer-workflow O/R/.github/workflows/release.yml --source-ref refs/tags/v$V --deny-self-hosted-runners` | S21, S22, S23, S42, S41 |
| PROV-03 | Immutable releases (repo setting) lock the tag and assets and add an automatic release attestation. Assets must be attached while the release is still a draft, so a "release published → build → upload assets" workflow breaks under immutability. Use draft → attach → publish from the workflow, or don't attach assets. | NICE | S A | Repo Settings → Releases shows whether immutable releases are on; read whether the workflow uploads assets after `published` | S12, S13 |
| PROV-04 | Builds are reproducible enough to re-check: `SOURCE_DATE_EPOCH` set from the last commit (hynek action) or a backend that is reproducible by default (uv_build, hatchling per L6). Anyone can rebuild the tag and compare sha256 with PyPI. | NICE | A | `git checkout v$V && uv build -o /tmp/rb && sha256sum /tmp/rb/*`, compared with `print-hash` output or PyPI's JSON `digests.sha256` | S41, L6, S27 |

### 2.7 Post-release (POST)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| POST-01 | Every PyPI release has a GitHub release for its tag. Watchers get notified, and it holds the notes (CHG-07). | SHOULD | R A | `gh release list --limit 5` matches the latest PyPI versions | S42 |
| POST-02 | Smoke test from the real index after upload, outside the repo, forcing a fresh fetch. | SHOULD | R | `uv run --no-project --with "dist==$V" --refresh-package dist -- python -c "import pkg"`, or `uvx --refresh "dist@$V" --version` for a CLI | S6 |
| POST-03 | The changelog reopens an `Unreleased` section (or the fragment directory is empty) on main after the release. | SHOULD | R | `grep -n '^## \[Unreleased\]' CHANGELOG.md`; `ls changelog.d/` is empty apart from templates | shared with library REL-04; S31, S32 |
| POST-04 | A post-release bump to `X.Y.(Z+1).dev0` is optional for static versions (`uv version --bump patch --bump dev`). Never publish those dev builds to PyPI. Dynamic versions do this automatically (L4). | NICE | R | Look at the version on main after the release | S6, S1, L3, L4 |
| POST-05 | Downstream: conda-forge's bot opens a version PR within hours. A maintainer must edit it when dependencies changed, and the bot stops after 3 open PRs. Homebrew and other distros: pointer only. | NICE | R | Check the feedstock's open PRs after release | S49 |
| POST-06 | `SECURITY.md` states supported versions and how to report vulnerabilities. Small projects: "latest minor only" is a fine policy. Backport branches (`release/X.Y`) are a pointer, needed only when supporting more than one line. | SHOULD | S A | `ls SECURITY.md .github/SECURITY.md`; it lists supported versions | S50 |
| POST-07 | The release process is written down (RELEASING.md or CONTRIBUTING): how to bump, tag, approve, recover, and who holds the permissions. | SHOULD | S A | `ls RELEASING* docs/release*`; `rg -n -i 'release' CONTRIBUTING*` | S43, S47 |

### 2.8 Release workflow security (SEC)

| ID | Item | Sev | Modes | Verify | Source |
|---|---|---|---|---|---|
| SEC-01 | `permissions: {}` (or `contents: read`) at workflow level. Each job adds only what it needs: `id-token: write` only on the publish job, and `contents: write` only on the job that creates the GitHub release. | MUST | S A | `yq '.permissions, .jobs.*.permissions' .github/workflows/release.yml`; `uvx zizmor .github/workflows/release.yml` (excessive-permissions) | S17, S24, S44, S43, S39 |
| SEC-02 | `actions/checkout` uses `persist-credentials: false` everywhere in release workflows. | MUST | S A | `uvx zizmor .github/` reports no `artipacked` | S28, S43, S44, S39 |
| SEC-03 | Release workflows read no Actions cache. Set `cache-mode: none` at workflow level, or `enable-cache: false` on setup-uv. setup-uv auto-disables its cache on release and tag-push events but **not** on `workflow_dispatch`. No `actions/cache`. | MUST | S A | `yq '."cache-mode"' release.yml` is `none`; `rg -n 'enable-cache\|actions/cache\|cache:' .github/workflows/release.yml`; zizmor `cache-poisoning` clean | S39, S17, S40, S45 |
| SEC-04 | No `pull_request_target`, `workflow_run`, or `issue_comment` triggers anywhere in the release path. | MUST | S A | `rg -n 'pull_request_target\|workflow_run\|issue_comment' .github/workflows/`; zizmor `dangerous-triggers` | S39, S45 |
| SEC-05 | No PyPI API token in repo, org, or environment secrets once trusted publishing works. Old tokens are revoked on PyPI too (the second Ultralytics wave used a leftover token). | MUST | S A | `gh secret list; gh secret list --env pypi` shows no PyPI token; PyPI account → API tokens is empty or scoped and justified | S28, S45, S39 (use-trusted-publishing) |
| SEC-06 | Every `uses:` is pinned to a full commit SHA with a `# vX.Y.Z` comment, and the repo setting "Require actions to be pinned to a full-length commit SHA" is on. | SHOULD | S A | `uvx zizmor .github/` (unpinned-uses); `gh api repos/O/R/actions/permissions --jq .sha_pinning_required` (field name from S44) | S43, S44, S39, S15 |
| SEC-07 | Dependabot updates `github-actions` with `cooldown: {default-days: 7}`, and hash-bump PRs are reviewed, not auto-merged. | SHOULD | S A | `yq '.updates[] \| select(."package-ecosystem"=="github-actions")' .github/dependabot.yml` | S19, S44, S39, S43 |
| SEC-08 | zizmor runs in CI on `.github/` (action or pre-commit) and is clean at the default persona. | SHOULD | S A | `uvx zizmor --quiet .github/` exits 0 | S44, S43, S39 |
| SEC-09 | No `${{ }}` expansion of attacker-influenced values (branch names, PR titles, release names, even `github.ref_name`) inside `run:`. Pass them through `env:` and quote them. | SHOULD | S A | zizmor `template-injection`; `rg -n 'run:.*\$\{\{' .github/workflows/` | S39 |
| SEC-10 | Accounts: 2FA (hardware key or app) on PyPI and GitHub for everyone who can publish or approve. Review trusted publishers and environment reviewers when a maintainer leaves. | SHOULD | S A | PyPI project → Collaborators and Publishing; GitHub environment reviewers list | S45, S24 |

Total: 63 items (VER 10, CHG 7, TRIG 9, GATE 8, PUB 8, PROV 4, POST 7, SEC 10).
