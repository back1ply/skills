# Analysis Methodology

Detailed methodology for deep skill analysis, semantic similarity, conflict detection, and weighted scoring.

---

## Contents

- Phase 2.5: Deep Skill Analysis
- Phase 3: Semantic Similarity Analysis
- Phase 3.5: Conflict Detection
- Phase 4: Weighted Scoring System
- Phase 5.5: Dependency Mapping

## Phase 2.5: Deep Skill Analysis

Go beyond frontmatter — read the full skill content:

### Extraction Targets

| Extraction | How to Find | Purpose |
|------------|-------------|---------|
| **Trigger Keywords** | "When to Use", "Use when", "Use this skill" sections | Better activation matching |
| **Anti-Patterns** | "Never", "Don't", "Avoid", "Forbidden" sections | Conflict detection |
| **Dependencies** | Tool references, MCP mentions, "Requires" statements | Dependency graph |
| **Token Estimate** | `character_count / 4` | Accurate context sizing |
| **Complexity Score** | Count of phases, sections, rules, tables | Maintenance burden |
| **Examples Count** | Number of code blocks | Quality indicator |

### Complexity Scoring

| Metric | Low (1-3) | Medium (4-6) | High (7-10) |
|--------|-----------|--------------|-------------|
| **Phases/Sections** | 1-2 | 3-5 | 6+ |
| **Rules Count** | 1-3 | 4-8 | 9+ |
| **Code Examples** | 0-1 | 2-4 | 5+ |
| **Total Lines** | <100 | 100-300 | 300+ |

---

## Phase 3: Semantic Similarity Analysis

### Capability Extraction

For each skill, extract:

1. **Actions (Verbs):** What does it DO?
   - `review`, `generate`, `test`, `plan`, `debug`, `refactor`, `document`

2. **Domains (Nouns):** What does it OPERATE ON?
   - `code`, `tests`, `git`, `docs`, `architecture`, `security`, `performance`

3. **Capability Signature:** `[Actions] x [Domains]`
   - Example: `code-reviewer` = `[review] x [code]`
   - Example: `test-generator` = `[generate] x [tests]`

### Overlap Detection Matrix

Compare capability signatures:

| Overlap Type | Definition | Action |
|--------------|------------|--------|
| **Exact Duplicate** | Same actions AND same domains | Remove one |
| **Superset** | Skill A covers all of Skill B + more | Consider removing B |
| **Partial Overlap** | Some shared capabilities | Evaluate which is better |
| **Complementary** | Different actions OR different domains | Keep both |

### Semantic Grouping

Group skills by primary purpose:

| Category | Typical Actions | Typical Domains |
|----------|-----------------|-----------------|
| **Code Quality** | review, refactor, lint | code, style |
| **Testing** | generate, run, validate | tests, coverage |
| **Git/VCS** | commit, branch, merge | git, pr |
| **Planning** | plan, design, architect | architecture, tasks |
| **Documentation** | document, explain, summarize | docs, comments |
| **Security** | audit, scan, validate | security, auth |

---

## Phase 3.5: Conflict Detection

Beyond overlaps, detect **contradictions** between skills:

### Conflict Types

| Conflict Type | Example | Severity |
|---------------|---------|----------|
| **Opposing Rules** | Skill A: "Always use IFERROR" vs Skill B: "Never use IFERROR" | High |
| **Style Clashes** | Skill A: "Use snake_case" vs Skill B: "Use camelCase" | Medium |
| **Trigger Conflicts** | Both skills claim same activation phrase | Medium |
| **Version Conflicts** | Skill A targets Node 18, Skill B requires Node 20 | Medium |

### Detection Method

1. **Extract Rules:** Find all `ALWAYS`, `NEVER`, `MUST`, `DON'T`, `FORBIDDEN` statements
2. **Normalize Targets:** Extract the subject of each rule (function names, patterns, tools)
3. **Compare Polarity:** Match `ALWAYS X` against `NEVER X` patterns
4. **Score Confidence:** Higher confidence for explicit contradictions

---

## Phase 4: Weighted Scoring System

Calculate a composite score for each skill:

### Scoring Factors

| Factor | Weight | Score 0-10 | How to Assess |
|--------|--------|------------|---------------|
| **Relevance** | 30% | 0-10 | Match to user's tech stack |
| **Uniqueness** | 25% | 0-10 | No other skill provides this |
| **Quality** | 20% | 0-10 | Docs, examples, maintenance |
| **Efficiency** | 15% | 0-10 | Value per token |
| **Usage** | 10% | 0-10 | How often it's activated |

### Score Calculation

```text
Final Score = (Relevance x 0.30) + (Uniqueness x 0.25) +
              (Quality x 0.20) + (Efficiency x 0.15) + (Usage x 0.10)
```

### Health Indicators

| Metric | Score 0-10 | Assessment Method |
|--------|------------|-------------------|
| **Freshness** | 10 = <30 days old, 0 = >1 year | File modification date |
| **Completeness** | 10 = all sections, 0 = bare | Has examples, rules, anti-patterns |
| **Specificity** | 10 = focused, 0 = too broad | Single clear purpose vs kitchen sink |
| **Testability** | 10 = clear success criteria | Has verification/validation steps |

### Recommendation Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| 8-10 | Essential | Keep - high value |
| 6-7.9 | Useful | Keep unless cleanup needed |
| 4-5.9 | Marginal | Consider removing |
| 0-3.9 | Remove | Low value, remove |

---

## Phase 5.5: Dependency Mapping

Map relationships between skills:

### Dependency Types

| Type | Indicator | Example |
|------|-----------|---------|
| **Requires** | Skill mentions another by name | "Use the X skill first" |
| **Enhances** | Skill extends another's capability | "After code review, use this for..." |
| **Conflicts** | Mutually exclusive usage | "Don't use with skill Y" |
| **MCP Dependency** | Requires specific MCP server | "Requires powerbi-desktop-mcp" |

### Visual Dependency Graph

```text
skill-curator
    |  enhances
    v
writing-dax  <-- no-calculate-dax
    |  requires MCP
    v
powerbi-mcp
```

### Dependency Insights

| Status | Meaning | Action |
|--------|---------|--------|
| **Orphan** | No dependencies, not depended on | Safe to remove if low value |
| **Critical** | Many skills depend on this | Careful before removing |
| **Broken** | Depends on missing skill/MCP | Fix or remove |
| **Circular** | A depends on B depends on A | Refactor to break cycle |
