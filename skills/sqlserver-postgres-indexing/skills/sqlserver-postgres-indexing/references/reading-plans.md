# Reading plans and measuring work: SQL Server and Postgres

Source: How to Think Like the Engine: SQL Server & PostgreSQL Edition (youtube.com/watch?v=ZV37v2pHaW8, 2026-10-26). Details are as the video describes them. Lines marked *(note)* are additions, not from the video.

## Contents
- Measuring work
- SQL Server plans
- Postgres plans
- Worked example: the same query, two plans

## Measuring work

Watch: [0:16:00](https://youtu.be/ZV37v2pHaW8?t=960)
- **SQL Server**: run `SET STATISTICS IO, TIME ON`. Output goes to the Messages tab: logical reads per table (8K pages), CPU time and elapsed time. Overhead is low and limited to your session.
- **Postgres**: run `EXPLAIN` with options. "Buffers" are the same 8K pages. Postgres users usually look at execution time instead ([0:59:05](https://youtu.be/ZV37v2pHaW8?t=3545)).
  - *(note)* The usual form is `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) <query>`. `ANALYZE` runs the query for real, so wrap writes in `BEGIN … ROLLBACK`. Since Postgres 18, `BUFFERS` is on by default with `ANALYZE`.
- **Why reads beat time**:
  - CPU and elapsed time vary 5–10% between identical runs, even on bare metal ([0:19:11](https://youtu.be/ZV37v2pHaW8?t=1151)).
  - SSMS's message time and plan time don't even match each other ([0:24:01](https://youtu.be/ZV37v2pHaW8?t=1441)).
  - Logical reads stay stable, but not perfectly. Ozar has documented cases where they vary.
- **Caveat**: fewer reads usually means faster, but not always. A version that reads slightly more data can still win if it reads it more efficiently or runs in parallel ([0:20:13](https://youtu.be/ZV37v2pHaW8?t=1213)).
- **Benchmarking**: alternate old and new, run many times, and take medians. Early runs are skewed by a cold cache.
- **First action**: record the baseline reads/buffers before changing anything.

## SQL Server plans

Watch: [0:22:17](https://youtu.be/ZV37v2pHaW8?t=1337)
- Turn on the **actual** plan in SSMS. It only affects your session and adds a little overhead. "Showplan", "query plan" and "execution plan" all mean the same thing.
- Read **right to left, top to bottom**. Each operator is a small "microservice" that does one or two jobs and passes rows to the next ([0:26:02](https://youtu.be/ZV37v2pHaW8?t=1562)).
- **Clustered index scan** = reading the table itself. **Racing stripes** (Erik Darling's term) on an icon = the operator ran in parallel.
- `COUNT(*)` example: scan → hash match (buckets) → compute scalar (a calculator icon, the count) → parallelism **gather streams** (a manager combining the workers' totals) ([0:28:04](https://youtu.be/ZV37v2pHaW8?t=1684)). The plan doesn't link operators back to query text, so you have to learn what each operator does.
- **Index seek** means "we know where to start reading". It can still read the whole index ([0:47:13](https://youtu.be/ZV37v2pHaW8?t=2833)).
- **Key lookup** means going back to the table for columns the index doesn't have. Plans look flat, but the lookup runs once per row: 3,000 Brents meant 3,000 lookups ([1:43:12](https://youtu.be/ZV37v2pHaW8?t=6192)).
- **Missing index hint** ("Clippy"): shows an estimated impact such as "99% faster". Take it as a starting point and design the index yourself ([0:31:08](https://youtu.be/ZV37v2pHaW8?t=1868)).
- **Parallel clue**: CPU time higher than elapsed time ([0:18:09](https://youtu.be/ZV37v2pHaW8?t=1089)).

## Postgres plans

Watch: [1:01:06](https://youtu.be/ZV37v2pHaW8?t=3666)
- Text plans are the norm. Use `FORMAT JSON` and paste the output into a visualizer:
  - explain.dalibo.com (PEV2). It also comes as a self-hosted HTML file.
  - pgMustard: gives advice and has AI features (about $500/year, per the video).
  - DBeaver's paid edition has a visualizer built in.
- **Privacy**: hosted visualizers store your plan on their server, and plans carry company IP. Keep the "ask me before sharing" warning switched on, or host PEV2 internally ([1:02:08](https://youtu.be/ZV37v2pHaW8?t=3728)).
- Data flows **bottom up**. Rather than reading the whole plan, look for the nodes with warning icons:
  - **slow**: took the most time.
  - **expensive estimate**: what the planner expected to cost most, which isn't necessarily the real cost.
  - **bad estimate**: wrong row count.
  - **filtered a lot**: read far more rows than it returned, which means you need an index ([1:04:02](https://youtu.be/ZV37v2pHaW8?t=3842)).
- Everything is called a "scan", including what SQL Server calls a seek. Judge by buffers: an index scan that reads 3 buffers is a seek ([1:37:01](https://youtu.be/ZV37v2pHaW8?t=5821)).
- **Hidden lookups**: on small results, the heap fetch is folded into the index node, so the plan looks as if only the index was touched. On larger results (16,000 Alexes) the index step and heap step show separately. This is by design, not a bug ([1:39:05](https://youtu.be/ZV37v2pHaW8?t=5945)).
  - *(note)* Technically, an Index Scan always visits the heap. Larger results usually switch to a Bitmap Index Scan feeding a Bitmap Heap Scan. An **Index Only Scan** is the one that avoids the heap.
- **Cost** is an abstract planner unit, like SQL Server's "query bucks" (Kendra Little's term), but on a different scale. Don't compare costs across engines ([1:38:02](https://youtu.be/ZV37v2pHaW8?t=5882)).
- **No built-in missing-index suggestions.** Use an extension, or simply index the filter on any query that reads a lot and that users complain about ([1:31:04](https://youtu.be/ZV37v2pHaW8?t=5464)).
  - *(note)* Common options: `hypopg` (hypothetical indexes), `pg_qualstats`, and managed-cloud index advisors.

## Worked example: the same query, two plans

Watch: [1:40:06](https://youtu.be/ZV37v2pHaW8?t=6006)
- The query: `DisplayName LIKE 'Brent%' AND Location LIKE 'Las Vegas%'`, with the same index on DisplayName in both engines.
- **Postgres** ignored the index and scanned the whole heap: about 400,000 buffers, roughly 1 second.
- **SQL Server** sought into Brent* (about 3,000 rows, estimated 1,000) and ran 3,000 key lookups to check Location: 38 ms.
- **Lesson**: each optimizer is a different "choose your own adventure book". They estimate rows differently and choose different plans. SQL Server's book is bigger, so planning takes longer, and it caches plans for reuse ([1:45:02](https://youtu.be/ZV37v2pHaW8?t=6302)).
- **First action after a migration**: compare plans for your top queries on both engines. Don't assume they'll match.
