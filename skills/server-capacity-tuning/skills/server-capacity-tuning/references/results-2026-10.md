# $12 Server Challenge: batch 2 results (2026-10-20/21)

Source: github.com/arjaythedev/twelve-dollar-server-challenge, benchmarks/batch-2.md, and the video (youtube.com/watch?v=-BFt49ula08). Synteq VPS, 1 vCPU (Xeon Platinum 8260) / 2 GB, process fd limit 65,535, kernel not tuned. Score = most users holding 5 minutes with p95 < 500 ms, p99 < 1 s, < 1% errors. **These numbers are for this box and date only.** CPU-bound entries scored about 2x higher here than on the DigitalOcean droplet used in batch 1.

## Contents
- Results table
- What each top entry did
- What stopped each entry

## Results table

| # | Entry | Users | req/s | p95 ms | p99 ms | err % | CPU % | µs/req | RAM MB | Stopped by |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Rust (raw io_uring) | 264,000 | 25,147 | 259 | 499 | 0.00 | 84 | 30 | 630 | latency, then OOM at 360k |
| 2 | x86-64 asm (io_uring) | 171,000 | 16,777 | 87 | 142 | 0.00 | 78 | 43 | 358 | p99 at 180k, OOM at 200k |
| 3 | Go (raw epoll + C helper) | 165,000 | 16,165 | 194 | 241 | 0.00 | 89 | 51 | 187 | fell off a cliff at 170k |
| 4 | x86-64 asm (epoll) | 155,000 | 15,182 | 208 | 294 | 0.00 | 89 | 55 | 211 | latency |
| 5 | C (io_uring) | 150,000 | 14,611 | 385 | 524 | 0.00 | 78 | 50 | 413 | latency |
| 6 | Go (io_uring) | 128,000 | 12,604 | 3 | 23 | 0.00 | 77 | 57 | 385 | connection slots (2 rings × 65k) |
| 7 | Kotlin (NIO, 2 JVMs) | 120,000 | 11,759 | 246 | 524 | 0.00 | 100 | 79 | 1,380 | CPU |
| 8 | C (epoll) | 107,000 | 10,493 | 212 | 409 | 0.94 | 78 | 69 | 169 | errors (idle closing) |
| 9 | Java (FFM epoll) | 102,000 | 10,023 | 86 | 128 | 0.85 | 66 | 61 | 555 | errors (idle resets) |
| 10 | V (epoll) | 100,000 | 9,848 | 1.5 | 2.9 | 0.51 | 76 | 72 | 384 | errors |
| 11 | Node (uWebSockets.js) | 97,000 | 9,471 | 264 | 484 | 0.00 | 92 | 90 | 336 | CPU/latency |
| 12 | Bun (raw TCP, from batch 1) | 90,000 | 8,826 | 140 | 359 | 0.00 | 83 | 87 | 301 | — |
| 12 | Scala (Netty) | 90,000 | 8,801 | 484 | 757 | 0.00 | 87 | 92 | 825 | latency |
| 12 | PyPy (epoll) | 90,000 | 8,801 | 280 | 474 | 0.00 | 89 | 94 | 270 | p95 |
| 15 | Lua (OpenResty) | 88,000 | 8,477 | 434 | 591 | 0.04 | 92 | 101 | 267 | CPU |
| 16 | Zig / Deno / Dart / C++ | 71,000 | ~6,555 | 1.0-34 | 1.5-80 | 0.93 | 31-94 | 44-134 | 184-475 | fd limit |
| 20 | F# (Oxpecker) | 65,000 | 6,392 | 84 | 229 | 0.00 | 55 | 80 | 1,255 | .NET abort past fd limit |
| 21 | C# (Native AOT epoll) | 64,000 | 6,300 | 23 | 48 | 0.00 | 31 | 46 | 163 | crash in EMFILE logging |
| 22 | Haskell (Warp) | 55,000 | 5,411 | 2.5 | 198 | 0.00 | 62 | 107 | 1,587 | OOM at 58k |
| 22 | Go (net/http) | 55,000 | 5,382 | 425 | 679 | 0.00 | 90 | 156 | 1,465 | OOM at 57k |
| 24 | Python (FastAPI) | 48,000 | 4,701 | 303 | 465 | 0.00 | 89 | 176 | 583 | CPU |
| 24 | Swift (Hummingbird) | 48,000 | 4,700 | 210 | 300 | 0.00 | 97 | 191 | 1,269 | CPU |
| 26 | Java (Quarkus) | 29,000 | 2,838 | 306 | 451 | 0.00 | 50 | 164 | 542 | disk sync (iowait 26-39%) |
| 27 | Bash (socat, behind Nginx) | 3,500 | 344 | 18 | 43 | 0.00 | 64 | — | 107 | errors >50% at 4k |

## What each top entry did
- **Rust #1**: raw io_uring, no framework, async executor, proxy or ORM. 8 rings of registered file tables (about 524k socket slots), multishot accept/receive, a 64-byte connection record, completion batching (32 completions or 215 µs), reads in a batch share one transaction, the feed uses range scans, zero-copy parsing, SQLite compiled from source with PGO.
- **asm io_uring #2**: raw io_uring with registered tables, shared receive buffers, idle sockets separated from active requests, PGO SQLite.
- **Go + C #3**: the whole request batch passes into C in one call; the helper is compiled with SQLite in one compilation unit (touches SQLite internals), shared read transactions, group commit, PGO.
- **asm epoll #4**: hand-written HTTP/JSON/token code, one epoll loop, writes batched, checkpoint finished at a quiet point in the loop, a budget for keep-alive connections.
- **C io_uring #5**: registered sockets, shared receive buffers, sheds idle connections based on /proc/meminfo.
- **Kotlin #7**: 2 JVMs on one port with SO_REUSEPORT (doubles the fd room), group commit, zero busy timeout with requeued writes.
- **Node #11**: uWebSockets.js (native C++ networking), better-sqlite3, one prepared statement returns the finished JSON, group commit per event-loop turn, idle timeout tuned to user think-time.

## What stopped each entry
- **CPU**: Kotlin, Lua, Swift, FastAPI, Node.
- **Memory (OOM)**: Haskell, Go net/http; Rust and asm io_uring only above their passing scores.
- **File descriptors**: Zig, Deno, Dart, C++ (71k tie); C# and F# crashed at the limit.
- **Disk sync**: Quarkus (`synchronous=FULL`, one commit per request).
- **Load generator**: capped the test at about 240k until server IPs and generators were added.
