---
name: sweep
description: Finds outdated notes, plans, specs, CLAUDE.md/AGENTS.md lines, memory entries and TODO/FIXME comments that could send a coding agent on a side quest. It checks each one against the current code and the git/issue history (Google's TODO-cleaner method), has a blind checker agent confirm every finding, and reports without editing. After approval it fixes lines, removes dead TODOs, and moves dead docs to an archive that a hook blocks agents from reading. Use when the user says "sweep", "find stale docs", "clean up old TODOs", "is my CLAUDE.md still true", or after a big rename or a change in requirements.
---

# Sweep

Distilled from "Google Just Released Something To Fix Claude Code's Biggest Problem" (AI LABS, 2026-11-17), which builds on Google's TODO cleaner ("Agent Distraction", 2026-11-06). Evidence rules and commands: [references/evidence.md](references/evidence.md). Archive hook: [references/archive-hook.md](references/archive-hook.md). Rules that stop new rot belong in the `distraction-rules` skill.

## Core mental model
Finding notes that look old is the easy part. The **history check** is the part worth copying ([0:07:10](https://youtu.be/JhZB3spnuIY?t=430)). A note can look stale and still carry weight, like "don't remove this or bug X comes back". Google's agent only proposed deleting a note when the history showed that the note *and the reason behind it* were both obsolete. A human reviewed every proposal. Over 6 months that cleared thousands of notes, with >95% of proposals accepted.

**No proof, no finding.** If staleness can't be proven, leave the note alone and don't report it as stale.

## Workflow
1. **Inventory** (read only). Collect candidates. For each, write a *claim*: what the artifact says is true right now.
   - CLAUDE.md / AGENTS.md / rules files: every path, name, route, command and "we use X" line.
   - Specs, tickets, plans: status tag and what each one says should exist.
   - Memory notes (Claude memory, second-brain notes the project loads).
   - `TODO`/`FIXME`/`HACK` comments, especially ones that link to an issue.
   - READMEs and docs that agents read while planning.
2. **Check each claim against the code and the history** ([evidence.md](references/evidence.md)). Use grep for the name or path, `git log -S`/`--follow` for renames and removals, and `git blame` plus the issue state for TODOs. Record the evidence (file:line, commit SHA, issue state).
3. **Classify** each candidate:
   - **stale**: proof that the claim and its reason are both outdated;
   - **conflict**: a memory note or rule disagrees with the code, with no proof which one is intended. The user decides; never call these stale ([0:12:29](https://youtu.be/JhZB3spnuIY?t=749));
   - **load-bearing**: looks old but the history shows it still guards something. Keep it;
   - **unproven**: no conclusive evidence. Drop it from the report, or list it as a count only.
4. **Blind verification.** Give every stale finding to a separate checker agent (a subagent with no chat history). Pass only the neutral claim and where to look. Leave out your verdict and reasoning, so the checker can't be steered into agreeing ([0:12:29](https://youtu.be/JhZB3spnuIY?t=749)). Example: "CLAUDE.md:14 says the products page is at `src/pages/products.tsx`. Is that true in the current code? Answer true / false / unclear, with evidence." Keep a finding as stale only if the checker answers *false* with evidence. If it answers *unclear*, move the finding to conflict.
5. **Report. Don't edit anything.** Use one table per class: artifact:line, claim, evidence, proposed action (update line / delete TODO / archive file). Conflicts get a question for the user.
6. **Apply only what the user approved:**
   - CLAUDE.md, rules and specs: fix the line in place, or set the ticket to `completed`/`dropped`. Don't delete the history of a decision.
   - Dead TODOs: delete the comment, one commit per batch, citing the issue or commit that proves it is dead.
   - Whole dead docs: add a one-line header (`Archived <date>: <reason>`), then `git mv` the file into the archive folder. Install the hook if it isn't there yet ([archive-hook.md](references/archive-hook.md)).
7. **Summarize**: counts per class, what changed, and the conflicts still open.

## Quick checks
| Signal | Likely class |
|---|---|
| Name or path in CLAUDE.md doesn't exist; `git log` shows a rename | stale: update to the new name (the video's "products page → catalog" case, [0:12:29](https://youtu.be/JhZB3spnuIY?t=749)) |
| TODO links to a closed issue, and the code it describes is gone or changed after the fix | stale |
| TODO links to a closed issue, but the comment warns what breaks if code is removed | load-bearing |
| Spec says a feature exists, code doesn't have it, no status tag | conflict: ask whether it was dropped |
| Memory says "always X", code does Y | conflict |
| Ticket `not started`, feature fully built | stale status: set it to `completed` |

## Rules of thumb
- Report, don't fix. A sweep that edits as it goes ends up removing load-bearing notes.
- One sweep pass costs less than the side quests it prevents (Google: +77% tokens per distracted session).
- Run it after renames, after requirement changes, and before handing a repo to a new agent workflow.
- Loop/monitor features stop when the session ends ([0:07:10](https://youtu.be/JhZB3spnuIY?t=430)). For a recurring sweep, schedule it outside the session.

## Known gaps
- The video's actual SKILL.md, verifier and hook code are paywalled and were never shown. This workflow and the hook are written from its description and Google's post.

## Sources
| Video | Channel | Date | Used for |
|---|---|---|---|
| [Google Just Released Something To Fix Claude Code's Biggest Problem](https://www.youtube.com/watch?v=JhZB3spnuIY) | AI LABS | 2026-11-17 | Sweep design: report-only, history check, blind checker agent, conflicts list, archive + read-blocking hook |

Also checked: [Google Developers Blog, "Agent Distraction"](https://developers.googleblog.com/agent-distraction/) (2026-11-06) for the TODO-cleaner method and its acceptance rate.
