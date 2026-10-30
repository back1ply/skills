---
name: mcp-security
description: Reviews and hardens MCP (Model Context Protocol) servers, clients, and agent tool setups using the lethal trifecta and the OWASP MCP Top 10. Use when building or reviewing an MCP server, installing a third-party MCP server, auditing .mcp.json / .claude/settings.json / agent configs, scoping agent tokens or OAuth, checking tool descriptions for poisoning, or when the user asks "is this MCP safe", "MCP security review", "prompt injection risk", or "agent permissions".
---

# MCP Security

Distilled from freeCodeCamp's "MCP Security Fundamentals Course" (Dan Barahona, AI Security University, 2026). Per-risk detail in [references/owasp-mcp-top10.md](references/owasp-mcp-top10.md).

## Core mental model: the lethal trifecta

Watch: [0:22:34](https://youtu.be/gYXLRMycVMk?t=1354)

An agent is exfiltration-vulnerable when, within one task, it has all three:

1. **Private data**: can read something sensitive (inbox, DB, private repos, secrets).
2. **Untrusted content**: ingests text someone outside your control wrote (issues, tickets, web pages, emails, PDFs, *tool descriptions*).
3. **External communication**: can send data anywhere an outsider can read (email, webhook, PR, ticket reply, a rendered markdown image URL).

Two legs is one integration away from trouble. **Defense: remove one leg.** Better prompts or classifiers don't fix it. The model is working as designed when it follows injected text.

## Workflow: reviewing an MCP setup

1. **Inventory.** List every MCP server the agent can reach (grep repos for `mcp.json`, `.mcp.json`, `.claude/settings.json`; check host configs). Note who published each one: the vendor itself, or a random community package?
2. **Trifecta scorecard.** One row per tool, three yes/no columns: reads private data / sees untrusted content / can exfiltrate. Flag any agent whose tools tick all three across one task, and name which leg to cut.
3. **Code and config checks.** Run the greps below, then walk the Top 10 checklist in the reference file.
4. **Report.** Per finding: the risk ID (MCP01–MCP10), the trifecta leg it touches, evidence (file:line), and the fix. Lead with any all-three-legs agent.

## Fast greps

| Look for | Risk |
|---|---|
| `child_process.exec`, `os.system`, `shell=True`, `eval(`, string-built SQL | MCP05 command injection |
| API keys / tokens in configs, env files, prompt logs | MCP01 secrets |
| `"latest"`, `^`/`~` ranges, unpinned `npx` / `uvx` MCP packages | MCP04 supply chain |
| Bind to `0.0.0.0`, no auth on local dev servers | MCP04 / MCP07 |
| Client token forwarded to downstream APIs | MCP07 confused deputy |
| Auto-approve / `enableAllProjectMcpServers`-style settings in repo configs | MCP01 / MCP09 |
| Long-lived or shared service tokens; dev creds usable in prod | MCP02 scope creep |
| Module-level singletons or caches holding per-user state | MCP10 cross-tenant leak |

## Minimum bar (six pillars)

1. **Identity and policy**: OAuth 2.1, short-lived scoped tokens, per-user delegation, no token pass-through.
2. **Isolation and lifecycle**: tested tenant boundaries; containers, non-root, bound to localhost.
3. **Trusted tooling**: every server inventoried; vendor-built or security-reviewed; pinned versions.
4. **Schema-driven validation**: validate inputs and outputs. Retrieved text is data, never a command.
5. **Oversight**: structured tool-call logs (identity, tool, params, time) sent to a SIEM, with behavioral baselines.
6. **Trifecta scorecard** for every agent and workflow, re-run whenever tools change.

## Rules of thumb

- Find a vendor's MCP server on the vendor's own site, never via search. Anyone can wrap anyone's API.
- Config files are now execution paths. Treat a cloned repo's agent settings as untrusted code.
- Tool names, parameter names and **default values** all reach the model. Scan the whole schema, not just the description.
- Wrap retrieved content in explicit untrusted-data tags, and anchor the user's goal in the system prompt.
- Instructions like "code freeze, don't touch prod" are suggestions to an agent. Enforce them with permissions instead.
- MCP is an API. Every classic API control (authN, server-side authZ, input validation) still applies.

The OWASP MCP Top 10 is a living list. If exact current IDs or wording matter, check owasp.org.

## Sources
| Video | Channel | Date | Used for |
|---|---|---|---|
| [MCP Security Fundamentals Course](https://www.youtube.com/watch?v=gYXLRMycVMk) | freeCodeCamp.org | 2026-10-22 | Everything; transcript in `data/raw/gYXLRMycVMk.json` |
