---
name: skill-publisher
description: Packages an existing skill repo for both the Claude Code plugin marketplace and skills.sh (npx skills add). Use when the user wants to add marketplace/skills.sh install support to a repo that has a SKILL.md, or asks to "publish a skill", "add plugin support", "make this installable via skills.sh", or "open a PR to add install methods".
---

# Skill Publisher

Adds Claude Code plugin marketplace + skills.sh support to any skill repo in one workflow.

This skill is about publishing. To build plugin parts (hooks, agents, commands, MCP servers, settings), use the official `plugin-dev` plugin; its `plugin-validator` agent is also a good final check.

## Canonical example
PR: https://github.com/keithbinkly/dbt-semantic-layer/pull/1 (made before the `marketplace.json` step below, so its marketplace install does not work; follow this file, not the PR)

## Workflow

### 1. Explore the repo
- Read `SKILL.md` frontmatter — capture `name:` (this is `<skill-name>`)
- Note root-level dirs: `references/`, `assets/`, `scripts/`, etc.
- Check if `.claude-plugin/plugin.json` already exists (skip if present)
- Grep scripts for hardcoded skill paths (e.g. `.claude/skills/kb-*` or old names)

### 2. Restructure into `skills/<skill-name>/`
```bash
mkdir -p skills/<skill-name>
git mv SKILL.md skills/<skill-name>/SKILL.md
git mv references skills/<skill-name>/references   # if exists
git mv assets skills/<skill-name>/assets           # if exists
mkdir -p .claude-plugin
```

### 3. Create `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
`plugin.json` makes the repo a plugin. `marketplace.json` makes it a marketplace. `/plugin marketplace add <owner>/<repo>` reads only `marketplace.json`; without it the command fails with "Marketplace file not found". Create both.

`.claude-plugin/plugin.json`:
```json
{
  "name": "<repo-name>",
  "description": "<one-line from SKILL.md description field>",
  "author": { "name": "<author>", "url": "https://github.com/<owner>" },
  "homepage": "https://github.com/<owner>/<repo>",
  "repository": "https://github.com/<owner>/<repo>",
  "license": "MIT",
  "keywords": ["<domain>", "skill"]
}
```
Skills auto-discovered from `skills/` — no need to list them explicitly.

`.claude-plugin/marketplace.json` (one plugin, living at the repo root):
```json
{
  "name": "<repo-name>",
  "owner": { "name": "<author>" },
  "plugins": [
    {
      "name": "<repo-name>",
      "source": "./",
      "description": "<same one-line description>"
    }
  ]
}
```
- The marketplace `name` is what users type after `@` in `/plugin install <plugin>@<marketplace>`.
- If the repo already has a `marketplace.json` listing several plugins, add an entry there instead of creating a new file.
- Don't set `version` in the marketplace entry (see the note below).

> **Version field and auto-update** (verified from Claude Code docs):
> - **Omit `version`** (recommended for actively-developed skills) → Claude Code uses the git commit SHA, so every push is treated as a new version and users auto-update.
> - **Set `version`** → acts as a pin. Users only update when you bump the string; pushing new commits without changing it does nothing for existing installs.
> - **Avoid setting `version` in both `plugin.json` and a marketplace entry** — `plugin.json` always wins silently, which can mask marketplace version changes.
> - Default for users: `"latest"` channel — receives new features as soon as released.

### 4. Update README
Replace/add an **Installation** section with:
```markdown
## Installation

### Via Claude Code Plugin Marketplace (recommended)
/plugin install <repo-name> --marketplace <owner>/<repo>
# One step on Claude Code 2.1.275+. Older versions:
# /plugin marketplace add <owner>/<repo>
# /plugin install <repo-name>@<repo-name>

### Via skills.sh
npx skills add <owner>/<repo>
# Global: npx skills add <owner>/<repo> -g
# Specific agent: npx skills add <owner>/<repo> -a claude-code
# Note: skills.sh installs SKILL.md skills only. Hooks, agents, commands and
# MCP servers (.mcp.json) are not installed; use the marketplace for those.

### Via the skills directory (Claude Code, no marketplace)
git clone https://github.com/<owner>/<repo> ~/.claude/skills/<repo-name>
# Loads as <repo-name>@skills-dir in the next session, hooks and MCP servers included.
# Update: git -C ~/.claude/skills/<repo-name> pull
```
Update any file path references in the README to reflect the new `skills/<skill-name>/` location.

**Pick the recommended method by what the repo ships:**
- Only `SKILL.md` skills: all three methods work the same.
- Any `hooks/`, `agents/`, `commands/` or `.mcp.json`: recommend the marketplace or the skills directory, and keep the skills.sh note, since skills.sh leaves those out.

### 5. Fix stale paths in scripts
- Replace any `kb-<skill-name>` or old root-level skill paths with `.claude/skills/<skill-name>/`

### 6. Commit, fork, push, open PR
```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: add Claude Code plugin marketplace and skills.sh support"

# If no push access to origin:
gh repo fork <owner>/<repo> --clone=false
git remote add fork https://github.com/<your-account>/<repo>
git push fork main

gh pr create \
  --repo <owner>/<repo> \
  --head <your-account>:main \
  --title "feat: add Claude Code plugin marketplace and skills.sh support" \
  --body "..."
```

## PR body template
```
## Summary
- Add `.claude-plugin/plugin.json` (plugin) and `.claude-plugin/marketplace.json` (marketplace) for Claude Code
- Move SKILL.md + references + assets into `skills/<skill-name>/` for skills.sh auto-discovery
- Update README with the three install methods
- Fix stale paths in scripts (if any)

## Install methods added
/plugin install <repo-name> --marketplace <owner>/<repo>
npx skills add <owner>/<repo>
git clone https://github.com/<owner>/<repo> ~/.claude/skills/<repo-name>

## Test plan
- [ ] `claude plugin validate .` passes
- [ ] `/plugin install <repo-name> --marketplace <owner>/<repo>` works
- [ ] `npx skills add <owner>/<repo> --list` shows `<skill-name>`
```

## Validate before committing
```bash
claude plugin validate .        # CLI
# or inside Claude Code:
/plugin validate .
```

## Test locally end-to-end
```bash
/plugin marketplace add ./path/to/repo
/plugin install <plugin-name>@<marketplace-name>   # both names come from marketplace.json
```
Or, with no marketplace step: `claude --plugin-dir ./path/to/repo` loads the plugin for one session.

## Optional plugin.json fields worth adding
```json
{
  "displayName": "dbt Semantic Layer Developer",  // spaces allowed, shown in UI
  "category": "data",
  "tags": ["dbt", "analytics", "metricflow"],
  "defaultEnabled": true
}
```

## Auto-prompt teammates on project open
Add to `.claude/settings.json` so team members are automatically prompted to install:
```json
{
  "extraKnownMarketplaces": {
    "<repo-name>": {
      "source": { "source": "github", "repo": "<owner>/<repo>" }
    }
  }
}
```

## Notes
- skills.sh discovers from repo root `SKILL.md` OR `skills/<name>/SKILL.md` — moving to `skills/` is cleaner but both work
- `plugin.json` and `marketplace.json` both belong in `.claude-plugin/` (not repo root)
- skills.sh only copies `SKILL.md` skills and their folders. It reads `.claude-plugin/plugin.json` to find skills, not to install the plugin, so hooks, agents, commands and `.mcp.json` are dropped
- A folder in `~/.claude/skills/` (or a project's `.claude/skills/`) that contains `.claude-plugin/plugin.json` loads as `<name>@skills-dir` with no install step. Turn it off with `claude plugin disable <name>@skills-dir`
- skills.sh install path for Claude Code: `.claude/skills/<skill-name>/` (project) or `~/.claude/skills/<skill-name>/` (global)
- If plugin has hooks/scripts, all paths in plugin.json must use `${CLAUDE_PLUGIN_ROOT}`, never hardcoded paths — plugins are copied to a cache dir on install
- Relative source paths (e.g. `./plugins/foo`) in marketplace.json only work with git-based distribution, not direct URL distribution
