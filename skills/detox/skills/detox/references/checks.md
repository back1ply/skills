# What each part checks

Read only your part. Write findings in the format of `findings-schema.md`. Raw files are in `<run>/raw/`.

## interface

Raw: `sessions.json` (from disk), `sidebar_sessions.json` (sidebar list: pinned, group), `sidebar.json`, `folders.json` (`active_used` = folders the user confirmed), `artifacts.json`, `mods.json`.

1. **Idle and one-off chats.** Unarchived Code sessions with titles that look like tests, one quick question, or personal and not work. Also sessions idle more than 30 days. Skip scheduled-task runs (they have `scheduled_task`). Two tables: "Test, one-off and personal" and "Idle 30+ days". Actions: Archive (`archive_session`, default) or Delete (`delete_session`).
2. **Sections, one table per active folder.** Only sessions whose `cwd` is in `active_used`. Group by topic from titles (for a business vault: YouTube, LinkedIn, newsletter, design, motion graphics, sales, and so on). One row per proposed section: name, chat count. Put the chat titles in `details` so the page can show exactly which chats move in. `folder` = that folder. Never propose sections for other folders, or for an active folder that no longer exists on disk (make that one flag row: "Folder is gone. Archive these chats, or reopen them in the live copy."). Flag existing sections named like "Test". Actions: Create and move (`create_section`, default) or Keep as is (`none`).
3. **Pins.** Pinned sessions idle more than 7 days: Unpin. The 3 most active unpinned sessions of the last 7 days: Pin. `set_pinned`.
4. **Artifacts.** Untitled ones, generic titles with many copies, probes and tests, and ones not updated in 30+ days. First cell is a link to `https://claude.ai/artifact/<id>`. Column "Last updated" (the listing has no last-opened date; never write "last opened"). Never write "unknown" for a date the listing gives. Actions: Keep (`none`) or Delete (`delete_artifact`, default; permanent, say so in the note).
5. **Mods.** One row per mod: name, what it does, on or off. Actions: Keep (`none`), Switch off (`mod_switch` on=false, default), Delete (`mod_delete`). If no mods, one info line.

`tokens` is `null` for every interface row.

## memory

Raw: `context.json` (global layer, then `projects`: one entry per active folder). Read the files it lists. Also read the last 30 days of the user's own messages if `recent_prefs.txt` exists.

Columns for every memory table: "File" (full path), "What is wrong", "What to do", plus "Line A" and "Line B" for conflicts. Short plain answers, no bold.

1. **Global layer.** `~/.claude/CLAUDE.md` and the memory folders. Rules that are outdated, said twice, or that contradict each other. Quote the two lines that clash.
2. **Each active project, one table per project** (`folder` = the project path). For each:
   - Work out what the project is about from its root CLAUDE.md (or AGENTS.md), its top folders and its recent files. Put that in the table `note`.
   - Root CLAUDE.md: short, routes to folder files, no rules repeated across levels, no stale facts (dates, paths that no longer exist). Offer a specific rewrite (`edit_file`). If there is none, suggest one (`create_file`).
   - Routing and index files (`route_files`): links and paths that point at nothing. Check each path exists. `edit_file`.
   - Important folders or files the CLAUDE.md or map never mentions. `edit_file`.
   - Top folders with no CLAUDE.md and no index (`top_dirs`): suggest one (`create_file`).
   - `recent_context`: files that contradict the CLAUDE.md or each other.
   - A folder with `exists: false`: one flag row, "Folder is gone, its chats point at nothing".
3. **Conflicts.** Two files that say different things about the same rule. One row per conflict: both lines, which is newer, suggested winner. Actions: Keep A, Keep B, Ask me (`none`, default).

`tokens`: for a file that loads in every chat (global CLAUDE.md, MEMORY.md, a root CLAUDE.md), the characters removed / 4, with `tokens_est: true`. Otherwise `null`.

Never edit. Findings only.

## skills

Raw: `skill_doctor.txt` (the /skill-doctor table: what Claude Code loads, context cost, uses, last used), `skills.json` (every SKILL.md on disk, with location and use counts from Code AND Cowork transcripts), `context_usage.txt` (the `/context` Skills table, when present).

Locations in `skills.json`: `global`, `plugin` (enabled plugin), `desktop-harness` (Claude app, Customize > Skills), `folder` (a `.claude/skills` inside a project), `plugin-stored` (catalog or disabled plugin copy, not loaded), `loose` (a SKILL.md outside any skills folder, not loaded).

"Loaded" means /skill-doctor lists it, or a session skill list shows it. A skill that only sits in a synced plugin folder on disk is not loaded. Never count it in the headline numbers.

1. **Count by category.** Group loaded skills (global, plugin, desktop-harness, folder) into 6 to 10 categories from their descriptions (for example video, design, sales, research, writing, data, dev tools, admin). Stats: total loaded, per category.
   Then one table of every loaded skill, sorted by category: name, category, location, last used, tokens, and a "Suggestion" column (Keep or Remove, with a few words why). Actions: Keep (`none`, default when the suggestion is Keep), Move to backup (`move_skill`, default when it is Remove), Make manual only (`manual_only`).
2. **Unused.** Loaded skills with no use in 30 days. Use the later of /skill-doctor last used and `skills.json` last used, because /skill-doctor misses Cowork. Actions: Move to backup (`move_skill`, default) or Make manual only (`manual_only`).
3. **Duplicates.** Same name in more than one loaded location, or identical copies. Keep one, say which. `move_skill` for the extras.
4. **Overlaps and conflicts.** Skills in the same category that do the same job. Name the pair and the one to keep.
5. **Fires by accident.** Skills that /skill-doctor flags as triggering when not asked, or that `skills.json` shows used in chats whose titles are about something else. Name the chat titles in `details`. Actions: Make manual only (`manual_only`, default) or Keep.
6. **Biggest context cost.** Top 15 by description tokens. Actions: Make manual only (default) or Move to backup.
7. **Unused plugins.** From the end of `skill_doctor.txt`. flag.

`tokens`: the skill's description tokens from /skill-doctor or `/context`.

## connectors

Raw: `connector_status.json` (every server, its kind and tool count), `connectors.json` (calls per server in chats, last used; servers are named by id for claude.ai connectors, map ids with the `connector` section names where you can), `context_usage.txt` (the `/context` MCP table, local and plugin servers only).

Put the token cost first: it is the first stat, and the first number column in every table.

1. **Every connector.** One info table: name, kind, token cost, tool count, last used, can write (yes or no).
2. **Unused.** Servers with no call in 30 days. kind `connector`: Switch off (`connector_off`, default) or Keep. Other kinds: flag.
3. **Broken (expired logins).** `failed` and `needs_auth` rows. Say "Reconnect it" in the action text. flag. Group the needs-auth plugin servers into one row per plugin.
4. **Heavy.** Top 10 by token cost, with tool count.
5. **Same service twice** (for example a custom MCP and the official connector for the same tool, a desktop vidiq and the VidIQ connector, Fireflies plugin and Fireflies connector). Keep one.
6. **Switch to Composio or CLI.** For used, heavy services: Composio (match by service name; Composio covers most common SaaS) or a CLI built with Printing Press (https://github.com/mvanhorn/cli-printing-press). `build_cli` rows are optional.
7. **Risky write access.** Services where tools include create, update, delete, send: list the risky ones (payments, email, CRM). flag. The note says the user must reduce this access in the tool's own settings, because Claude cannot.

`tokens`: MCP tool definitions are deferred by default, so only tool names and server instructions enter every chat (https://code.claude.com/docs/en/costs#reduce-mcp-server-overhead). Estimate per server: (characters of its tool names as `mcp__<server>__<tool>` + characters of its server instructions) / 4, with `tokens_est: true`. The full schema size from `context_usage.txt` (when the server is listed) goes in its own column, "Full schemas", because it only loads when Claude uses the connector. Never count full schemas as a per-chat saving.

## scheduled

Raw: `scheduled.json` (Code tab and Cowork tasks: `where` says which, runs seen, last run, failures in last 10, models used in last 10).

Order every table: failing first, then on and off (some runs fail, some pass), then healthy.

1. **Every task.** One info table: name, where (Code tab or Cowork), status (Failing / On and off / Healthy), last run, failures in last 10, model.
2. **Failing.** failures > 0: show the error. flag.
3. **Stale.** Last run more than 30 days ago, or never: Pause (default) or Delete. `task_update`.
4. **Not useful anymore.** Tasks whose description points at a finished project, a folder that is gone, or a tool that is no longer connected. Say why in `details`. Pause (default) or Delete. `task_update`.
5. **Outdated model.** Any model older than the current family (current: Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1). Example: claude-opus-4-8 to claude-opus-5-5. `task_update`.
6. **Sonnet can do it.** Simple tasks (fetch, format, post) on Opus: suggest Sonnet 5.5. Anthropic's advice: Sonnet costs less, keep Opus for complex multi-step work (https://code.claude.com/docs/en/costs#choose-the-right-model).

`tokens` is `null` for every scheduled row. These save plan usage, not context.
