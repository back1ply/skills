# AI readiness: converting cultural agreements into hard guardrails

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), playbook pp. 94-98 and conclusion pp. 99-101. Use it for the "cheapest move up" on any dimension whose rule is only agreed.

## Contents
- The altitude idea
- The six stages
- Keeping gates from rotting
- Signals you have this gap
- Discipline: the evidence test

## The altitude idea
Read: field guide pp. 94-95
- An agreement and a guardrail are the same rule at different altitudes. Conversion changes where the rule lives, not what it says.
- Saying it louder (clearer wiki, sterner rules file) keeps the rule at the altitude where it already failed.
- **Portable question:** what is the earliest stage this rule can live on?
- **Pick one this week:** take the review comment you are tired of typing, name the earliest stage that would mean you never type it again, and build that one gate.

## The six stages
Read: field guide pp. 95-96

| Stage | Holds | Example | Watch out |
|---|---|---|---|
| 1 Type system | Illegal states that hurt | A money value object, so a raw float cannot be written | Over-modeling |
| 2 Pre-commit | Fast, local, file-level rules | Secrets, formatter, debug statements | Bypassable (`--no-verify`, uninstalled hooks): on its own a faster agreement |
| 3 CI | Anything that must hold before merge | Lint as errors, tests, mutation thresholds, server-side secret scan, fitness functions | Only a guardrail if CI is trustworthy; a flaky pipeline turns every gate back into a suggestion |
| 4 Policy-as-code | Rules not about code | No public buckets, required tags, two approvals for prod, no `:latest` | Agents now write the infrastructure files these rules govern |
| 5 AI harness | "We told the AI not to" | A pre-tool-use hook that deterministically blocks destructive commands or protected paths | Protects this agent run, not the repo; composes with CI, does not replace it |
| 6 Enforced review | Judgment that cannot become a check | Branch protection that blocks merge until a required review exists | Enforces that a decision point exists, not its content; slice by risk |

- A rules file (CLAUDE.md, .cursorrules, copilot-instructions.md) is advisory. Per the guide (2026), a NeurIPS 2025 workshop result found 73% enforcement accuracy with the rules in the prompt; hold the figure lightly, the direction is the point.

## Keeping gates from rotting
Read: field guide p. 97
- **Ratchet on new code:** enforce on new and changed code only, so legacy debt drains as files are touched.
- **Scope each gate** to the one rule a violation would hurt. A gate that cries wolf trains people to ignore it.
- **Mirror every bypassable stage** with a non-bypassable one (pre-commit secret scan plus the same scan in CI).
- **Demote the doc to intent:** keep the wiki for why; let the stage hold the rule.
- Gates are not a tax on velocity: they absorb the manual "verification tax" on every AI pull request (DORA's framing, per the guide).

## Signals you have this gap
Read: field guide p. 97
- When a standard keeps getting violated, the reflex is to say it louder rather than move it lower.
- The most important standards have no owner named next to their gate.
- The only enforcement for AI is a rules file.
- Review is the dumping ground for rules that could have been a type, a hook or a build failure.
- **First action:** rank the agreed column by what a violation costs and convert the top few to their earliest stage.

## Discipline: the evidence test
Read: field guide pp. 99-101
- Gates rot one reasonable exception at a time (Vaughan's normalization of deviance). An agent feels no friction when it bypasses, so the baseline slides faster and silently, and the strongest gates collect the most exception requests.
- Discipline is institutional, not personal: a gate held by one vigilant person is green until they are on holiday.
- **Test:** pick the gate you are proudest of, find the last time it was bypassed and who flagged it (the artifact, the alert, the name). If you cannot produce it, that gate is not the level its config suggests.
