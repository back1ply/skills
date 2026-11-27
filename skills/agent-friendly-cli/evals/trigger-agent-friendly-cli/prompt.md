---
description: Trigger test. This request should load the agent-friendly-cli skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Our Go CLI is built with cobra: it exits 1 on bad flags and prints help to stdout. Audit it so Claude Code and Codex can call it reliably from a shell.
