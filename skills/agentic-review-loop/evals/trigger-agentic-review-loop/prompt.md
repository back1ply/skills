---
description: Trigger test. This request should load the agentic-review-loop skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Design an AI code review process for my team of six: each dev runs their own review skill on pull requests, the author's agent answers every finding, and we score which review skills are worth keeping.
