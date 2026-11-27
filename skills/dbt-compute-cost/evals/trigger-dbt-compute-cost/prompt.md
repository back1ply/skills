---
description: Trigger test. This request should load the dbt-compute-cost skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Our dbt runs cost too much in Snowflake and CI takes 40 minutes. How do I cut warehouse spend with state-aware runs and right-sizing?
