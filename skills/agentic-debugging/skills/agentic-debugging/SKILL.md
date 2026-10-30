---
name: agentic-debugging
description: Debugs code nobody on hand fully understands (agent-written, unfamiliar, or too large to read) by treating the bug as a constraint satisfaction problem, using Cindy Sridharan's two-tier framework (facts vs hypotheses), a control vs variable comparison, a hypotheses-by-fact matrix, progressive signal discovery, and elimination-only adversarial review. Use when debugging with an agent, when an agent's root-cause claim sounds plausible but unproven, when a bug fix "didn't fix it", when reviewing an agent's repro or diagnosis, or the user says "find the root cause", "why is this slow / leaking / hanging", "I don't understand this code", or "verify this diagnosis".
---

# Agentic debugging

Distilled from "How to effectively debug when you no longer understand the code" (Cindy Sridharan, Medium, 2026-10-15). Detail in [references/framework.md](references/framework.md); the article's three bugs as worked examples in [references/case-studies.md](references/case-studies.md); team and infrastructure changes in [references/factory.md](references/factory.md).

## Core mental model
Debugging is a **constraint satisfaction problem**, not open-ended guessing ([source](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Agentic%20Debugging%20Is%20a%20Constraint%20Satisfaction%20Problem)).
- **Factual tier**: gathered data (logs, profiles, traces, packet captures, configs, versions, bug reports). Immutable: the agent may question how a fact was gathered, never alter or dismiss it. Every fact is a constraint.
- **Derivative tier**: everything inferred (hypotheses, narratives, repros). Where agents sound most convincing and are most often wrong.
- A hypothesis is valid only if it satisfies **every** fact. One contradicting fact discards it.
- **Code is an unreliable narrator**: it says what *can* happen, not what *did*. Read code *last*, to explain collected facts, never first to generate theories ([source](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Code%20is%20an%20Unreliable%20Narrator)).

## Workflow: the three-step loop
0. **Collect facts first.** Start with what is already there (bug report, logs, telemetry, config, version history). Keep the factual tier *fat*: many sources, and the same data type from several instances of the bug.
1. **Isolate high-fidelity signals with a control.** Compare the failing case (variable) to a control. Present in variable but not control = signal; present in both = noise (noise can still eliminate hypotheses, but never says where to look). Control = happy path for simple bugs; a *louder, differently-failing sad path* for tricky ones. Confirm the control isn't broken the same way.
2. **Find the most promising hypothesis.** Build a hypotheses-by-fact matrix. Read **columns**: a signal satisfied by ~1 hypothesis is *strong*; by many is *weak* (SLOs/SLIs like P99 usually are). Read **rows**: a hypothesis needs no ✗. If no row is all ✓, apply the five tactics (below) before inventing anything new.
3. **Validate against every fact**, signals *and* noise. Demand a citation into the factual tier for each claim; claims without one are dropped.
- **No strong signal, or every hypothesis still fails?** Don't generate more hypotheses: go back to step 1 one layer down (logs → telemetry → host state → packets → process state → kernel). Stop at the first *strong* signal; the goal is the strongest, not the deepest ([source](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Progressive%20Signal%20Discovery)).

## When every hypothesis falls short (five tactics, in order)
1. Re-verify how facts were gathered (wrong host, time window, tool version). Ask whoever gathered them; don't edit them.
2. **Split** coarse hypotheses ("the deploy did it" → each change in the deploy).
3. **Merge** too-fine ones (host 17 disk, host 42 GC… → "something shared in that AZ").
4. **Combine** complementary ones that each explain part and contradict nothing. Each cause must be necessary: drop one and some fact goes unexplained.
5. Only then a new hypothesis, built from existing facts. Still nothing → descend a layer.

## Quick checks
| Look for | Why |
|---|---|
| Agent opened by reading code and proposing a cause | Narrative before facts; restart from step 0 |
| No control in the investigation | Can't tell signal from noise |
| Diagnosis rests on P99 / error rate alone | Weak signal; fits almost any hypothesis |
| A repro (especially synthetic or non-prod) treated as proof | A repro is a hypothesis; it must reproduce the *strongest real signal* |
| "Independent reviewer agreed" | Same model and context = one opinion counted twice; reviewers must try to *eliminate* |
| Many live hypotheses after hours | Fat derivative tier = too few or too weak constraints |
| Multi-cause claim | Remove each cause in turn; every one must be needed |

## Rules of thumb
- Fat on facts, thin on hypotheses.
- Turn signals into arithmetic (counts, bytes, lookups): 5 vs ~400 DNS addresses cracked the latency bug.
- Adversarial review verifies nothing; use it to eliminate (signals in the control, hypotheses with a ✗, causes not strictly needed).
- Every human nudge (a control, a constraint, a citation demand) marks a step the agent should have taken itself; add it to the process.
- Where a fix has trade-offs (rollback, escalation, which of two fixes), present the options with reasoning and let a human decide.

## Known gaps
- The article's diagrams and matrices are images: the layer lists per platform (Kubernetes, macOS, web, mobile), the end-to-end loop diagram and the matrix tables are summarized here, not copied.
- The bugs are from the author's workplace; system details are as the article describes them.

## Sources
| Article | Author / site | Date | Used for |
|---|---|---|---|
| [How to effectively debug when you no longer understand the code](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b) | Cindy Sridharan, Medium | 2026-10-15 | Entire skill: framework, tactics, review, cases, factory changes |
