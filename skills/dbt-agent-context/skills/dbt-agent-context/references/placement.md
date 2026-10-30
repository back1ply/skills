# dbt agent context: where each kind of context goes

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10). Details are as the videos describe them. Key names come from the speakers' words; the exact YAML was on slides.

## Contents
- Current dbt syntax for meta
- Okta's three-layer agent context framework
- Green Dot's Meta:Context card (DRIED)
- Recruit's domain context as code
- Anaconda's organizational knowledge base
- Agents Schema (publishing context to the warehouse)
- Context spectrum and the "dbt map"

## Current dbt syntax for meta

Since dbt 1.10 (backported to 1.9), custom attributes belong under `config.meta` for both models and columns. Custom keys directly under `config` raise `CustomKeyInConfigDeprecation`. Agents Schema reads `config.meta` first, then the old top-level `meta`.

```yaml
models:
  - name: fct_orders
    config:
      meta:
        agent: {}        # Okta-style sub-block, keys below
    columns:
      - name: amount
        config:
          meta:
            agent: {}
```

## Okta's three-layer agent context framework

Watch: [0:06:11](https://youtu.be/SEgoqvU8Zrs?t=371)

- **What**: everything an agent needs before it can trust a table. Built entirely in dbt and shipped through normal PRs.
- **Why it was needed**: three problems from the experiment phase ([0:04:09](https://youtu.be/SEgoqvU8Zrs?t=249)): *context fragmentation* (Snowflake semantic views built in the UI drifted away from dbt logic), *no auditability* (UI clicks, no version control), and *context as one monolithic blob* (all instructions in one field, with no split between "always know" and "look up").

**Layer 1: local resource hints (meta).** An `agent` sub-block in model meta ([0:07:11](https://youtu.be/SEgoqvU8Zrs?t=431)):

| Key (per the talk) | Purpose |
|---|---|
| maturity | Whether the model is a safe candidate |
| synonyms | Map business words to the model |
| use_for / avoid_for | "Use this for question X, avoid it for Y" |
| implicit filters | e.g. always filter a snapshot table to the current snapshot date |

At column level ([0:08:00](https://youtu.be/SEgoqvU8Zrs?t=480)): synonyms, aggregation rules (sum, never average), what NULLs mean, and SQL predicates required for the column to make sense. **Use the same meta keys in every domain.** Don't invent keys per domain.

**Layer 2: navigation rules and context docs** ([0:09:01](https://youtu.be/SEgoqvU8Zrs?t=541)). Markdown files that say "given this question, go to this model, apply these rules". Meta says what a model is good for. Context docs say how to move between models.
- *Company-level*: applies to everything (fiscal year starts Feb 1, org-wide defaults, data freshness).
- *Domain-level*: routing rules, business rules, cross-model logic, known pitfalls, explicitly out-of-scope topics.
- Planned next: cross-domain and persona-based docs.

**Layer 3: semantic surface** ([0:11:04](https://youtu.be/SEgoqvU8Zrs?t=664)). Governed dimensions, metrics and verified queries: the default path to a consistent answer. Okta moved UI-built Snowflake semantic views into dbt with a custom slash-command skill (GET_DDL output converted to a dbt semantic view spec), then added a custom materialization for Cortex agents. Model, semantic view and agent became nodes in one DAG ([0:13:06](https://youtu.be/SEgoqvU8Zrs?t=786)). Okta opened a dbt-core GitHub discussion on whether agents should be a materialization or a first-class node type.

**Routing skill** ([0:21:08](https://youtu.be/SEgoqvU8Zrs?t=1268)): semantic layer first ("should be 80% of your metrics"). If that fails, read the context docs to pick a semantic view. If that fails, use a model and read its use_for / avoid_for.

**First action**: add an `agent` sub-block with use_for / avoid_for / synonyms to your 5 most-asked marts, and write one company-level context doc.

## Green Dot's Meta:Context card (DRIED)

Watch: [0:05:09](https://youtu.be/vuXqA_vNssw?t=309)

- **What**: a typed "context card" in the meta block of the metric's own YAML, so one semantic-layer call returns numbers and meaning together. It goes through the same PRs and CI as the metric.
- **Five categories, DRIED** ([0:06:09](https://youtu.be/vuXqA_vNssw?t=369)), each aimed at a known way agents get analysis wrong:

| Category | Holds |
|---|---|
| **D**escriptions | The metadata most tools already cover |
| **R**elationships | What it correlates with, what it decomposes into |
| **I**nvestigations | Causal dimensions, known root causes |
| **E**xpectations | Healthy range, warning and critical thresholds |
| **D**ecisions | SLAs, limits, business rules, what to do when it moves |

- The full card has 36 fields, but "three core fields will change an agent's answer".
- **Example** ([0:09:01](https://youtu.be/vuXqA_vNssw?t=541)): program Q's decline rate was 10x program F's. Without the card, Claude guessed rate limits but couldn't check, because the caps lived in a spreadsheet. With caps in the card, it found that only Q caps transactions per account, flagged the per-account vs per-program mismatch, and proposed the query that would settle it. The confirmed cause was written back under known root causes.
- **Write-back** ([0:10:02](https://youtu.be/vuXqA_vNssw?t=602)): findings go back into the card, or reveal a missing dimension or a metric that should be split.
- Context can sit at any level and cascade like column docs ([0:23:11](https://youtu.be/vuXqA_vNssw?t=1391)). Per-partner SLAs were handled with case logic instead of splitting metrics.
- The public repo and authoring skill were mentioned in the talk without a URL. Search "Meta:Context dbt" before linking.
- **First action**: for one KPI, fill healthy range, business rules and known root causes, then ask the same question before and after.

## Recruit's domain context as code

Watch: [0:06:14](https://youtu.be/4gFcivfHR3A?t=374)

- **What**: an issue-driven alternative to building an ontology. (1) Pick the target issue. (2) Find the hidden context needed to solve it. (3) Write it as code and extract core rules.
- **The issue** ([0:08:01](https://youtu.be/4gFcivfHR3A?t=481)): with the right tables, semantic layer and golden queries, the text-to-SQL agent still failed, because many event names contained "reserve" (quick_reserve_button, quick_reserve_icon, ...).
- **The spec** ([0:09:01](https://youtu.be/4gFcivfHR3A?t=541)): one YAML file models *user action → target UI part → log entry*. Per measurement ID: description, trigger (action type such as conversion or tap), target (object kind, label, state), event assignments (event name). It is loaded into BigQuery tables as context for the agent.
- **Keeping it fresh** ([0:13:03](https://youtu.be/4gFcivfHR3A?t=783)): the log design must be written and reviewed *before* implementation. CI flags conflicting events across active projects and rule violations. Front-end logging code is generated from the spec, and QA runs Selenium/Appium scenarios and checks fired events in BigQuery against the spec.
- **Context = implementation + design + intent** ([0:18:01](https://youtu.be/4gFcivfHR3A?t=1081)). dbt covers implementation, the spec covers design, and intent (product journeys, roadmaps) is future work. They plan Gherkin scenarios for drop-off detection.
- Answers were rated by an LLM judge: 5 stars = fully from golden queries, down to 2 = possible misunderstanding, don't use ([0:25:07](https://youtu.be/4gFcivfHR3A?t=1507)).
- **First action**: when an agent confuses similarly named items, write a reviewed spec for just that family of items, not a company ontology.

## Anaconda's organizational knowledge base

Watch: [0:02:06](https://youtu.be/PitSWUhaLP4?t=126)

- **What's missing**: organizational knowledge, not tool capability. Slack incident threads, meeting trade-offs and PR explanations are "a trail of tested knowledge".
- **Failures first**: a big interview-built memory file worked for weeks, then went silently stale ([0:03:07](https://youtu.be/PitSWUhaLP4?t=187)). RAG and source MCPs leave the agent guessing what to trust when sources disagree.
- **v1 → v3** ([0:06:12](https://youtu.be/PitSWUhaLP4?t=372)): v1 summarized sources into wiki-like articles, but the article was both output and storage, so dropped details were gone for good. v2 extracted atomic **facts, decisions (what/who/when/why), entities (canonical names and aliases), prescriptions (procedures and where they apply)**. v3 added **temporal validity and supersession**, "a dbt snapshot for business context": facts have valid_from/valid_to, decisions record what they replaced, and search hides superseded items by default.
- **Pipeline** ([0:09:03](https://youtu.be/PitSWUhaLP4?t=543)): ingest with confidence score, extract, index, dedupe, resolve entities, reflect (find conflicts and stale facts, escalate low-confidence ones to a human), build a taxonomy, route sources to articles, write articles, self-critique against sources, run a deterministic quality gate (shallow articles, blame attribution, leaked secrets), then human review. Cheap models extract. Frontier models handle judgment steps.
- **Serving**: an MCP with hybrid search for articles, exact plus semantic search for facts, and fuzzy search for entities. An **agent inbox** lets agents propose new facts; once a human accepts, they re-enter the pipeline as a new source ([0:12:10](https://youtu.be/PitSWUhaLP4?t=730)). A `report_outcome` tool logs retrieved vs used items for retrieval tuning.
- **Order**: the agent starts with the dbt project (models, metrics, a validating query), then searches the knowledge base with a sharper pattern. Pointing AGENTS.md at the catalog made the agent skip dbt. Removing the pointer made it forget the knowledge base. Getting this balance right is unsolved ([0:18:04](https://youtu.be/PitSWUhaLP4?t=1084)).
- **Protect human edits**: give curated facts high confidence so re-runs don't overwrite them ([0:24:01](https://youtu.be/PitSWUhaLP4?t=1441)).
- **First action**: before building anything, list 20 questions that need context missing from dbt. That list is your eval set.

## Agents Schema (publishing context to the warehouse)

Repo: [dbt-labs/agents_schema](https://github.com/dbt-labs/agents_schema) (checked 2026-10-26). Talks: [Okta 0:16:00](https://youtu.be/SEgoqvU8Zrs?t=960), [dbt Labs/Fivetran 0:16:00](https://youtu.be/Ehm6_yfc7RE?t=960).

- A standard `AGENTS` schema of plain tables in your warehouse. GitHub workflows ingest dbt (`target/manifest.json`), Looker, Omni, OSI, Sigma and markdown skills. Destinations: Snowflake, Databricks, BigQuery, ClickHouse. One secret: `WAREHOUSE_CREDENTIALS`.
- `AGENTS.ROOT(provider, key, content)` is the registry and glossary, where an agent starts. Skills are rows like `(user, skill/revenue/arr)`. `AGENTS.SKILL_USE` maps skills to the tables they use.
- dbt tables: `AGENTS.DBT_MODEL` and `AGENTS.DBT_COLUMN` (description, tags, `meta` as VARIANT/JSON), plus `AGENTS.DBT_DEPENDENCY` (DAG edges). dbt semantic-layer metrics are not synced. Metric tables exist only for OSI (`AGENTS.OSI_METRIC`, the spec's canonical semantic source) and Sigma. A Meta:Context card on a dbt metric therefore reaches agents only through the Semantic Layer API, unless it is also on the column's meta.
- Okta: on merge to main, GitHub Actions syncs the manifest and context docs. The same docs are staged for Cortex, which reads them as skills, while Claude reads them via MCP. Merging a context fix updates every agent with no redeploy ([0:27:06](https://youtu.be/SEgoqvU8Zrs?t=1626)).
- Fivetran Context Layer (vendor) also writes to `AGENTS`. See case-studies.md.

## Context spectrum and the "dbt map"

Watch: [0:04:08](https://youtu.be/Ehm6_yfc7RE?t=248)

- Context tells an agent: **meaning, authority (what to trust), rules, change over time, evidence**.
- It runs on a spectrum from simple (semantic, structural) to complex (situational, interpretive). Don't try to load everything at once.
- A dbt project is already a map ([0:07:13](https://youtu.be/Ehm6_yfc7RE?t=433)): model prefixes (fct_, stg_) signal trust, the semantic layer adds business meaning, lineage shows origins, and tests, docs and ownership establish trust. The edge of the map (Slack exceptions, two teams' definitions, support tickets, calls) is where the hard questions live.
- "What was ARR at end of August?" splits immediately: booked or current, ACV, services included, which table is authoritative, access, regulatory limits ([0:06:11](https://youtu.be/Ehm6_yfc7RE?t=371)).
- Just-in-time context (skills, MCP, kept across sessions) vs just-in-case context (searchable stores of unstructured text) ([AN68dnWqhmk 0:00:00](https://youtu.be/AN68dnWqhmk?t=0)).
