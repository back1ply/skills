# Server capacity: limits and fixes

Source: "I Asked Developers to Max Out a $12 Server (again)" (youtube.com/watch?v=-BFt49ula08, 2026-10-23) and the challenge's batch-2 report (github.com/arjaythedev/twelve-dollar-server-challenge, benchmarks/batch-2.md). Setup: 1 vCPU / 2 GB, SQLite with 500k posts, a Twitter-like API, about 1 request per user every 10 s. Numbers are per the report.

## Contents
- CPU: less work per request
- Memory: per-connection cost
- File descriptors: the 65k connection wall
- Disk sync: durability costs
- SQLite checkpoints
- Load generator limits
- Correctness traps in fast servers

## CPU: less work per request
- **What**: the server spends its single core on framework layers, object building and serialization.
- **Example**: Go net/http 55k users vs Go with raw epoll + a C helper 165k on the same box. The winner was about 30 µs CPU per request; FastAPI 176 µs. ([0:05:38](https://youtu.be/-BFt49ula08?t=338), [0:19:35](https://youtu.be/-BFt49ula08?t=1175))
- **Detect**: CPU near 100% at the failing load; p95 rises gradually instead of errors jumping.
- **Fix / do** (biggest wins first):
  1. Let SQLite produce the response JSON, and send its bytes straight out (no row objects → JSON.stringify).
  2. Prepare statements once; build constant responses (errors, health) ahead of time.
  3. Drop layers you don't need (framework, ASGI, ORM, reverse proxy hop). Lua/OpenResty did the reverse and removed the app server instead of Nginx; that works too. ([0:11:45](https://youtu.be/-BFt49ula08?t=705))
  4. Cut language boundary crossings: one call into C per batch, not per column. ([0:19:35](https://youtu.be/-BFt49ula08?t=1175))
  5. Batch completions: the winner waits for about 32 completions or 215 µs before doing work. ([0:21:39](https://youtu.be/-BFt49ula08?t=1299))
  6. Read-heavy feeds: find the newest N ids, then use a range scan when they're close together, falling back to the normal query. ([0:14:56](https://youtu.be/-BFt49ula08?t=896), [0:22:39](https://youtu.be/-BFt49ula08?t=1359))
  7. Profile-guided optimization (PGO) of the build, including SQLite compiled from source.
- **First action**: profile one request end to end and count the copies/allocations between the database row and the socket.

## Memory: per-connection cost
- **What**: at 100k+ connections, every kilobyte per connection is about 100 MB.
- **Example**: Haskell had p95 2.5 ms but was OOM-killed at 58k; it had already shrunk buffers and stack growth. The Rust winner keeps a 64-byte connection record and allocates I/O buffers only while a request is active ("one extra KB per connection would add about 264 MB"). ([0:06:16](https://youtu.be/-BFt49ula08?t=376), [0:21:39](https://youtu.be/-BFt49ula08?t=1299)) The Zig entry compresses idle fiber stacks against a shared reference stack and hands the pages back to the OS. ([0:10:47](https://youtu.be/-BFt49ula08?t=647))
- **Detect**: OOM kills in the journal; cgroup memory near the RAM size.
- **Fix / do**:
  1. Shared receive buffers; no response buffer kept on idle connections.
  2. Small network buffers and thread/fiber stacks.
  3. Watch available memory and shed idle connections or stop accepting before the OOM killer acts (the C io_uring entry does this). ([0:18:10](https://youtu.be/-BFt49ula08?t=1090))
- **First action**: divide peak memory by open connections at the failing load. That's your per-connection cost.

## File descriptors: the 65k connection wall
- **What**: each socket uses a file descriptor; the process limit here was 65,535. Extra clients wait in the listen queue until they time out.
- **Example**: Zig (31% CPU), Deno, Dart and C++ (94% CPU) all scored exactly 71,000. They serve 65,535 users and the rest time out, about 0.93% of requests, just under the 1% rule. ([0:09:17](https://youtu.be/-BFt49ula08?t=557))
- **Detect**: errors cluster just under or over 1% while CPU has headroom; the open-fd count sits at the limit.
- **Fix / do**:
  1. Raise `ulimit -n` / the systemd `LimitNOFILE` if the rules allow. This is usually the real-world fix; the challenge didn't allow it.
  2. Close idle keep-alive connections near the limit (`Connection: close` or RST). Clients reconnect on their next request. C epoll 107k, Java FFM 102k and V 100k used this.
  3. More processes: the fd limit is per process. Kotlin ran 2 JVMs on one port with SO_REUSEPORT and reached 120k. That adds connection room, not CPU. ([0:16:11](https://youtu.be/-BFt49ula08?t=971))
  4. io_uring registered/fixed files: sockets live in ring tables, not the process fd table. The winner's 8 rings allow about 524k slots. Add multishot accept/receive so one submission yields many events. ([0:17:12](https://youtu.be/-BFt49ula08?t=1032), [0:21:39](https://youtu.be/-BFt49ula08?t=1299))
  5. Tune the idle timeout to user think-time. Too short turns keep-alive into constant reconnects. ([0:13:51](https://youtu.be/-BFt49ula08?t=831))
- **First action**: log the open fd count next to the error rate during a load test.

### Crashing at the limit
- **Example**: C# hit 64k with only 31% CPU, then every probe above that aborted. On EMFILE, its error path wrote to `Console.Error`, whose first use opens a new handle. That failed too, unhandled. ([0:07:41](https://youtu.be/-BFt49ula08?t=461)) F# (.NET) also aborted at the fd limit; the video blamed checkpoint I/O, but the report corrected that on 2026-10-22: iowait was 1-6%.
- **Fix / do**: the fd-exhaustion path must not allocate handles. Pre-open the log, count and drop, back off accept.
- **First action**: run the server with a low `ulimit -n` and confirm it degrades instead of crashing.

## Disk sync: durability costs
- **What**: SQLite's default `synchronous=FULL` fsyncs every commit; with one commit per request, the server waits on the disk.
- **Example**: Quarkus scored 29k at only 50% CPU, with 26-39% iowait. ([0:03:58](https://youtu.be/-BFt49ula08?t=238))
- **Detect**: high iowait with idle CPU.
- **Fix / do**:
  1. **Group commit**: collect writes for one event-loop turn, commit them in one transaction, and answer all of them only after that commit. ([0:13:51](https://youtu.be/-BFt49ula08?t=831))
  2. WAL mode with `synchronous=NORMAL`: commits can return before the log reaches disk. A power loss (not a process crash) can drop the last commits; the database isn't corrupted. The challenge allowed NORMAL or stronger, never OFF. ([0:24:06](https://youtu.be/-BFt49ula08?t=1446))
  3. One dedicated writer connection plus a read pool. With several writer processes, use a zero busy timeout and requeue instead of blocking the event loop. ([0:16:11](https://youtu.be/-BFt49ula08?t=971))
- **First action**: measure iowait under load before tuning code.

## SQLite checkpoints
- **What**: WAL mode appends changes to a log; a checkpoint copies them into the main database file. If that work lands on the request path, latency spikes.
- **Example**: under constant writes a background checkpoint never catches up. The epoll assembly entry finishes the checkpoint at a quiet point in the event loop so the log can restart. V and F# checkpoint on their own thread. ([0:18:47](https://youtu.be/-BFt49ula08?t=1127), [0:14:56](https://youtu.be/-BFt49ula08?t=896))
- **Fix / do**: disable auto-checkpoint on the request path (`wal_autocheckpoint=0`) and checkpoint from a background thread; force a full checkpoint when the WAL gets large.

## Load generator limits
- **What**: one client IP can open only about 60k connections to one target IP:port (source ports).
- **Example**: 4 generators × 1 target IP capped the test at about 240k; the winner passed 240k at 79% CPU. With 3 more server IPs and a 5th generator, the true score was 264k. ([0:23:09](https://youtu.be/-BFt49ula08?t=1389))
- **Fix / do**: check generator CPU and port use; add generator machines or target IPs before concluding the server is maxed.

## Correctness traps in fast servers
Found in the code review; avoid them in production:
- Reads in a batch that can see uncommitted writes (Deno, Zig). Deno also served snapshots up to 20 ms stale.
- Auth tokens without `exp` accepted (11 entries).
- `start.sh` scripts that restart the app themselves, hiding crashes from systemd.
- Toolchain installs that pipe a download straight into a shell, with no checksum check.
- SQL built by string concatenation (the Bash entry).
- Coupling to SQLite internals for speed (the Go + C entry): the creator called it a maintenance trade-off he wouldn't make in the real world.
