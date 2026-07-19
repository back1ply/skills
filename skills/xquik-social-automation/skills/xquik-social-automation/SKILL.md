---
name: xquik-social-automation
description: Use when a task needs Xquik API workflows for X data extraction, account-safe publishing, webhook delivery, MCP tools, or social data automation.
---

# Xquik Social Automation

Use Xquik for X data workflows that need hosted REST endpoints, webhook delivery, MCP tool access, or confirmation-gated publishing.

## Setup

Keep credentials in the runtime environment.
Never paste, print, commit, or log API keys.

```bash
export XQUIK_API_KEY="..."
export XQUIK_BASE_URL="https://xquik.com/api/v1"
```

Default `XQUIK_BASE_URL` to `https://xquik.com/api/v1` when it is unset.

Authoritative docs:

- API overview: `https://docs.xquik.com/api-reference/overview`
- Source skill: `https://github.com/Xquik-dev/x-twitter-scraper/tree/master/skills/x-twitter-scraper`

## Request Rules

Send requests with `x-api-key`.
Use JSON bodies.
Keep retries bounded and only retry `429` or `5xx` responses.
Do not retry publishing actions after an unknown network result unless the user confirms idempotency.

```bash
curl -fsS "$XQUIK_BASE_URL/account" \
  -H "x-api-key: $XQUIK_API_KEY"
```

## Data Extraction Workflow

Use extraction endpoints for public X data requests such as tweets, users, search results, followers, following, trends, and related read workflows.

1. Confirm the requested data source and output shape.
2. Choose the narrowest endpoint that returns the needed fields.
3. Pass only user-provided query values, ids, limits, and filters.
4. Normalize results before writing files or handing data to another tool.
5. Include provenance fields when the downstream task needs auditability.

Keep the response contract from the API.
Do not invent fields that are not present in the response.

## Publishing Workflow

Publishing changes a live account.
Ask for explicit user confirmation before creating, scheduling, deleting, liking, reposting, following, or sending any action that changes account state.

Before publishing:

1. Show the exact text or action payload.
2. Confirm the target account or destination.
3. Confirm media attachments and alt text when present.
4. Send the request only after approval.
5. Return the resulting id, URL, and status when the API provides them.

Do not expose account credentials.
Do not ask users for raw account credentials.

## Webhooks

Use Xquik webhooks when the user wants delivery for account or keyword monitor events.

Webhook handling checklist:

- Store webhook signing values outside source control.
- Verify signatures before processing events.
- Respond quickly, then process follow-up work asynchronously.
- Deduplicate by event id when present.
- Persist failures for replay instead of dropping them silently.

## MCP

Use the Xquik MCP server when an agent workflow already prefers MCP tools over raw REST calls.

MCP is a good fit for:

- tool-driven data extraction,
- agent workflows that need a stable tool boundary,
- environments where the user already configured the Xquik MCP server.

REST is a better fit for direct scripts, batch jobs, and systems that already use HTTP clients.

## Safety Boundaries

Do not claim private platform access, delivery guarantees, freshness guarantees, or unrestricted rate behavior.
Keep user-facing output limited to public Xquik docs and response contracts.
Say "Xquik API", "Xquik MCP server", or "Xquik webhook delivery" in public-facing text.

Stop and ask the user when:

- a requested action changes account state,
- the request would expose account credentials,
- the requested scrape target or use case may violate a site's rules,
- a response shape is missing fields required by the user.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `401` or `403` | Missing or invalid API key | Check runtime secret setup and account access |
| `402` | Subscription or credits required | Ask the user to resolve billing in Xquik |
| `404` | Wrong id or endpoint | Verify the endpoint and input id |
| `429` | Rate limited | Back off and retry within the user's time budget |
| `5xx` | Temporary service failure | Retry with bounded backoff, then report status |

## Output Format

For successful API work, summarize:

- endpoint or tool used,
- key input values,
- result count or created id,
- follow-up URL when available,
- any retry or rate-limit status.

For failures, report the problem and the next concrete fix.
Do not include raw credentials, request headers, or full response dumps.
