---
name: dbt-agent-context
description: Designs and maintains the business context AI agents need to answer questions over a dbt project correctly, using patterns from dbt Summit 2026 (Okta, Checkr, Green Dot, LangChain, Nordstrom, Anaconda, Recruit, AlphaSense, dbt Labs/Fivetran). Covers where each kind of context belongs (config.meta, context docs, semantic layer, knowledge base), Agents Schema, eval-driven context loops, and "match the fix to the failure". Use when building conversational BI / text-to-SQL / analytics agents on dbt, an agent gives inconsistent or wrong metric answers, writing model/column descriptions or meta for AI, setting up Agents Schema or dbt MCP context, or the user says "context engineering", "context layer", "semantic layer isn't enough", "metric drift", or "AI-ready dbt project".
---

# dbt Agent Context

Distilled from 11 dbt Summit 2026 talks (dbt Labs channel, 2026-10). See Sources. Detail: [references/placement.md](references/placement.md) (where each kind of context goes, with key tables), [references/feedback-loop.md](references/feedback-loop.md) (evals and upkeep), [references/case-studies.md](references/case-studies.md) (per-talk notes, vendor tools).

## Core mental model

Every agent meets your data cold ([Okta 0:06:11](https://youtu.be/SEgoqvU8Zrs?t=371)). Three layers make data AI-ready ([Checkr 0:07:08](https://youtu.be/rnLMk-GRx7Y?t=428)):
1. **Warehouse + dbt project** = the dictionary (what exists).
2. **Semantic layer** = the grammar (joins, valid calculations, one definition per metric). This stops *metric drift*: the same question getting a different answer each time.
3. **AI context** = fluency: synonyms, rules, what a number *means*. The semantic layer defines calculations. Context explains how to talk about them and interpret them. Translate the semantic layer, don't duplicate it.

The semantic layer gets the math right but not the meaning: "right math, wrong interpretation, no error raised" ([Green Dot 0:02:07](https://youtu.be/vuXqA_vNssw?t=127)). Context is infrastructure. Agents are disposable. Write it once in dbt, ship it through PRs, and let every agent read the same copy ([Okta 0:26:04](https://youtu.be/SEgoqvU8Zrs?t=1564)).

## Decision rules: where does this piece of context go?

| Context | Put it in | From |
|---|---|---|
| What a model is for, whether it's safe, synonyms, `use_for` / `avoid_for`, implicit filters | model `config.meta` agent sub-block, same keys across all domains | Okta |
| Aggregation rule (sum, never average), what NULL means, required predicates | column `config.meta` | Okta |
| Meaning of a metric: healthy range, thresholds, causal dimensions, known root causes, related metrics, business rules / SLAs | `config.meta` next to the metric, so it comes back in the same semantic-layer call | Green Dot "DRIED" card |
| Which model answers which question, cross-model rules, gotchas, out-of-scope topics | Markdown context docs: one company-level (fiscal year, freshness), one per domain | Okta, LangChain workspace guides |
| Governed metrics, dimensions, verified queries | Semantic layer, the default answer path | all |
| Incidents, decisions, "why did X spike" knowledge that changes over time | Knowledge base of atomic facts with valid_from/valid_to; the agent queries dbt *first* | Anaconda |
| Meaning hidden in the product (event names, UI actions) | A reviewed spec file, written *before* the feature ships | Recruit "domain context as code" |

Publish it to the warehouse with **Agents Schema** ([dbt-labs/agents_schema](https://github.com/dbt-labs/agents_schema)). A GitHub Action reads `manifest.json` plus markdown skills and writes `AGENTS.ROOT` (provider/key/content), `AGENTS.DBT_MODEL` and `AGENTS.DBT_COLUMN` (with `config.meta` as JSON), and `AGENTS.DBT_DEPENDENCY`. Any agent with SQL access reads the same context. It does **not** sync dbt metric definitions (only OSI and Sigma metrics). A card on a standalone metric reaches agents only through the semantic-layer call, per Green Dot. To cover both paths, put it in the measure column's `config.meta`.

## Workflow: make a dbt project agent-ready

1. **Gate and fix descriptions.** In CI, block merging any model without a description. A required description isn't a good one, so humans still review content ([Nordstrom 0:12:10](https://youtu.be/wVXGX58Znts?t=730)). Write for an AI reader: "Status of the account" isn't enough. List the values, what each means, and when to filter on them ([LangChain 0:02:06](https://youtu.be/2yJxBnldB5A?t=126)). Persist docs to the warehouse, and give the agent the dbt repo so it can trace lineage.
2. **Mark what's trusted.** Expose or endorse only marts / gold (dims and facts). Agents and dashboards never read bronze or silver ([Nordstrom 0:18:04](https://youtu.be/wVXGX58Znts?t=1084)). Answer "please expose staging" with a new fact model, not by lowering the bar ([LangChain 0:28:05](https://youtu.be/2yJxBnldB5A?t=1685)).
3. **Add meta and context docs** using the table above. Start with one KPI and three fields you already know, such as healthy range and business rules ([Green Dot 0:15:11](https://youtu.be/vuXqA_vNssw?t=911)).
4. **Write a routing skill** for the agent: semantic layer first, then context docs to pick a semantic view, then a model plus its `use_for` / `avoid_for` meta ([Okta 0:22:09](https://youtu.be/SEgoqvU8Zrs?t=1329)).
5. **Build golden evals**: real stakeholder questions across easy, medium and hard, plus out-of-scope and vague ones the agent should decline or clarify ([Data Culture 0:10:02](https://youtu.be/sCqjOmH_0Tg?t=602)). Score correctness on the *result* with the layered match ladder. Record the expected *query plan* (fields, table, filter) for each question so failures can be diagnosed. If the answer comes from a trusted dashboard tile, the plan alone can be the check, as Checkr does ([Checkr 0:13:07](https://youtu.be/rnLMk-GRx7Y?t=787)).
6. **Loop**: run the evals, cluster failures, match the fix to the failure (below), re-run, then merge via a PR reviewed by an SME. Details in feedback-loop.md.

## Quick checks: match the fix to the failure

| Symptom | Fix |
|---|---|
| Picks the wrong field or table | Add synonyms ([Checkr 0:17:02](https://youtu.be/rnLMk-GRx7Y?t=1022)) |
| Asks too many clarifying questions | Add sample values to field definitions |
| Drifts into rabbit holes, answers the wrong question | Add behavioral guidance about which analyses the team usually does |
| Different answer each run | Metric missing from the semantic layer, or too many candidate models |
| Right number, wrong conclusion | Add a metric context card: expectations, decisions, known root causes |
| Near-identical names (events, tables) mean different things | Domain spec file with descriptions per item ([Recruit 0:08:01](https://youtu.be/4gFcivfHR3A?t=481)) |
| Two teams' numbers disagree for the same metric name | Agree on one definition, give the variants different names, and record both in the glossary. A bot otherwise picks one and spreads the confusion faster ([Nordstrom 0:07:11](https://youtu.be/wVXGX58Znts?t=431)) |
| Two agents disagree | Context is duplicated per agent. Move it to one source ([Euno 0:22:10](https://youtu.be/TgUeC1LWc7o?t=1330)) |

## Rules of thumb

- **Use the context you already have; don't make it up.** Confluence, PRDs, meeting transcripts and Slack threads are the raw material ([Checkr 0:12:07](https://youtu.be/rnLMk-GRx7Y?t=727)).
- Business people won't write docs, but they will talk. Record the SME conversation and draft context from the transcript ([Green Dot 0:16:00](https://youtu.be/vuXqA_vNssw?t=960)).
- **Less is more.** Blanket context doubled tokens and slowed answers in one team's test. Add context where evals fail, and drop fields nobody queries ([Checkr Q&A 0:24:02](https://youtu.be/rnLMk-GRx7Y?t=1442)).
- Typed fields beat prose: you can count coverage and check whether the agent used a threshold ([Green Dot 0:08:01](https://youtu.be/vuXqA_vNssw?t=481)).
- The best rules are the residue of a real investigation. Frontier models given the raw facts didn't write them ([Green Dot 0:12:06](https://youtu.be/vuXqA_vNssw?t=726)).
- A single memory file goes stale silently, and plain RAG can't tell which source is current. Keep sources, atomic facts, validity dates and human review ([Anaconda 0:20:06](https://youtu.be/PitSWUhaLP4?t=1206)).
- Don't wait for perfect context or a finished semantic layer. Ship a company overview doc, then follow the agent's low-confidence questions ([LangChain 0:14:07](https://youtu.be/2yJxBnldB5A?t=847)).
- Agents can write context back (findings, feedback), but humans decide what gets merged.
- **Score evals by result, not by exact match.** Exact match marks correct answers wrong when a column is renamed or an extra row or column appears. Use the scoring ladder in feedback-loop.md, and set a ship bar (Data Culture won't ship an agent below 90%) ([Data Culture 0:12:02](https://youtu.be/sCqjOmH_0Tg?t=722)).

## Known gaps

- For agents that *write* dbt code (sandbox validation, spec locking, skill libraries), see the companion skill `dbt-agentic-dev`.
- Exact YAML schemas (Okta's agent sub-block, Green Dot's 36-field card, Recruit's log-design file) were shown on slides, not in transcripts. Key names here come from the talks' wording. Check before treating them as a spec.
- Results (LangChain 40x self-serve questions, AlphaSense 3-5 weeks to hours, Anaconda's 35-question eval) are per the videos. Anaconda's speaker said the eval wasn't statistically significant.
- The Nordstrom talk had no English captions. It was distilled from YouTube's German auto-caption track, so names and figures from it are approximate.

## Sources

| Video | Channel | Date | Used for |
|---|---|---|---|
| [Is context engineering the new analytics engineering?](https://www.youtube.com/watch?v=rnLMk-GRx7Y) | dbt Labs | 2026-10-26 | Three layers, Omni's five fields, eval harness, match fix to failure, less-is-more Q&A |
| [From AI experiment to production: how Okta governs context for agents at scale](https://www.youtube.com/watch?v=SEgoqvU8Zrs) | dbt Labs | 2026-10-26 | Three-layer framework, meta agent sub-block, context docs, Agents Schema pipeline, routing skill |
| [Meta:Context: a business context schema in dbt Semantic Layer](https://www.youtube.com/watch?v=vuXqA_vNssw) | dbt Labs | 2026-10-26 | DRIED context card, typed fields, write-back, seven-model test |
| [No drift allowed: LangChain's context playbook with Hex](https://www.youtube.com/watch?v=2yJxBnldB5A) | dbt Labs | 2026-10-26 | AI-audience descriptions, workspace guides, endorsements, suggestion loop |
| [YAML doesn't know why: building the business context your agents are missing](https://www.youtube.com/watch?v=PitSWUhaLP4) | dbt Labs | 2026-10-26 | Knowledge base v1 to v3, atomic facts, temporal validity, agent inbox |
| [Beyond semantic models: "Domain context as code" for high-accuracy text-to-SQL](https://www.youtube.com/watch?v=4gFcivfHR3A) | dbt Labs | 2026-10-26 | Issue-driven context, log-design YAML, CI/QA against the spec |
| [With great context comes great autonomy: leveling up your agent context](https://www.youtube.com/watch?v=Ehm6_yfc7RE) | dbt Labs | 2026-10-26 | Context spectrum, dbt as the map, Agents Schema ROOT, traces |
| [AlphaSense scales AI on enterprise data with dbt-first governance and context from Euno](https://www.youtube.com/watch?v=TgUeC1LWc7o) | dbt Labs | 2026-10-26 | Automated/governed/scoped context, agentic remodeling, reconcile once |
| [Governed by default: how data teams at Nordstrom turn dbt governance into an AI advantage](https://www.youtube.com/watch?v=wVXGX58Znts) | dbt Labs | 2026-10-26 | Conflicting metric definitions, description gate, gold-only exposure, business-owned glossary (German captions) |
| [Don't ship what you can't measure: Evaluation-driven development for AI analytics agents](https://www.youtube.com/watch?v=sCqjOmH_0Tg) | dbt Labs | 2026-10-26 | Golden questions, layered result scoring, LLM judge, accuracy by context layer |
| [From analytics engineering to context engineering in 4 minutes](https://www.youtube.com/watch?v=AN68dnWqhmk) | dbt Labs | 2026-10-02 | Just-in-time vs just-in-case context, dbt-context-engineering package |
