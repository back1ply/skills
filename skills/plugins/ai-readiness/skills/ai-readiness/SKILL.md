---
name: ai-readiness
description: Scores a repository, product or team estate on Jurgen De Smet's 20-dimension AI-readiness instrument (howreadyfor.ai) from evidence, not opinion. Places each dimension on the 1-5 ladder (Blind, Tacit, Visible but inert, Acted on, Durable) by its tell, reports the floor first, calibrates scores across repos, and names the cheapest move up per dimension, including converting cultural agreements into hard guardrails. Use when the user asks "how ready are we for AI agents", "score this repo on howreadyfor.ai", "answer the AI readiness questions for <repo>", "what is our floor", "which standards are only agreed, not enforced", or compares two codebases for agent readiness. PRIVATE: never commit, push or share this skill.
---

# AI readiness: score a codebase from evidence

Distilled from "AI Readiness for Engineering Organizations" (Jurgen De Smet, Lean Tech BV, 2026) and the online instrument at howreadyfor.ai. Ladder and rules in [references/ladder-and-scoring.md](references/ladder-and-scoring.md); the 20 dimensions in the five cluster files; how to collect evidence in [references/evidence-protocol.md](references/evidence-protocol.md).

## Core mental model

One question climbs every dimension: does the system act on this, or does a human have to choose to? Levels 1-3 need someone to remember; 4-5 the machine acts. Level 3 is the trap: written down and agreed, yet an agent that never reads the wiki treats it like a 1. The work is the jump from 3 to 4. Read the floor (lowest dimension), not the total: AI attacks the minimum.

## Workflow: score a scope

1. **Fix the scope** before question one: one repo, one product, a team's estate, or the org. Score the worst case inside it. Mid-modernisation: score the new platform and the old estate separately; the gap is the finding.
2. **Pull the live wording.** Run `uv run S/scripts/extract_questions.py <out.md>`, where `S` is this skill's folder. It fetches howreadyfor.ai/assess and writes each dimension's question, levels and tells. If its tells differ from the cluster files, the live page wins; note the drift.
3. **Collect evidence read-only** per [references/evidence-protocol.md](references/evidence-protocol.md): config files, CI history, `git` history, hook config, ownership files. Every score cites a `file:line`, commit or command result; every "none" names its search. For more than one repo, give each repo (or each half of the 20) its own agent with the protocol as its brief.
4. **Score each dimension by its tell**, using the cluster files:
   [foundation-structure](references/foundation-structure.md) (1-4), [truth-signals](references/truth-signals.md) (5-8), [flow-throughput](references/flow-throughput.md) (9-12), [memory-intent](references/memory-intent.md) (13-16), [enforcement-release](references/enforcement-release.md) (17-20). Not knowing is a 1. Anything that needs a person to choose is 3 at most.
5. **Calibrate.** Re-read the ladder text for every score that differs between repos or agents and apply one reading to all. Report each change ("Q9 3→2: nothing reports branch age").
6. **Spot-check** the load-bearing claims yourself (gates said to block, absences, dates) before reporting. An agent's evidence is a lead until you have opened the file.
   **Check reliability** when the score will drive a decision: have a second agent score the same scope independently (fresh context, no shared notes) and compare. Report exact agreement per cluster; every disagreement is a tell to tighten or an evidence gap, so settle it before reporting ([references/evidence-protocol.md](references/evidence-protocol.md), "Reliability and history").
7. **Mark what needs the owner** (`NEEDS OWNER: <question>`), mostly team-shaped tells, and ask at most three, each with your recommended answer.
8. **Report** floor first, then sum and band, the pattern across clusters, the three decisions, and the cheapest move up per low dimension (use [references/guardrail-playbook.md](references/guardrail-playbook.md) for any "only agreed" rule). Put the 20-row table in an HTML file built from [assets/scorecard-template.html](assets/scorecard-template.html).
9. **Save the scores** as a dated record (scope, date, 20 scores, evidence per score) where the owner keeps assessment history, and compare with the previous record: name every dimension that dropped and why (a gate switched to warn-only, a waiver past its date, a stale branch). A drop with no change in the repo means the scoring drifted, not the system.
10. **Re-score after a fix.** Before a change meant to lift a dimension, predict which dimension moves and to what level. After it lands, re-score only the predicted dimension plus its cluster, and report predicted versus actual. A fix that moved nothing, or moved something else, is the finding.

## Quick checks

| Look for | Why |
|---|---|
| A CI stage wrapped to warn (`catchError`, `continue-on-error`, `allow_failure`) | A gate that warns is level 3, not 4 |
| Exception or waiver lists without expiry dates, or dates nothing enforces | Separates 4 from 5 |
| Oldest remote branch (`git for-each-ref --sort=committerdate refs/remotes`) | Trunk-based tell |
| CI build retention (keep-last-N) | Short retention makes flake and rerun rates unknowable, which scores 1-2 |
| CODEOWNERS and commit-author spread (`git shortlog -sn`) | Ownership and bus factor |
| Rules that live only in CLAUDE.md, a wiki or review comments | The "agreed" column: candidates for conversion |

## Rules of thumb

- A 92 with one dimension at 1 is a 1 with a flattering total.
- Score what is true today, not what is planned. Supplier-owned code still counts.
- One- or two-person codebases floor at 1 on Organizational design and Code ownership by construction. Report that floor, then the engineering floor without them, and still treat a bus factor of 1 as a real finding.
- Tacit (2) means one person knows and nothing requires or measures it. Don't give a 1 when the owner demonstrably acts on it, or a 3 when nothing is reported.
- A level-5 gate looks identical to a level-4 one in config. Only history shows the difference: the last bypass and who flagged it.
- The cited research supports why each dimension matters, not the ladder; see [references/research.md](references/research.md) before quoting a paper.
- Test the score against what actually went wrong: low-scored dimensions should be where agents caused rework (revert and fix commits, agent session logs). If the rework clusters elsewhere, question the score before the repo.
- Hold the skill to its own ladder: a one-off scoring is level 3 for the instrument itself; dated history plus re-scoring after fixes is what makes it act.

## Known gaps

- The book's diagrams and charts are not in the text and were not distilled.
- The series' separate essays on converting agreements into guardrails and on discipline were not fetched; the field guide's playbook and conclusion cover them in [references/guardrail-playbook.md](references/guardrail-playbook.md).
- Bands and level wording change on the site; step 2 catches drift in tells, not in bands.
- Numbers in the cluster files are as the guide or essays report them (2026), not re-verified against the underlying studies.

## Sources

| Source | Author / site | Date | Used for |
|---|---|---|---|
| [AI Readiness for Engineering Organizations (field guide PDF)](https://jurgendesmet.substack.com) | Jurgen De Smet, Lean Tech BV | 2026 | Chapters, signals, Level 4 bars, playbook, conclusion |
| [The AI Readiness self-assessment](https://howreadyfor.ai/assess/) | Lean Tech BV | read 2026-11-03 | Current questions, levels and tells |
| [Method](https://howreadyfor.ai/method/) | Lean Tech BV | read 2026-11-03 | Scoring rules, bands, data handling |
| [AI Readiness: Twenty Questions, One Honest Number](https://jurgendesmet.substack.com/p/ai-readiness-twenty-questions-one) | Jurgen De Smet, Substack | 2026-08-25 | Floor vs sum, "Score 4 when" bars |
| The 20 per-dimension essays of the AI Readiness series (linked per dimension in each cluster file) | Jurgen De Smet, Substack | 2026 | Detection signals, practices and moves folded into the cluster files |
| The 20 long-form dimension pages, `https://howreadyfor.ai/d/<slug>` | Lean Tech BV | read 2026-11-03 | Level detail and examples folded into the cluster files |

License: the field guide is CC BY-NC-ND 4.0 and the site is all rights reserved. This is a private adaptation for the owner's own use; sharing it would breach both.
