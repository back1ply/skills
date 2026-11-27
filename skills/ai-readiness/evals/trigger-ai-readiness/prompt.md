---
description: Trigger test. This request should load the ai-readiness skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Score our main repository on the howreadyfor.ai AI-readiness ladder from evidence, and tell me the floor first.
