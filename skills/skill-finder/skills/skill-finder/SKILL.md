---
name: skill-finder
description: Finds new skills, plugins and MCP servers to install by searching GitHub and marketplaces. Use when the user asks to 'find a skill', 'discover plugins', 'search for an MCP', 'what plugins exist for X', 'is there a tool for X', 'fill my skill gaps', says they keep doing something by hand or checking it manually, or when Claude lacks a tool for the task. To audit skills already installed (duplicates, overlaps, conflicts), use skill-curator instead.
---

# Skill Finder

Proactively identify capability gaps and discover Claude Code plugins, skills, and MCP servers through targeted web searches. Recommend marketplace installations with exact commands.

---

## When to Use This Skill

### Explicit Triggers

- User says: "find a skill for X", "search for a plugin", "I need an MCP for Y"
- User says: "what plugins exist for X?", "is there a skill for Y?"
- User says: "fill my skill gaps", "what am I missing?", "improve my setup"

### Implicit Triggers (Proactive Gap Detection)

Recognize these situations and **proactively offer to search**:

| Situation | Example | Action |
|-----------|---------|--------|
| **Task beyond current skills** | User asks for Kubernetes help but no K8s skill | Offer: "I notice I don't have a K8s skill. Want me to search for one?" |
| **Repeated tool limitations** | Claude struggles with browser automation | Offer: "A browser automation plugin would help. Shall I find one?" |
| **Missing integrations** | User mentions Jira but no Jira MCP | Offer: "I could search for a Jira integration MCP" |
| **Complex domain tasks** | DAX, Terraform, GraphQL without skills | Offer: "There might be specialized skills for this domain" |

---

## Gap Detection Framework

### Step 1: Analyze Current Capability State

Before searching, assess what's already available:

```text
1. Check installed plugins: Read .claude/settings.json or .claude/settings.local.json
2. Check local skills: Glob for SKILL.md files
3. Check MCP servers: Read mcp.json or settings for "mcpServers"
4. Check CLAUDE.md: Any custom instructions?
```

### Step 2: Identify the Gap Category

| Gap Type | Indicators | Search Strategy |
|----------|------------|-----------------|
| **Language/Framework** | User working in unfamiliar stack | Search: "[language] claude code plugin" |
| **Tool Integration** | User mentions external service | Search: "[service] MCP server claude" |
| **Workflow** | User describes process Claude can't do | Search: "[workflow] claude code skill" |
| **Domain Knowledge** | Specialized field (finance, bio, etc.) | Search: "[domain] claude code plugin" |
| **Automation** | Repetitive task needs automation | Search: "[task] automation claude MCP" |

### Step 3: Formulate Search Strategy

For each gap, create targeted searches:

```text
Primary Search (GitHub-focused):
- "[capability] claude code plugin site:github.com"
- "[capability] MCP server site:github.com"
- "[capability] claude skills site:github.com"

Secondary Search (Broader):
- "[capability] claude code marketplace"
- "[capability] anthropic plugin"
- "awesome claude code [capability]"

MCP-Specific:
- "[service] MCP server"
- "model context protocol [capability]"
- "mcp-server-[service] github"
```

---

## Search Execution

### Primary Sources to Search

| Source | URL Pattern | What to Find |
|--------|-------------|--------------|
| **GitHub Topics** | `github.com/topics/claude-code` | Community plugins |
| **GitHub Search** | `github.com/search?q=claude+code+plugin` | All repos |
| **Anthropic Official** | `github.com/anthropics/claude-plugins-official` | Official/Endorsed |
| **MCP Registry** | `github.com/topics/mcp-server` | MCP servers |
| **Awesome Lists** | Search "awesome claude code" | Curated collections |
| **npm Registry** | `npmjs.com/search?q=mcp-server` | Published MCPs |

### Search Query Templates

**For Skills/Plugins:**
```text
Search: "[need] claude code plugin github"
Search: "[need] skill claude anthropic"
Search: "claude-code [need] site:github.com"
```

**For MCP Servers:**
```text
Search: "[service] MCP server github"
Search: "mcp-server-[service]"
Search: "[service] model context protocol"
```

**For Marketplaces:**
```text
Search: "claude code marketplace [category]"
Search: "claude plugins official [need]"
```

---

## Search Execution Protocol

### Step 1: Execute Web Search

Use WebSearch or mcp__tavily__tavily_search:

```text
Query: "[specific need] claude code plugin github"
Focus: site:github.com for code repositories
Timeframe: Recent (prefer actively maintained)
```

### Step 2: Evaluate Results

For each result, extract:

| Field | What to Look For |
|-------|------------------|
| **Repository** | Full GitHub URL |
| **Stars** | Popularity indicator (>10 = decent, >100 = popular) |
| **Last Update** | Activity (<6 months = active) |
| **Install Method** | How to install (marketplace, manual, npm) |
| **Plugin Type** | Skill, Agent, Command, Hook, or MCP |

### Step 3: Verify Compatibility

Before recommending, check:

```text
1. Is it for Claude Code specifically? (not Claude.ai or API)
2. Does it have a plugin.json or SKILL.md?
3. Is it in the official marketplace already?
4. Are there known issues or deprecation notices?
```

---

## Result Presentation Format

### Discovery Report

```markdown
## 🔍 Skill/Plugin Discovery Results

**Search Query:** [what you searched for]
**Gap Identified:** [capability that's missing]

---

### Found Options

#### Option 1: [Plugin Name] ⭐ Recommended
- **Source:** [GitHub URL]
- **Stars:** ⭐ [count] | **Updated:** [date]
- **Type:** [Plugin/MCP/Skill]
- **Capabilities:** [what it does]
- **Install Command:**
  ```bash
  # If in official marketplace:
  claude mcp add [name]

  # If external marketplace:
  claude plugins add [name]@[marketplace]

  # If manual install:
  git clone [url] ~/.claude/plugins/[name]
  ```

#### Option 2: [Alternative]
- **Source:** [URL]
- **Why Consider:** [unique features]
- **Install:** [command]

---

### No Plugin Found?

If no suitable plugin exists:
1. **DIY Option:** Create a custom SKILL.md for this capability
2. **Request:** Open an issue on claude-plugins-official
3. **Workaround:** [alternative approach without plugin]
```

---

## MCP Server Discovery

### MCP-Specific Search

When looking for MCP servers:

```text
1. Search GitHub: "mcp-server-[service]" or "[service] MCP"
2. Check npm: npm search mcp-server-[service]
3. Check official MCP registry: github.com/anthropics/mcp-servers
```

### MCP Result Format

```markdown
## 🔌 MCP Server Discovery

**Service Needed:** [e.g., Notion, Slack, PostgreSQL]

### Found MCP Servers

#### [mcp-server-name]
- **Repository:** [GitHub URL]
- **npm Package:** [if available]
- **Capabilities:**
  - [tool 1]
  - [tool 2]
- **Install:**
  ```bash
  # Add to .mcp.json or settings:
  {
    "mcpServers": {
      "[name]": {
        "command": "npx",
        "args": ["-y", "[package-name]"],
        "env": {
          "API_KEY": "${[SERVICE]_API_KEY}"
        }
      }
    }
  }
  ```
- **Required Env Vars:** [list any needed]

### Official MCP Servers

Check: https://github.com/anthropics/mcp-servers
- filesystem, git, github, gitlab, google-drive, postgres, sqlite, slack, memory, fetch, brave-search, puppeteer, sequential-thinking
```

---

## Marketplace Priority

When multiple options exist, recommend in this order:

| Priority | Source | Trust Level | Recommendation |
|----------|--------|-------------|----------------|
| 1 | `@claude-plugins-official` (Anthropic) | Highest | **Strong recommend** |
| 2 | `@claude-plugins-official` (Endorsed) | High | **Recommend** |
| 3 | Official MCP servers (Anthropic) | High | **Recommend** |
| 4 | Popular GitHub repos (>100 stars) | Medium | Consider |
| 5 | Active GitHub repos (<6mo update) | Medium | Consider |
| 6 | New/unverified repos | Low | Use caution |

---

## Proactive Gap Detection Examples

### Example 1: Browser Automation Gap

```text
User: "I need to scrape data from this website"

Claude thinks: "I don't have browser automation capability"

Claude responds:
"I can help with web scraping. However, I notice I don't currently have
browser automation tools. Let me search for a suitable plugin...

[Executes search: "browser automation claude code plugin github"]

Found: playwright@claude-plugins-official (Microsoft, Endorsed)
- Full browser control, screenshots, PDF generation
- Install: `claude mcp add playwright`

Shall I help you install this?"
```

### Example 2: Database Integration Gap

```text
User: "Query my PostgreSQL database for user stats"

Claude thinks: "No PostgreSQL MCP configured"

Claude responds:
"I'd need database access for this. Let me find a PostgreSQL MCP server...

[Executes search: "postgresql MCP server github"]

Found: mcp-server-postgres (Official)
- Direct SQL queries, schema inspection
- Install: Add to .mcp.json with your connection string

Would you like the setup instructions?"
```

### Example 3: Domain Skill Gap

```text
User: "Help me write complex DAX measures for Power BI"

Claude thinks: "DAX is specialized - likely skills exist"

Claude responds:
"DAX has specific patterns and gotchas. Let me check if there are
specialized skills for this...

[Executes search: "DAX power bi claude code skill github"]

Found: dax plugin with writing-dax-measures skill
- SQLBI patterns, performance optimization
- Install: Add to your plugins directory

This would give me DAX-specific knowledge. Want me to help install it?"
```

---

## Search Result Evaluation Criteria

### Quality Signals (Good)

| Signal | Indicator |
|--------|-----------|
| ⭐ Popular | >50 GitHub stars |
| 🔄 Active | Updated within 6 months |
| 📚 Documented | Has README with examples |
| ✅ Tested | Has tests or CI/CD |
| 🏷️ Versioned | Semantic versioning |
| 📦 Published | On npm/marketplace |

### Warning Signals (Caution)

| Signal | Indicator |
|--------|-----------|
| ⚠️ Stale | No updates >1 year |
| ⚠️ Undocumented | No README or sparse docs |
| ⚠️ No stars | 0-5 stars (unverified) |
| ⚠️ Archived | Repository archived |
| ⚠️ Security | No security policy, hardcoded secrets |

---

## Common Gap Categories & Search Terms

### Development Tools

| Gap | Search Terms |
|-----|--------------|
| TypeScript | "typescript claude code", "typescript-lsp" |
| Python | "python claude code", "pyright-lsp" |
| Testing | "testing claude plugin", "playwright", "jest" |
| Git workflow | "git claude code", "commit-commands" |
| Code review | "code review claude", "pr-review-toolkit" |

### Integrations

| Gap | Search Terms |
|-----|--------------|
| GitHub | "github MCP server", "github claude" |
| Slack | "slack MCP", "slack integration claude" |
| Notion | "notion MCP server" |
| Jira | "jira MCP", "atlassian claude" |
| Database | "[db-name] MCP server" |

### Specialized Domains

| Gap | Search Terms |
|-----|--------------|
| Data Engineering | "data engineering claude", "dbt skill" |
| DevOps | "kubernetes claude", "terraform plugin" |
| ML/AI | "machine learning claude skill" |
| Finance | "finance claude plugin", "trading MCP" |

---

## Post-Discovery Actions

### After Finding a Plugin

1. **Verify compatibility** with user's Claude Code version
2. **Check dependencies** (Node.js version, npm packages)
3. **Review permissions** the plugin needs
4. **Offer install command** with exact syntax
5. **Explain capabilities** the plugin adds

### Installation Guidance

```markdown
## Installation Options

### Option A: Official Marketplace
```bash
# For official/endorsed plugins
claude mcp add [plugin-name]
```

### Option B: External Marketplace
```bash
# For third-party marketplaces
claude plugins add [name]@[marketplace-url]
```

### Option C: Manual Install
```bash
# Clone to plugins directory
git clone [repo-url] ~/.claude/plugins/[name]

# Or for MCP servers, add to .mcp.json:
{
  "mcpServers": {
    "[name]": { ... }
  }
}
```
```

---

## Integration with Skill Curator

After installing new plugins, recommend running `skill-curator`:

```text
"New plugin installed! Run /skill-curator to:
- Verify it doesn't conflict with existing skills
- Check for duplicates you can now remove
- Update your skill health report"
```

---

## Important Rules

1. **ALWAYS search before saying "I can't do X"** — a plugin might exist
2. **ALWAYS prefer official/endorsed** over external alternatives
3. **ALWAYS verify recency** — don't recommend abandoned repos
4. **ALWAYS provide install commands** — exact, copy-pasteable
5. **ALWAYS check if already installed** before recommending
6. **NEVER recommend plugins with security red flags**
7. **NEVER install without user confirmation**
8. **OFFER proactively** when you recognize capability gaps
9. **EXPLAIN what the plugin adds** before recommending install
10. **SEARCH GitHub specifically** — 99% of results will be there
