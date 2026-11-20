# Command blocks

Copy-paste commands for set-up verification and audits. Replace `O/R` with the GitHub owner/repo. All `gh api` calls are read-only. Unless marked "not run", the blocks were run on Windows (Git Bash) with zizmor 1.32.0, actionlint (latest via `go run`), yq, and uv.

**Workflow lint and security** (SEC-01 to SEC-09)

```
uvx zizmor@1.32.0 --persona pedantic .github/
actionlint .github/workflows/*.yml       # without a local install: go run github.com/rhysd/actionlint/cmd/actionlint@latest .github/workflows/*.yml
rg -n 'pull_request_target|workflow_run|issue_comment' .github/workflows/
rg -n 'enable-cache: true|actions/cache|^\s+cache: ' .github/workflows/release.yml   # setup-python's cache: key; enable-cache: false is fine
rg -n 'PYPI_API_TOKEN|TWINE_PASSWORD|password:' .github/workflows/
```

**Trigger and job chain** (TRIG-01, TRIG-02, GATE-01, GATE-03, GATE-07)

```
yq '.on' .github/workflows/release.yml
yq '.jobs | to_entries | .[] | {"job": .key, "needs": .value.needs, "permissions": .value.permissions}' .github/workflows/release.yml
rg -c 'uv build|python -m build' .github/workflows/release.yml      # exactly 1
```

**Gate steps on a scratch tag** (GATE-02, CHG-01, TRIG-07, VER-05)

In a throwaway clone with a tag `vX.Y.Z` on main, run each gate step's own script, taken from the workflow so the test can't drift from it:

```
export GITHUB_SHA=$(git rev-parse HEAD) TAG=vX.Y.Z
step() { yq -r ".jobs.$1.steps[] | select(.name == \"$2\") | .run" .github/workflows/release.yml; }
bash -c "$(step build 'Version matches tag (GATE-02)')" && echo pass
TAG=v0.0.0 bash -c "$(step build 'Version matches tag (GATE-02)')" || echo "mismatch rejected"
```

Repeat for the main-branch, changelog, and artifact steps; a gate that never fails isn't a gate.

**Repository settings** (GATE-06, TRIG-05, TRIG-06, SEC-05), not run (needs a repo with these settings)

```
gh api repos/O/R/environments/pypi --jq '{rules: .protection_rules, admins_bypass: .can_admins_bypass}'
gh api repos/O/R/environments/pypi/deployment-branch-policies --jq '.branch_policies[] | {name, type}'
gh api repos/O/R/rulesets --jq '.[] | select(.target == "tag") | {id, name, enforcement}'
gh secret list; gh secret list --env pypi
```

**Version handling** (VER-03, VER-06, VER-07)

```
uv version --short
uv version --bump minor --bump rc --dry-run      # preview a pre-release
uv lock --check                                   # the bump commit included uv.lock
```

**After a release** (POST-01, POST-02, PROV-01), not run (needs a published release)

```
uv run --no-project --with "dist==X.Y.Z" --refresh-package dist -- python -c "import pkg"
uvx pypi-attestations@0.0.31 verify pypi --repository https://github.com/O/R <wheel URL from the PyPI file list>
gh release view vX.Y.Z --json isPrerelease,body
```
