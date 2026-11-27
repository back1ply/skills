# Repo tasks. Run `just` to list them. Each recipe calls the `repo` CLI in tools/.
set windows-shell := ["bash", "-cu"]
set positional-arguments

repo := "uv run -q --project " + quote(justfile_directory() / "tools") + " repo"

default:
    @just --list

# Scaffold a plugin, rebuild the README, run the checks. Args go to `repo new`.
[group('make')]
new +args:
    {{repo}} new "$@"
    just readme check

# Rebuild README.md from tools/readme_template.md and the marketplace.
[group('make')]
readme:
    {{repo}} readme

# Copy shared CLI rules from agent-friendly-cli into python-cli-packaging.
[group('make')]
sync:
    {{repo}} sync

# Every default rule (SKL, REG, MAN, CNT, DOC): what CI runs. Extra args go to `repo check`.
[group('check')]
check *args:
    {{repo}} check "$@"

# Confirm skills.sh finds exactly the published skills (needs npx).
[group('check')]
discovery:
    {{repo}} check --select DSC

# Long reference files missing a Contents section (all files, or the ones given).
[group('check')]
refs *files:
    if [ $# -gt 0 ]; then {{repo}} check --select REF --paths "$@"; else {{repo}} check --select REF; fi

# Claude Code's own validator for the marketplace and every plugin.
[group('check')]
validate:
    claude plugin validate .
    for p in skills/*/.claude-plugin/plugin.json; do d=${p%/.claude-plugin/plugin.json}; claude plugin validate "$d" >/dev/null || { claude plugin validate "$d"; exit 1; }; done; echo "ok every plugin validates"

# Everything: tests, default rules, skills.sh discovery, Claude Code validation.
[group('check')]
all: test check discovery validate

# The repo CLI's own tests, lint and lockfile check.
[group('check')]
test:
    cd tools && uv lock --check -q && uv run -q pytest && uv run -q ruff check . && uv run -q ruff format --check .

# List every rule with its ID.
[group('check')]
rules:
    {{repo}} rules

# Turn on the pre-push hook for this clone.
[group('setup')]
hooks:
    git config core.hooksPath scripts/hooks
