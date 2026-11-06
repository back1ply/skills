# Findings file format

Each part sub-agent writes one file: `<run>/findings/<part>.json`. Parts: `interface`, `memory`, `skills`, `connectors`, `scheduled`.

```json
{
  "part": "skills",
  "title": "Skills",
  "summary": "One plain sentence: the main finding, with real numbers.",
  "stats": [ {"label": "Skills loaded", "value": "214"} ],
  "tables": [
    {
      "id": "skills-unused",
      "title": "Not used in 30 days",
      "note": "One line on how this was measured and its limits.",
      "columns": ["Skill", "Where", "Last used", "Context cost"],
      "rows": [
        {
          "id": "skills-unused-example-skill",
          "cells": ["example-skill", "global", "never", "18 tokens"],
          "mode": "approve",
          "tick": false,
          "folder": "",
          "tokens": 18,
          "tokens_est": false,
          "actions": [
            {"label": "Move to backup", "apply": {"kind": "move_skill", "path": "/Users/x/.claude/skills/example-skill"}},
            {"label": "Make manual only", "apply": {"kind": "manual_only", "path": "/Users/x/.claude/skills/example-skill/SKILL.md"}}
          ],
          "default": 0
        }
      ]
    }
  ]
}
```

## Row fields

- `mode`: `approve` (checkbox plus action dropdown, changes only on a tick), `flag` (shown with a comment box, the user does it), `info` (no action).
- `tick`: always `false`. The user ticks. Never pre-tick.
- `actions`: required on `approve` rows. One to three choices, in the user's words (Archive / Delete, Keep / Switch off / Delete, Keep / Delete). A choice that changes nothing uses `{"kind": "none"}`.
- `default`: index into `actions`. "Approve all" ticks the row and picks this one. Pick the safest choice that still helps (Archive before Delete).
- `tokens`: context tokens saved in every chat if the default action is applied. A whole number, or `null` when it saves no context (interface rows, scheduled tasks: those save plan usage, not context). Never guess. Use a measured number from `/context`, `/skill-doctor` or the file size (characters / 4). If it is an estimate, set `tokens_est: true` and the page shows "est.".
- `folder`: the active folder the row belongs to (full path), or `""`. The page filters on it.
- `details`: optional list of short strings shown when the row is opened. Use it for the chats a new section would hold.
- A cell is a string, or `{"text": "...", "href": "https://..."}` for a link (artifact links: `https://claude.ai/artifact/<id>`).
- Every `approve` and `flag` row gets a comment box on the page. No field needed.

## Apply kinds

- `archive_session` {session_id}
- `delete_session` {session_id} (permanent)
- `create_section` {name, folder, session_ids}
- `set_pinned` {session_id, pinned}
- `delete_artifact` {url} (permanent)
- `mod_switch` {name, on}
- `mod_delete` {name, path} (moves the mod folder to `~/.claude/detox-backup/YYYY-MM-DD/`)
- `edit_file` {path, change} (change is a plain description; Claude shows the diff before writing)
- `create_file` {path, change}
- `move_skill` {path} (to `~/.claude/detox-backup/YYYY-MM-DD/`)
- `manual_only` {path}
- `connector_off` {name, id}
- `task_update` {task_id, change}
- `build_cli` {service}
- `none`

## Rules

- Every number and every row comes from a raw file. If a value is not in the raw data, write `unknown`.
- Each row `id` is unique across the whole page: `<table id>-<slug>`.
- Cap a table at 40 rows. If there are more, keep the 40 with the biggest effect and put the rest count in `note`.
- Write cells as plain answers. "What is wrong" and "What to do" in a few words each, never a paragraph. No bold, no markdown in cells.
- Plain words. No em dashes. Do not use the banned word s-h-i-p. Say publish or deliver.
