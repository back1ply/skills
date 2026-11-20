---
name: skill-curator
description: Audits the skills already installed in Claude Code, Gemini, Cursor, Copilot, Windsurf or a custom setup. Finds duplicates, overlaps, conflicts and gaps, and recommends what to remove, merge or fix. Use when the user asks to 'review installed skills', 'audit my skills', 'find duplicate skills', 'detect skill overlaps', 'optimize skills' or 'troubleshoot skill conflicts'. To search for new skills to install, use skill-finder instead.
---

# Skill Curator

A comprehensive skill auditing system for AI coding assistants. Automatically discover, analyze, and optimize skills across any platform.

## Supported Platforms

| Platform | Skill Locations | Config Format |
|----------|-----------------|---------------|
| **Gemini CLI** | `.gemini/skills/`, `~/.gemini/skills/` | `SKILL.md` + JSON |
| **Claude Code** | `.claude/`, plugins, `CLAUDE.md` | Markdown + JSON |
| **Cursor** | `.cursor/rules/`, `.cursorrules` | Markdown |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown |
| **Windsurf** | `.windsurfrules`, `.codeium/` | Markdown |
| **Custom** | User-specified paths | Various |

---

## Marketplace Preference Hierarchy (Claude Code)

When analyzing Claude Code plugins, always prefer official sources over third-party alternatives.

| Priority | Type | Source | Trust Level |
|----------|------|--------|-------------|
| 1. Official | Made by Anthropic | `@claude-plugins-official` | Highest |
| 2. Endorsed | Third-party in official marketplace | Listed in `marketplace.json` | High |
| 3. External | Third-party marketplaces | Other `@marketplace` sources | Medium |
| 4. Custom | User's own plugins | Local/personal repos | User-managed |

**Preference Rules:**

1. If official alternative exists, recommend replacing external with official
2. If endorsed alternative exists, recommend replacing external with endorsed
3. If duplicate across marketplaces, keep the higher-priority source
4. If no official/endorsed equivalent, keep external (note it in report)

Fetch the authoritative list from: `https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json`

For full marketplace listings, identification methods, and overlap resolution rules, see **`references/marketplace-reference.md`**.

---

## Phase 0: Quick Start Mode

Offer analysis depth at the start:

```text
Quick or Full Analysis?

[Q] Quick: Auto-detect everything, use smart defaults (2 min)
[F] Full: Complete profile questionnaire + deep analysis (5 min)
```

### Quick Mode: Auto-Profile from Workspace

Detect automatically instead of asking questions:

| Detection | Files to Check | Inference |
|-----------|----------------|-----------|
| **Tech Stack** | `package.json`, `requirements.txt`, `*.csproj`, `go.mod`, `Cargo.toml` | Primary language/framework |
| **Workflow** | `.github/`, `.gitlab-ci.yml`, `CODEOWNERS` | Solo vs team indicators |
| **Priority** | Existing skill categories | Security skills = security priority |
| **Platform** | `.agent/`, `.claude/`, `.cursor/` | AI assistant in use |

**Quick Mode Weights:** Relevance 35%, Uniqueness 25%, Quality 20%, Efficiency 15%, Usage 5%

---

## Phase 1: User Profile Discovery

> Skip in Quick mode.

Gather these four data points to personalize recommendations:

1. **Tech Stack** — Primary languages/frameworks (Python/FastAPI, TypeScript/React, Go, Rust, etc.)
2. **Workflow Type** — Solo developer, small team (2-5), or large team/enterprise
3. **AI Usage Priorities** — Rank: Speed, Quality, Security
4. **Primary Use Cases** — Writing code, code review, debugging, testing, documentation, planning

---

## Phase 2: Automated Discovery

### Step 1: Detect Platform

Check for platform indicators in this order:

```text
1. .gemini/skills/    -> Gemini CLI
2. .claude/           -> Claude Code
3. .cursor/           -> Cursor
4. .github/copilot-*  -> GitHub Copilot
5. .windsurfrules     -> Windsurf
6. Ask user           -> Custom/Unknown
```

### Step 2: Scan Skill Directories

Execute discovery based on detected platform:

**Gemini CLI:** Scan `.gemini/skills/**/SKILL.md` and `~/.gemini/skills/**/SKILL.md`, check MCP server configurations, parse each SKILL.md frontmatter.

**Claude Code:** Scan `.claude/settings.json` for plugins, check `CLAUDE.md` files, parse plugin manifests, fetch official `marketplace.json` for source classification, classify each plugin as Official/Endorsed/External/Custom.

**Cursor:** Scan `.cursor/rules/*.md` and `.cursorrules` in project root.

**Copilot/Windsurf:** Scan instruction files in standard locations, parse markdown content for capability definitions.

### Step 3: Build Skill Inventory

```markdown
| # | Skill Name | Source | Description | Est. Tokens |
|---|------------|--------|-------------|-------------|
| 1 | skill-name | path   | description | ~500        |
```

---

## Analysis Phases

After discovery, run these analysis phases in order:

1. **Deep Skill Analysis** — Read full skill content, extract trigger keywords, anti-patterns, dependencies, token estimates, and complexity scores
2. **Semantic Similarity** — Extract capability signatures (`[Actions] x [Domains]`), detect overlaps (exact duplicate, superset, partial, complementary), group by semantic category
3. **Conflict Detection** — Find contradictions between skills (opposing rules, style clashes, trigger conflicts, version conflicts)
4. **Weighted Scoring** — Calculate composite score per skill: Relevance (30%), Uniqueness (25%), Quality (20%), Efficiency (15%), Usage (10%)
5. **Dependency Mapping** — Map requires/enhances/conflicts/MCP relationships, identify orphans, critical nodes, broken dependencies

For detailed methodology, scoring tables, and detection methods, see **`references/analysis-methodology.md`**.

For the standard report output template, see **`references/report-template.md`**.

---

## Operational Rules

- Offer Quick vs Full mode at the start of every audit
- Use automated discovery — never ask users to paste configuration
- Calculate semantic overlap, not just name matching
- Check for conflicts between skill rules
- Provide weighted scores with justification
- Give exact commands, not vague instructions
- Show dependency relationships for critical skills
- Never recommend removing a skill without understanding the user's workflow
- Never assume platform — detect or ask
- Ask about tech stack before stack-specific recommendations
- Prioritize removing high-token duplicates over low-token unique skills
- Consider that some overlap is intentional (tiered tools for different contexts)
- Prefer official/endorsed plugins over external alternatives (Claude Code)
- Fetch the official marketplace.json to identify endorsed plugins
- Recommend replacing external plugins when official/endorsed equivalent exists

---

## Example Workflow

**Scenario:** Gemini user, Python/FastAPI stack, solo developer, quality-focused

**Discovery finds:** 3 code review skills (similar), 2 Python skills (both relevant), 1 JavaScript testing skill (wrong stack), 1 planning skill (unique)

**Result:** Remove 3 skills (2 duplicate code reviewers + wrong-stack JS skill), save ~800 tokens, 43% reduction. Keep best code reviewer, both Python skills (complementary), and unique planning skill.

---

## Reference Files

For detailed methodology, templates, and extended references:

- **`references/analysis-methodology.md`** — Deep analysis, semantic similarity, conflict detection, weighted scoring, and dependency mapping methodology
- **`references/report-template.md`** — Standard audit report template with backup commands, consolidation suggestions, and verification steps
- **`references/marketplace-reference.md`** — Complete official/endorsed plugin listings, identification methods, replacement lookup, and overlap resolution rules
- **`references/portfolio-templates.md`** — Recommended skill sets by developer role (Python Data Scientist, TypeScript Full-Stack, Power BI/DAX, DevOps, Solo Generalist)
