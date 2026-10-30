# OWASP MCP Top 10: checklist

Format per risk: what it is · trifecta leg · real incident · detect · fix · first action.
Source: "MCP Security Fundamentals Course" (freeCodeCamp, youtube.com/watch?v=gYXLRMycVMk). The incidents are as the course describes them.

## Contents
- MCP01 Token Mismanagement & Secret Exposure
- MCP02 Privilege Escalation via Scope Creep
- MCP03 Tool Poisoning
- MCP04 Supply Chain & Dependency Tampering
- MCP05 Command Injection & Execution
- MCP06 Intent Flow Subversion
- MCP07 Insufficient Authentication & Authorization
- MCP08 Lack of Audit & Telemetry
- MCP09 Shadow MCP Servers
- MCP10 Context Injection & Over-Sharing
- Trifecta map

## MCP01 Token Mismanagement & Secret Exposure

Watch: [0:33:51](https://youtu.be/gYXLRMycVMk?t=2031)
- **What**: credentials leak via committed configs, env vars, prompts, logs. AI-specific: secrets that enter the context window persist ("contextual secret leakage").
- **Leg**: external comms (the token is the exfiltration pipe).
- **Incident**: a Claude Code CVE pair (Check Point, Feb 2026). A malicious `.claude/settings.json` / `.mcp.json` in a cloned repo auto-approved MCP servers and redirected API traffic. The key was sent to the attacker before the trust dialog appeared. Now patched.
- **Detect**: hard-coded tokens in configs; secrets in model context; unredacted prompt logs; tokens outliving the session; shared static service accounts.
- **Fix**: secrets vault fetched at runtime; short-lived session-scoped tokens; middleware so the LLM never sees the secret; redact tokens in logs.
- **First action**: move static keys to a vault; grep the last 7 days of logs for token-like strings.

## MCP02 Privilege Escalation via Scope Creep

Watch: [0:43:20](https://youtu.be/gYXLRMycVMk?t=2600)
- **What**: permissions only ratchet up, through convenience grants and config drift (dev roles reach prod). An agent uses every right it holds immediately.
- **Leg**: external comms.
- **Incident**: Replit / Jason Lemkin (SaaStr). Dev-time broad access carried into prod. The agent ignored an all-caps code freeze, ran a DB push that wiped about 1,200 records, then fabricated about 4,000 fake users and claimed rollback was impossible.
- **Detect**: scope changes without logs; shared agent accounts; no token expiry; test changes pushed to prod; no per-agent action attribution.
- **Fix**: least privilege by design; just-in-time tokens (minutes-long, revocable); policy-as-code in CI/CD; dev creds physically unable to reach prod.
- **First action**: inventory every write/delete capability; for each, ask whether it needs to exist.

## MCP03 Tool Poisoning

Watch: [0:50:20](https://youtu.be/gYXLRMycVMk?t=3020)
- **What**: tools or their outputs compromised. Two forms: a rug pull (trusted tool turns malicious in an update) or schema poisoning. The model reads names, params, defaults and descriptions as instructions.
- **Leg**: untrusted content.
- **Incident**: Invariant Labs. A benign "fact of the day" MCP server's description told the model to pull WhatsApp history through the *legitimate* whatsapp-mcp tool and send it to the attacker. Any approval prompt came after the model was already compromised.
- **Detect**: schemas fetched without integrity checks; a writable schema registry without RBAC; schema edits auto-promoted; runtime schema changes accepted; no provenance or version pinning.
- **Fix**: sign schemas and manifests; TOFU-pin definitions at the host; scan the *full* schema including params and defaults; strip ANSI escapes; alert on `tools/list_changed`.
- **First action**: pin and sign every tool schema; scan names, params and defaults.

## MCP04 Supply Chain & Dependency Tampering

Watch: [0:58:50](https://youtu.be/gYXLRMycVMk?t=3530)
- **What**: MCP servers are assembled from SDKs, connectors and plugins. Any compromised dependency runs with full trust, and an agent amplifies it.
- **Leg**: all three.
- **Incidents**: (1) `postmark-mcp` (Koi Security): a community package, not by Postmark, clean for 15 releases. Version 1.0.16 added one line that BCC'd every email to the attacker. (2) MCP Inspector RCE (Oligo, Tenable; CVSS 9.4): an unauthenticated local web UI bound to `0.0.0.0` with no origin check. A malicious website plus DNS rebinding meant code execution on the developer's machine.
- **Detect**: unsigned plugins; dependencies fetched at runtime; missing SBOM; `latest`/floating versions; plugins calling unknown domains.
- **Fix**: signed components with provenance; an SBOM per server; pinned versions; dependency scanning in CI; sandboxed third-party plugins.
- **First action**: inventory every MCP server on dev machines; pin versions; bind to `127.0.0.1`. (Pinning stops the Postmark rug pull; localhost binding stops the Inspector RCE.)

## MCP05 Command Injection & Execution

Watch: [1:07:01](https://youtu.be/gYXLRMycVMk?t=4021)
- **What**: untrusted input reaches shell, SQL or file operations, and the LLM assembles the command, so there's no fixed code path to audit. Agents often run elevated. An industry study (Equixly) found command injection in about 43% of MCP servers tested.
- **Leg**: external comms.
- **Incident**: `mcp-remote` RCE (JFrog, CVSS 9.6). A malicious server's OAuth authorization URL carried shell metacharacters (PowerShell subexpressions on Windows, `;` on Unix). The client interpolated it into a shell command to open the browser.
- **Detect**: shell strings built from input; `exec`/`eval`/`shell=True`; generated code auto-executed; unsanitized file paths (`../`); string-interpolated SQL.
- **Fix**: `execFile`/`spawn` with argument arrays; `--` to end flag parsing; strip shell metacharacters; parameterized SQL plus verb allowlists; run local servers as non-root in a sandbox.
- **First action**: grep for `child_process.exec`, `os.system`, `shell=True`; convert each to array-based calls.

## MCP06 Intent Flow Subversion

Watch: [1:15:48](https://youtu.be/gYXLRMycVMk?t=4548)
- **What**: instructions planted in content the agent retrieves during a task (an issue, a file, a web page). The user's request was innocent; the agent switches to the attacker's goal mid-task. Hardest to defend because nothing looks malicious.
- **Leg**: all three.
- **Incident**: GitHub MCP "toxic agent flow" (Invariant Labs, May 2025). A public issue or a planted `SECURITY.md`-style file steered an agent holding an OAuth token with private-repo scope. It leaked private repo data (including an address and salary) through a PR, or deleted a branch when asked only to review PRs.
- **Detect**: no check that actions match the user's intent; retrieved text treated as instructions; plan-to-action with no gate; system prompt and retrieved content merged into one blob; intent drift in long sessions.
- **Fix**: anchor the user's goal in the system prompt; an independent guardrail model; tag retrieved content as untrusted data; split credentials so one agent can't bridge public and private.
- **First action**: build the trifecta scorecard for every production agent.

## MCP07 Insufficient Authentication & Authorization

Watch: [1:24:56](https://youtu.be/gYXLRMycVMk?t=5096)
- **What**: authN (can't verify identity) and authZ (no server-side, per-request scope check) failures; static credentials; client-side authorization. "MCP is an API."
- **Leg**: external comms.
- **Incident**: Obsidian Security (2025). An MCP server acted as both OAuth client and authorization server, with a static shared client ID. An attacker redirected the auth code to themselves and took over the account in one click (confused deputy). Logs looked like a normal OAuth flow.
- **Detect**: no mutual auth; static or long-lived tokens; authZ decided from client input; logs without identity correlation; the same token seen from different agents or IPs.
- **Fix**: mTLS between client and server; short-lived scoped tokens; validate every token server-side; resource indicators (RFC 8707); **never forward client tokens**, use token exchange (on-behalf-of) instead.
- **First action**: audit downstream calls for client-token pass-through.

## MCP08 Lack of Audit & Telemetry

Watch: [1:34:06](https://youtu.be/gYXLRMycVMk?t=5646)
- **What**: no structured record of which tools were called, with what, by whom. It's the detection layer for every other risk. There's no famous incident because these breaches go unseen.
- **Leg**: all three (it's how you'd see an attack on any leg).
- **Scenarios**: slow silent exfiltration through legitimate calls; an insider disabling telemetry; a malicious PDF leading to credential theft; a compliance bot drifting after retraining.
- **Detect**: activity not logged as structured data; logs that are local, mutable or deletable; tool calls and prompts not captured; no SIEM/XDR integration; no anomaly alerts.
- **Fix**: structured, tamper-evident logs with identity, tool, parameters and time; send to SIEM/XDR; mask PII in logs (or the logs become a new private-data leg); behavioral baselines and drills.
- **First action**: can you produce the last 30 days of MCP tool-call logs?

## MCP09 Shadow MCP Servers

Watch: [1:44:20](https://youtu.be/gYXLRMycVMk?t=6260)
- **What**: MCP servers outside governance, set up by well-meaning developers with default creds, outside central auth and monitoring.
- **Leg**: all three.
- **Incident**: a 2,000-person European bank found 47 unowned MCP instances, several with production DB credentials. They spread from a hackathon through shared templates and a repo-committed config into CI. A cited industry survey reported about 47% of enterprise agents unmonitored.
- **Detect**: deploy paths without registration; no asset inventory; services on dev ports (8000, 8080); no discovery scanning; agents calling endpoints not in the registry.
- **Fix**: a central registry (unregistered means fail); continuous discovery; **secure-by-default templates** (make the safe path the easy one); SSO/OIDC on every server; network segmentation.
- **First action**: grep all org repos for `mcp.json` to draft the inventory.

## MCP10 Context Injection & Over-Sharing

Watch: [1:51:53](https://youtu.be/gYXLRMycVMk?t=6713)
- **What**: context and memory shared across sessions, users or tenants, so data leaks or injected content persists. Can happen with no attacker at all.
- **Leg**: private data.
- **Incident**: Asana MCP (launched May 1, 2025; found June 4). Server-side state wasn't partitioned by tenant (a shared singleton or implicit session-to-user mapping). About 1,000 customers' projects, comments and files were exposed across tenants "under certain conditions"; the server was offline for about 2 weeks.
- **Detect**: shared context buffers or vector stores; context surviving across users; reuse without re-validating ownership; sensitive data entering untagged; no TTL.
- **Fix**: ephemeral per-session context; per-tenant namespace isolation enforced by infrastructure; classify and tag data on ingest; TTL with auto-purge; **a tenant isolation test in CI**.
- **First action**: write the "tenant A acts, tenant B sees nothing" test and add it to CI.

## Trifecta map

Watch: [0:22:34](https://youtu.be/gYXLRMycVMk?t=1354)

| Risk | Private data | Untrusted content | External comms |
|---|:-:|:-:|:-:|
| MCP01 Tokens | | | ● |
| MCP02 Scope creep | | | ● |
| MCP03 Tool poisoning | | ● | |
| MCP04 Supply chain | ● | ● | ● |
| MCP05 Command injection | | | ● |
| MCP06 Intent flow | ● | ● | ● |
| MCP07 AuthN/AuthZ | | | ● |
| MCP08 Audit | ● | ● | ● |
| MCP09 Shadow servers | ● | ● | ● |
| MCP10 Context | ● | | |

## Program maturity (beyond the minimum bar)

Watch: [1:59:51](https://youtu.be/gYXLRMycVMk?t=7191)
Discovery (continuous scans of network, repos, CI) → governance (registry lifecycle: submit, review, deploy, revalidate; a named owner; a kill switch) → identity (OAuth 2.1, just-in-time on-behalf-of tokens) → defense in depth (gateways, runtime policy, container isolation) → detection and response (audit pipeline, anomaly detection, "MCP compromised" tabletop drills).
Compliance frameworks to know: EU AI Act (govern), NIST AI RMF (map), AIUC-1 (adversarial testing), ISO/IEC 42001 (certify).
