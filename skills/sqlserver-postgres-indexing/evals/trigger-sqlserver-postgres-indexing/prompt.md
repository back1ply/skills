---
description: Trigger test. This request should load the sqlserver-postgres-indexing skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

This Postgres query does a sequential scan on a 40M-row orders table filtered by customer_id and created_at. Which index should I add, and in what column order?
