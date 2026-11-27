# AGENTS.md

## Repo tooling

The `repo` CLI in `tools/` (a uv project, see `tools/README.md`) checks and maintains this repo. The `justfile` wraps it; run `just` to list the recipes.

- `just new NAME --category CAT --description "What it does. Use when ..." [--from path/SKILL.md]`: scaffold a plugin (folder, plugin.json, marketplace entry), then rebuild the README and run the checks. Never add a plugin by hand.
- `just check`: every default rule, the same as CI. Families: `SKL` (Agent Skills spec and Claude Code rules for every SKILL.md), `REG` (folders, plugin.json and marketplace agree), `MAN` (no `version`, no author email, `repository` is this repo), `CNT` (counts in prose match the files), `DOC` (README and shared CLI rules are up to date), `REF` (long reference files have a Contents section). `just rules` lists every rule ID.
- `just discovery`: skills.sh must find exactly the published skills (rule family `DSC`, needs npx).
- `just refs [FILES]`: only rule `REF001`: reference files over 100 lines need a `## Contents` near the top. It is a default rule, so `just check` and CI run it too.
- `just readme`: rebuild README.md from `tools/readme_template.md`. Edit the template, not README.md.
- `just test`: the CLI's own tests. A new rule needs a planted-bug case in `tools/tests/test_rules.py`; a test fails without one.

## Where new skills go

New skills go in `skills/<plugin>/skills/<skill>/` in this repo, never in `~/.agents/skills` or `~/.claude/skills`. This applies to skills made by book-to-skill, youtube-to-skill, and article-to-skill too: ignore their default personal install location. Unpublished or private skills go in `skills/plugins/` (gitignored).

## Git

Commit and push directly to `main`. Don't create feature branches or pull requests unless asked.

## CodeScene

After changing code, run `code_health_review` on the changed files. If Code Health drops, fix the issues, run the review again, and use `code_health_score` to confirm the result. Before finishing, run `pre_commit_code_health_safeguard` and only stop when it passes.

## Shared CLI rules

`agent-friendly-cli` owns the language-neutral CLI contract. `python-cli-packaging` copies 44 of its checklist rows and its `scripts/cli_contract.py`. After editing either source, run `just sync`; rule `DOC002` (in `just check` and CI) fails when they drift.

## Pre-push checks

`scripts/hooks/pre-push` runs `repo check` (step 0, plus `DSC` when skills change, and the CLI's tests when `tools/` changes), `claude plugin validate`, SkillEvaluator Tier 1, gitleaks, lychee, and (when workflows change) zizmor and actionlint on what a push changes. Enable it once per clone with `just hooks`. Skip once with `git push --no-verify`.
