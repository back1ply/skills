# dbt compute levers beyond dbt State

Sources: dbt Summit 2026 talks (dbt Labs channel, 2026-10). Results are per the videos. Vendor tools (Espresso AI) are as presented.

## Contents
- Right-size off the critical path (Espresso AI)
- Split compute, not data (KOHO on Redshift)
- Two modes, one codebase (WMCHealth)
- Measure contention, not just totals (VMO2 on BigQuery)

## Right-size off the critical path (Espresso AI)

Watch: [0:01:05](https://youtu.be/9WB2aT_xCUE?t=65)

- **Critical path**: the longest dependent chain sets total latency. Everything else has slack.
- Warehouses aren't DAG-aware. One warehouse for all models queues work in series. Running independent nodes in parallel can halve wall time at the same cost ([0:03:07](https://youtu.be/9WB2aT_xCUE?t=187)).
- **Sizing math** ([0:05:10](https://youtu.be/9WB2aT_xCUE?t=310)): each t-shirt size doubles machines and price per hour, but speedup ranges from about 2x down to almost nothing, depending on how parallel the remaining work is (Amdahl's law). Look at the time vs cost curve per query. Small → medium may be nearly free if it runs twice as fast. Medium → large for a 10% speedup isn't worth it.
- **Do it yourself** ([0:08:00](https://youtu.be/9WB2aT_xCUE?t=480)):
  1. Compute the critical path (software or an agent can do it from the manifest and run timings).
  2. Downsize everything off it, aggressively for short queries (a 5-second query is rarely on the path).
  3. **Upsize queries that spill** to local or remote disk. They often get more than 2x faster, so they end up cheaper too ([0:09:01](https://youtu.be/9WB2aT_xCUE?t=541)).
  4. Use per-model warehouse config, measure, iterate.
- **Why it's hard to keep right** ([0:10:02](https://youtu.be/9WB2aT_xCUE?t=602)): each query has its own CPU and memory profile. Concurrency and queuing on shared warehouses change the answer. Data growth differs by model (scans grow linearly, joins N log N), so revisit regularly. A model can be on the critical path in one job and off it in another.
- Espresso AI automates this with a proxy plus reinforcement learning, routing at runtime. Authentic Insurance reported about 40% savings per quarter ([0:18:04](https://youtu.be/9WB2aT_xCUE?t=1084)). The DIY heuristics above work without it.

## Split compute, not data (KOHO on Redshift)

Watch: [0:19:03](https://youtu.be/C05o-rKXZ44?t=1143)

- **Starting point**: one provisioned Redshift cluster for ingestion, dbt, BI, ML and ad hoc work. Over 15k raw datasets, 3k+ dbt nodes, 200+ TB. The nightly dbt run took 6.5h and spilled into business hours, with regulatory settlement-file SLAs at risk. Bad ad hoc queries caused locks that slowed dbt. The usual fix of "add nodes" just grew the bill ([0:18:02](https://youtu.be/C05o-rKXZ44?t=1082)).
- **Hub and spoke via data sharing**: the provisioned cluster stays the producer, owning raw data. Each read-only team (BI, data science, ML) gets its own serverless workgroup reading the same storage. No copies, no new pipelines, the same governed ingestion ([0:20:04](https://youtu.be/C05o-rKXZ44?t=1204)).
- **The blocker**: dbt had to stay on the producer, because the adapter used Postgres catalog tables that only see the connected database. So the cluster stayed sized for the 6-hour dbt run, 24 hours a day ([0:21:06](https://youtu.be/C05o-rKXZ44?t=1266)).
- **The fix**: `datasharing: true` in the dbt-redshift profile (beta, dbt-redshift 1.11+; also a project setting on the dbt platform). The adapter then uses Redshift `SHOW` commands and can read and write across databases and clusters (`{{ config(database='other_db') }}`). dbt moved to its own serverless workgroup, so it can use more compute for a shorter time ([0:22:07](https://youtu.be/C05o-rKXZ44?t=1327)).
- **Result**: 6.5h → 2h at about the same cost, zero model changes, about 2 months. It also gave per-team chargeback (each team chooses between optimizing models and paying for compute) and room to run marts several times a day ([0:25:03](https://youtu.be/C05o-rKXZ44?t=1503)).
- **Transferable rule**: when workloads contend, give each its own elastically sized compute over shared storage, and put dbt on compute you pay for only while it runs. The same idea applies to Snowflake (warehouse per workload) and BigQuery (reservations and assignments).

## Two modes, one codebase (WMCHealth)

Watch: [0:04:10](https://youtu.be/hGGS2Et4BIc?t=250)

- **Need**: clinicians want active patients' data every 5 minutes (2-5% of rows). Analysts want full history nightly. Same business logic.
- **Rejected** ([0:03:08](https://youtu.be/hGGS2Et4BIc?t=188)): a bigger warehouse (not cost-effective), two projects (duplicate logic, against DRY), and incrementals alone (downstream processing was still too heavy, especially with window functions and aggregations).
- **Pattern**:
  - `env_var('ENV_NRT')` = 1 adds a filter in an upstream **anchor** model (active, not-discharged encounters). In the actual Jinja it's about three lines.
  - The same flag switches `materialized` (small active set as a `table`, history as `incremental`) and the target database (`live_prod` vs `prod`, identical schemas) ([0:06:12](https://youtu.be/hGGS2Et4BIc?t=372)).
  - **Inner joins to the anchor carry the filter downstream for free.** Only models that left-join the anchor need an explicit where filter. You don't touch every model ([0:07:14](https://youtu.be/hGGS2Et4BIc?t=434)).
  - Two identical dbt platform jobs with the same DAG, differing only in the env var: the live job every 5 minutes, nightly with 0 ([0:08:00](https://youtu.be/hGGS2Et4BIc?t=480)).
- **Result**: 4,340s → 278s (-93.6%), more than 99% fewer rows processed (billions → millions), under the 5-minute SLA on an extra-small warehouse ([0:09:02](https://youtu.be/hGGS2Et4BIc?t=542)).
- **Operational notes**: separate databases avoid races between the two jobs. Ingest facts every 1-3 minutes but dimensions every few hours (they rarely change). End-to-end latency is about 5 minutes plus ingestion, roughly 8-10 minutes. Source freshness set to warn with a 10-minute tolerance. In dev, set the env var per developer or in the run command ([0:27:02](https://youtu.be/hGGS2Et4BIc?t=1622)).
- **Applies to**: today's orders vs order history, active vs historical transactions, any active vs archive split.

## Measure contention, not just totals (VMO2 on BigQuery)

Watch: [0:12:05](https://youtu.be/bPZHJ47MpWo?t=725)

- Plot slot use against the reservation line (theirs is 5,000). Peaks above it mean queuing that delays everything. A heat map of competition over time shows a "rush hour" (sustained high contention for about 30 minutes) versus short bursts.
- On-demand pricing turns saved bytes into money directly (about $96, -25% per run of one job). On reservations, saved slots become *capacity*, valuable mostly at peak hours (6-7am in their case), not mid-afternoon ([0:14:07](https://youtu.be/bPZHJ47MpWo?t=847)).
- Count all costs: compute, CI pipeline time (every PR triggers validation), developer hours lost to waiting and context switching, and opportunity cost (decisions not made).
