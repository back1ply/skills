# dbt State: how it decides, configs, rollout, limits

Sources: dbt Summit 2026 talks (dbt Labs channel, 2026-10). Config names and defaults checked against docs.getdbt.com on 2026-10-26. Results are per the videos.

## Contents
- How dbt State decides
- Configs (current names and defaults)
- Development: auto-deferral and clones
- Rollout checklist
- Limits and gotchas
- Results reported

## How dbt State decides

Watch: [dbt Labs 0:02:30](https://youtu.be/3VWBjDq8yp4?t=150)

For each selected node, State answers two questions:
1. **Did the code change?** Compare the query, and upstream queries, with the last recorded build.
2. **Is there new data that someone needs?** Check source freshness. By default this is the warehouse information schema, a metadata-only query that costs nothing. You can override it with `loaded_at_query` (e.g. "only fresh if 1,000+ new rows and 2+ hours passed"). That query costs a little, so use it only where metadata is misleading, such as streaming sources that always look fresh ([0:22:07](https://youtu.be/3VWBjDq8yp4?t=1327)).

Then for each node it decides: **skip** (the object already exists and is current), **zero-copy clone** (an equivalent build exists in another environment), or **rebuild**. It only acts when the result is provably the same as a run without State ([0:08:01](https://youtu.be/3VWBjDq8yp4?t=481)). RxBenefits compares it to memoization ([0:06:12](https://youtu.be/Yn-UXiMvZ4I?t=372)).

Availability at the talk: dbt Core 1.7-1.12 via a pip-installed plugin, built into dbt v2 (`dbt login`), and a checkbox on the dbt platform ([0:06:34](https://youtu.be/3VWBjDq8yp4?t=394)). Usage-based pricing: check current docs.

## Configs (current names and defaults)

Set under `+state:` in `dbt_project.yml` (project, folder or model), except the profile-level ones.

| Config | Default | Use |
|---|---|---|
| `lag_tolerance` | `45m` | Minimum time since the last build before new upstream data triggers a rebuild. Code changes always rebuild. Set it from stakeholder SLAs per folder. Higher in dev. Very high for lookup tables. RxBenefits: "how long do you let the grass grow before you mow" ([0:18:02](https://youtu.be/Yn-UXiMvZ4I?t=1082)) |
| `require_fresh_data_from` | `any` | `all` for joins where you must wait for every parent (late-arriving data). Keep `any` when one parent almost never updates, or the model would never rebuild ([0:20:03](https://youtu.be/Yn-UXiMvZ4I?t=1203)) |
| `pre_clone` | `if_missing` | `always` clones prod incremental models and snapshots into dev before each run, so dev tests the real incremental path rather than a first-run full refresh ([0:22:05](https://youtu.be/Yn-UXiMvZ4I?t=1325)) |
| `compare_unrendered_code` | `false` | Default compares only rendered SQL, so `invocation_id()`, `run_started_at`, `env_var('AIRFLOW_RUN_ID')` or UUID macros rebuild every run. `true` rebuilds only when **both** the Jinja template and the rendered SQL changed, so fewer rebuilds. Trade-off: with `true`, changes that appear only in rendered SQL (e.g. introspective macros like `get_column_values` picking up new values) won't trigger a rebuild. Use it per model, not project-wide. (RxBenefits described the default differently ([0:21:04](https://youtu.be/Yn-UXiMvZ4I?t=1264)); this row follows docs.getdbt.com, 2026-10) |
| `execute_hooks_on_any_reuse` | `false` | Run pre- and post-hooks even when a node is reused |
| `evaluate_volatile_sql` | `false` | Compare the runtime output of volatile SQL functions |
| `allow_clones` (profile) | `true` | Set `false` on prod so dev or CI tables are never cloned into prod ([0:08:00](https://youtu.be/Yn-UXiMvZ4I?t=480)) |
| `defer_to_target` (profile) | `prod` | Self-managed: which target to defer to |

**Explain a decision**: `dbt state explain --verbose -s my_model` (v2), `dbt-state explain` (v1 plugin), or the **Explain** tab on a platform job run. It shows table, query and data-freshness analysis ([0:11:06](https://youtu.be/3VWBjDq8yp4?t=666)).

## Development: auto-deferral and clones

Watch: [dbt Labs 0:09:04](https://youtu.be/3VWBjDq8yp4?t=544)

- Building one model in dev used to fail because its parents didn't exist there, unless you managed `--defer --state` manifests. State defers automatically. `state:modified` no longer needs a manifest file either ([0:10:05](https://youtu.be/3VWBjDq8yp4?t=605)).
- Building a model plus its parents in dev gives zero-copy clones of unchanged parents, and skips the changed model if that exact version already ran ([0:13:09](https://youtu.be/3VWBjDq8yp4?t=789)).
- Clones work **across dev environments**: after rebasing on a merged but undeployed change, you clone a colleague's build instead of re-running it ([0:15:10](https://youtu.be/3VWBjDq8yp4?t=910)). Cloning needs read access to the other environment. Without it you still get skips and deferral ([0:29:06](https://youtu.be/3VWBjDq8yp4?t=1746)).
- Coming, per the talk: lag tolerance recommendations from warehouse query history (who actually reads a table, how often), and **column-aware** CI that rebuilds downstream models only if they use the changed column ([0:17:01](https://youtu.be/3VWBjDq8yp4?t=1021)).

## Rollout checklist

Watch: [RxBenefits 0:25:03](https://youtu.be/Yn-UXiMvZ4I?t=1503)

1. Enable it in **all environments and all projects** at once. It only reuses work it has recorded, so a gradual rollout hides the savings. (RxBenefits enabled one project's environments, assuming that covered everything, and found later it didn't.)
2. Expect no change on the first run. Reuse starts on the second.
3. Add a scheduled **full test job**, because reused models don't re-run their tests.
4. Set **spend alerts** on the warehouse.
5. Audit Jinja and `select *` views. Find steady rebuilders with `explain`.
6. Tune `lag_tolerance` with stakeholders, then consolidate jobs. Keep a separate job only for multi-hour full refreshes that would block a frequent cadence ([0:26:03](https://youtu.be/3VWBjDq8yp4?t=1563)).
7. Check unsupported modes early. RxBenefits hit "compatible mode" being unsupported, and dbt fixed it in about 2 weeks. VMO2's custom FinOps configs (dynamic storage billing model, on-demand vs reservation routing) didn't yet work under State ([VMO2 0:19:01](https://youtu.be/bPZHJ47MpWo?t=1141)).

## Limits and gotchas

- It can't reuse work done where State wasn't enabled, including a colleague without it ([RxBenefits 0:16:00](https://youtu.be/Yn-UXiMvZ4I?t=960)).
- It doesn't track DDL/DML outside dbt (stored procedures, tasks), but it detects the mismatch and rebuilds.
- Views rebuild only when their query changes, since upstream data doesn't matter for a stored query. Exception: `select *` from an external table (not from a CTE or subquery) always recreates, to avoid stale views ([dbt Labs 0:30:06](https://youtu.be/3VWBjDq8yp4?t=1806)).
- Snapshots ran on every build at the time of the talk, so schedule daily snapshots separately ([0:27:05](https://youtu.be/3VWBjDq8yp4?t=1625)).
- No alerting on reuse. Keep `dbt source freshness` for monitoring.
- Not a substitute for good modeling. Projects with lots of full refreshes gain less.

## Results reported

| Team | Result (per the video) |
|---|---|
| RxBenefits ([0:08:00](https://youtu.be/Yn-UXiMvZ4I?t=480)) | Prod, about 60 days: dbt warehouse cost -59% (over $8k), about 716k model reuses. Lower environments: 92% fewer builds. This came *after* already cutting about $600k/yr via Gen2 and adaptive warehouses and auto-suspend |
| dbt Labs ([0:03:31](https://youtu.be/3VWBjDq8yp4?t=211)) | 19 clashing jobs → 2 |
| Fanatics (per description) | 25-30% model reuse, about 15% Snowflake savings on a pilot |
| VMO2 ([0:11:05](https://youtu.be/bPZHJ47MpWo?t=665)) | 1,424-model job: 1h53 → 1h13 (-35%), slots 4,500 → 3,400 per hour, peaks over the 5,000 reservation nearly gone. Only 32 models were reused, and the baseline was their normal run without v2 or State. The speakers credited several factors, not State alone: faster Rust startup per model, heavy queries over their object-style source data, and fewer parallel clashes at peak ([0:24:01](https://youtu.be/bPZHJ47MpWo?t=1441)) |
| CarGurus ([0:12:04](https://youtu.be/yqCrNVFzLg8?t=724)) | Rolling out. Target: 75% of jobs on State by year end |
