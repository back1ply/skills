# Agentic debugging: the article's three bugs

Source: How to effectively debug when you no longer understand the code (https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b, 2026-10-15). Details are as the article describes them; systems are the author's workplace's.

## Contents
- The latency bug
- The memory leak
- The hang
- What the human added each time

## The latency bug
Read: [The Latency Bug](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=The%20Latency%20Bug)
- **What**: server-side P99 regressed when a feature flag was on for client and server, at production scale.
- **Wrong turn**: the agent read the code (~9,000 lines) and blamed inefficient cert reloading. It sounded plausible, and an independent subagent couldn't disprove it, because P99 fits almost any hypothesis.
- **Detect**: control (flag off on both) vs variable (flag on on both); TCP handshake identical (noise); on a live production host, DNS lookups returned ~5 addresses in the control vs ~400 in the variable (strong signal).
- **Root cause**: the new code path didn't use the sharded client (client-side routing).
- **First action next time**: set up the control before any code reading; turn signals into counts.
- **Prevention**: a pre-deploy check that the client's DNS lookups match the last good run would have caught it even at pre-prod scale.

## The memory leak
Read: [The Memory Leak](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=The%20Memory%20Leak)
- **Facts in the bug report**: regression introduced in a recent version (last good version known); amortization (the big recent change) was opt-in and off for the reporter; heap profile pointed at the plain recursive state-machine call, not the amortized entry point; it happened only when no credentials were supplied up front.
- **Wrong turns**: "long-standing state machine bug, bound the retries" (contradicts *recent*); "amortization did it" (contradicts *off by default*); then four more hypotheses.
- **Fix in the framework**: split "the amortization work" into "process-wide cache, on by default" and "amortization, off" (tactic 2), then combine the cache with "state machine designed for single use" (tactic 4). Only the combination satisfies every fact; each cause is necessary.
- **Repro**: the user's repro hit the same heap-profile frame, so it was trusted.
- **Decision for a human**: two fixes (turn off the cache, or make the state machine safe to re-enter) with different trade-offs.

## The hang
Read: [The Hang](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=The%20Hang)
- **What**: a desktop daemon (on pre-release OS versions) that exposes a WebSocket remote service as a virtual file system hit intermittent 60 s timeouts. No crashes or errors were logged, it couldn't be reproduced reliably, users restarted the daemon (wiping live state), and new logging would take weeks to ship. The only evidence was users' `sysdiagnose` bundles.
- **Wrong first hunch**: slow server responses; server telemetry didn't support it.
- **Control**: a sad path: users with genuine permission failures (loud, logged), instead of setting up a local happy path.
- **Layers**: logs (nothing) → packet capture (handshake completes, then silence) → process state (nothing running in the auth path: waiting, not looping) → kernel IPC table (the auth daemon still holds the one-time reply right for the request: strong signal). The author used Mach port tooling with the agent's help, data they couldn't read unaided.
- **Rejected repro**: a coworker's clock-skew repro; its packet sequence diverged and no unanswered reply right appeared. A real problem, not this one.
- **Citations**: about a third of challenged claims had no citation and were dropped.

## What the human added each time
Read: [Mind The Gap](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Retooling%20the%20Agentic%20Factory%20Floor%20For%20Autonomy%20And%20Accountability)
- Latency: a **control** (the agent didn't set one up until asked).
- Memory leak: **constraints** from the bug report, and a repro (the agent didn't apply them until told).
- Hang: **citations** for claims (not provided until demanded).
- Lesson: the agent was capable each time; what held it back was how far it was willing to go. Encode these steps in the process instead of relying on the person prompting.
