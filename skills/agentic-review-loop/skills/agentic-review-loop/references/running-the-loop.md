# Agentic review loop: running it

Source: Toward a Self-Improving Agentic Code Review Loop (https://www.robinwieruch.de/agentic-code-review-loop/, 2026-10-09). Details are as the article describes them, from one product team of five developers over three weeks.

## Contents
- Personal review skills
- Firing reviews
- Answering findings
- Later rounds
- The human review
- The baseline reviewer
- Where it could go, and the risks

## Personal review skills
Read: [Every Developer Brings Their Own Reviewer](https://www.robinwieruch.de/agentic-code-review-loop/#every-developer-brings-their-own-reviewer)
- **What**: a review skill = instructions a developer's own coding agent follows when asked to review a PR. Examples from the team: one hunts duplicated code, one reads the API contract first, one runs an adversarial pass.
- **Why not one shared reviewer**: five reviewers who think alike find the same five things; a shared prompt gets tuned to findings the team already knows and stops surprising anyone.
- **Why not host skills in the cloud**: the skill is only half the reviewer; the other half is the developer's harness, which doesn't move with a prompt file. Central hosting also erodes diversity and moves the token cost away from whoever runs the review.
- **Comment format**: label every AI comment with the model, so nobody mistakes it for a colleague's opinion, e.g.
  ```
  [Model Name]:
  > [SUGGESTION] `user-list.tsx:56` The empty check is repeated in every list
  > component. The base list already knows whether it is loading.
  ```

## Firing reviews
- **Fire and forget**: the developer who fires a review does not read its findings. Reading your own agent's review first makes you the bottleneck again.
- **Automating the trigger** (in progress on the team): one top-level agent loops every ~15 minutes, finds PRs it hasn't reviewed, and launches a subagent per new PR to run the full review.
- **First action**: give your review skill a visible model label and a severity tag on each finding.

## Answering findings
Read: [The Author's Agent Answers](https://www.robinwieruch.de/agentic-code-review-loop/#the-authors-agent-answers)
- A PR can collect 20-50 findings; no human reads 50 carefully. The author's agent checks each against the actual code and replies in-thread, model-labelled:
  - **fix**: names the commit;
  - **decline**: real but not worth the change;
  - **refute**: wrong, with evidence (e.g. "Non-issue: the field is required by the schema, so an empty value is rejected before this branch can run.").
- Answering is the harder job. One agent walking 50 findings in one session runs out of context and starts rubber-stamping. Hand each finding, or a small batch of related ones, to a fresh subagent that reads the code and returns a verdict.
- How a developer's agent answers is their own setup; recommend, don't prescribe.

## Later rounds
- After fixes land, a second round is fair when the first found a lot.
- **A later round must read the earlier threads first.** Otherwise agent 1 says "move to A", the author moves, agent 2 says "move back to B".
- Cap rounds (applies to the baseline loop too).

## The human review
Read: [The Human Review Is Still There](https://www.robinwieruch.de/agentic-code-review-loop/#the-human-review-is-still-there)
- A developer still reviews and signs the PR. They may use their agent to explore or check hunches, but their inline comments are their own; no fire and forget here.
- What moves off the human: naming, missing tests, duplicated helpers, unhandled error paths.
- What stays: is this the right change, was it asked for, does the design fit the product direction. Agents answer those confidently and badly.

## The baseline reviewer
Read: [A Baseline to Measure Against](https://www.robinwieruch.de/agentic-code-review-loop/#a-baseline-to-measure-against)
- GitHub Copilot reviewed every PR, untuned, answered and scored like the personal skills. The author's agent loops on it: answer, push fixes, re-request, repeat until a round has nothing meaningful, with a cap and knowledge of earlier rounds.
- Numbers (3 weeks, per the article): 385 inline comments, 255 answered; 71% accepted (personal skills 73%), 16% refuted (twice the personal rate); shallow, with 2 of 3 reviews leaving no inline comment and the rest typically 2. Coverage: 271 PRs vs 94 for personal skills, because nobody has to remember to fire it.
- Keep a baseline for coverage and as a fixed bar: a personal skill that can't beat the free reviewer needs work.

## Where it could go, and the risks
Read: [Where This Could Go](https://www.robinwieruch.de/agentic-code-review-loop/#where-this-could-go)
- Direction: weekly scoring → developers tune → precision and depth rise together → shorter human review. This is the quality control of a "software factory".
- Further out (an outline, not a plan): a classifier at PR end estimating "nothing left to find"; small low-finding high-score PRs merge on their own, large ones earn it through rounds; architecture and security stay with a human regardless.
- Before any score merges anything: record it silently for a while and compare with what the human review still found. Model confidence isn't calibrated just because it's a number.
- Watch for the human review quietly becoming a rubber stamp once five agents have approved.
