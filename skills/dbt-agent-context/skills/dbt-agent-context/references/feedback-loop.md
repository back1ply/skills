# dbt agent context: evals, feedback loops and upkeep

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10). Details are as the videos describe them.

## Contents
- Checkr's eval harness and the four-step loop
- Data Culture's evaluation-driven development
- The simple start (no pipeline)
- LangChain's suggestion loop
- Write-back and agent feedback
- Cost control: less context
- Testing chunking and search for unstructured context
- Measuring

## Checkr's eval harness and the four-step loop

Watch: [0:13:07](https://youtu.be/rnLMk-GRx7Y?t=787)

- **Golden evals**: real stakeholder prompts paired with the correct answer *on a dashboard tile*. Because a tile exists, the dbt model and semantic definitions are known to be fine. The expected answer is a **query plan** (select these fields from this table with this filter), not a number. A failure therefore means a fluency gap, not a data or semantics problem.
- **Agent harness**: run evals via the BI API to get hundreds of pass/fail results. Then a Claude agent with three skills takes over:
  1. *diagnose error*: cluster failures (e.g. 10 evals where the agent couldn't find the topic);
  2. *author context*: pull from a vector store of curated company knowledge (RevOps data dictionary repo, PRDs, Slack channels) and write the right kind of context for that failure type;
  3. *verify fix*: re-run the failing cluster with the proposed changes and measure the lift. When the cluster passes, open a merge request for an SME to review.
- **The loop** ([0:16:01](https://youtu.be/rnLMk-GRx7Y?t=961)): (1) ask questions in stakeholders' own phrasing and jargon, (2) watch where the agent stumbles, (3) match the fix to the failure, (4) retest.
- **Example** ([0:17:02](https://youtu.be/rnLMk-GRx7Y?t=1022)): "Why is ops load going up?" sent the agent chasing a data-quality issue. The cause wasn't a wrong field. The agent lacked guidance that "load" means queues and "up" means wait time.
- **FRT result** ([0:18:02](https://youtu.be/rnLMk-GRx7Y?t=1082)): synonyms (SLA attainment, FRT, SLA rate pointing to one field), per-channel targets in different units, edge-case rules (missed or abandoned calls fail SLA), and a root-cause frame (pattern → driver → impact). An hours-long investigation took minutes, per the video.

## Data Culture's evaluation-driven development

Watch: [0:09:01](https://youtu.be/sCqjOmH_0Tg?t=541). Adapted from Chip Huyen's *AI Engineering*. How it relates to Checkr: Checkr scores on the query plan because every expected answer comes from a trusted dashboard tile, so data and semantics are already known to be right. Data Culture scores on the result and uses the plan only to diagnose failures. Use result scoring in general, and plan scoring when that dashboard-tile condition holds. Rule: "don't ship what you can't measure".

**1. Define what correct means: golden questions** ([0:09:01](https://youtu.be/sCqjOmH_0Tg?t=541))
- Real stakeholder questions for the use case (they used about 20-40, by judgment), spread across easy, medium and hard, and across analysis types (time series, aggregation, ranking).
- Include **graceful-failure** questions: out of scope (the agent should decline) and vague or ambiguous ones (the agent should ask or state its assumptions).

**2. Compare results, not SQL** ([0:11:02](https://youtu.be/sCqjOmH_0Tg?t=662)). Two analysts write different SQL for the same answer. Compare query plans (tables, fields) only for diagnosis.

**3. Score in layers** ([0:12:02](https://youtu.be/sCqjOmH_0Tg?t=722)). Naive exact match flagged correct answers as wrong (renamed column, extra row, extra column). Their ladder:

| Layer | Check | Catches |
|---|---|---|
| Exact match | MD5 of the stringified expected vs actual result | Identical answers |
| Value match | Ignore column names, compare values as lists | Renamed columns ("gross_revenue" vs "revenue") |
| Overlap match | Compare only shared columns | Agent added an extra column |
| Approximate match | Numeric tolerance | Rounding (23.5 vs 23.49) |
| LLM judge | Stronger model scores groundedness, relevance, comprehensiveness; < 0.8 = fail | The 10-20% the deterministic layers can't decide (e.g. timestamp vs date_trunc filter) |

Run it in CI. In production, parse the agent's SQL with sqlglot to check tables and fields, judge the rest with the LLM, write low scores to a warehouse table for review, and add new real questions to the golden set ([0:27:17](https://youtu.be/sCqjOmH_0Tg?t=1637)).

**What context moved accuracy** (per the video; added in this order, so the gains build on each other) ([0:17:01](https://youtu.be/sCqjOmH_0Tg?t=1021)):

| Context added | E-commerce | Healthcare |
|---|---|---|
| Raw tables | 0% | 0% |
| Kimball facts/dims | 50% | low (domain codes; `slot_status` filtered on a value that doesn't exist) |
| + column descriptions | small gain | gain (valid values) |
| + business rules in markdown (week starts Monday, exclude frozen appointments) | 78% (biggest jump) | gain |
| + verified queries for complex patterns | 94.7% | 92% |

Some additions made accuracy *drop*. They rolled those back, which is why every change needs a measured eval run ([0:26:17](https://youtu.be/sCqjOmH_0Tg?t=1577)). They publish an open-source template (golden questions, models on Agents Schema, two-layer evals); its URL was on a slide. Next for them: evaluating *interpretation* (does the agent read "revenue" the way the business does), currently with a human in the loop.

## The simple start (no pipeline)

Watch: [0:15:08](https://youtu.be/rnLMk-GRx7Y?t=908)

1. Gather one artifact where the team explains a metric (Confluence page, meeting transcript).
2. Paste it, plus the dbt model code and your tool's context-writing guidelines, into any LLM. Ask it to extract synonyms, identify sample values, and write terse behavioral guidance and edge cases.
3. Review it, then paste it in. One stakeholder conversation yields a lot.

Variant: interview the SME on Zoom while you play the naive data person, then have the agent model from the transcript ([0:29:05](https://youtu.be/rnLMk-GRx7Y?t=1745)).

## LangChain's suggestion loop

Watch: [0:08:01](https://youtu.be/2yJxBnldB5A?t=481)

- The BI agent (Hex Context Studio) shows which questions people ask and where it had low confidence ([0:16:00](https://youtu.be/2yJxBnldB5A?t=960)). Act on clusters: lots of marketing questions this month means write a marketing metrics guide.
- Repeated questions are a signal to build a dashboard or a new dbt model, so the agent stops rebuilding the same logic.
- Planned cadence ([0:31:07](https://youtu.be/2yJxBnldB5A?t=1867)): weekly, pull the top 5 suggestions via CLI and have Claude open a PR that edits descriptions or guides, then review and merge. They admit "everybody's responsibility is nobody's", so automate the pull.
- Use the BI notebook as a proving ground for undefined metrics: iterate options with stakeholders on real numbers, then lock the agreed logic into a dbt model so it becomes context ([0:21:05](https://youtu.be/2yJxBnldB5A?t=1265)).
- The goal isn't zero questions. It's better questions reaching the data team.

## Write-back and agent feedback

- Green Dot: a confirmed root cause gets written back to the metric card ([0:10:02](https://youtu.be/vuXqA_vNssw?t=602)). Their skill tells Claude to notice confusion or wrong numbers and offer to file feedback. A 25-person pilot produced 12 well-formatted feedback items in 24 hours, per the video ([0:24:01](https://youtu.be/vuXqA_vNssw?t=1441)).
- Anaconda: an agent inbox for proposed facts, plus `report_outcome` (retrieved vs used) and saved investigations (what was searched, concluded, still open) ([0:15:16](https://youtu.be/PitSWUhaLP4?t=916)).
- Okta next steps ([0:28:10](https://youtu.be/SEgoqvU8Zrs?t=1690)): regression tests that run verified queries against agents on every context change, and automatic correction feedback into context docs.
- Rule across all talks: agents propose, humans merge.

## Cost control: less context

Watch: [0:24:02](https://youtu.be/rnLMk-GRx7Y?t=1442)

- An audience team (migrated from Looker) found a light blanket pass of AI context made answers slower and doubled tokens on a well-structured dbt project.
- Checkr's answer: cut fields from topics. Query history showed 80% of fields in a 5-table topic were never queried. Add context only where answers are inconsistent (precision) or wrong (recall). "My favorite thing to do is delete stuff."
- Recruit: too much context hurts accuracy and wastes tokens ([0:05:13](https://youtu.be/4gFcivfHR3A?t=313)). Euno: context must be *scoped* to the task and role. Connecting 20 MCPs is expensive ([0:05:08](https://youtu.be/TgUeC1LWc7o?t=308)).

## Testing chunking and search for unstructured context

Watch: [AN68dnWqhmk 0:01:00](https://youtu.be/AN68dnWqhmk?t=60)

- Same DAG shape for every source: extract, transform (AI summaries), chunk, embed, search. The [dbt-context-engineering](https://github.com/dbt-labs/dbt-context-engineering) package does this as dbt models using your existing profiles.
- Run parallel pipelines with different chunk sizes. Use a larger embedding model for messy text (session logs) and a smaller one for uniform text. Write eval searches.
- Sample during development instead of embedding the whole corpus. Iterate rather than aiming for perfect.

## Measuring

- Coverage: share of metrics with a context card, and how complete each card is ([Green Dot 0:08:01](https://youtu.be/vuXqA_vNssw?t=481)).
- Traces: per run, which context was used, confidence, unmapped terms, conflicts between sources (e.g. a Notion page vs a dbt definition) ([Fivetran 0:23:05](https://youtu.be/Ehm6_yfc7RE?t=1385)).
- Benchmarks that regenerate from real answers, so a 95% POC is still 95% a month later ([Euno 0:25:02](https://youtu.be/TgUeC1LWc7o?t=1502)).
- LLM-as-judge for coverage that penalizes made-up facts (Anaconda). Treat small eval sets as directional only.
