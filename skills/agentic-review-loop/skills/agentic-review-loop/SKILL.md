---
name: agentic-review-loop
description: Sets up, runs and measures a team-wide AI code review loop where each developer fires their own review skill at pull requests, the author's agent answers every finding (fix, decline, refute), a human reviews last, and a scorecard rates each review skill on precision and depth, using Robin Wieruch's process and three weeks of numbers. Use when designing AI pull-request review for a team, tuning a personal review skill or agent, answering a pile of AI review comments, deciding whether to keep Copilot or another baseline reviewer, scoring which AI reviewer is any good, or the user says "who reviews the reviewers", "review loop", "AI review comments", "review scorecard", or "software factory".
---

# Agentic review loop

Distilled from "Toward a Self-Improving Agentic Code Review Loop" (Robin Wieruch, robinwieruch.de, 2026-10-09). Detail in [references/running-the-loop.md](references/running-the-loop.md) and [references/scorecard.md](references/scorecard.md).

## Core mental model
Once every developer has a review agent, review volume stops being the problem; **trusting the reviewers** is. The loop makes every finding a data point: a review skill posts it, the author's agent gives it a verdict, and the verdicts score the skills ([source](https://www.robinwieruch.de/agentic-code-review-loop/#scoring-the-reviewers)). Agents do the pattern matching; the human review is kept for "is this the right change?"

## Workflow: one pull request
1. **PR opens**; the author asks for reviews as usual.
2. **Each teammate fires their own review skill, fire and forget.** Findings go in as inline comments labelled with the model that wrote them. The developer who fired it doesn't read them ([source](https://www.robinwieruch.de/agentic-code-review-loop/#every-developer-brings-their-own-reviewer)).
3. **The author's agent answers every finding**: *fix* (name the commit), *decline* (not worth it), or *refute* (wrong, with evidence). Give each finding or small batch its own fresh subagent; one agent working through 50 findings fills its context and starts waving them through ([source](https://www.robinwieruch.de/agentic-code-review-loop/#the-authors-agent-answers)).
4. **Another round if the first found a lot.** A later round must read the earlier threads first, or agents argue the PR back and forth between approaches.
5. **A human reviews last** and owns their comments: right change? was it asked for? does the design fit? ([source](https://www.robinwieruch.de/agentic-code-review-loop/#the-human-review-is-still-there))

## Team rules
- **Personal skills, not one shared reviewer.** Diversity finds more; a shared reviewer overfits to known findings. Nobody aligns prompts; everyone tunes their own.
- **Every AI finding gets a reply**, any wording, from the developer or their agent. Silent fixes make findings unscoreable ([source](https://www.robinwieruch.de/agentic-code-review-loop/#the-silent-fix-problem)).
- **Keep an untuned baseline reviewer** (e.g. Copilot) on every PR: it covers PRs nobody fired at, and it's the bar a personal skill must beat.
- **Cap review rounds.** A reviewer asked often enough always finds something.
- Review skills run in each developer's own harness (local agent setup), not centrally in the cloud: the harness is half the reviewer, and the token cost stays with whoever chose to run it.

## Scoring (weekly)
- **Precision** = accepted ÷ answered findings (declined nits count against it like wrong findings).
- **Depth** = valid findings landed on PRs that several skills reviewed.
- Use both. Precision alone ranks the near-silent skill first, which is the one to fix first.
- Fixes by quadrant: shallow → look for more; often wrong → add a verification step before posting; deep but noisy → stop posting nits.
- Lean toward depth until precision nears a floor (~70% in the author's view), then trim nits, not depth.
- Compare scorecards week to week to see whether a skill change helped. Method and caveats: [references/scorecard.md](references/scorecard.md).

## Quick checks
| Look for | Why |
|---|---|
| Unanswered findings with changed lines | Silent fixes; the score can't see them |
| Round 2 contradicting round 1 | Later rounds didn't read earlier threads |
| One agent answering 30+ findings | Context fills; verdicts get shallow |
| A skill with ~100% precision and 1-2 findings per PR | Silent, not good |
| Five agent approvals and a 2-minute human review | Rubber stamp forming |

## Known gaps
- The article's charts (overall outcome breakdown, the per-skill scorecard and its week-over-week movement) are images. Per-skill names and numbers in the article are deliberately altered by the author; the totals are real.
- No tooling is published; the scraping and classification were done ad hoc with an agent.

## Sources
| Article | Author / site | Date | Used for |
|---|---|---|---|
| [Toward a Self-Improving Agentic Code Review Loop](https://www.robinwieruch.de/agentic-code-review-loop/) | Robin Wieruch, robinwieruch.de | 2026-10-09 | Entire skill: loop, rules, scorecard, baseline, risks |
