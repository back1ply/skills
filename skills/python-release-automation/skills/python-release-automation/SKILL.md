---
name: python-release-automation
description: Sets up, runs, and audits releases of Python packages (CLIs or libraries) from GitHub to PyPI - one version source, changelog gate, a single tag trigger, tests on the exact released commit, build once and publish the same files, trusted publishing behind an approval, yanking instead of deleting, and a hardened release workflow. Use when creating or reviewing a release workflow, cutting a release or pre-release, recovering from a bad release, or choosing between uv version, hatch-vcs, towncrier, git-cliff, or release-please.
---

# Python release automation

A release is the one step in a project that can't be undone: a version number, once on PyPI, is spent forever, and a bad workflow can publish code nobody tested or hand an attacker your PyPI identity. This skill covers the path from "main is ready" to "users can install it". The checklist has 63 items with stable IDs (`GATE-02`, `SEC-03`) in [references/checklist.md](references/checklist.md). Cite those IDs in every finding.

What the package contains (metadata, typing, CLI behaviour) belongs to the sister skills `python-cli-packaging` and `python-library-packaging`. Items marked "shared" in the checklist point there.

Pick the mode from the request:

| Mode | When | Ends with |
|---|---|---|
| **Set up** | A repo has no release automation, or a token-era workflow | The patterns in place, every MUST passing, a TestPyPI dry run done |
| **Release** | Cut a release or pre-release, or recover from a bad one | The version on PyPI with attestations, a GitHub release, the changelog reopened |
| **Audit** | Review an existing release setup | Findings covering every MUST and SHOULD item |

## Safety

Releasing is outward-facing and permanent. Never push a tag, approve a deployment, yank, or delete anything on PyPI without the user's explicit go-ahead for that specific action. Audit and set-up work stays local until the user says to push. Read-only `gh api` calls are fine.

## Set up

1. **Inventory.** Build backend, how the version is set, changelog method, existing workflows, secrets (`gh secret list`), and who can push tags.
2. **Pick the version source (VER-01, VER-02).** uv_build means a static version bumped with `uv version`. Tag-derived versions need hatchling + hatch-vcs or setuptools + setuptools-scm, plus `fetch-depth: 0` (VER-04).
3. **Pick the changelog method (CHG-02).** Solo or small: hand-written Keep a Changelog. Many contributors: towncrier with `towncrier check` on PRs. Commit-derived tools only with enforced Conventional Commits (CHG-04).
4. **Add the workflows** from [references/patterns.md](references/patterns.md): `release.yml`, `zizmor.yml`, `dependabot.yml`. Adjust the package name and test command; keep the job chain, permissions, and gates.
5. **One-time GitHub and PyPI setup** (patterns.md): trusted publisher, `pypi` environment with a reviewer and a `v*` tag rule, tag ruleset, SHA-pinning requirement, old tokens removed.
6. **Write RELEASING.md** from the pattern (POST-07) and `SECURITY.md` with supported versions (POST-06).
7. **Verify locally:** `uvx zizmor@1.32.0 --persona pedantic .github/` and actionlint clean; the gate steps pass on a scratch tag (checks.md). Then a TestPyPI dry run with a pre-release version.

## Release

1. **Prepare on a branch:** `uv version --bump <part>`, commit with `uv.lock`; move changelog entries under the new version and edit them for users (VER-03, CHG-01, CHG-05). Merge after CI passes.
2. **Tag the merge commit on main** and push that one tag: `git push origin vX.Y.Z` (TRIG-03, TRIG-07). Ask the user first.
3. **The workflow** tests the tagged commit, checks version == tag and the changelog, builds once, waits for approval, publishes, then creates the GitHub release.
4. **After:** smoke test from PyPI (POST-02), verify attestations (PROV-01), confirm the changelog has an empty `Unreleased` section (POST-03).

**Recovery:** a version is spent once uploaded (PUB-06). Failed before upload: fix and retag. Uploaded but broken: yank with a reason and release the next patch (PUB-05). Compromised: delete the malicious files and follow the runbook (PUB-07).

## Audit

1. **Read** every workflow that can publish, `pyproject.toml`, CHANGELOG, RELEASING.md, and the repo settings through `gh api` (checks.md).
2. **Run** zizmor (pedantic) and actionlint on `.github/`, and the gate steps on a scratch tag.
3. **Report.** Fails (MUST first) as `ID | evidence | fix`; not checked as `ID | reason | what would check it`; n/a grouped by cause in one line each; passes one line each. The audit is done when every MUST and SHOULD ID appears in exactly one list.

## The MUST items

**Version:** VER-01 one version source · VER-02 uv_build means a static version · VER-04 `fetch-depth: 0` for tag-derived versions · VER-05 no local version (`+g...`) in uploaded files.
**Changelog:** CHG-01 a section for this version exists at the tag, and the workflow checks it · CHG-04 commit-derived changelogs need enforced Conventional Commits.
**Trigger:** TRIG-01 exactly one publish trigger · TRIG-02 `release` triggers use `types: [published]` · TRIG-04 tags created with `GITHUB_TOKEN` fire nothing, so publish in that same workflow.
**Gates:** GATE-01 tests run on the exact tagged commit · GATE-02 built version == tag · GATE-03 build once, publish that same artifact.
**Publishing:** PUB-01 the publish job lives in a top-level workflow, not a reusable one · PUB-05 yank broken releases, don't delete · PUB-06 never re-upload a version or move a published tag.
**Security:** SEC-01 `permissions: {}` at the top, `id-token: write` only on the publish job · SEC-02 `persist-credentials: false` · SEC-03 no Actions cache in the release path · SEC-04 no `pull_request_target`/`workflow_run`/`issue_comment` in the release path · SEC-05 no PyPI tokens once trusted publishing works.

## Defaults for disputed choices

Reasoning and both sides are in [references/disputes.md](references/disputes.md).

- **Version source:** static + `uv version --bump` with uv_build; tag-derived is fine on hatchling/setuptools with VER-04 and VER-05 enforced.
- **Trigger:** tag push (the pattern) or `release: published`, never both for publishing.
- **Jobs:** separate test, build, publish, and GitHub-release jobs in one top-level workflow.
- **Changelog:** hand-written for solo maintainers; towncrier for many contributors; commit-derived only with enforced Conventional Commits and a human edit.
- **Release bots** (release-please, python-semantic-release): only with frequent releases and existing Conventional Commits discipline.
- **Approval:** keep a required reviewer on `pypi` even when solo.
- **Action pins:** full SHAs with Dependabot and a 7-day cooldown.
- **Extra provenance:** PyPI attestations are enough unless you ship assets outside PyPI.
- **Bad release:** yank; delete only malicious files.

## References

- [references/checklist.md](references/checklist.md): all 63 items with severity, modes, verification, and sources.
- [references/patterns.md](references/patterns.md): one-time setup, `release.yml`, `zizmor.yml`, `dependabot.yml`, CHANGELOG shape, RELEASING.md, and the tag-derived-version variant.
- [references/checks.md](references/checks.md): copy-paste commands for set-up verification and audits.
- [references/disputes.md](references/disputes.md): debated choices with both sides.
- [references/sources.md](references/sources.md): 51 sources and the local tests behind the items.
