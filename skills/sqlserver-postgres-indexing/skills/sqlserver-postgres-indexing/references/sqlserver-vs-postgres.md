# SQL Server vs Postgres: engine differences that affect tuning

Source: How to Think Like the Engine: SQL Server & PostgreSQL Edition (youtube.com/watch?v=ZV37v2pHaW8, 2026-10-26). Details are as the video describes them. Lines marked *(note)* are additions, not from the video.

## Contents
- Storage: clustered tables vs heaps
- Updates, locking and versions
- Hints vs hardware
- Ecosystem: built in vs extensions
- Quick comparison

## Storage: clustered tables vs heaps

Watch: [0:48:00](https://youtu.be/ZV37v2pHaW8?t=2880)
- **SQL Server**: most tables have a clustered index, so the table is sorted by the key you choose (often ID). A table without one is a heap, and its rows are identified by a RID (file:page:slot). All objects share one big data file, usually split only as it approaches a terabyte, mainly for backup and CHECKDB throughput ([0:56:00](https://youtu.be/ZV37v2pHaW8?t=3360)).
- **Postgres**: every table is an unsorted **heap**, and every primary key is nonclustered. Each row has a `CTID` (page number, tuple number). The tuple is really a row *version*, and `xmin`/`xmax` record which transactions can see it. You can `SELECT ctid, xmin, xmax` to see them ([0:51:05](https://youtu.be/ZV37v2pHaW8?t=3065)).
  - Each object gets its own files, split every 1 GB.
  - Page size can be changed only by compiling Postgres yourself, which almost nobody does.
  - *(note)* `CLUSTER` reorders a table once, and Postgres doesn't keep it in order afterwards.
- **What this means for indexes**:
  - Postgres index entries point to the CTID. SQL Server's point to the clustering key, which is added automatically ([1:32:07](https://youtu.be/ZV37v2pHaW8?t=5527)).
  - Looking rows up by ID in Postgres needs a separate index (the PK index) on top of the heap. SQL Server's clustered table already is that index.

## Updates, locking and versions

Watch: [1:57:09](https://youtu.be/ZV37v2pHaW8?t=7029)
- **SQL Server (default)**: updates rows **in place** on the page. One page gets written, and nonclustered indexes are untouched unless they contain the changed column. The costs:
  - **Readers and writers block each other.** This is why people reach for `NOLOCK` ([2:00:00](https://youtu.be/ZV37v2pHaW8?t=7200)).
  - **Rollbacks are slow**, because the old row has to be fetched back from the transaction log.
- **Postgres**: every update writes a **new row version**, on another page if there's no room on the current one ([2:02:00](https://youtu.be/ZV37v2pHaW8?t=7320)). The upside:
  - Readers read the old version instead of waiting, so readers and writers don't block each other.
  - Rollbacks are cheap: Postgres just marks which version is live with xmin/xmax.

  The downsides:
  - It can mean up to twice as many page writes in the worst case.
  - Dead versions have to be cleaned up by **vacuum** ([2:04:03](https://youtu.be/ZV37v2pHaW8?t=7443)).
  - *(note)* Ozar says index entries aren't touched unless the changed column is indexed. In Postgres that holds only for **HOT updates**: no indexed column changed *and* the new version fits on the same page. Otherwise every index gets a new entry. Leaving free space with `fillfactor` on hot tables helps.
- **Why heaps suit row versioning**: in a clustered table that's full, adding a version forces a **page split**, which causes locking, logging and cleanup problems. Think of a `LastAccessDate` that changes on every login ([2:12:05](https://youtu.be/ZV37v2pHaW8?t=7925)).
- **SQL Server versioning options** (all opt-in, which most apps never do until advised):
  - **RCSI** (since 2005): keeps versions in tempdb ([2:05:04](https://youtu.be/ZV37v2pHaW8?t=7504)).
  - **Accelerated Database Recovery** (2019): keeps versions inside user tables, like Postgres. Version cleanup was single-threaded in 2019 and one thread per database in 2022. Ozar still didn't recommend it, because user databases already run out of disk ([2:07:07](https://youtu.be/ZV37v2pHaW8?t=7627)).
  - **Optimized locking** (2025): Ozar is a "huge fan". It's on, and can't be turned off, in Azure SQL DB ([2:08:01](https://youtu.be/ZV37v2pHaW8?t=7681)).
- **Costs of keeping versions in user tables**: more cleanup work, slower rollbacks and killed queries, trouble with duplicate-key violations, and long or high-volume transactions make it worse. Only SQL Server backups grow, because it backs up raw pages ([2:09:01](https://youtu.be/ZV37v2pHaW8?t=7741)).
- **What each community complains about**: SQL Server people talk about fragmentation and index rebuilds. Postgres people talk about vacuum.
- **First action**: don't index frequently updated columns. On SQL Server, consider RCSI before adding `NOLOCK` hints.

## Hints vs hardware

Watch: [1:48:06](https://youtu.be/ZV37v2pHaW8?t=6486)
- **SQL Server** has always allowed hints, for example `WITH (INDEX(1))` to force a scan of the clustered index.
- **Postgres** avoided hints for decades, because the community treats bad plans as bugs to fix in the planner. Postgres 19 adds them through new optional contrib modules: `pg_plan_advice`, set with `SET pg_plan_advice.advice = 'INDEX_SCAN(t idx)'`. Release is expected in late 2026. Ozar disagrees that you'll "probably never need" hints: his very first demo attempt produced a bad plan ([1:49:08](https://youtu.be/ZV37v2pHaW8?t=6548)).
  - *(note)* Before Postgres 19, the `pg_hint_plan` extension is the usual route.
- **Each community's habit**: SQL Server people throw hints at problems, and Postgres people throw hardware. The reason is licensing. Per the video (2026), 4 cores of Azure SQL DB cost about $750–2,000/month, and the same budget buys about 8–16 cores of managed Postgres ([1:50:09](https://youtu.be/ZV37v2pHaW8?t=6609)). Per-core licensing makes SQL Server shops stingy with CPU per query, while Postgres shops often find more hardware cheaper than tuning time ([1:56:08](https://youtu.be/ZV37v2pHaW8?t=6968)).
- **His preference**: tune queries, indexes and settings first.

## Ecosystem: built in vs extensions

Watch: [1:20:01](https://youtu.be/ZV37v2pHaW8?t=4801)
- **SQL Server**: one vendor, with everything in the box (Query Store, availability groups, plans in SSMS). Extensions are taboo, so skills transfer between employers.
- **Postgres**: a small core team (7 people, employed by various companies) keeps the core small to keep support load down. Features come as extensions: thousands of them, with no official store.
  - Each company has its own standard set, so you relearn the tooling with every new job.
  - More extensions mean more conflicts and more upgrade risk ([1:29:01](https://youtu.be/ZV37v2pHaW8?t=5341)).
- **Support**:
  - Microsoft offers enterprise support ("one throat to choke"). Always arrive with a minimal repro script ([1:14:02](https://youtu.be/ZV37v2pHaW8?t=4442)).
  - Postgres support goes through mailing lists, third-party vendors, or hiring a feature's author directly. Plan for more time spent building relationships ([1:27:07](https://youtu.be/ZV37v2pHaW8?t=5227)).

## Quick comparison

| | SQL Server | Postgres |
|---|---|---|
| Table storage | Clustered index (usually) | Heap, always |
| Row pointer in indexes | Clustering key (heap: RID) | CTID |
| Measure | `STATISTICS IO` logical reads | `EXPLAIN (ANALYZE, BUFFERS)` buffers |
| Plan direction | Right to left, top to bottom | Bottom up |
| "Seek" | Index Seek | Index Scan (low buffers) |
| Missing-index hints | Built in | Extensions only |
| Update | In place (row versioning is opt-in) | New row version + vacuum |
| Hints | Always available | Postgres 19 `pg_plan_advice`, or `pg_hint_plan` |
