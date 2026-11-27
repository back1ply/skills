---
description: Trigger test. This request should load the skill-finder skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Is there a plugin or MCP server for managing Jira tickets? Find one I can install.
