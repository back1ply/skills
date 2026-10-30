# dbt agentic dev: end-to-end workflows by team

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10). Details and results are as the videos describe them.

## Contents
- Riot Games: five-station assembly line
- DocuSign: three phases, one agent each
- Zendesk: model promotion with skill workflows
- Careem: analyst request to validated PR
- Nordstrom: multi-agent DDLC
- Ramp: weekly reports from automations

## Riot Games: five-station assembly line

Watch: [0:13:07](https://youtu.be/txI6XKFxguo?t=787)

- **Problem** ([0:02:07](https://youtu.be/txI6XKFxguo?t=127)): "architecture diagrams do not enforce behavior". Under deadline pressure, people wire dashboards straight to raw. Three taxes: *unboxing* (logic braided into giant PySpark jobs), *testing* (no standard assertions or contracts), *exclusivity* (one line of logic required learning Spark, deploys and repo conventions).
- **Pilot**: the Echoes on the Rift event: cross-title identity (Wild Rift + LoL), 5 years of history, 60+ metrics. One source table was 18 TB, about 129B events, per the video.
- **Stations**: (1) discover sources (traces "mastery" to a raw column `proficiency_level`), (2) profile it (range 0-7, documented), (3) build the silver fact with naming, column order and a left join so players without mastery aren't dropped, (4) build gold (pivot to top champions, fold into the cross-title profile mart), (5) validate, then human PR review.
- **Harness**: "a lightweight Python harness around any language model" that injects skills and the schema catalog, registers tools, and runs the loop ([0:11:04](https://youtu.be/txI6XKFxguo?t=664)).
- **Playbook origin**: started as a Notion page of layer contracts. An agent converted it to YAML, and a human checked it matched ([0:25:01](https://youtu.be/txI6XKFxguo?t=1501)).
- **Result**: same two-month window as a previous hand-built event, but this time with on-call duty, shifting scope, travel, *and* building the harness and playbooks, while delivering more.
- **Redundant models** (Q&A): put the business data model in the skills, add "if it exists, don't build", and rely on PR review ([0:22:07](https://youtu.be/txI6XKFxguo?t=1327)).

## DocuSign: three phases, one agent each

Watch: [0:13:05](https://youtu.be/RQ97J3IccX0?t=785)

- Stack: Claude Code orchestrating dbt agent skills (analytics engineering, unit tests, running dbt commands, semantic layer), the dbt MCP server, dbt v2/Fusion with the VS Code extension and language server, plus GitHub and Atlassian MCPs and custom skills (code review).
- **Phase 0, setup and discovery**: picks the repo from a Jira-board→repo mapping (8-9 dbt projects), plus environment and branch. Options: dry run, "starter pack" vs "full delivery" ([0:19:03](https://youtu.be/RQ97J3IccX0?t=1143)).
- **Phase 1, dbt development**: explores existing models and sources (including clustering and performance), writes SQL and YAML, adds unit tests, compiles with Fusion, runs the review agent.
- **Phase 2, orchestration**: dbt platform job or Airflow DAG, then the PR.
- Coordination is described in one master markdown file, not coded hand-offs. Teams plug their own sub-skills into it ([0:38:20](https://youtu.be/RQ97J3IccX0?t=2300)).
- **Controls they chose to keep** ([0:11:03](https://youtu.be/RQ97J3IccX0?t=663)): branch isolation, validation, CI impact analysis, human approval. Making these boundaries explicit is what made it safe to automate the rest.
- **Four lessons** ([0:23:07](https://youtu.be/RQ97J3IccX0?t=1387)): context beats clever prompts; conventions must be explicit; specialize the work; keep the human gates.
- Result: 50% productivity gain from requirement to a review-ready asset (pilot, per the video). The bigger win was consistency in naming, tests and semantics.

## Zendesk: model promotion with skill workflows

Watch: [0:13:04](https://youtu.be/n7aBWe4RB4k?t=784)

- **The use case** ([0:04:08](https://youtu.be/n7aBWe4RB4k?t=248)): marketing, sales and finance each built their own "created pipeline" metric in the functional layer, with circular dependencies and no contracts. Promotion to the foundational layer means one shared definition, stable names, history, tests and SLAs. "Promotion is more than SQL."
- **Crawl**: manual SDLC (intake, acceptance criteria, manual lineage analysis, sign-off, build, UAT, deploy, repoint consumers).
- **Walk** ([0:10:02](https://youtu.be/n7aBWe4RB4k?t=602)): write skills for each repeatable step. Stakeholder alignment and business UAT stay human. A shared code-review skill gave everyone consistent reviews. Velocity more than doubled over 6 months of sprints, per the video.
- **Run**: phases chained as skill workflows, each phase's output feeding the next: (1) promotion plan (scan dbt models for usage, write a field-availability CSV of candidates), (2) build models plus schema/YAML generators, then a series of PRs, (3) human-gated merge, (4) docs: DAG runbooks, curation docs, Monte Carlo alerts ([0:14:05](https://youtu.be/n7aBWe4RB4k?t=845)).
- dbt MCP tools are "the hands and legs of the agent": get lineage, node details, `dbt show`, `dbt test`, manifest and catalog ([0:16:01](https://youtu.be/n7aBWe4RB4k?t=961)).
- Requirements come in a fixed PRD template ("curation doc") owned by one team. Skills read it. When the template changes, the next skill user opens a PR to update the skill ([0:32:01](https://youtu.be/n7aBWe4RB4k?t=1921)).

## Careem: analyst request to validated PR

Watch: [0:16:00](https://youtu.be/6BPrk0LBl3o?t=960)

Plain English request ("daily food revenue per merchant") → the skill router recognizes a dbt onboarding request → spec locking (revenue type, currency, status filter, grain) → lineage and context lookup (orders fact, column docs, blast radius) → SQL plus tests inferred from existing models' patterns (e.g. unique on merchant_id) → branch and PR → CI sandbox run → self-fix loop → green → human review. Platform built in about 3 months on dbt Core, Airflow, Kyuubi and OpenMetadata (all open source). About 90% of new models now come through it, per the video ([0:21:06](https://youtu.be/6BPrk0LBl3o?t=1266)). Next: make the semantic layer the single context source, and cache MCP tool calls to cut token use ([0:26:02](https://youtu.be/6BPrk0LBl3o?t=1562)).

## Nordstrom: multi-agent DDLC

Watch: [0:18:04](https://youtu.be/wVXGX58Znts?t=1084) (German auto-captions; approximate)

A developer or analyst describes the change → a team of agents on the dbt MCP server: requirements agent → build agent (bronze→silver→gold to documented standards) → tests → validator agent → high-quality PR. Engineers review it, and dbt linters fail the build if anything is missing. Documented engineering standards made enforcement possible "because the whole context already exists". Pipelines went from next-quarter to days, per the video.

## Ramp: weekly reports from automations

Watch: [0:21:05](https://youtu.be/Di8R8dlwpxA?t=1265)

A dashboard-as-code (WaveDash) plus a scheduled automation in the remote agent platform (Inspect) running the data agent: "this is the weekly report for project X, read this dashboard", with sub-agents sent to Datadog (tech health), GitHub (what shipped) and the data (why numbers moved). Open problem: report format. Long essays from agents are unpleasant to read.
