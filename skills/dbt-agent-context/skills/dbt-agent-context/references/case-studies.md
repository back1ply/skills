# dbt agent context: per-talk notes and vendor tools

Sources: dbt Summit 2026 talks on the dbt Labs channel (2026-10). Vendor features are as presented by the vendor. Check current docs before relying on them.

## Contents
- Checkr + Omni
- Okta (Snowflake Cortex)
- Green Dot (Meta:Context)
- LangChain + Hex
- Anaconda (Kilo)
- Recruit / CarSensor
- dbt Labs + Fivetran Context Layer
- AlphaSense + Euno
- Nordstrom

## Checkr + Omni ([rnLMk-GRx7Y](https://www.youtube.com/watch?v=rnLMk-GRx7Y))
- About 6,000 dbt models in Snowflake. Claude over the Snowflake MCP gave a different wrong answer each time and skipped joins ([0:05:06](https://youtu.be/rnLMk-GRx7Y?t=306)).
- Omni's five AI context fields ([0:10:04](https://youtu.be/rnLMk-GRx7Y?t=604)): **synonyms**, **sample values** (valid values such as channel = chat/email/phone), **field descriptions** (free from dbt), **AI context** (free-text behavioral guidance, e.g. "SLA without a channel → break out every channel, targets differ"), **sample queries** (validated multi-step analyses). Other BI tools have similar fields (LookML has `ai_context`, which Agents Schema syncs).
- Omni can push models back to dbt as PRs, and can pair an Omni branch with a dbt dev schema so a content validator catches broken dashboards before merge.
- "Off-roading": let permitted users go beyond the semantic layer, but tell them the answer is less trusted.

## Okta (Snowflake Cortex) ([SEgoqvU8Zrs](https://www.youtube.com/watch?v=SEgoqvU8Zrs))
- Framework and Agents Schema pipeline: see placement.md.
- Two consumers, one context ([0:24:00](https://youtu.be/SEgoqvU8Zrs?t=1440)): Claude reads meta via SQL/MCP, context docs as markdown, and semantic views via MCP tools. Cortex reads meta via an attached search service, context docs as staged skills, and semantic views via text-to-SQL. Agent configs were emptied of their own instructions to avoid drift.
- Wins: fix one layer, merge, and every agent is smarter (no redeploy). The 100th question gets the same quality as the first.
- Mindset: it's the BI-to-dbt shift again. Govern the layer underneath, and treat the front end (dashboard then, agent now) as replaceable.

## Green Dot (Meta:Context) ([vuXqA_vNssw](https://www.youtube.com/watch?v=vuXqA_vNssw))
- Embedded finance and bank, heavily regulated. Piloting conversational BI with Claude plus the dbt Semantic Layer.
- Regulated-industry adopters wanted interpretation, thresholds and rules governed like metadata, "where the regulators can audit it". One wrote cards for 30 KPIs.
- Seven-model test ([0:11:05](https://youtu.be/vuXqA_vNssw?t=665)): given raw materials minus judgment, all models flagged the untested claim, and 0 of 7 wrote the rule "a per-account value exactly at the cap is a policy ceiling, not demand". The card is "the residue of an investigation".

## LangChain + Hex ([2yJxBnldB5A](https://www.youtube.com/watch?v=2yJxBnldB5A))
- Three-person data team. Context layers: dbt descriptions (persisted to BigQuery), the dbt repo as a Hex reference repo, workspace guides (markdown in the dbt repo: company overview, marketing pipeline, pricing and billing), semantic layer (Hex's, which the Hex agent built for them), and **endorsements**.
- Endorsements ([0:06:17](https://youtu.be/2yJxBnldB5A?t=377)): only marts get endorsed (tagged in dbt, synced to Hex), plus data-team-built source-of-truth dashboards such as ARR. Edits to an endorsed dashboard need data-team review. Unfinished assets can be hidden from AI.
- Rolled out with role-based training per stakeholder group. Self-serve questions grew 40x, per the video ([0:23:07](https://youtu.be/2yJxBnldB5A?t=1387)).
- Pricing and billing changes fast: go deep with RevOps, finance and sales, and keep a dedicated guide so "revenue" gives the same answer in Hex, Slack or any other agent.

## Anaconda (Kilo) ([PitSWUhaLP4](https://www.youtube.com/watch?v=PitSWUhaLP4))
- Stack: dbt MCP, dbt skills, Wizard CLI, Semantic Layer, plus a self-built knowledge base. Demo ([0:13:12](https://youtu.be/PitSWUhaLP4?t=792)): a revenue spike was traced from ARR model to intermediate model to warehouse rows (settlement credit deductions) to a KB article on known backend bugs (a webhook race condition). The answer named the engineer who ran the manual retry, and the investigation was saved back.
- Eval: 35 situational questions comparing dbt only, dbt + RAG, and dbt + KB. RAG and KB were similar overall, and the KB won on questions with conflicting or outdated sources. The speaker said it's not statistically significant.
- Open problems: retrieval noise as the KB grows, duplicate categories, the dbt vs KB boundary, eval rigor, auditability across many LLM steps, access control.
- The speaker described it as vibe-coded; v1 took 2-3 days.

## Recruit / CarSensor ([4gFcivfHR3A](https://www.youtube.com/watch?v=4gFcivfHR3A))
- Slack analytics agent for PMs measuring A/B-tested UX changes. Stack: dbt context (manifest, table definitions) + dimensional data marts + domain context.
- Skeptical of company-wide ontologies: no working real-world examples seen. Solve one issue at a time instead.
- Side benefit: the YAML spec replaced Excel/Sheets log designs and cut logging incidents for engineering too. "Metadata over the metadata".

## dbt Labs + Fivetran Context Layer ([Ehm6_yfc7RE](https://www.youtube.com/watch?v=Ehm6_yfc7RE))
- Three source types ([0:13:08](https://youtu.be/Ehm6_yfc7RE?t=788)): **knowledge** (docs, wiki, skill files), **operational** (databases, ERP, CRM), **analytic** (dbt, Hex/Omni/Sigma metrics).
- Fivetran Context Layer (vendor; waitlist at launch): parses connected sources, builds a search index and catalog, runs ontology discovery (links a Postgres revenue table to a Notion revenue doc), and writes everything to the `AGENTS` schema. Served via an Agent Context MCP. Concept tables decode jargon (HRBP, SKO). Trust signals include verified pages, page age and query frequency. Traces show low-confidence runs, unmapped terms and conflicts.
- Fiscal-year example: "FY27 starts in February". Exactly the kind of fact agents can't guess.

## AlphaSense + Euno ([TgUeC1LWc7o](https://www.youtube.com/watch?v=TgUeC1LWc7o))
- Euno's view: context must be **automated** (ready before it's needed), **governed** (who or which agent may access what) and **scoped** (only the slice the task needs) ([0:04:07](https://youtu.be/TgUeC1LWc7o?t=247)). Table context = lineage, code, owners, usage, quality, intent, sensitivity, access, certification.
- Use case 1, remodel legacy logic ([0:11:03](https://youtu.be/TgUeC1LWc7o?t=663)): one 287-field table behind 12 dashboards and 300 users, with 68 upstream models but the logic in the BI layer. Rebuilt as a 13-model star schema in about 15 prompts. Pattern: **quantify the problem first → supply the judgment the agent can't have (undocumented concept merges, scope cuts) → prove parity against the legacy model before shipping**. About half the diff was tests and docs.
- Use case 2, redesign billing ([0:15:10](https://youtu.be/TgUeC1LWc7o?t=910)): no code, just a Notion proposal with two Mermaid diagrams (current state traced to column level, and target with conformed dimensions and one fact per business process). It also produced a hand-off prompt for the next session. Impact analysis that takes seconds "stops being a discipline and becomes a default".
- Use case 3: many agents read one context platform via MCP. "If each agent reconciles on its own, they will disagree."
- Rule-based trust labels ([0:29:10](https://youtu.be/TgUeC1LWc7o?t=1750)), e.g. "built in Tableau and only queries gold dbt models → trusted", "PII upstream → not AI-ready", "unused 6 months → not ready". When definitions conflict, show both (product churn vs finance churn) with owner and usage, and let the user choose.
- Long AI plans: let it draft, read it as the reviewer, add bullet critiques, then iterate 2-3 cycles before handing to the architect.

## Nordstrom ([wVXGX58Znts](https://www.youtube.com/watch?v=wVXGX58Znts))
Distilled from YouTube's German auto-captions (the upload had no English track). Wording is approximate.
- **"Customer trips" counted two ways** ([0:06:10](https://youtu.be/wVXGX58Znts?t=370)). The customer team, which owns the metric, counts one purchase per customer per day per channel. The store team counts one trip per salesperson, so a shopper buying cosmetics, shoes and apparel is 3 trips, not 1. Neither is wrong. Leaders debated whose number was right instead of deciding. A bot on this data just picked one answer and spread the confusion "faster and to more people" ([0:08:03](https://youtu.be/wVXGX58Znts?t=483)).
- **Clean data is necessary but not sufficient** ([0:10:09](https://youtu.be/wVXGX58Znts?t=609)). A perfectly clean column named `customer_trip` still means different things to two orgs. Fix it with context, not more tests.
- **Governed at build** ([0:11:09](https://youtu.be/wVXGX58Znts?t=669)): tests, data quality and contracts are mandatory. Model and column metadata are enforced, and a model without a description doesn't merge. But "a required description isn't a good description". Checking it exists is automatable; checking it's right needs people.
- **Layers with rules** ([0:18:04](https://youtu.be/wVXGX58Znts?t=1084)): medallion on BigQuery, with explicit rules for what may enter each layer and what quality it needs. All consumers, dashboards and agents alike, read only gold.
- **Multi-agent dev lifecycle on the dbt MCP server** ([0:19:06](https://youtu.be/wVXGX58Znts?t=1146)): agents gather requirements, build bronze→silver→gold to the documented standards, write tests, and a separate agent validates. The output is a high-quality PR, never a deploy. Humans review it, and dbt linters fail the build if anything is missing.
- **Context management layer** ([0:21:06](https://youtu.be/wVXGX58Znts?t=1266)): centralized on DataHub, backed by GitHub. It holds dbt metadata, Looker metadata, KPIs and a business glossary. **The business writes the glossary**, under its own governance process.
- **Deliberately human-in-the-loop** for trust, even where more could be automated ([0:22:07](https://youtu.be/wVXGX58Znts?t=1327)).
- Results, per the video: pipelines in days instead of months; 2-5x faster for pilot teams; an agent on a new gold dataset in one sprint instead of about 6 months. Natural language runs through Looker's agents (where teams work) and Claude (where executives work), on the same context.
- **Lessons** ([0:27:05](https://youtu.be/wVXGX58Znts?t=1625)): build quality and contracts into the dev lifecycle early; plan warehouse access control (BigQuery IAM needed per-project isolation); build a context eval framework; keep one source of truth synced across platforms.
