---
description: Trigger test. This request should load the agent-orchestration-checklist skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

I want to hand a big refactor to an orchestrator agent that spins up sub-agents. What should I decide up front, and how do I judge the result without reading all the code?
