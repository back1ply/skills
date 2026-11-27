---
description: Trigger test. This request should load the agentic-debugging skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

An agent wrote our payment retry module and it double-charges about 1 in 200 orders. Nobody on the team understands the code. Help me find the root cause systematically.
