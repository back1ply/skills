---
name: dbt-compute-cost
description: Cuts dbt warehouse spend and run time and speeds up the dev loop, using results from dbt Summit 2026 (RxBenefits, dbt Labs, Virgin Media O2, CarGurus, KOHO, WMCHealth, Espresso AI). Covers dbt State (skip/clone/rebuild, lag_tolerance, require_fresh_data_from, pre_clone, auto-deferral, dbt state explain), right-sizing warehouses off the critical path, splitting compute (Redshift data sharing), one-codebase near-real-time pipelines via env_var, dbt v2 migration, and v2 dev tooling (lint, checks, compare changes, batch/local tests). Use when dbt runs are slow or expensive, jobs rebuild unchanged models, CI takes too long, planning a dbt Core to v2 migration, setting up dbt State, sizing Snowflake/BigQuery/Redshift compute for dbt, or the user says "reduce dbt cost", "dbt State", "state-aware orchestration", "too many jobs", or "near real-time dbt".
---

# dbt Compute Cost

Distilled from 8 dbt Summit 2026 talks (dbt Labs channel, 2026-10). See Sources. Detail: [references/dbt-state.md](references/dbt-state.md) (how it decides, configs, rollout, limits), [references/compute-levers.md](references/compute-levers.md) (sizing, splitting compute, two-mode pipelines), [references/v2-and-devex.md](references/v2-and-devex.md) (migration playbook, lint/checks/compare/tests).

## Core mental model

1. **Only build what would come out different.** dbt used to be stateless and rebuilt every selected model. dbt State remembers code and data state per model and skips, clones or rebuilds each one, only when it can prove the same outcome ([dbt Labs 0:01:28](https://youtu.be/3VWBjDq8yp4?t=88)).
2. **Most models aren't in a hurry.** Only the critical path sets total run time. Everything else can run on cheaper compute without finishing later ([Espresso 0:02:06](https://youtu.be/9WB2aT_xCUE?t=126)).
3. **Design beats brute force.** Before buying a bigger warehouse, cut the rows processed ([WMCHealth 0:09:02](https://youtu.be/hGGS2Et4BIc?t=542)) or separate workloads that compete ([KOHO 0:19:03](https://youtu.be/C05o-rKXZ44?t=1143)).
4. **The biggest cost is often people waiting**: 2-hour jobs, 30-minute CI, rework. VMO2 counts developer and opportunity cost alongside compute ([VMO2 0:05:11](https://youtu.be/bPZHJ47MpWo?t=311)).

## Workflow: pick the lever

1. **Measure where time and money go**: per job and model runtime, rebuilds of unchanged models, peak contention (BigQuery slots over the reservation, Snowflake queuing, Redshift locks), CI duration, and how long developers wait.
2. **Rebuilding unchanged models → turn on dbt State** in *every* environment and project (it only reuses work it has recorded). Run twice before judging ([RxBenefits 0:15:11](https://youtu.be/Yn-UXiMvZ4I?t=911)). Then tune `lag_tolerance` per folder to real SLAs and collapse schedule-based jobs (dbt Labs went from 19 to 2 jobs) ([dbt Labs 0:03:31](https://youtu.be/3VWBjDq8yp4?t=211)).
3. **One warehouse size for everything → right-size per model**: downsize short and off-critical-path models, upsize models that spill to disk (faster *and* cheaper) ([Espresso 0:08:00](https://youtu.be/9WB2aT_xCUE?t=480)).
4. **Teams fighting over one cluster → split compute, not data**: producer plus per-team consumers via data sharing. Move dbt to its own elastic compute (Redshift: `datasharing: true`) ([KOHO 0:22:07](https://youtu.be/C05o-rKXZ44?t=1327)).
5. **Need minutes-fresh data for a small active subset → two modes, one codebase**: an env var filters an upstream "anchor" model. Inner joins carry the filter downstream ([WMCHealth 0:04:10](https://youtu.be/hGGS2Et4BIc?t=250)).
6. **Slow dev loop and CI → dbt v2**: static analysis catches errors while typing (VMO2 is testing whether this can replace a 20-30 minute `limit 0` CI pipeline). Use compare changes before pushing, and batch or local unit tests ([VMO2 0:08:00](https://youtu.be/bPZHJ47MpWo?t=480)).
7. **Prove it**: compare cost with and without State (Cost Insights), slot or credit peaks, runtime, dev wait time. Isolate each change. VMO2's 35% mixed the v2 engine and State ([VMO2 Q&A 0:24:01](https://youtu.be/bPZHJ47MpWo?t=1441)).

## Quick checks

| Look for | Do |
|---|---|
| Many jobs on different schedules, often clashing | Model-level `lag_tolerance` plus State. Keep a separate job only for multi-hour full refreshes ([dbt Labs 0:25:03](https://youtu.be/3VWBjDq8yp4?t=1503)) |
| Tests stopped running since State | Reused models skip their tests. Add a scheduled full test job (daily or weekly) ([RxBenefits 0:11:06](https://youtu.be/Yn-UXiMvZ4I?t=666)) |
| A model rebuilds every run | `dbt state explain --verbose -s model` (v1 plugin: `dbt-state explain`). Usual causes: nondeterministic Jinja (`invocation_id`, run timestamps, env vars), so use `compare_unrendered_code: true` on that model; a `select *` view over an external table; DDL outside dbt; a source updating every few minutes with no lag tolerance |
| Dev incremental passes, prod incremental fails | `pre_clone: always` so dev starts from a zero-copy clone of prod ([RxBenefits 0:22:05](https://youtu.be/Yn-UXiMvZ4I?t=1325)) |
| Worried dev tables get cloned into prod | `allow_clones: false` on the prod profile target |
| Model joins several sources with late arrivals | `require_fresh_data_from: all` instead of the default `any` |
| Peak contention over the slot reservation | State reuse and faster runs flatten peaks. Freed capacity matters most at peak hours ([VMO2 0:14:07](https://youtu.be/bPZHJ47MpWo?t=847)) |
| Lookup tables that almost never change | Very high `lag_tolerance` (RxBenefits uses up to a year) |

## Rules of thumb

- State is not a substitute for bad practice. Heavy full-refresh projects gain less. Views and their tests are where RxBenefits saw the most reuse ([RxBenefits 0:14:08](https://youtu.be/Yn-UXiMvZ4I?t=848)).
- `state:modified+` and dbt State are complementary. State applies after select/exclude.
- Agents running `dbt build` without knowing the DAG cost far less with State, because only the diff builds ([dbt Labs 0:05:34](https://youtu.be/3VWBjDq8yp4?t=334)).
- Bigger t-shirt sizes double cost but rarely double speed (Amdahl's law). Re-check sizing as data grows.
- Keep source freshness for alerting. State's freshness checks are for execution efficiency, not monitoring ([dbt Labs 0:21:06](https://youtu.be/3VWBjDq8yp4?t=1266)).
- Migrations: staged bets, a named owner on the keyboard, smallest project first, one per week, code freeze, full mirror run in staging ([CarGurus 0:09:01](https://youtu.be/yqCrNVFzLg8?t=541)).
- "You can't experiment when you're drowning in maintenance." Spend the time you get back on the next thing ([CarGurus 0:14:07](https://youtu.be/yqCrNVFzLg8?t=847)).

## Known gaps

- Companion skills: `dbt-agent-context` (context for analytics agents) and `dbt-agentic-dev` (agents that write dbt code).
- Results are per the videos and depend on each stack: RxBenefits 59% lower dbt warehouse cost over 60 days in prod and 92% fewer builds in lower environments; Espresso customer about 40% per quarter; VMO2 about 25% compute and 35% faster (v2 plus State combined); KOHO 6.5h to 2h at about the same cost; WMCHealth 72 to about 5 minutes. dbt State pricing and trials change, so check the dbt docs.
- The KOHO video's YouTube description describes a different KOHO talk (an AI analytics tool). This skill follows the transcript (Redshift data sharing).
- Config names and commands were checked against docs.getdbt.com (2026-10-26). Slide-only details (Cost Insights screens, heat maps) aren't reproduced.

## Sources

| Video | Channel | Date | Used for |
|---|---|---|---|
| [Reduce, reuse, recycle: how dbt State cut rebuilds by 92% at RxBenefits](https://www.youtube.com/watch?v=Yn-UXiMvZ4I) | dbt Labs | 2026-10-26 | Production results, rollout advice, configs explained, limits |
| [Optimizing your runs for lower compute, fresher data, and faster iteration with dbt State](https://www.youtube.com/watch?v=3VWBjDq8yp4) | dbt Labs | 2026-10-26 | How State decides, auto-deferral, clones, explain, 19→2 jobs, roadmap |
| [Most of your dbt models aren't in a hurry: How to stop paying for the whole DAG](https://www.youtube.com/watch?v=9WB2aT_xCUE) | dbt Labs | 2026-10-26 | Critical path, Amdahl sizing, spill, per-model warehouses |
| [What changes when 300 dbt users at Virgin Media O2 move to dbt v2 and dbt State](https://www.youtube.com/watch?v=bPZHJ47MpWo) | dbt Labs | 2026-10-26 | Hidden costs, slot contention, static analysis vs CI, migration problems |
| [From dbt Core to dbt v2: How CarGurus unlocked dbt State and AI at scale](https://www.youtube.com/watch?v=yqCrNVFzLg8) | dbt Labs | 2026-10-26 | Staged migration playbook, autofix, cutover steps, governed agents |
| [Getting instant feedback: The dbt v2-powered dbt developer experience](https://www.youtube.com/watch?v=81T3CTclWOw) | dbt Labs | 2026-10-26 | Lint, checks, docs v2, compare changes, local and batch tests |
| [Scaling dbt on Amazon Redshift: KOHO cut transformation runtime 70% without rewriting a single model](https://www.youtube.com/watch?v=C05o-rKXZ44) | dbt Labs | 2026-10-26 | Hub-and-spoke compute via data sharing, dbt on its own serverless |
| [From 72 minutes to 5: how one environment variable powers two dbt pipelines](https://www.youtube.com/watch?v=hGGS2Et4BIc) | dbt Labs | 2026-10-26 | Near-real-time plus historical from one codebase |
