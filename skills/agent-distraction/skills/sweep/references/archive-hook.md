# Sweep: archive folder and read-blocking hook

Source: Google Just Released Something To Fix Claude Code's Biggest Problem (youtube.com/watch?v=JhZB3spnuIY, 2026-11-17), [0:11:29](https://youtu.be/JhZB3spnuIY?t=689). The video described the hook but never showed it. The script here is written for this skill.

## Contents
- Why an archive instead of deleting
- Install
- What it blocks and what it doesn't
- First action

## Why an archive instead of deleting
Old plans are still a record of past decisions, so keep them. But if agents can read them, they act on them. The archive keeps the files in git while the hook keeps them out of agent context.

## Install
1. Copy `scripts/block_archive.py` from this skill to `<project>/.claude/hooks/block_archive.py`.
2. Add this to `<project>/.claude/settings.json`, merging with any existing `hooks`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write|MultiEdit|NotebookEdit|Grep|Glob|Bash",
        "hooks": [
          { "type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/block_archive.py\"" }
        ]
      }
    ]
  }
}
```
3. Optional: a different folder. Set `"env": { "SWEEP_ARCHIVE_DIR": "specs/archive" }` in the same settings file.
4. Add the archive folder to a `.ignore` file at the repo root. ripgrep-based search tools honor `.ignore`, so a repo-wide Grep never surfaces archived text.
5. Test it: ask the agent to read a file in the archive. It should be refused with the "Blocked:" message.

## What it blocks and what it doesn't
- Blocks any tool call whose path, pattern or shell command contains the archive folder, case-insensitively, with either kind of slash.
- Allows commands that start with `mv` or `git mv`, so the sweep can move files in.
- Doesn't catch a search rooted above the archive whose results include it (step 4 covers that), or a shell command that reaches the folder without naming it. The hook is a guardrail, not a sandbox.
- Exit code 2 blocks the call and shows the reason to the agent. Malformed input exits 0, so a broken event never locks the session.

## First action
Install the hook before the first file moves into the archive, then run step 5.
