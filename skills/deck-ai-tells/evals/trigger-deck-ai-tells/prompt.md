---
description: Trigger test. This request should load the deck-ai-tells skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Does this deck look AI-generated? I made it in Gamma: every slide has emoji bullets and three icons in a row.
