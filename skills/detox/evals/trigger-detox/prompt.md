---
description: Trigger test. This request should load the detox skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Clean up my Claude: it's bloated with too many skills and connectors. Audit my setup and give me a checklist of what to change.
