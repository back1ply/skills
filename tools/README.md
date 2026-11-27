# skills-repo

The `repo` command: checks and chores for this marketplace. It checks every skill against the [Agent Skills spec](https://agentskills.io/specification) that skills.sh uses and against Claude Code's skill rules. It also keeps the manifests, README and shared CLI rules in step. It is internal to this repo and never published.

## Run it

From anywhere in the repo, through the justfile (`just` lists the recipes):

```
just check            # every default rule
just test             # the tool's own tests
```

Or directly with uv:

```
uv run --project tools repo check
uv run --project tools repo --help
```

Installed as a tool instead: `uv tool install ./tools` (or `pipx install ./tools`), then run `repo check` inside the repo. Outside it, pass `--root PATH`.

## Commands

| Command | What it does |
|---|---|
| `repo check [--select CODES] [--paths FILE...] [--format text\|json\|github\|sarif] [--fix]` | Run rules and print findings. `--fix` first rewrites what fixable rules flag (DOC). `--format github` prints GitHub Actions annotations; `sarif` is for code-scanning tools. Exit 1 if any error-level finding. |
| `repo rules [--json]` | List every rule with its ID. This list is the source of truth. |
| `repo new NAME --category CAT --description "..." [--from SKILL.md]` | Scaffold a plugin, its plugin.json, SKILL.md, trigger eval stubs and marketplace entry. |
| `repo readme [--check]` | Rebuild README.md from `tools/readme_template.md`. |
| `repo sync [--check]` | Copy agent-friendly-cli's shared rows into python-cli-packaging. |

Exit codes: 0 ok, 1 problems found or a command failed, 2 usage error.

Rules are grouped by family. `SKL` covers SKILL.md, `REG` folder and manifest agreement, `MAN` manifest rules, `CNT` counts in prose, `DOC` generated files, `REF` reference files (over 100 lines need a Contents section), and `EVL` trigger eval cases. Those run by default. `DSC` (skills.sh discovery, which needs npx) runs only with `--select`. Rules marked `note:` inform but never fail a check.

## Trigger evals

Every skill has two `claude plugin eval` cases in its plugin's `evals/` folder: `trigger-<skill>`, a request that should load the skill, and `no-trigger-<skill>`, a near-miss that must not. Skills with `disable-model-invocation: true` get only the second. Rules `EVL001` (both cases exist) and `EVL002` (only keys and grader types the runner accepts) check them for free.

Running them is billed, because every case is a real Claude session, so nothing runs them automatically. Run one plugin by hand with `just trigger-evals PLUGIN [--runs N]`, which keeps reports local (`--no-publish`) and caps spend at $1.

## Layout

```
src/skills_repo/
  config.py      paths, URLs, limits, categories
  model.py       Repo, Plugin, Skill: loaded once, read by everything
  findings.py    Finding(path, rule, message, severity, line, subject); text/JSON/GitHub/SARIF output
  rules/         one module per family; each rule is a function registered with @rule
  core/          logic with no argparse: README rendering, shared-rule sync, scaffolding, eval cases
  commands/      one module per subcommand: build_parser() and main(argv) -> int
  cli.py         the root parser and lazy dispatch
tests/           each rule passes on a clean fixture repo and fails on its planted bug
```

To add a rule, write a function in the right `rules/` module, decorate it with `@rule("XXX000", "title")` (add `fix=` if it can repair itself), and add its planted bug to `tests/test_rules.py`. A test fails if any rule has no planted bug.

## Old commands

| Before | Now |
|---|---|
| `uv run scripts/check_skills.py` | `repo check --select SKL` |
| `uv run scripts/check_registry.py` | `repo check --select REG` |
| `uv run scripts/lint_manifests.py` | `repo check --select MAN` |
| `uv run scripts/check_counts.py` | `repo check --select CNT` |
| `uv run scripts/lint_references.py [FILES]` | `repo check --select REF [--paths FILES]` |
| `uv run scripts/check_discovery.py` | `repo check --select DSC` |
| `uv run scripts/new_plugin.py ...` | `repo new ...` |
| `uv run scripts/build_readme.py [--check]` | `repo readme [--check]` (also rule DOC001) |
| `python scripts/sync_shared.py [--check]` | `repo sync [--check]` (also rule DOC002) |

The justfile recipe names didn't change.
