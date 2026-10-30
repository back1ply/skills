---
name: sqlserver-postgres-indexing
description: Diagnoses slow queries and designs indexes on Microsoft SQL Server and PostgreSQL by thinking like the engine (8K pages, clustered tables vs Postgres heaps, seeks/scans, key lookups, reads as the unit of work), and explains how the two engines differ on plans, updates, locking/MVCC, hints and tooling. Use when a SQL Server or Postgres query is slow, choosing which columns go in an index and in what order, reading an execution plan or EXPLAIN output, comparing STATISTICS IO with EXPLAIN BUFFERS, migrating between SQL Server and Postgres, or the user mentions key lookup, index seek vs scan, missing index recommendation, CTID, heap, RCSI, vacuum, or "why isn't my index used".
---

# SQL Server & Postgres indexing: think like the engine

Distilled from Brent Ozar's free class "How to Think Like the Engine: SQL Server & PostgreSQL Edition" (Brent Ozar Unlimited). Plan-reading detail is in [references/reading-plans.md](references/reading-plans.md), and engine differences are in [references/sqlserver-vs-postgres.md](references/sqlserver-vs-postgres.md).

## Core mental model

Both engines store tables and indexes as **8K pages** and read or write whole pages, never single rows. A query's cost is mostly **how many pages it touches** ([0:10:03](https://youtu.be/ZV37v2pHaW8?t=603)). With no index that matches the filter, the engine reads every page, so `WHERE DisplayName = 'x'` reads as much as `COUNT(*)` ([0:25:02](https://youtu.be/ZV37v2pHaW8?t=1502)). A nonclustered index is a narrower, sorted copy of some columns, and your job is to put the right columns on it in the right order ([0:42:04](https://youtu.be/ZV37v2pHaW8?t=2524)). The payoff in the demo: 300,000 reads dropped to 8 on SQL Server, and about 400,000 dropped to 3 on Postgres ([0:40:02](https://youtu.be/ZV37v2pHaW8?t=2402), [1:36:00](https://youtu.be/ZV37v2pHaW8?t=5760)).

## Workflow: tune a slow query

1. **Measure pages, not time.**
   - SQL Server: run `SET STATISTICS IO, TIME ON` and compare **logical reads**. It's safe in production because it only affects your session ([0:16:00](https://youtu.be/ZV37v2pHaW8?t=960)).
   - Postgres: run `EXPLAIN (ANALYZE, BUFFERS)` and compare **buffers** ([1:00:05](https://youtu.be/ZV37v2pHaW8?t=3605)).
   - Don't worry about physical reads; they depend on what's in cache. Reading less is better either way ([0:20:13](https://youtu.be/ZV37v2pHaW8?t=1213)).
2. **Get the actual plan.** In SSMS, turn on the actual plan (not the estimated one) and read it **right to left, top to bottom**. In Postgres, add `FORMAT JSON` and paste the output into a visualizer, where data flows **bottom up** ([0:22:17](https://youtu.be/ZV37v2pHaW8?t=1337), [1:04:02](https://youtu.be/ZV37v2pHaW8?t=3842)).
3. **Find the waste.** Look for scans of the whole table, operators that **remove most of the rows they read** (a sign of a missing index), and key lookups that run thousands of times ([1:06:05](https://youtu.be/ZV37v2pHaW8?t=3965)).
4. **Design the index.** Put a column from the WHERE clause first, because you can only seek on the **leading column** ([0:43:05](https://youtu.be/ZV37v2pHaW8?t=2585)). Add the columns the query needs if you want to avoid lookups. Leave out frequently updated columns where you can ([1:59:12](https://youtu.be/ZV37v2pHaW8?t=7152)).
5. **Re-measure.** Run the old and new versions alternately, many times, and compare **medians, not averages**. Below about 5%, the difference is noise ([0:21:15](https://youtu.be/ZV37v2pHaW8?t=1275)).
6. **Report** the change in reads and elapsed time. Reads prove the fix, and elapsed time is what users notice ([0:26:02](https://youtu.be/ZV37v2pHaW8?t=1562)).

## Quick checks

| Look for | Meaning |
|---|---|
| SQL Server CPU time > elapsed time | The query went parallel |
| "Index Seek" | You know where to start reading, but it may still read everything ([0:47:13](https://youtu.be/ZV37v2pHaW8?t=2833)) |
| Key Lookup (SQL Server) | Goes back to the table for columns the index lacks; runs once per row |
| Postgres "Index Scan" with low buffers | What SQL Server calls a seek. Postgres calls everything a "scan" ([1:37:01](https://youtu.be/ZV37v2pHaW8?t=5821)) |
| Postgres "Rows Removed by Filter" ≈ rows read | The query needs an index on that filter |
| Plan cost compared across engines | Meaningless: different units ([1:38:02](https://youtu.be/ZV37v2pHaW8?t=5882)) |
| Reads/buffers compared across engines | Also meaningless; off-row storage settings change them ([1:00:05](https://youtu.be/ZV37v2pHaW8?t=3605)) |
| SQL Server green missing-index hint | Ozar calls it "Clippy": a quick, best-effort guess, not a design |

## Rules of thumb

- If you have to find rows by a column, you need an index on that column, whether or not you like indexing varchar columns. Full-text and hash tricks fail for "starts with" searches ([0:33:01](https://youtu.be/ZV37v2pHaW8?t=1981)).
- Every index is another copy to keep in sync. More indexes mean slower inserts, updates and deletes ([0:35:04](https://youtu.be/ZV37v2pHaW8?t=2104)).
- SQL Server silently adds the clustering key, and Postgres adds the CTID, to every nonclustered index so it can find the row in the table ([0:45:09](https://youtu.be/ZV37v2pHaW8?t=2709)).
- Large values (MAX types, JSON, XML) are stored off-row and cost extra reads ([0:11:03](https://youtu.be/ZV37v2pHaW8?t=663)).
- Choose collations before the first big data load. Changing one later rewrites every index. For migrations, test sort order and WHERE behavior on both engines first ([0:39:13](https://youtu.be/ZV37v2pHaW8?t=2353), [1:36:00](https://youtu.be/ZV37v2pHaW8?t=5760)).
- The same query and the same indexes can get very different plans on the two engines, because each has its own optimizer and its own row estimates. Re-check hot queries after a migration ([1:47:05](https://youtu.be/ZV37v2pHaW8?t=6425)).
- Don't paste plans into public visualizers without permission, because plans contain company IP. Host the visualizer internally ([1:02:08](https://youtu.be/ZV37v2pHaW8?t=3728)).

## Known gaps

- The class covers single-table seeks, scans and lookups only. It doesn't cover multi-column key order, joins, statistics or B-tree internals. Ozar defers those to his paid index-tuning classes and doesn't explain how to make Postgres choose the Brent/Las Vegas lookup plan.
- Slides, printed page handouts and demo scripts are at brentozar.com/go/engine. They aren't in the transcript.
- His demo setup was SQL Server 2025 with SSMS 22, Postgres 18 with default settings, and the Stack Overflow 2024 database. Prices and timings are from the video (2026).

## Sources

| Video | Channel | Date | Used for |
|---|---|---|---|
| [How to Think Like the Engine: SQL Server & PostgreSQL Edition](https://www.youtube.com/watch?v=ZV37v2pHaW8) | Brent Ozar Unlimited | 2026-10-26 | Page/index mental model, measuring, plan reading, index design rules, engine differences |
