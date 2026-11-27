---
description: Trigger test. This request should load the data-storytelling skill.
tags: [trigger, positive]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "This is a short test session. If a skill applies, use it as you normally would. Keep the reply under 150 words and do not edit files."
---

Critique this slide: the title is 'Q3 Revenue', it has a 3D pie chart with nine slices and a legend. What's the takeaway, and how do I make it clearer?
