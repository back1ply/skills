# Claude Code Official Marketplace Reference

> **Source:** `https://github.com/anthropics/claude-plugins-official`
> **Always fetch fresh data** — this list may be outdated

---

## Official Plugins (Made by Anthropic)

| Plugin | Category | Purpose |
|--------|----------|---------|
| typescript-lsp | LSP | TypeScript/JavaScript code intelligence |
| pyright-lsp | LSP | Python type checking |
| csharp-lsp | LSP | C# code intelligence |
| gopls-lsp | LSP | Go code intelligence |
| rust-analyzer-lsp | LSP | Rust code analysis |
| clangd-lsp | LSP | C/C++ code intelligence |
| php-lsp | LSP | PHP (Intelephense) |
| swift-lsp | LSP | Swift (SourceKit-LSP) |
| kotlin-lsp | LSP | Kotlin code intelligence |
| jdtls-lsp | LSP | Java (Eclipse JDT.LS) |
| lua-lsp | LSP | Lua code intelligence |
| pr-review-toolkit | Productivity | 6 specialized PR review agents |
| commit-commands | Productivity | Git commit/push/PR workflow |
| feature-dev | Development | Exploration + architecture agents |
| code-review | Productivity | Automated PR review |
| code-simplifier | Productivity | Code refinement |
| frontend-design | Development | Bold UI design |
| plugin-dev | Development | Plugin creation toolkit |
| claude-code-setup | Productivity | Codebase analysis |
| claude-md-management | Productivity | CLAUDE.md maintenance |
| security-guidance | Security | Security warnings |
| hookify | Productivity | Custom hooks via markdown |
| ralph-loop | Development | Iterative AI loops |
| agent-sdk-dev | Development | Agent SDK development |
| explanatory-output-style | Learning | Educational insights |
| learning-output-style | Learning | Interactive learning |

---

## Endorsed Plugins (Third-party in Official Marketplace)

| Plugin | Category | Purpose | Author |
|--------|----------|---------|--------|
| superpowers | Development | TDD, debugging, brainstorming, subagent dev | Jesse Vincent |
| context7 | Development | Up-to-date documentation lookup | Upstash |
| serena | Development | Semantic code analysis | Community |
| playwright | Testing | Browser automation | Microsoft |
| github | Productivity | GitHub API integration | GitHub |
| gitlab | Productivity | GitLab integration | GitLab |
| supabase | Database | Database/auth/storage | Supabase |
| firebase | Database | Google Firebase | Google |
| stripe | Development | Payments integration | Stripe |
| figma | Design | Design file integration | Figma |
| linear | Productivity | Issue tracking | Linear |
| asana | Productivity | Project management | Asana |
| atlassian | Productivity | Jira/Confluence | Atlassian |
| slack | Productivity | Team communication | Slack |
| notion | Productivity | Documentation | Notion |
| sentry | Monitoring | Error monitoring | Sentry |
| vercel | Deployment | Frontend deployment | Vercel |
| pinecone | Database | Vector database | Pinecone |
| greptile | Development | AI codebase search | Greptile |
| huggingface-skills | Development | ML models/datasets | HuggingFace |
| circleback | Productivity | Meeting/email context | Circleback |
| laravel-boost | Development | Laravel toolkit | Community |

---

## Quick Lookup: Finding Replacements

| If installed... | Replace with... |
|-----------------|-----------------|
| Any `*-browser` automation | `playwright@claude-plugins-official` |
| Any `superpowers` from external | `superpowers@claude-plugins-official` |
| Any docs lookup tool | `context7@claude-plugins-official` |
| Any code review tool | `pr-review-toolkit@claude-plugins-official` |
| Any git workflow tool | `commit-commands@claude-plugins-official` |

---

## No Official Alternative (Keep External)

These capabilities have **no official equivalent** — external plugins are acceptable:

- Advanced Python frameworks (Django/FastAPI agents)
- Data engineering patterns (Spark, dbt, Airflow)
- Comprehensive UI/UX design databases
- Business analytics / KPI dashboards
- Domain-specific skills (DAX, Power BI, etc.)

---

## Marketplace Identification

### How to Identify Plugin Source

Parse the plugin identifier format: `plugin-name@marketplace-name`

```text
pr-review-toolkit@claude-plugins-official  -> Official (Anthropic-made)
superpowers@claude-plugins-official        -> Endorsed (third-party, in official)
python-dev@some-other-marketplace          -> External (third-party marketplace)
my-skill@my-repo                           -> Custom (user's own)
```

### Identifying Official vs Endorsed

- **Official:** `author.name` = "Anthropic" AND `author.email` is on the `anthropic.com` domain
- **Endorsed:** Listed in marketplace but author is NOT Anthropic

### Overlap Resolution by Source

When two plugins have overlapping capabilities:

| Scenario | Action |
|----------|--------|
| Official vs External (same capability) | **Remove external**, keep official |
| Endorsed vs External (same capability) | **Remove external**, keep endorsed |
| Official vs Endorsed (same capability) | Keep official (unless endorsed is clearly superior) |
| External vs Custom (same capability) | User choice (ask or keep custom) |
