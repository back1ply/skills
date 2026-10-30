# dbt v2 migration and the faster dev loop

Sources: dbt Summit 2026 talks (dbt Labs channel, 2026-10). dbt v2 is the Rust engine formerly called "Fusion". Speakers use both names. Feature states (beta, experimental) are as of the talks.

## Contents
- Migration playbook (CarGurus)
- What breaks at enterprise scale (VMO2)
- Static analysis levels
- dbt lint and format
- dbt checks
- Docs v2, compare changes, faster tests

## Migration playbook (CarGurus)

Watch: [0:05:11](https://youtu.be/yqCrNVFzLg8?t=311)

Start: 80 developers, dbt Core 1.8 self-hosted, 950 models in 3 projects, on-prem GitHub Enterprise, an EC2 dev box per developer (constant support pings), Airflow. Pain points: dev environment upkeep, teams unable to self-diagnose failures, config drift breaking prod on merge.

**Four sequential bets:**
1. **Orchestration to the dbt platform, one-to-one** (same dbt version) for a quick win. Surprises: slim CI needed GitHub SaaS (they migrated mid-project), and developers needed ad hoc runs without job-edit rights, so they built a small Streamlit app. Build slack into the plan ([0:07:15](https://youtu.be/yqCrNVFzLg8?t=435)).
2. **Clean parse on v2, in parallel**: one dedicated engineer, about 3 weeks. `dbt autofix` resolved about 70% of deprecations. The rest came with clear guidance. Today, **baseline** static analysis mode lowers the bar, and agents and skills help with deprecations ([0:08:00](https://youtu.be/yqCrNVFzLg8?t=480), [0:25:01](https://youtu.be/yqCrNVFzLg8?t=1501)).
3. **Cut over project by project**: smallest first, one per week over a month, with a code freeze per project. The same 8 steps each time ([0:09:01](https://youtu.be/yqCrNVFzLg8?t=541)):
   1. Push the migration branch to staging.
   2. Open it in the Studio IDE.
   3. Flip the staging release track to v2.
   4. Run test jobs.
   5. Validate outputs (a full mirror run of prod in staging, which is expensive, so only once).
   6. Merge to prod.
   7. Flip the prod release track.
   8. Monitor at least one full overnight run.
4. **Turn on dbt State**, job by job.

Success factors: named people hands-on daily, an open line to dbt, constant stakeholder communication, and a launch day for the whole company. Unexpected win: compile time. A minute or two per compile, multiplied across every change, was a real developer experience cost ([0:27:03](https://youtu.be/yqCrNVFzLg8?t=1623)).

Governed agents built afterwards ([0:16:01](https://youtu.be/yqCrNVFzLg8?t=961)): a PR review agent grading against a rubric; a job-triage agent (a webhook on failure investigates via MCP and posts the likely cause and fix to Slack). **MCP is read-only; writes go through human-approved API calls.** Also a Slack analytics agent that shows its SQL, and a "receptionist" agent that interviews requesters until the ticket is well scoped, since the bottleneck was ticket quality, not code generation ([0:20:07](https://youtu.be/yqCrNVFzLg8?t=1207)).

## What breaks at enterprise scale (VMO2)

Watch: [0:17:00](https://youtu.be/bPZHJ47MpWo?t=1020)

Scale: 360 dbt users, 100+ projects, 440 GCP projects, tens of millions of dollars a year on BigQuery, 28 prod jobs running about 9 hours a day.
- Reaching **static analysis baseline** across the project was the biggest effort: edge-case Jinja, ambiguous SQL, package updates, deleting dead models. Benefits start there ([0:21:03](https://youtu.be/bPZHJ47MpWo?t=1263)).
- Failures they hit: macro-built clone tables (for Analytics Hub sharing) wouldn't materialize; UDFs failed runs (dbt helped fix both).
- Hard requirement before go-live: custom FinOps configs (choosing physical vs logical storage billing per dataset, routing to on-demand vs reservations at run time) must work under v2 and State. They save "millions a year".
- Next: strict mode with column-level checking.

## Static analysis levels

Watch: [0:04:06](https://youtu.be/81T3CTclWOw?t=246)

- v2 rewrote the Jinja runtime in Rust, so dbt understands SQL grammar, not just templates.
- **Baseline** (always on): checks that rendered SQL is grammatically valid. Enough for linting.
- **Strict** (`+static_analysis: strict`): type checking, column existence, and column-level lineage. If it compiles locally, it should run remotely. Needed for column lineage in Docs v2.
- VMO2 is testing whether live static analysis can retire their `limit 0` CI pipeline (20-30 minutes per push), which would save about 30 minutes per developer per day ([VMO2 0:08:00](https://youtu.be/bPZHJ47MpWo?t=480)).

## dbt lint and format

Watch: [0:07:09](https://youtu.be/81T3CTclWOw?t=429)

- `dbt lint` reads your SQLFluff config and adds dbt-specific rules, e.g. refs and sources as top-of-file CTEs, no hard-coded relation names (common in agent-written SQL), no `OR` in join conditions (forces extra scans), no functions on filter columns. Several are performance rules.
- `dbt lint --fix` for auto-fixable rules. `dbt format` reformats files. In VS Code, enable the dbt LSP linter to see diagnostics in the Problems tab.
- **No introspective queries run during linting**: the engine fills those gaps symbolically. That's where the claimed 40-250x speedup over SQLFluff comes from ([0:12:06](https://youtu.be/81T3CTclWOw?t=726)).

## dbt checks

Watch: [0:14:10](https://youtu.be/81T3CTclWOw?t=850)

- SQL assertions about the *project*, replacing Jinja-heavy dbt_project_evaluator logic. They run against a local **project information schema** (manifest-derived tables such as models, data tests, edges, lineage, exposures, groups, macros, metrics, in Parquet, queried with DuckDB). Explore with `dbt show` (e.g. `describe` an info table).
- Examples: every model has a primary-key test; nothing refs deprecated models; each source is read by only one staging model; no unused staging models; public models have contracts ([0:17:00](https://youtu.be/81T3CTclWOw?t=1020)).
- `dbt check` runs them, and they also run in `dbt build` (skip with `--skip-checks`). Set severity to warn or error. A selection filter limits failures to the selected nodes. Parse-level metadata today; compile-level (column lineage, propagated PII tags) planned.

## Docs v2, compare changes, faster tests

- **Docs v2** ([0:22:04](https://youtu.be/81T3CTclWOw?t=1324)): `dbt compile` (strict, for column lineage) → `dbt docs generate` → `dbt docs serve`. A static site powered by the info schema plus DuckDB-Wasm, hostable on S3.
- **Compare changes** (VS Code extension) ([0:24:00](https://youtu.be/81T3CTclWOw?t=1440)): builds the modified model and diffs its data against prod: rows added or removed, columns changed or dropped, primary-key differences. The demo caught a filter that dropped 90k rows. VMO2 calls it their favorite feature.
- **Local unit tests** (experimental, Snowflake and BigQuery): unit tests set to local compute are transpiled and run on DuckDB with no network round trips ([0:27:00](https://youtu.be/81T3CTclWOw?t=1620)).
- **Batch tests**: multiple `not_null`/`unique` tests on one model squashed into a single scan, saving compute and time on big projects ([0:29:02](https://youtu.be/81T3CTclWOw?t=1742)).
- Also: IntelliSense for models, columns and macros, live CTE previews, and rename refactors that propagate downstream (VMO2).
