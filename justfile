# Repo tasks. Run `just` to list them. Every check is also a plain script in scripts/.
set windows-shell := ["bash", "-cu"]
set positional-arguments

default:
    @just --list

# Scaffold a plugin, rebuild the README, run the checks. Args go to scripts/new_plugin.py.
[group('make')]
new +args:
    uv run -q scripts/new_plugin.py "$@"
    just readme check

# Rebuild README.md from scripts/readme_template.md and the marketplace.
[group('make')]
readme:
    uv run -q scripts/build_readme.py

# Copy shared CLI rules from agent-friendly-cli into python-cli-packaging.
[group('make')]
sync:
    uv run -q scripts/sync_shared.py

# Fast offline checks: what CI runs.
[group('check')]
check:
    uv run -q scripts/check_skills.py
    uv run -q scripts/check_registry.py
    uv run -q scripts/lint_manifests.py
    uv run -q scripts/check_counts.py
    uv run -q scripts/build_readme.py --check
    uv run -q scripts/sync_shared.py --check

# Confirm skills.sh finds exactly the published skills (needs npx).
[group('check')]
discovery:
    uv run -q scripts/check_discovery.py

# Long reference files missing a Contents section (all files, or the ones given).
[group('check')]
refs *files:
    uv run -q scripts/lint_references.py "$@"

# Claude Code's own validator for the marketplace and every plugin.
[group('check')]
validate:
    claude plugin validate .
    for p in skills/*/.claude-plugin/plugin.json; do d=${p%/.claude-plugin/plugin.json}; claude plugin validate "$d" >/dev/null || { claude plugin validate "$d"; exit 1; }; done; echo "ok every plugin validates"

# Everything: offline checks, skills.sh discovery, Claude Code validation.
[group('check')]
all: check discovery validate

# Turn on the pre-push hook for this clone.
[group('setup')]
hooks:
    git config core.hooksPath scripts/hooks
