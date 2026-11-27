# Report Template

Standard output template for skill audit reports. Copy and fill in values.

---

## Contents

- Full Report Structure
- Actionable Output Commands
  - Backup Commands
  - Auto-Consolidation Suggestions
  - Removal Commands
  - Installation Commands
  - Verification Steps

## Full Report Structure

```markdown
## Skill Inventory

- **Platform Detected:** [Platform Name]
- **Total Skills Found:** X
- **Estimated Token Overhead:** ~Y tokens
- **Marketplaces Used:** X (list them)

---

## User Profile Summary

- **Stack:** [Languages/Frameworks]
- **Workflow:** [Solo/Team/Enterprise]
- **Priority:** [Speed/Quality/Security]

---

## Marketplace Analysis (Claude Code)

| Plugin | Current Source | Type | Better Alternative | Action |
|--------|----------------|------|-------------------|--------|
| name | marketplace | Official/Endorsed/External/Custom | alternative or (none) | Replace/Keep |

**Legend:**
- Official = Made by Anthropic
- Endorsed = Third-party in official marketplace
- External = Third-party marketplace
- Custom = User's own

**Marketplace Cleanup Commands:**
```bash
# Replace external with official/endorsed
/plugin uninstall plugin-name@external-marketplace
/plugin install plugin-name@claude-plugins-official

# Remove redundant marketplace (if empty after cleanup)
/plugin marketplace remove marketplace-name
```

---

## Duplicates & Overlaps

| Skills | Overlap Type | Recommendation | Token Savings |
|--------|--------------|----------------|---------------|
| A, B   | Exact        | Remove B       | ~300          |

---

## Conflicts

| Skills | Issue | Severity | Action |
|--------|-------|----------|--------|
| A / B  | Opposing rules on X | High | Review |

---

## Health Report

| Skill | Fresh | Complete | Specific | Testable | Health |
|-------|-------|----------|----------|----------|--------|
| name  | 8     | 6        | 9        | 4        | 6.8    |

---

## Skill Scores

| Skill | Rel | Uniq | Qual | Eff | Use | **Score** | Tier |
|-------|-----|------|------|-----|-----|-----------|------|
| name  | 8   | 9    | 7    | 6   | 8   | **7.6**   | Useful |

---

## Recommendations

### Remove (Low Value)
1. `skill-name` — Reason, saves ~X tokens

### Consider Removing (Marginal)
1. `skill-name` — Reason

### Keep (Valuable)
1. `skill-name` — Why it's valuable

### Gaps Identified
1. Missing capability — Suggested skill to add

---

## Summary

- **Before:** X skills, ~Y tokens
- **After:** X skills, ~Y tokens
- **Savings:** Z tokens (N% reduction)
```

---

## Actionable Output Commands

### Backup Commands

Before making changes, backup current configuration:

**Gemini/Antigravity:**
```bash
cp -r .agent/skills .agent/skills.backup.$(date +%Y%m%d)
```

**Claude Code:**
```bash
cp -r .claude .claude.backup.$(date +%Y%m%d)
```

**Cursor:**
```bash
cp -r .cursor/rules .cursor/rules.backup.$(date +%Y%m%d)
```

### Auto-Consolidation Suggestions

When two skills have >70% capability overlap, offer a merge:

```markdown
**Merge Suggestion:** skill-a + skill-b -> skill-combined

**Shared Capabilities:**
- [capability 1]
- [capability 2]

**Unique to A:**
- [capability 3]

**Unique to B:**
- [capability 4]

**Proposed Action:** Generate merged SKILL.md draft
**Token Savings:** ~500 (30% reduction)
```

### Removal Commands

Provide exact commands for each removal:

```bash
# Remove skill: [skill-name]
rm -rf .agent/skills/[skill-name]

# Or for single-file skills:
rm .cursor/rules/[rule-name].md
```

### Installation Commands

**Gemini (via MCP skill-loader):**
```text
Use mcp_agent-skill-loader_install_skill with skill_name: "[skill-name]"
```

**Claude Code:**
```bash
claude plugins add [plugin-name]
```

**Manual:**
```bash
mkdir -p .agent/skills/[skill-name]
# Then create SKILL.md with appropriate content
```

### Verification Steps

After changes:

```text
1. List skills to confirm changes took effect
2. Test a sample prompt that would trigger the skill
3. Verify no errors in AI assistant startup
4. Confirm token reduction in context usage (if measurable)
```
