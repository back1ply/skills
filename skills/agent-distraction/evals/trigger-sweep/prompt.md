---
description: Trigger test. This request should load the sweep skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Go through this repo's TODO comments, old specs and CLAUDE.md lines and find the ones that are out of date and could send an agent on a side quest. Report only, don't edit anything.
