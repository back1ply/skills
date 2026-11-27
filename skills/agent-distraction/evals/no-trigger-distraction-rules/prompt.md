---
description: Trigger test. This near-miss request must not load the distraction-rules skill.
tags: [trigger, negative]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Write a CLAUDE.md for a new FastAPI project: how to run the tests, how to lint, and the folder layout.
