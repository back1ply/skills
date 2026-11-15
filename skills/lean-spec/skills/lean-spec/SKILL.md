---
name: lean-spec
description: Lightweight Markdown specs for coding agents (Kiro-style bugfix template, spec deltas, same-commit sync) instead of a spec framework.
disable-model-invocation: true
---

# Lean spec

A spec is the **contract** for one change: short Markdown in `specs/`, written before the code, kept true after it. Pick one branch:

| Change | Branch |
|---|---|
| Bug fix | Bugfix spec |
| Feature or behavior change in existing code | Delta spec |
| Refactor, rename, typo, no behavior change | No spec. Go straight to the code. |

Bugfix and Delta end with **Sync**. A no-spec change needs Sync only if it touched behavior a living spec describes.

## Bugfix spec

File: `specs/bugfix-<slug>.md`

```
# Bugfix: <short description>
Current:     WHEN <condition> THEN the system <wrong behavior>
Expected:    WHEN <condition> THEN the system SHALL <correct behavior>
Unchanged:   WHEN <condition> THEN the system SHALL CONTINUE TO <behavior that must survive>
             (one line per nearby behavior, each naming its test)
Root cause:  <file:line and one sentence on why it happens>
Constraints: <code or interfaces the fix must not touch>
Regression:  <path to the test that fails today>
```

1. Write the regression test and run it. Done when it goes **red** for the reason in Current.
2. Find the root cause. Done when Root cause names the line that produces the wrong behavior and explains why, not just where the symptom shows.
3. Fill Unchanged with the behaviors next to the fix that a careless patch could break, and Constraints with what the fix must leave alone. Done when each Unchanged line names an existing test or a new one you wrote. Where the input space is wide, prefer a property-based test.
4. Fix the root cause. Done when the regression test and every Unchanged test are green, and the diff stays inside Constraints.

Keep it under 20 lines. A bug fix gets this template, never a full feature spec.

## Delta spec

A **living spec** `specs/<area>.md` holds the current requirements for one area. A change is a **delta** against it: `specs/changes/<yyyy-mm-dd>-<slug>.md`.

```
# Change: <title>
Why: <one or two sentences>
Reuse: <existing modules, classes, endpoints this builds on>

## ADDED
### Requirement: <name>
System SHALL <behavior>
- Scenario: WHEN <condition> THEN <result>

## MODIFIED
### Requirement: <name>
<full replacement text, copied from the living spec and edited>
- Scenario: ...

## REMOVED
### Requirement: <name>
Reason: <why>
```

If `specs/<area>.md` does not exist yet, create it in step 5 from the delta's ADDED requirements only. Do not back-fill the rest of the area.

1. Search the codebase and `specs/` for the behavior first. Done when Reuse lists what already exists (or says "nothing found" after a real search). Agents regenerate classes that already exist; this step stops that.
2. Write the delta. Leave empty sections out. Done when every ADDED and MODIFIED requirement has at least one scenario and the file is under about 100 lines.
3. Show the delta to the user before writing code. In plan mode, the delta is the plan. Done when the user approves it.
4. Implement. Done when every scenario maps to a passing test.
5. Fold the delta into the living spec, in the same commit as the code:
   - Re-read the current living spec first. If a MODIFIED requirement changed since the delta was written (a **stale base**), merge both changes by hand rather than overwriting the newer text.
   - Move the delta to `specs/archive/`.

   Done when the living spec describes the new behavior and nothing in `specs/changes/` refers to finished work.

## Sync

Spec and code change together, in the same commit (or linked PRs across repos). Done when searching the living specs (`specs/*.md`, excluding `specs/archive/` and `bugfix-*` files) for the changed behavior finds only the new version.

When code and spec disagree and the change was not intended, that is **drift**: stop and ask the user which one is right. Fix the loser in the same commit.

## Project setup

On first use in a project, offer to add this line to its `CLAUDE.md`:

```
Behavior changes update the matching file in specs/ in the same commit (lean-spec skill).
```
