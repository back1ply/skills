# AGENTS.md

## Repo scripts

Tooling lives in `scripts/` and runs through the `justfile` (`just` lists the recipes). Each script does one job, prints one summary line, and exits 1 on a problem.

- `just new NAME --category CAT --description "What it does. Use when ..." [--from path/SKILL.md]`: scaffold a plugin (folder, plugin.json, marketplace entry), then rebuild the README and run the checks. Never add a plugin by hand.
- `just check`: the offline checks CI runs. `check_skills.py` (Agent Skills spec plus Claude Code rules for every SKILL.md), `check_registry.py` (folders, plugin.json and marketplace agree), `lint_manifests.py` (no `version`, no author email, `repository` is this repo), `check_counts.py` (item counts in prose match the checklists), `build_readme.py --check`, `sync_shared.py --check`.
- `just discovery`: `skills add --list` on the published files must find exactly the published skills.
- `just refs [FILES]`: reference files over 100 lines need a `## Contents` near the top. The hook checks only changed files.
- `just readme`: rebuild README.md from `scripts/readme_template.md`. Edit the template, not README.md.

## Where new skills go

New skills go in `skills/<plugin>/skills/<skill>/` in this repo, never in `~/.agents/skills` or `~/.claude/skills`. This applies to skills made by book-to-skill, youtube-to-skill, and article-to-skill too: ignore their default personal install location. Unpublished or private skills go in `skills/plugins/` (gitignored).

## Git

Commit and push directly to `main`. Don't create feature branches or pull requests unless asked.

## CodeScene

After changing code, run `code_health_review` on the changed files. If Code Health drops, fix the issues, run the review again, and use `code_health_score` to confirm the result. Before finishing, run `pre_commit_code_health_safeguard` and only stop when it passes.

## Shared CLI rules

`agent-friendly-cli` owns the language-neutral CLI contract. `python-cli-packaging` copies 44 of its checklist rows and its `scripts/cli_contract.py`. After editing either source, run `just sync`; the `sync-check` workflow fails when they drift.

## Pre-push checks

`scripts/hooks/pre-push` runs the repo scripts above (step 0), `claude plugin validate`, SkillEvaluator Tier 1, gitleaks, lychee, and (when workflows change) zizmor and actionlint on what a push changes. Enable it once per clone with `just hooks`. Skip once with `git push --no-verify`.
