# Skills

29 agent skills in 27 plugins, for data work, dbt, code quality, and working with coding agents. Each plugin installs on its own.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Open_Standard-blue.svg)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet.svg)](https://code.claude.com/)

## Install

**Claude Code:** add the marketplace once, then install any plugin from the [catalog](#catalog) by name:

```
/plugin marketplace add back1ply/skills
/plugin install mcp-security@skills
```

**Any agent ([skills.sh](https://skills.sh)):**

```
npx skills add back1ply/skills
```

Add `-g` to install globally, or `-a claude-code` to target one agent.

**Running a skill:** installed as a plugin, a skill runs as `/<plugin>:<skill>` (for example `/quality-pass:quality-pass`). Installed with skills.sh, it runs as `/<skill>`. The plugin and skill names match except in `arjancodes-playbook` (skill: `design-patterns-pythonic`) and `designite-skills` (skills: `designite-java`, `designite-csharp`, `designite-python`).

## Catalog

### Data and BI

| Plugin | What it does |
|---|---|
| `writing-dax-measures` | Write, review, and debug DAX measures in Power BI and Analysis Services |
| `etl-pipeline-design` | Design, evaluate, and troubleshoot ETL/ELT pipelines |
| `kpi-checklists` | Define and implement KPIs, from strategy to a live dashboard |
| `data-storytelling` | Critique and build charts, slides, and data presentations around audience and message |
| `sqlserver-postgres-indexing` | Diagnose slow queries and design indexes on SQL Server and PostgreSQL |

### dbt

| Plugin | What it does |
|---|---|
| `dbt-agent-context` | Give AI agents the business context they need to answer questions over a dbt project |
| `dbt-agentic-dev` | Design and review agent workflows that write, test, and ship dbt models, from prompt to PR |
| `dbt-compute-cost` | Cut dbt warehouse spend and run time with dbt State, right-sizing, and v2 tooling |

### Code quality and design

| Plugin | What it does |
|---|---|
| `quality-pass` | One-command quality pass: sends each changed file to the best installed review skill ([see below](#quality-pass-works-best-with)) |
| `designite-skills` | Code smell analysis for Java, C#, and Python using open-source tools ([README](skills/designite-skills/README.md)) |
| `arjancodes-playbook` | Pythonic design patterns, clean architecture, typing, and testing (from ArjanCodes) |

### Working with coding agents

| Plugin | What it does |
|---|---|
| `agent-orchestration-checklist` | Hand big tasks to an orchestrator agent and judge the result without reading every line |
| `agentic-debugging` | Debug code nobody fully understands: facts vs hypotheses, controls, and elimination |
| `agentic-review-loop` | Run and measure a team AI code review loop with a per-reviewer scorecard |
| `impatient-programming` | XP's 29 rules rewritten for teams building with coding agents (CC BY 4.0, [README](skills/impatient-programming/README.md)) |
| `humanitys-last-prompt-engineer` | Prompt engineering techniques, role templates, and scoring frameworks |
| `improve-system` | Review your setup, capture learnings, audit for rot, and recap sessions |
| `channel-artifact` | Create shareable Claude Code channel artifacts with live web UIs |

### Backend, infrastructure, and security

| Plugin | What it does |
|---|---|
| `go-observability` | Logs, metrics, alerts, profiles, and traces for Go services |
| `server-capacity-tuning` | Find what limits a small server's capacity and pick the fixes that raise it |
| `mcp-security` | Review and harden MCP servers, clients, and agent tool setups (OWASP MCP Top 10) |

### Business

| Plugin | What it does |
|---|---|
| `saas-ai-moats` | Score how well a SaaS business can survive AI: 10 attacks and 8 moats that still work |

### Making and managing skills

| Plugin | What it does |
|---|---|
| `youtube-to-skill` | Turn YouTube videos, playlists, or channels into skills, or answer questions about a video |
| `article-to-skill` | Turn articles, blog posts, and docs pages into skills, or answer questions about an article |
| `skill-finder` | Find and activate the right skill for a task |
| `skill-curator` | Audit, improve, and maintain a skill library |
| `skill-publisher` | Package a skill repo for the Claude Code marketplace and skills.sh, then open a PR |

### quality-pass: works best with

`quality-pass` works alone with built-in checks, and does more with these installed:

```
npx skills add amElnagdy/guard-skills -g                    # test-guard, clean-code-guard, docs-guard
/plugin install mattpocock-skills@claude-plugins-official   # tdd, codebase-design, improve-codebase-architecture
```

The full list is in its `SKILL.md`.

## Sources

Some skills are distilled from talks and articles. The source text is kept in `data/` (never installed) so each skill can be checked against it. That text belongs to its authors, so check their terms before reusing it.

<details>
<summary>Skills made from videos</summary>

Built with `youtube-to-skill`. Transcripts are in `data/raw/<id>.json`. Regenerate this table with `uv run skills/youtube-to-skill/skills/youtube-to-skill/scripts/sources.py --readme README.md --marker video-skills`.

<!-- video-skills:start -->
| Skill | What it does | Sources |
|---|---|---|
| `agent-orchestration-checklist` | Checklist for handing big coding tasks to an orchestrator agent that spins up sub-agents (Claude Code, Codex) and judging the result without reading all the code, using Maximilian Schwarzmüller's five developer skills for the AI era (judgment, orchestration, ownership, broad expertise, curiosity). | [What I would focus on](https://www.youtube.com/watch?v=I6V5dmoZplU) |
| `dbt-agent-context` | Designs and maintains the business context AI agents need to answer questions over a dbt project correctly, using patterns from dbt Summit 2026 (Okta, Checkr, Green Dot, LangChain, Nordstrom, Anaconda, Recruit, AlphaSense, dbt Labs/Fivetran). | [From AI experiment to production: how Okta governs context for agents at scale](https://www.youtube.com/watch?v=SEgoqvU8Zrs)<br>[Is context engineering the new analytics engineering?](https://www.youtube.com/watch?v=rnLMk-GRx7Y)<br>[Meta:Context: a business context schema in dbt Semantic Layer](https://www.youtube.com/watch?v=vuXqA_vNssw)<br>[Governed by default: how data teams at Nordstrom turn dbt governance into an AI advantage](https://www.youtube.com/watch?v=wVXGX58Znts)<br>[YAML doesn't know why: building the business context your agents are missing](https://www.youtube.com/watch?v=PitSWUhaLP4)<br>[No drift allowed: LangChain's context playbook with Hex](https://www.youtube.com/watch?v=2yJxBnldB5A)<br>[Don't ship what you can't measure: Evaluation-driven development for AI analytics agents](https://www.youtube.com/watch?v=sCqjOmH_0Tg)<br>[Beyond semantic models: "Domain context as code" for high-accuracy text-to-SQL](https://www.youtube.com/watch?v=4gFcivfHR3A)<br>[AlphaSense scales AI on enterprise data with dbt-first governance and context from Euno](https://www.youtube.com/watch?v=TgUeC1LWc7o)<br>[With great context comes great autonomy: leveling up your agent context](https://www.youtube.com/watch?v=Ehm6_yfc7RE)<br>[From analytics engineering to context engineering in 4 minutes](https://www.youtube.com/watch?v=AN68dnWqhmk) |
| `dbt-agentic-dev` | Designs and reviews AI-agent workflows that write, test and ship dbt models (prompt to validated PR), using patterns from dbt Summit 2026 (Careem, Riot Games, DocuSign, Zendesk, Nordstrom, Ramp, dbt Wizard). | [From prompt to PR: sandbox-validated dbt changes before human review](https://www.youtube.com/watch?v=6BPrk0LBl3o)<br>[When skills meet scale: an agent assembly line for dbt](https://www.youtube.com/watch?v=txI6XKFxguo)<br>[AI-augmented analytics engineering at DocuSign: dbt v2, dbt MCP, and agent skills](https://www.youtube.com/watch?v=RQ97J3IccX0)<br>[AI-powered data development: How agentic SDLC & dbt-MCP transformed our data engineering workflow](https://www.youtube.com/watch?v=n7aBWe4RB4k)<br>[dbt Wizard: your AI teammate for data development](https://www.youtube.com/watch?v=Cn_RhdpeX9U)<br>[Ramp's internal AI stack: agents, sandboxes, and an AI-first BI tool](https://www.youtube.com/watch?v=Di8R8dlwpxA)<br>[Governed by default: how data teams at Nordstrom turn dbt governance into an AI advantage](https://www.youtube.com/watch?v=wVXGX58Znts)<br>[From dbt Core to dbt v2: How CarGurus unlocked dbt State and AI at scale](https://www.youtube.com/watch?v=yqCrNVFzLg8) |
| `dbt-compute-cost` | Cuts dbt warehouse spend and run time and speeds up the dev loop, using results from dbt Summit 2026 (RxBenefits, dbt Labs, Virgin Media O2, CarGurus, KOHO, WMCHealth, Espresso AI). | [Optimizing your runs for lower compute, fresher data, and faster iteration with dbt State](https://www.youtube.com/watch?v=3VWBjDq8yp4)<br>[Reduce, reuse, recycle: how dbt State cut rebuilds by 92% at RxBenefits](https://www.youtube.com/watch?v=Yn-UXiMvZ4I)<br>[What changes when 300 dbt users at Virgin Media O2 move to dbt v2 and dbt State](https://www.youtube.com/watch?v=bPZHJ47MpWo)<br>[From dbt Core to dbt v2: How CarGurus unlocked dbt State and AI at scale](https://www.youtube.com/watch?v=yqCrNVFzLg8)<br>[Most of your dbt models aren't in a hurry: How to stop paying for the whole DAG](https://www.youtube.com/watch?v=9WB2aT_xCUE)<br>[From 72 minutes to 5: how one environment variable powers two dbt pipelines](https://www.youtube.com/watch?v=hGGS2Et4BIc)<br>[Getting instant feedback: The dbt v2-powered dbt developer experience](https://www.youtube.com/watch?v=81T3CTclWOw)<br>[Scaling dbt on Amazon Redshift: KOHO cut transformation runtime 70% without rewriting a single model](https://www.youtube.com/watch?v=C05o-rKXZ44) |
| `go-observability` | Reviews and builds observability for Go services (logs, metrics, alerts, profiles, traces) using Jonathan Hall's Boot.dev course. | [Logging & Observability Full Course (Prometheus, Grafana, OpenTelemetry)](https://www.youtube.com/watch?v=jhS_VD247Qo) |
| `mcp-security` | Reviews and hardens MCP (Model Context Protocol) servers, clients, and agent tool setups using the lethal trifecta and the OWASP MCP Top 10. | [MCP Security Fundamentals Course](https://www.youtube.com/watch?v=gYXLRMycVMk) |
| `saas-ai-moats` | Scores how well a SaaS business can survive AI, using Rob Walling's 10 AI attacks (6 supply-side, 4 demand-side) and the 8 moats that still work when code is nearly free (trusted by buyers, system of record, allowed to act, output nobody checks, official approval, everyone's in it, learning loop, hard to keep running). | [The Only SaaS Moats Left in 2026](https://www.youtube.com/watch?v=KpILHX2D-AA) |
| `server-capacity-tuning` | Finds what limits how many users a single small server can handle (CPU, memory, file descriptors, disk sync, or the load generator itself) and picks the optimizations that raise it, using results from the $12 Server Challenge (about 30 web servers on 1 vCPU / 2 GB with SQLite). | [I Asked Developers to Max Out a $12 Server (again)](https://www.youtube.com/watch?v=-BFt49ula08) |
| `sqlserver-postgres-indexing` | Diagnoses slow queries and designs indexes on Microsoft SQL Server and PostgreSQL by thinking like the engine (8K pages, clustered tables vs Postgres heaps, seeks/scans, key lookups, reads as the unit of work), and explains how the two engines differ on plans, updates, locking/MVCC, hints and tooling. | [How to Think Like the Engine: SQL Server & PostgreSQL Edition](https://www.youtube.com/watch?v=ZV37v2pHaW8) |
<!-- video-skills:end -->

</details>

<details>
<summary>Skills made from articles</summary>

Built with `article-to-skill`. Article text is in `data/articles/<id>.json`. Regenerate this table with `uv run skills/article-to-skill/skills/article-to-skill/scripts/sources.py --readme README.md`.

<!-- articles:start -->
| Skill | What it does | Sources |
|---|---|---|
| `agentic-debugging` | Debugs code nobody on hand fully understands (agent-written, unfamiliar, or too large to read) by treating the bug as a constraint satisfaction problem, using Cindy Sridharan's two-tier framework (facts vs hypotheses), a control vs variable comparison, a hypotheses-by-fact matrix, progressive signal discovery, and elimination-only adversarial review. | [How to effectively debug when you no longer understand the code](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b) |
| `agentic-review-loop` | Sets up, runs and measures a team-wide AI code review loop where each developer fires their own review skill at pull requests, the author's agent answers every finding (fix, decline, refute), a human reviews last, and a scorecard rates each review skill on precision and depth, using Robin Wieruch's process and three weeks of numbers. | [Toward a Self-Improving Agentic Code Review Loop](https://www.robinwieruch.de/agentic-code-review-loop/) |
| `server-capacity-tuning` | Finds what limits how many users a single small server can handle (CPU, memory, file descriptors, disk sync, or the load generator itself) and picks the optimizations that raise it, using results from the $12 Server Challenge (about 30 web servers on 1 vCPU / 2 GB with SQLite). | [Challenge repo, batch-2 report](https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/main/benchmarks/batch-2.md) |
<!-- articles:end -->

</details>

## Contributing

Each plugin is a folder under `skills/`. That's why `skills` appears three times in a path like `skills/mcp-security/skills/mcp-security/SKILL.md`:

```
skills/                                  <- this repo (marketplace name: "skills")
├── .claude-plugin/marketplace.json      <- one entry per plugin; what /plugin install reads
├── skills/
│   └── <plugin>/                        <- one installable plugin
│       ├── .claude-plugin/plugin.json   <- name, description, keywords
│       └── skills/                      <- folder name Claude Code requires inside a plugin
│           └── <skill>/
│               ├── SKILL.md             <- what the agent loads
│               ├── references/          <- detail files, loaded on demand
│               └── scripts/             <- helper scripts, where needed
└── data/                                <- source text for the Sources tables; never installed
```

To add a skill: create `skills/<plugin>/` with `plugin.json` and `skills/<name>/SKILL.md`, add an entry to `.claude-plugin/marketplace.json`, and add a row to the matching [catalog](#catalog) table. skills.sh ignores the plugin layer and picks up every `SKILL.md`.

`.gitignore` ignores everything by default and lists what gets published, so other files at the repo root stay local.

## License

MIT (see [LICENSE](LICENSE)), except `impatient-programming`, which is CC BY 4.0 (see its [LICENSE](skills/impatient-programming/LICENSE) and [NOTICE](skills/impatient-programming/NOTICE.md)).
