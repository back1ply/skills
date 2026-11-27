---
description: Trigger test. This request should load the design-patterns-pythonic skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Replace this long if/elif chain that dispatches on payment type with a Pythonic strategy pattern.
