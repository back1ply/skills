# Sweep: evidence rules per artifact

Source: Google Just Released Something To Fix Claude Code's Biggest Problem (youtube.com/watch?v=JhZB3spnuIY, 2026-11-17) and Google's "Agent Distraction" post (2026-11-06). The commands are standard git/gh/rg, not from the video.

## Contents
- What counts as proof
- CLAUDE.md, AGENTS.md and rules lines
- Specs, tickets and plans
- TODO / FIXME comments
- Memory and notes
- Checker prompt template

## What counts as proof
- **Stale** needs both: (1) the claim is false in the current code, *and* (2) the history shows why. Examples: a rename commit, a removal commit, the issue closed as fixed or won't-fix, or a later decision recorded in a spec or commit message.
- If you have (1) without (2), it's a **conflict**. The code may be the thing that's wrong.
- Age alone is never proof. A 5-year-old TODO with an open issue is valid work, just not for this session.

## CLAUDE.md, AGENTS.md and rules lines
- **Paths**: `test -e <path>`. If missing, run `git log --diff-filter=DR --summary -- <path>` to find the delete or rename, and the new name.
- **Names, routes, components**: `rg -n "<name>"`. If missing, run `git log -S"<name>" --oneline` to find the commit that removed it.
- **Commands** (`npm run x`, `just y`): check the manifest (package.json scripts, justfile). Don't run the command just to test it.
- **"We use X"**: check the dependency manifests and imports.
- **First action**: list every path and identifier in the file, then grep each one. This catches most of the rot quickly.

## Specs, tickets and plans
- Read the status tag first. `in progress` means the plan wins over half-built code, so don't report it.
- `not started` but built: run `rg` for the feature's entry points. If they're found, it's a stale status.
- `completed` but missing from the code: look for a removal commit. If one exists, the ticket should be `dropped` (stale). If there's none, it's a conflict.
- No tag and not built: always a conflict ("was this dropped?"). This is the video's email-only login case ([0:06:11](https://youtu.be/JhZB3spnuIY?t=371)).

## TODO / FIXME comments
- Find them: `rg -n "(TODO|FIXME|HACK|XXX)\b"`. Note the ones that link to an issue (`TODO(#123)`, `TODO(bug/123)`, URLs).
- Issue state: `gh issue view <n> --json state,stateReason,closedAt`. Closed as completed or not planned is a stale candidate. Open is valid work, so leave it alone.
- History check (Google's step): `git blame -L <line>,<line> <file>`, then `git log -L <start>,<end>:<file>` or `git log --since=<closedAt> -- <file>`. Did the code the TODO describes change after the issue closed?
- **Load-bearing tells**: the comment says what breaks ("do not remove", "regression of #123", "workaround for"). Keep these, even when the issue is closed.
- TODOs without an issue link: report only when the code shows the work is done (for example, "TODO: add retry" and retry logic sits right below it).

## Memory and notes
- Memory notes and second-brain entries have no linked record. Proof can only come from the code.
- If a note contradicts the code, it's a conflict, never stale. Corrections in memory may record what the user wants, which the code doesn't do yet.
- Notes that mention files or names that no longer exist are stale only if the history shows the rename or removal.

## Checker prompt template
```
You are checking claims about this repository. For each claim, inspect the current
code (and git history if useful) and answer exactly: true / false / unclear,
with file:line or commit evidence. Do not suggest fixes.

1. <artifact:line> says: "<claim, quoted or paraphrased neutrally>"
2. ...
```
Leave out your verdict, your reasoning and words like "outdated" or "suspected". Run it as a fresh subagent so it has no chat history.
