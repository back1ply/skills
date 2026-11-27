---
description: Trigger test. This near-miss request must not load the dbt-agent-context skill.
tags: [trigger, negative]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

How do I add a not_null test to a column in a dbt schema.yml?
