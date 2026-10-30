---
name: server-capacity-tuning
description: Finds what limits how many users a single small server can handle (CPU, memory, file descriptors, disk sync, or the load generator itself) and picks the optimizations that raise it, using results from the $12 Server Challenge (about 30 web servers on 1 vCPU / 2 GB with SQLite). Use when load testing or capacity planning a service, reading p95/p99 results, hitting "Too many open files" / EMFILE, OOM kills or iowait under load, tuning SQLite (WAL, synchronous, group commit, checkpoints), comparing epoll vs io_uring, keep-alive and idle-connection handling, or asking "how many users can my server handle".
---

# Server capacity tuning

Distilled from "I Asked Developers to Max Out a $12 Server (again)" (Arjay McCandless, 2026-10-23), checked against the challenge repo's official results (github.com/arjaythedev/twelve-dollar-server-challenge). Detail in [references/limits-and-fixes.md](references/limits-and-fixes.md); per-entry results in [references/results-2026-10.md](references/results-2026-10.md).

## Core mental model
Every server stops at one limit first: **CPU, memory, file descriptors (connections), disk sync waits, or the load generator**. Language matters less than which limit you hit and how you move it. At 1 vCPU / 2 GB, the same Go service went from 55k users (net/http, out of memory) to 165k (raw epoll + C SQLite helper). Six entries stopped at the 65k file-descriptor limit, not because they were slow (four tied at 71k with CPU anywhere from 31% to 94%). Find the binding limit before optimizing anything.

## Workflow: find and raise the limit
1. **Define pass/fail** like the challenge: hold the load for 5 minutes with p95 < 500 ms, p99 < 1 s and < 1% errors. Search by doubling the user count, then narrow it down; confirm with the full hold.
2. **At the first failing load, record**: CPU %, peak memory (cgroup), iowait %, open fds and connection count, error types (timeouts, resets, EMFILE), OOM kills, and the load generator's own CPU and ports.
3. **Name the limit** with the table below. If CPU is low and the run still fails, it's not CPU.
4. **Fix that limit only**, then re-run. A new limit shows up; repeat.
5. **Check the trade-offs** you made against production needs: durability, correctness, maintenance (see Rules of thumb).

## Quick checks: which limit?
| Symptom at the failing load | Limit | First fix (details in limits-and-fixes) |
|---|---|---|
| CPU ~90-100%, latency climbs smoothly | CPU | Less work per request: no framework/ORM layers, prepared statements, let SQLite build the JSON |
| Process OOM-killed, or memory near RAM | Memory | Shrink per-connection memory: small/shared buffers, no idle response buffers |
| Errors stuck at ~0.9-1% while CPU is low; fds at ~65k | File descriptors | Close idle keep-alive connections under pressure, a second process (SO_REUSEPORT), or io_uring registered files |
| Crash exactly at the fd limit | Fd-exhaustion error path | Make the EMFILE path allocate nothing (no logging that opens a handle) |
| iowait 20-40%, CPU about 50% | Disk sync | Group commit; WAL + `synchronous=NORMAL` if the durability trade-off is OK |
| Server CPU low, generator out of ports/CPU | Load generator | More generator machines or target IPs (about 60k source ports per client IP → target) |
| Latency spikes at intervals, WAL file grows | SQLite checkpoints | Checkpoint on its own thread, or at a quiet point in the event loop |

## Rules of thumb
- Persistent connections cost fds and memory even while users are idle. Users who "think" for about 10 s between requests make idle-connection cost the main design problem.
- Batch everything per event-loop turn: completions, reads in one transaction, writes in one group commit. A little latency buys a lot of throughput.
- One writer connection plus a read pool avoids fighting over SQLite's write lock. Never let a busy database wait block an event loop: queue and retry.
- Moving SQL row → JSON into SQLite itself (json functions) removes many copies and allocations in every language.
- Results depend on hardware. The same code scored about 2x higher on the second VPS. Compare only runs on the same box.
- Things the fast entries did that the creator wouldn't ship: `synchronous=NORMAL` (a power loss can drop the last commits), compiling against SQLite internals, reads that can see uncommitted writes, skipping token expiry checks.

## Known gaps
- Only one workload was tested (a small read-heavy feed API on SQLite, about 1 request per user every 10 s). Write-heavy or multi-core workloads may rank differently.
- The video shows charts and code on screen that aren't in the transcript. The repo has the code for every entry.

## Sources
| Source | Channel | Date | Used for |
|---|---|---|---|
| [I Asked Developers to Max Out a $12 Server (again)](https://www.youtube.com/watch?v=-BFt49ula08) | Arjay McCandless | 2026-10-23 | Techniques, limits, trade-offs; transcript in `data/raw/-BFt49ula08.json` |
| [Challenge repo, batch-2 report](https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/main/benchmarks/batch-2.md) | arjaythedev | 2026-10-22 | Official numbers and the F# correction |
