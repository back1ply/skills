---
description: Trigger test. This request should load the dbt-agent-context skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Our text-to-SQL agent over the dbt project gives different answers for 'active customers' every week. Where should that business definition live so the agent gets it right?
