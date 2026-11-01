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
- Find the skill: `SKILL.md` at the repo root, or already nested at `skills/<name>/SKILL.md`.
- Read its frontmatter `name:`. This is `<skill-name>`. Before using it in any path or command, check it matches `^[a-z0-9]+(-[a-z0-9]+)*$` (lowercase letters, digits, single hyphens). If it doesn't, stop and ask the user for a valid name; never paste an unchecked name into a shell command.
- Note the skill's own folders next to `SKILL.md`: `references/`, `assets/`, `scripts/`, `templates/`, etc.
- Read the repo's license (`LICENSE` file or GitHub's license field). Use that identifier in the manifests. If there is none, leave `license` out and tell the user.
- Check whether `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` already exist. Update them instead of replacing them.
- Grep scripts and docs for hardcoded skill paths (e.g. `.claude/skills/kb-*` or old names).
- Note the default branch: `gh repo view <owner>/<repo> --json defaultBranchRef -q .defaultBranchRef.name`.

Set up the shell state every later step uses, and leave the default branch, whether or not step 2 runs:
```bash
skill_md=SKILL.md                          # or skills/<name>/SKILL.md if already nested
name=$(yq --front-matter=extract '.name' "$skill_md")
[[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "invalid skill name: $name"; exit 1; }
git checkout -b add-plugin-support         # or `git checkout` it if it already exists
```

### 2. Restructure into `skills/<skill-name>/`
Skip this step if the skill is already at `skills/<skill-name>/SKILL.md`.

skills.sh copies only the skill folder, so everything the skill uses must end up inside `skills/<skill-name>/`. List what sits next to `SKILL.md` (`git ls-files` at the root) and decide, file by file, what belongs to the skill: anything `SKILL.md` or its references link to, such as `references/`, `assets/`, `scripts/`, `templates/`, `examples/` or `data/`. Leave repo-level files (`README.md`, `LICENSE`, CI config) where they are. If a folder serves both the skill and the repo (for example `scripts/` with CI scripts), ask the user which files go with the skill.

```bash
mkdir -p "skills/$name" .claude-plugin
git mv SKILL.md "skills/$name/SKILL.md"
for d in references assets scripts templates examples data; do   # adjust to the list you made
  if [ -e "$d" ]; then git mv "$d" "skills/$name/$d"; fi
done
```
Then check that every relative link in `skills/$name/SKILL.md` and its references points to a file that exists under `skills/$name/`.

### 3. Create `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
`plugin.json` makes the repo a plugin. `marketplace.json` makes it a marketplace. `/plugin marketplace add <owner>/<repo>` reads only `marketplace.json`; without it the command fails with "Marketplace file not found". Create both.

Write both files with a JSON tool, never by pasting text from the repo into a template or into a shell command. A description that contains `"` or `}` can otherwise break out of a JSON string and add fields, such as a different plugin `source`; one that contains `'` can break out of a shell string and run commands. Read the values with tools so the text never passes through shell quoting:
```bash
desc=$(yq --front-matter=extract '.description' "skills/$name/SKILL.md")
license=$(gh api 'repos/<owner>/<repo>/license' -q '.license.spdx_id' 2>/dev/null)
# No license (empty or NOASSERTION)? Drop the --arg and the license field, and tell the user.
jq -n --arg name "$name" --arg desc "$desc" --arg owner '<owner>' \
      --arg repo '<owner>/<repo>' --arg license "$license" '{
  name: $name, description: $desc,
  author: {name: $owner, url: ("https://github.com/" + $owner)},
  homepage: ("https://github.com/" + $repo),
  repository: ("https://github.com/" + $repo),
  license: $license
}' > .claude-plugin/plugin.json

jq -n --arg name "$name" --arg desc "$desc" --arg owner '<owner>' '{
  name: $name, owner: {name: $owner},
  plugins: [{name: $name, source: "./", description: $desc}]
}' > .claude-plugin/marketplace.json
```
- `plugin.json`: skills are found automatically under `skills/`, so don't list them.
- `marketplace.json`: its `name` is what users type after `@` in `/plugin install <plugin>@<marketplace>`. `"source": "./"` points at the repo root, where `plugin.json` lives.
- If the repo already has a `marketplace.json` listing several plugins, add an entry there with `jq` instead of creating a new file.

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
/plugin install <skill-name> --marketplace <owner>/<repo>
# One step on Claude Code 2.1.275+. Older versions:
# /plugin marketplace add <owner>/<repo>
# /plugin install <skill-name>@<marketplace-name>

### Via skills.sh
npx skills add <owner>/<repo>
# Global: npx skills add <owner>/<repo> -g
# Specific agent: npx skills add <owner>/<repo> -a claude-code
# Note: skills.sh installs SKILL.md skills only. Hooks, agents, commands and
# MCP servers (.mcp.json) are not installed; use the marketplace for those.

### Via the skills directory (Claude Code, no marketplace)
git clone https://github.com/<owner>/<repo> ~/.claude/skills/<skill-name>
# Loads as <skill-name>@skills-dir in the next session, hooks and MCP servers included.
# Update: git -C ~/.claude/skills/<skill-name> pull
```
Update any file path references in the README to reflect the new `skills/<skill-name>/` location.

**Pick the recommended method by what the repo ships:**
- Only `SKILL.md` skills: all three methods work the same.
- Any `hooks/`, `agents/`, `commands/` or `.mcp.json`: recommend the marketplace or the skills directory, and keep the skills.sh note, since skills.sh leaves those out.

### 5. Fix paths in scripts and docs
The skill lands in a different place for each install method (a plugin cache folder, `~/.claude/skills/`, a project's `.claude/skills/`), so never rewrite paths to a fixed `.claude/skills/<skill-name>/`.
- In `SKILL.md` and its references, point to files relative to the skill folder (`scripts/foo.py`, `references/bar.md`).
- Inside hook commands and MCP server commands or arguments, use `${CLAUDE_PLUGIN_ROOT}`.
- In `plugin.json` component fields (`hooks`, `commands`, `agents`, `mcpServers` paths), use `./` paths relative to the plugin root.
- In scripts, find files relative to the script's own location (Python: `Path(__file__).parent`; bash: `"$(dirname "$0")"`).

### 6. Validate
```bash
claude plugin validate .
npx skills add . -l    # must list <skill-name>
```

### 7. Commit, then get approval before pushing
```bash
git add -A .claude-plugin "skills/$name" README.md   # plus any script or doc you changed
git status --short    # confirm nothing is missing and nothing extra is staged
git commit -m "feat: add Claude Code plugin marketplace and skills.sh support"
```

**Stop here and ask the user.** Pushing and opening a PR are visible to others and notify the repo owner. Show the user the target repo, the branch, `git diff --stat <default-branch>...HEAD` and the PR title and body, and wait for a clear yes before running anything below.

### 8. Push and open the PR
Write the PR body (see the template below) to a file outside the repo, so it never gets committed. Then push the branch you committed on, never `main`:
```bash
pr_body=$(mktemp)    # write the filled-in template into "$pr_body"
branch=$(git branch --show-current)

# With push access to <owner>/<repo>:
git push -u origin "$branch"
gh pr create --repo '<owner>/<repo>' --base '<default-branch>' --head "$branch" \
  --title "feat: add Claude Code plugin marketplace and skills.sh support" --body-file "$pr_body"

# Without push access: fork, then push to the fork
gh repo fork '<owner>/<repo>' --clone=false
fork_url="https://github.com/<your-account>/<repo>"
git remote get-url fork >/dev/null 2>&1 && git remote set-url fork "$fork_url" || git remote add fork "$fork_url"
git push -u fork "$branch"
gh pr create --repo '<owner>/<repo>' --base '<default-branch>' --head "<your-account>:$branch" \
  --title "feat: add Claude Code plugin marketplace and skills.sh support" --body-file "$pr_body"
```

## PR body template
```
## Summary
- Add `.claude-plugin/plugin.json` (plugin) and `.claude-plugin/marketplace.json` (marketplace) for Claude Code
- Move SKILL.md and its folders into `skills/<skill-name>/` for skills.sh auto-discovery
- Update README with the three install methods
- Fix paths in scripts (if any)

## Install methods added
/plugin install <skill-name> --marketplace <owner>/<repo>
npx skills add <owner>/<repo>
git clone https://github.com/<owner>/<repo> ~/.claude/skills/<skill-name>

## Test plan
- [ ] `claude plugin validate .` passes
- [ ] `/plugin install <skill-name> --marketplace <owner>/<repo>` works
- [ ] `npx skills add <owner>/<repo> --list` shows `<skill-name>`
```

## Test locally end-to-end
```bash
/plugin marketplace add ./path/to/repo
/plugin install <plugin-name>@<marketplace-name>   # both names come from marketplace.json
```
Or, with no marketplace step: `claude --plugin-dir ./path/to/repo` loads the plugin for one session.

## Optional fields worth adding
In `plugin.json`:
```json
{
  "displayName": "dbt Semantic Layer Developer",
  "defaultEnabled": true
}
```
`displayName` is the name shown in the UI and may contain spaces.

In the plugin's `marketplace.json` entry (not `plugin.json`, where Claude Code ignores them):
```json
{
  "category": "data",
  "tags": ["dbt", "analytics", "metricflow"]
}
```

## Auto-prompt teammates on project open
Add to `.claude/settings.json` so team members are automatically prompted to install:
```json
{
  "extraKnownMarketplaces": {
    "<marketplace-name>": {
      "source": { "source": "github", "repo": "<owner>/<repo>" }
    }
  }
}
```

## Notes
- skills.sh discovers from repo root `SKILL.md` OR `skills/<name>/SKILL.md` — moving to `skills/` is cleaner but both work
- `plugin.json` and `marketplace.json` both belong in `.claude-plugin/` (not repo root)
- skills.sh finds `SKILL.md` files and copies each skill's folder. It does not install the plugin, so hooks, agents, commands and `.mcp.json` are dropped
- A folder in `~/.claude/skills/` (or a project's `.claude/skills/`) that contains `.claude-plugin/plugin.json` loads as `<name>@skills-dir` with no install step. Turn it off with `claude plugin disable <name>@skills-dir`
- skills.sh install path for Claude Code: `.claude/skills/<skill-name>/` (project) or `~/.claude/skills/<skill-name>/` (global)
- Plugins are copied to a cache dir on install, so never hardcode absolute paths. Component paths in `plugin.json` are `./` paths relative to the plugin root; `${CLAUDE_PLUGIN_ROOT}` goes inside hook and MCP command strings and arguments
- Relative source paths (e.g. `./plugins/foo`) in marketplace.json only work with git-based distribution, not direct URL distribution
