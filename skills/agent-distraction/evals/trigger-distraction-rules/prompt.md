---
description: Trigger test. This request should load the distraction-rules skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

My coding agent keeps rebuilding a feature we dropped months ago because an old line in CLAUDE.md still mentions it. How do I set up this project so agents stop acting on stale instructions?
