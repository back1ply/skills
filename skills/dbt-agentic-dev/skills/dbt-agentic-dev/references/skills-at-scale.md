# dbt agentic dev: layered context, skill libraries, platforms and tools

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10), plus the dbt-labs GitHub repos (checked 2026-10-26). Vendor and product details are as presented. Check current docs before relying on them.

## Contents
- Layered context (Riot)
- Team skill libraries (Zendesk)
- Skill structure that survives model upgrades
- Internal AI platform niches (Ramp)
- dbt tooling for agents

## Layered context (Riot)

Watch: [0:08:00](https://youtu.be/txI6XKFxguo?t=480)

| Layer | Holds | Built by | Changes |
|---|---|---|---|
| System prompt / harness | Persona, tools, how to self-correct | Platform engineers | Rarely |
| Injected skills (playbooks) | Warehouse standards: YAML rules, naming, schema contracts, per-layer expectations (e.g. silver: naming, primary key constraints, left joins only, never cross join) | Engineers and analysts together | Per standard change |
| Task prompt | One sentence of intent ("model for each player's top three champion masteries") | Analyst | Every request |

Nobody re-explains standards per request. "Encode the rules → playbook → activate with a specific prompt." A plain "never cross join" in the skill was enough in practice. Add warehouse-side query limits if you need a hard stop ([0:27:06](https://youtu.be/txI6XKFxguo?t=1626)).

## Team skill libraries (Zendesk)

Watch: [0:17:01](https://youtu.be/n7aBWe4RB4k?t=1021)

- **Skill sprawl** is the enterprise problem: every developer writes their own.
- **One central repo** (their "ZDP AI Skills Library") is both the contribution path and the distribution path. Each workflow ships as a **plugin**, so using a colleague's workflow is one install in the terminal ([0:19:03](https://youtu.be/n7aBWe4RB4k?t=1143)).
- **Maintenance in three layers** ([0:20:06](https://youtu.be/n7aBWe4RB4k?t=1206)):
  - *Review*: a small set of approvers merges PRs to the library.
  - *Governance*: tags for maturity, value and distributability ("certified" vs "community").
  - *Evals*: run the new skill in a sandbox against sandbox data, a human scores the result, and the score goes back in the repo. Approvers merge only after looking at eval results.
- **Observability**: a skills explorer showing contributions, invocations, community vs certified skills.
- **The harness is the platform offering**: "the car without the engine". Developers get tools, skills and MCP servers pre-packaged, and plug in any model ([0:23:07](https://youtu.be/n7aBWe4RB4k?t=1387)).
- DocuSign's version: one master orchestration markdown plus team sub-skills, under governance.

## Skill structure that survives model upgrades

Watch: [Zendesk 0:27:04](https://youtu.be/n7aBWe4RB4k?t=1624)

Every skill follows the same declared shape: **name, description, actions, what to do, what not to do, what to expect**. Their view: inconsistent results across model versions usually trace back to badly structured skills. Standardize the declaration and the test artifacts, then compare models apples to apples. Current frontier models are "more than enough" for most data engineering, so own the harness and skills, not the intelligence.

## Internal AI platform niches (Ramp)

Watch: [0:09:02](https://youtu.be/Di8R8dlwpxA?t=542)

One tool per niche, like the modern data stack:

| Niche | Ramp's tool | Notes |
|---|---|---|
| Remote coding agent platform | Inspect | Jira-like board where each ticket is an agent session. Spawns an open-source coding agent in a sandbox VM with any repo's image. Triggered from chat or Slack ("Inspect fix this"). Custom agents and schedules. Passed 1M sessions, per the video ([0:12:03](https://youtu.be/Di8R8dlwpxA?t=723)) |
| Data agent | Ramp Research | **A configuration inside the remote agent platform**, not a separate product. Can reach Snowflake, Postgres and more. They're considering "data as an MCP" instead |
| Desktop agent app | Glass | Preinstalled by IT and pre-connected to internal systems. Per-department markdown context injected into every session, for people who don't work in a repo ([0:16:01](https://youtu.be/Di8R8dlwpxA?t=961)) |
| Internal apps | Ramplify | Easy hosting led to about 3 apps per employee. Most are unused and torn down. Apps work best as artifacts to hand to someone |
| Dashboards | WaveDash | Dashboards as SQL files in a repo, rendered as markdown for agents, vibe-codable, CI plus a review agent. Anyone can merge a change to one dashboard ([0:19:03](https://youtu.be/Di8R8dlwpxA?t=1143)) |

Also: agent traces (to analyze transcripts) and enterprise search. Principles: no single-lab lock-in (a model picker everywhere); make context first, worry about a context platform later ([0:23:09](https://youtu.be/Di8R8dlwpxA?t=1389)); build a culture of prose review like code review ([0:08:01](https://youtu.be/Di8R8dlwpxA?t=481)).

## dbt tooling for agents

- **[dbt-labs/dbt-mcp](https://github.com/dbt-labs/dbt-mcp)**: MCP server for dbt (lineage, node details, running dbt commands, semantic layer, discovery).
- **[dbt-labs/dbt-agent-skills](https://github.com/dbt-labs/dbt-agent-skills)**: in Claude Code, `/plugin marketplace add dbt-labs/dbt-agent-skills` then `/plugin install dbt@dbt-agent-marketplace` (plus `dbt-migration`). Skills include using-dbt-for-analytics-engineering, running-dbt-commands, adding-dbt-unit-test, building-dbt-semantic-layer, using-dbt-state, working-with-dbt-mesh, troubleshooting-dbt-job-errors, configuring-dbt-mcp-server. DocuSign customized the run-commands skill to avoid full rebuilds.
- **dbt v2 / Fusion**: static compile against the warehouse catalog (level 2 feedback), plus the VS Code extension and language server.
- **dbt Wizard** ([talk](https://www.youtube.com/watch?v=Cn_RhdpeX9U)): a dbt-specific agent on three surfaces: the dbt platform (Studio IDE and a standalone workspace, plus an "explore" mode for read-only business users), a CLI (works on dbt v1 or v2 without a platform account), and a desktop app (private preview at the talk; parallel threads, forking a conversation, panes for lineage, queries, charts and CI). Its harness is a fork of Codex, per the speakers (2026-10), and supports skills, MCP and bring-your-own-key. Why use it over a general agent, per the speakers: comes ready to use, dbt-specific tools (lineage search, warehouse drivers), and it can steer harder toward dbt work than a general tool ([0:34:02](https://youtu.be/Cn_RhdpeX9U?t=2042)). Even so, it adapts to each project's own conventions rather than forcing one style. Use AGENTS.md or CLAUDE.md to enforce yours.
