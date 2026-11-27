---
description: Trigger test. This request should load the humanitys-last-prompt-engineer skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Improve this prompt using proper prompting techniques: 'write a blog post about our product'.
