---
description: Trigger test. This request should load the server-capacity-tuning skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Our 1 vCPU server falls over at 800 concurrent users with 'Too many open files'. Find what limits it and how to raise capacity.
