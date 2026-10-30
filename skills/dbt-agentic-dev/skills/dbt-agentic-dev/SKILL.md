---
name: dbt-agentic-dev
description: Designs and reviews AI-agent workflows that write, test and ship dbt models (prompt to validated PR), using patterns from dbt Summit 2026 (Careem, Riot Games, DocuSign, Zendesk, Nordstrom, Ramp, dbt Wizard). Covers sandbox validation loops, spec locking, structural guardrails vs prompt rules, layered context (harness, skills/playbook, task), phase-split multi-agent workflows, team skill libraries, and what humans must still review. Use when building or improving a Claude Code / Codex / dbt Wizard workflow for dbt development, wiring the dbt MCP server or dbt agent skills into an agent, letting analysts request models in plain English, reviewing AI-generated dbt PRs, or the user says "agentic SDLC", "agent writes dbt models", "prompt to PR", "AI data engineer", or "skill sprawl".
---

# dbt Agentic Dev

Distilled from 7 dbt Summit 2026 talks (dbt Labs channel, 2026-10). See Sources. Detail: [references/validation.md](references/validation.md) (feedback levels, sandbox isolation, review), [references/workflows.md](references/workflows.md) (end-to-end pipelines from each team), [references/skills-at-scale.md](references/skills-at-scale.md) (layered context, skill libraries, platforms, tools).

## Core mental model

"Any LLM can write code. Confidence to merge comes from end-to-end validation" ([Careem 0:05:14](https://youtu.be/6BPrk0LBl3o?t=314)). SQL generation was never the bottleneck. The bottlenecks are context switching, unwritten conventions, and reviewing work you didn't write ([DocuSign 0:04:08](https://youtu.be/RQ97J3IccX0?t=248), [Wizard 0:01:04](https://youtu.be/Cn_RhdpeX9U?t=64)).

The roles change ([Riot 0:06:12](https://youtu.be/txI6XKFxguo?t=372)): **analysts give the *what*** (metrics, business logic). **The agent does the *how*** (naming, tests, layering, boilerplate). **Engineers own the system**: playbooks, review gates, eval suites. Done right, model #200 costs tokens, not another sprint ([Riot 0:18:03](https://youtu.be/txI6XKFxguo?t=1083)). AI proposes; engineers stay accountable ([DocuSign 0:12:05](https://youtu.be/RQ97J3IccX0?t=725)).

## Workflow: build a prompt-to-PR system for dbt

1. **Pick one repeatable workflow** (new mart model, layer promotion, metric add), not the whole SDLC. Inventory its unwritten conventions first ([DocuSign 0:26:04](https://youtu.be/RQ97J3IccX0?t=1564)).
2. **Layer the context** ([Riot 0:08:00](https://youtu.be/txI6XKFxguo?t=480)): harness/system prompt (persona, tools, self-correction) → skills as playbooks (naming, layer contracts, join rules, required tests, per layer) → a one-sentence task prompt. Give it structured project access: [dbt MCP](https://github.com/dbt-labs/dbt-mcp) (`get_lineage`, `get_node_details`, `get_model_health`, plus `compile`/`show`/`test`/`build`) and [dbt agent skills](https://github.com/dbt-labs/dbt-agent-skills).
3. **Lock the spec before any SQL** ([Careem 0:09:02](https://youtu.be/6BPrk0LBl3o?t=542)): the agent asks about grain, which metric "revenue" means (GMV, GTV, order count), filters, currency, and ownership (gold vs temporary). "AI writes bad SQL" usually means the spec was vague.
4. **Split into phases with their own agents** ([DocuSign 0:14:07](https://youtu.be/RQ97J3IccX0?t=847)): discovery → dbt development and validation → orchestration/PR. A failed compile retries only its phase. Keep one monolithic prompt and you won't know what broke.
5. **Validate cheaply, then really** ([Riot 0:15:08](https://youtu.be/txI6XKFxguo?t=908)): parse → compile (dbt v2/Fusion checks columns, types and functions in seconds, no warehouse) → execute in a sandbox (row counts, nulls, assumptions). Loop on failure until green.
6. **Make the sandbox structural** ([Careem 0:11:05](https://youtu.be/6BPrk0LBl3o?t=665)): credentials that can read prod but only write dev, macros that force dev schema and storage, ephemeral compute, CI checks for layer direction and location.
7. **Hand humans a reviewable PR**: lineage and downstream impact, test results, before/after data, and a list of assumptions the agent made ([Wizard 0:18:04](https://youtu.be/Cn_RhdpeX9U?t=1084)). Humans approve. The agent never deploys ([Nordstrom 0:19:06](https://youtu.be/wVXGX58Znts?t=1146)).
8. **Measure speed and trust**: cycle time, review comments per PR, incidents, and whether engineers actually trust it ([DocuSign 0:27:07](https://youtu.be/RQ97J3IccX0?t=1627)).

## Decision rules

- **Prompt rule or structural guardrail?** If breaking it corrupts data, costs real money or touches prod, enforce it in IAM, macros, CI or the build. Prompts drift ([Careem 0:22:06](https://youtu.be/6BPrk0LBl3o?t=1326)). Style and conventions can live in skills.
- **Skill or harness?** A broad rule that doesn't change the user flow goes in a skill. Flow behavior (compile-only edits, a separate validation step, approval checkpoints) belongs in the harness ([Wizard 0:33:01](https://youtu.be/Cn_RhdpeX9U?t=1981)).
- **Analyst request or engineer request?** Route analysts' models to a temporary layer that expires (Careem: 30 days, then promote or drop). Engineers' go to bronze/silver/gold ([Careem 0:33:01](https://youtu.be/6BPrk0LBl3o?t=1981)).
- **Read or write access for agents?** Give agents MCP for reading (lineage, metadata, queries). Route every write through validated, human-approved API calls. CarGurus' triage, PR-review and analytics agents all work this way ([CarGurus 0:17:02](https://youtu.be/yqCrNVFzLg8?t=1022)). Clear requests often matter more than code generation: their "receptionist" agent interviews requesters until the ticket is well scoped ([0:20:07](https://youtu.be/yqCrNVFzLg8?t=1207)).
- **What stays human?** Aligning cross-team definitions, business UAT, evolving definitions over time, cost-sensitive incrementality (partition pruning, backfills), legacy schema drift, final merge ([Careem 0:24:00](https://youtu.be/6BPrk0LBl3o?t=1440), [Zendesk 0:11:02](https://youtu.be/n7aBWe4RB4k?t=662)).

## Quick checks: failure → fix

| Failure | Fix |
|---|---|
| Agent burns warehouse compute catching typos | Add the compile level (Fusion) before execution |
| Plausible model, wrong metric | Spec locking with glossary-backed choices |
| Duplicate models from parallel requests | CI checks the merged manifest; enforce naming so the same metric gets the same column name; check "exists already?" in the skill ([Careem 0:31:09](https://youtu.be/6BPrk0LBl3o?t=1869)) |
| Agent ignores the dbt skills or skips unit tests | Narrower phase agents with explicit required steps ([DocuSign 0:29:10](https://youtu.be/RQ97J3IccX0?t=1750)) |
| Full-table scans or rebuilds during tests | Limit rows in dev, defer to prod state, review incremental logic by hand |
| Reviewer drowns in the PR body | Trim the PR template using reviewers' feedback ([DocuSign 0:31:12](https://youtu.be/RQ97J3IccX0?t=1872)) |
| Hidden decisions ("null duration = crash") | Surface assumptions as a list; validate with a fresh sub-agent that doesn't share the builder's reasoning ([Wizard 0:21:08](https://youtu.be/Cn_RhdpeX9U?t=1268)) |
| Every engineer writes their own skills | Central skill library, shared as plugins, with review, maturity tags and evals ([Zendesk 0:18:03](https://youtu.be/n7aBWe4RB4k?t=1083)) |
| Parallel agents clobber each other's dev schemas | One schema per work tree (short hash suffix) plus deferral ([Wizard 0:32:00](https://youtu.be/Cn_RhdpeX9U?t=1920)) |

## Rules of thumb

- Separate the mechanics of SQL (agents are good at it) from business semantics (be extremely precise) ([Riot 0:20:04](https://youtu.be/txI6XKFxguo?t=1204)).
- Source discovery only works if raw tables are documented. Keep a data dictionary of raw events ([Riot 0:29:08](https://youtu.be/txI6XKFxguo?t=1748)).
- Test quality beats test count. Without good tests, the sandbox proves nothing ([Careem 0:25:02](https://youtu.be/6BPrk0LBl3o?t=1502)).
- Keep guardrails engine-agnostic (Spark, Trino, DuckDB) ([Careem 0:23:08](https://youtu.be/6BPrk0LBl3o?t=1388)).
- Own the harness and skills, not the model. Use a fixed skill structure (name, description, actions, do/don't, expected output) so a model upgrade doesn't change results ([Zendesk 0:27:04](https://youtu.be/n7aBWe4RB4k?t=1624)). Ramp keeps a model picker to avoid lab lock-in.
- Writing is the job: an agent is "a person in a box onboarded 50,000 times". Review prose like code ([Ramp 0:06:12](https://youtu.be/Di8R8dlwpxA?t=372)).
- Gate data access on documentation: Ramp's agent can't query Snowflake until it has read the data skill ([Ramp 0:32:00](https://youtu.be/Di8R8dlwpxA?t=1920)).

## Known gaps

- For the context agents read (meta, context docs, evals of analytics agents), see the companion skill `dbt-agent-context`.
- Skill and YAML examples (Riot's silver skill, Careem's CI checks, DocuSign's orchestration markdown) were on slides only, so they aren't reproduced here.
- Results are per the videos: Careem about 90% of new models and weeks to hours, DocuSign 50%, Zendesk 2-2.5x velocity, Wizard design partners 15-20% fewer incidents. Wizard's desktop app was in private preview at the time.

## Sources

| Video | Channel | Date | Used for |
|---|---|---|---|
| [From prompt to PR: sandbox-validated dbt changes before human review](https://www.youtube.com/watch?v=6BPrk0LBl3o) | dbt Labs | 2026-10-26 | Four pillars, spec locking, sandbox isolation, self-correcting loop, transient layer, human limits |
| [When skills meet scale: an agent assembly line for dbt](https://www.youtube.com/watch?v=txI6XKFxguo) | dbt Labs | 2026-10-26 | Layered context, five-station assembly line, parse/compile/execute, cost curve |
| [AI-augmented analytics engineering at DocuSign: dbt v2, dbt MCP, and agent skills](https://www.youtube.com/watch?v=RQ97J3IccX0) | dbt Labs | 2026-10-26 | Phase-split agents, controls to keep, four lessons, where to start |
| [AI-powered data development: How agentic SDLC & dbt-MCP transformed our data engineering workflow](https://www.youtube.com/watch?v=n7aBWe4RB4k) | dbt Labs | 2026-10-26 | Promotion workflow, skill workflows, skills library and governance |
| [dbt Wizard: your AI teammate for data development](https://www.youtube.com/watch?v=Cn_RhdpeX9U) | dbt Labs | 2026-10-26 | Review gap, impact as a DAG, assumptions, validation sub-agent, harness vs skill |
| [Ramp's internal AI stack: agents, sandboxes, and an AI-first BI tool](https://www.youtube.com/watch?v=Di8R8dlwpxA) | dbt Labs | 2026-10-26 | Sandboxed remote agents, dashboards as code, context per department, prose |
| [Governed by default: how data teams at Nordstrom turn dbt governance into an AI advantage](https://www.youtube.com/watch?v=wVXGX58Znts) | dbt Labs | 2026-10-26 | Multi-agent DDLC ending in a PR, linters failing the build (German captions) |
| [From dbt Core to dbt v2: How CarGurus unlocked dbt State and AI at scale](https://www.youtube.com/watch?v=yqCrNVFzLg8) | dbt Labs | 2026-10-26 | Read-only MCP with human-approved writes, triage and receptionist agents |
