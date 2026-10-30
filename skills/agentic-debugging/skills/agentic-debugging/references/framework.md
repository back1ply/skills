# Agentic debugging: the framework in detail

Source: How to effectively debug when you no longer understand the code (https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b, 2026-10-15). Details are as the article describes them.

## Contents
- Play to agent strengths
- The factual tier: what to collect
- Step 1: controls and signals
- Step 2: the hypotheses-by-fact matrix
- Single vs multi-cause hypotheses
- Progressive signal discovery
- Step 3: validation
- Agent repros
- Adversarial review at each step
- Prompt snippets

## Play to agent strengths
Read: [Play to Agentic Strengths](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Play%20to%20Agentic%20Strengths%2C%20not%20Human%20Strengths)
- **Strengths to lean on**: processing huge data volumes; cross-referencing layers (kernel, filesystem, packets, process state, stacks); knowing almost every tool and data format; testing every hypothesis tirelessly; writing throwaway tooling on demand.
- **Weaknesses to guard against**: narratives from thin evidence; fixating on obscure edge cases; walking past their own best earlier finding.
- **Don't**: make the agent debug the way a human would (local repro first, pattern-match old incidents). That was the first mistake on the latency bug.

## The factual tier: what to collect
Read: [Bottom Factual Tier](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Bottom%20Factual%20Tier), [Fat on Facts](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Fat%20on%20Facts%2C%20Thin%20on%20Hypotheses)
- Sources: error logs, crash reports, stack traces, profiler data, telemetry, system traces, kernel data, DNS data, blackbox measurements, performance counters, user reports, service config, feature-flag values, dependency versions, deploy config, version-control history, platform and sidecar config.
- Two kinds of fatness: *different* data types from all sources, and the *same* type from different instances of the bug (pcaps from several users, profiles from two hosts). Repeating across instances and absent from the control = probably real.
- Facts are gathered by tools, not conjured by the agent. The agent can request more or flag doubts about collection, never alter them.
- A fat derivative tier signals one of two factual-tier flaws: **too few constraints** applied (memory leak: facts eliminated 2 of 6 hypotheses), or **low-quality constraints** that fit everything (latency bug: P99 fit all 7).

## Step 1: controls and signals
Read: [Step 1](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Step%201%3A%20Isolate%20high-fidelity%20signals%20in%20the%20factual%20tier)
- **What**: compare the variable (failing) against a control; keep only the differences.
- **Example**: flag off on client and server (control) vs flag on on both (variable). TCP handshake time was the same in both (noise); DNS lookup returned ~5 addresses vs ~400 (signal).
- **Pick the control**: happy path for simple bugs. For tricky ones, a *sad path that also fails but louder*, often already in your data (for the hang: users with genuine permission-denied auth failures, which left errors, vs the silent hang).
- **First action**: before any hypothesis, name the control and why you trust it isn't broken the same way.

## Step 2: the hypotheses-by-fact matrix
Read: [Step 2](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Step%202%3A%20Isolate%20the%20most%20promising%20hypothesis%20in%20the%20derivative%20tier), [When Every Hypothesis Falls Short](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=When%20Every%20Hypothesis%20Falls%20Short)
- Rows = hypotheses, columns = high-fidelity signals/facts, cells ✓ / ✗.

  | Hypothesis | Fact A | Fact B | Fact C |
  |---|---|---|---|
  | H1 | ✓ | ✗ | ✓ |
  | H2 | ✓ | ✓ | ✓ |

- **Columns** → signal strength: count ✓ per column; a column with one ✓ is a strong signal and names the hypothesis to validate. The latency bug's P99 column was all ✓ (7 hypotheses, among them server regression, cert reloading, client routing, capacity, event-loop stalls, throttling, slow upstream); the DNS column had one.
- **Rows** → survival: a hypothesis survives only with no ✗. No all-✓ row = the hypothesis set is wrong; apply the five tactics (in SKILL.md) before inventing new ones.
- Don't validate every hypothesis (slow, token-heavy); *steer* to the single most promising one.
- **First action**: ask the agent to output this matrix before it proposes a fix.

## Single vs multi-cause hypotheses
Read: [Single vs Multi-Cause](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Single%20vs%20Multi-Cause%20Hypothesis)
- Most bugs have one cause; conditions such as "only at production scale" are conditions, not second causes.
- Multi-cause: memory leak = process-wide cache re-entering an engine + state machine designed for single use. Metastable failure: capacity drop explains *onset*, unbounded client retries explain *persistence*.
- Each cause must be strictly necessary. Never add complexity to explain away an inconvenient fact.

## Progressive signal discovery
Read: [Progressive Signal Discovery](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Progressive%20Signal%20Discovery)
- Trigger: every signal is weak, or no hypothesis survives the five tactics.
- Start cheap (bug report, logs, telemetry, config), then descend one layer at a time; each layer narrows what the next must explain. Stop at the first strong signal.
- Latency bug: layer 1 telemetry/config/code/postmortems (weak P99) → layer 2 ssh to a production host (DNS lookups, strong).
- Hang: logs (nothing) → packet capture (handshake then silence) → process state (something *waiting*, not looping) → kernel IPC table (auth daemon still holding the reply right: strong).
- Agents shine here: each layer needs different tools; humans usually stop after one or two.

## Step 3: validation
Read: [Step 3](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Step%203%3A%20Validate%20the%20most%20promising%20hypothesis%20against%20every%20constraint%20in%20the%20factual%20tier)
- Check the candidate against every fact, including noise (identical handshake times must also be explained).
- Too few facts → several hypotheses survive and can't be told apart; go collect more.
- **First action**: require a citation (log line, profile frame, capture) for each claim. On the hang, about a third of challenged claims had none and were dropped.

## Agent repros
Read: [Agentic Repros](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Agentic%20Repros%20Require%20Additional%20Scrutiny)
- A repro belongs in the derivative tier. It proves *a* bug, not *the* bug; facts about the real user outrank it.
- Check **signal parity**: the repro must produce the strongest real signal. Hang: a clock-skew repro looked right but its packet sequence diverged and the IPC reply right was missing, so it was a different bug. Memory leak: the user's repro hit the same heap-profile frame, so it was trusted.
- A falsified repro is noise; drop it from the investigation.

## Adversarial review at each step
Read: [Pitfalls](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=Pitfalls%20of%20%E2%80%9CAdversarial%E2%80%9D%20Reviews), [Incorporating review](https://copyconstruct.medium.com/how-to-effectively-debug-when-you-no-longer-understand-the-code-bd3dcb2c5f7b#:~:text=How%20to%20Incorporate%20an%20Adversarial%20Review%20Into%20The%20Three%20Step%20Debugging%20Loop)
- Limits: a reviewer can't see missing facts, so it can't catch "too few constraints"; same model + same context = one opinion counted twice. The wrong cert-reloading theory passed an independent subagent check.
- Use it to **eliminate**, at every step:
  - Step 1: drop signals that also appear in the control; check the control isn't broken the same way; check how each fact was gathered.
  - Step 2: estimate how many hypotheses fit each signal (without chasing them); read the matrix by rows; confirm split/merge/combine was tried before new hypotheses; confirm descending a layer was justified.
  - Step 3: find one fact the hypothesis fails; for combined hypotheses, remove each cause and see whether some fact goes unexplained.

## Prompt snippets
Ready-made instructions that encode the framework (written for this skill, not quoted):
- "Don't read the code yet. List every fact we have and where it came from."
- "Name a control and explain why it isn't broken the same way. List what differs between control and variable."
- "Build a hypotheses-by-fact matrix. Which column has the fewest ✓? Which row has no ✗?"
- "Cite the fact behind each claim. Drop any claim you can't cite."
- "Does your repro show the same strongest signal as the user's report?"
- "As a reviewer, try to find one fact this hypothesis doesn't explain."
