# AGENTS.md

## Where new skills go

New skills go in `skills/<plugin>/skills/<skill>/` in this repo, never in `~/.agents/skills` or `~/.claude/skills`. This applies to skills made by book-to-skill, youtube-to-skill, and article-to-skill too: ignore their default personal install location. Unpublished or private skills go in `skills/plugins/` (gitignored).

## Git

Commit and push directly to `main`. Don't create feature branches or pull requests unless asked.

## CodeScene

After changing code, run `code_health_review` on the changed files. If Code Health drops, fix the issues, run the review again, and use `code_health_score` to confirm the result. Before finishing, run `pre_commit_code_health_safeguard` and only stop when it passes.

## Shared CLI rules

`agent-friendly-cli` owns the language-neutral CLI contract. `python-cli-packaging` copies 43 of its checklist rows and its `scripts/cli_contract.py`. After editing either source, run `python scripts/sync_shared.py`; the `sync-check` workflow fails when they drift.
