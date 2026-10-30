# dbt agentic dev: validation, sandboxes and review

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10). Details are as the videos describe them.

## Contents
- Three feedback levels (parse, compile, execute)
- Careem's four pillars and sandbox isolation
- Spec locking
- Validation as its own stage (dbt Wizard)
- What a reviewable PR contains
- Where humans are still required

## Three feedback levels (parse, compile, execute)

Watch: [Riot 0:15:08](https://youtu.be/txI6XKFxguo?t=908)

| Level | Answers | Cost |
|---|---|---|
| 1. Parse | Is it SQL? select/from present, braces matched | Free |
| 2. Compile | Hallucinated columns, tables or functions? Date function on a numeric column? dbt v2 (Fusion) checks against the warehouse catalog statically | Seconds, no warehouse |
| 3. Execute | Real data: is the boolean really boolean, do row counts make sense, null or invalid rates | Warehouse compute |

- Without level 2, agents jump from 1 to 3 and run queries just to find typos: slow feedback and wasted compute ([0:16:01](https://youtu.be/txI6XKFxguo?t=961)).
- DocuSign compiled locally with Fusion before opening the PR, so CI builds didn't run for an hour on broken code ([0:22:06](https://youtu.be/RQ97J3IccX0?t=1326)).
- Riot's eval suite per model: contract checks, e.g. "model has a surrogate key" and "dbt compile passes", run before human review ([0:12:05](https://youtu.be/txI6XKFxguo?t=725)).
- **First action**: add `dbt compile`/parse (Fusion if available) as a required step before any agent `dbt build`.

## Careem's four pillars and sandbox isolation

Watch: [0:05:14](https://youtu.be/6BPrk0LBl3o?t=314)

Pillars: **context** (OpenMetadata: table and column docs with types, deep lineage, glossary of tribal terms like AOV, centralized metric formulas), **specs**, **structural guardrails**, **agent loop**.

Why human review alone failed ([0:03:09](https://youtu.be/6BPrk0LBl3o?t=189)): agents produce more code than people can read line by line. Reviewers check patterns, and one missed corner case breaks downstream pipelines and leadership's trust.

Isolation ([0:12:07](https://youtu.be/6BPrk0LBl3o?t=727)), "physical guardrails, not prompt rules":
- **Access**: the IAM role for agent runs can read prod and write only dev, so no accidental prod overwrites.
- **Storage**: custom and overridden materialization macros force dev schema plus dev bucket/path whenever the profile is dev.
- **Compute**: a dev engine (Kyuubi serverless SQL gateway on Spark) bound to the same role. Clusters are ephemeral, cheap, and torn down after the run.

Agent loop ([0:14:14](https://youtu.be/6BPrk0LBl3o?t=854)): compile → test → materialize in sandbox → analyze downstream impact via lineage → on failure, read the error and fix (demo: int vs bigint mismatch, then a missing column fixed by a join) → repeat until green → PR. CI checks include medallion direction (bronze→silver→gold), storage location per domain, and the sandbox run ([0:18:02](https://youtu.be/6BPrk0LBl3o?t=1082)). "Failing is free" in the sandbox.

**First action**: list the three things an agent could break in prod, and make each impossible through credentials or macros, not instructions.

## Spec locking

Watch: [Careem 0:09:02](https://youtu.be/6BPrk0LBl3o?t=542)

Before writing SQL, the agent confirms:
- **Grain**: one row per merchant per day? per city? per brand?
- **Metric**: the glossary lists the candidate meanings ("revenue" = GMV, GTV or order count), and the user picks one.
- **Filters**: completed orders only? a specific merchant or city?
- **Currency / units**: e.g. USD vs AED.
- **Ownership**: gold metric or temporary analysis.

Built on a general brainstorming skill plus glossary context. Questions adapt to the request ([0:29:07](https://youtu.be/6BPrk0LBl3o?t=1747)). The locked spec is shown back to the user before generation.

## Validation as its own stage (dbt Wizard)

Watch: [0:20:07](https://youtu.be/Cn_RhdpeX9U?t=1207)

- While editing, the agent only compiles and parses. Materializing is saved for an explicit validation step, because that's slow and costs money.
- The validation plan lists the commands. You can uncheck steps or add custom criteria in plain language, e.g. "no more than a 5% drop in rows" ([0:24:01](https://youtu.be/Cn_RhdpeX9U?t=1441)).
- Validation runs in a **sub-agent that only gets what it needs to validate**, so the builder's assumptions don't bias it ([0:21:08](https://youtu.be/Cn_RhdpeX9U?t=1268)).
- Every change produces a summary card with **assumptions made** (demo: "crash sessions = null duration" exposed a real bug, since a crash flag existed but went unused) ([0:18:04](https://youtu.be/Cn_RhdpeX9U?t=1084)).
- Impact is shown as a DAG of affected models, not just a diff. Queries are logged with human-run vs agent-run labels ([0:26:04](https://youtu.be/Cn_RhdpeX9U?t=1564)).
- Isolation: each work tree gets its own schema (short hash suffix), with automatic deferral to prod state ([0:32:00](https://youtu.be/Cn_RhdpeX9U?t=1920)).
- **First action**: in your own Claude Code setup, add a step that writes an "assumptions" list and spawns a fresh validator agent with only the diff, the tests and the spec.

## What a reviewable PR contains

- Lineage and downstream impact, test results, before/after data comparison ([Wizard 0:02:04](https://youtu.be/Cn_RhdpeX9U?t=124)).
- The locked spec and the assumptions list.
- A short body. DocuSign's first PRs were too long. Three reviewers said which parts helped, and only the useful agent output stayed ([0:31:12](https://youtu.be/RQ97J3IccX0?t=1872)).
- Zendesk: reviewers judge **eval results, not just tests** for skill-driven changes ([0:30:06](https://youtu.be/n7aBWe4RB4k?t=1806)).
- Nordstrom: the agent framework's goal is "a very high-quality PR", never a deploy. dbt linters in the pipeline fail the build if standards are missing, "governed at build" ([0:20:06](https://youtu.be/wVXGX58Znts?t=1206)).

## Where humans are still required

Watch: [Careem 0:24:00](https://youtu.be/6BPrk0LBl3o?t=1440)

- **Definitions that changed over time** ("active merchant" meant 1 year, later 3 years). History isn't versioned.
- **Cost-sensitive incrementality**: agents may full-scan. Guide partition pruning and backfills.
- **Legacy schema drift** (`total_order_amount_v1`, `_v2`): needs good tests and judgment.
- **Cross-team definition alignment** and **business UAT** (Zendesk kept both human).
- Riot: humans keep business meaning and final judgment. The agent removes scaffolding work.
- DocuSign: limit rows (e.g. 1,000) when testing, and customize run-command skills so they never trigger a full rebuild ([0:35:17](https://youtu.be/RQ97J3IccX0?t=2117)).
