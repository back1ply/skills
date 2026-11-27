---
description: Trigger test. This request should load the python-library-packaging skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

We're extracting a reusable library from our app. Review the public API, add py.typed and set sensible dependency ranges.
