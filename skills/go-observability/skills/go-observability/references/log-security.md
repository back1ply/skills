# Go observability: log security

Source: Logging & Observability Full Course, Boot.dev / Jonathan Hall (youtube.com/watch?v=jhS_VD247Qo, 2026-10-29), chapter 8. Details are as the video describes them. Code shown here is written for this skill, not copied from the video.

Watch: ([4:19:27](https://youtu.be/jhS_VD247Qo?t=15567))

## Contents
- What not to log
- Sanitized HTTP errors
- Obfuscation (IP addresses)
- Filtering as a backstop
- Encrypting log values

## What not to log
- **Obvious**: passwords, API keys, card numbers, SSNs.
- **Less obvious** ([4:19:27](https://youtu.be/jhS_VD247Qo?t=15567)):
  - account numbers;
  - anything that reveals other users exist;
  - internal architecture details;
  - PII (names, addresses, phones, and **IP addresses** in many jurisdictions);
  - unreleased business information.
- Sensitivity is a spectrum. Some things should never be stored (keep only a password hash, hand cards to a processor); some are mildly private (an internal table name) ([4:20:29](https://youtu.be/jhS_VD247Qo?t=15629)).
- **Credentials that don't look like credentials**: DSNs and connection strings. Log a sanitized DSN without the password. Keep the user/db name only if it helps debugging (multi-tenant, many DBs) ([4:22:32](https://youtu.be/jhS_VD247Qo?t=15752)).
- **Full request/response bodies**: a common prod-debugging leak of API keys, card data, health records. Instead log only the JSON **keys** (optionally value types) to learn the shape without the data ([4:33:45](https://youtu.be/jhS_VD247Qo?t=16425)).
- **URLs and paths**: usually safe, but some APIs put keys in query strings, so even `path` can leak ([4:36:50](https://youtu.be/jhS_VD247Qo?t=16610)).
- Security says "log only what you need"; debugging says "log everything that might help". These pull against each other; choose on purpose for each field ([4:31:42](https://youtu.be/jhS_VD247Qo?t=16302)).
- **First action**: grep for `dsn`, `body`, `URL.String()`, `RemoteAddr`, `password`, `token` near logger calls.

## Sanitized HTTP errors
- Raw errors in responses leak data. `sql: no rows in result set` tells an attacker that user doesn't exist (user enumeration). `table migrated_users does not exist` reveals internals and sloppy deploys ([4:24:35](https://youtu.be/jhS_VD247Qo?t=15875)).
- **Do**: in the `httpError` helper, for **401, 403 and 500** send `http.StatusText(status)` to the client, keep the original text for other codes, and **still store the full error in the log context** ([4:28:40](https://youtu.be/jhS_VD247Qo?t=16120)) ([4:30:42](https://youtu.be/jhS_VD247Qo?t=16242)).
- Auth failures: one generic "unauthorized" for wrong user or wrong password. To help real users, use flows like "if you have an account, we sent a reset email" ([4:28:40](https://youtu.be/jhS_VD247Qo?t=16120)).
- A missing table should be a 500 and logged as an error; an unknown user is a 401. Different states, both with generic client text ([4:27:39](https://youtu.be/jhS_VD247Qo?t=16059)).

## Obfuscation (IP addresses)
- Log enough to tell clients apart without identifying them ([4:37:51](https://youtu.be/jhS_VD247Qo?t=16671)).
- `redactIP(addr)`:
  1. `net.SplitHostPort` the address; on error, return the input.
  2. `net.ParseIP(host).To4()`; if it's not IPv4, return the input (or truncate IPv6 to its prefix).
  3. Replace the last octet with `x`, e.g. `192.168.1.x` ([4:38:53](https://youtu.be/jhS_VD247Qo?t=16733)).
- Alternatives: hash the IP, or don't log it.

## Filtering as a backstop
- 100% accurate filtering is impossible (even with an LLM, which is expensive). Fix leaks at the source; filtering is the last line of defense ([4:44:02](https://youtu.be/jhS_VD247Qo?t=17042)).
- In `ReplaceAttr`:
  - if `a.Key` is in a sensitive list (keys such as password, key, API key, secret, pin, credit card; exact spellings were on screen; plus app-specific ones such as `user`), replace the value with `REDACTED` ([4:46:03](https://youtu.be/jhS_VD247Qo?t=17163));
  - for any string value that parses as a URL with `u.User` set and a password present, rebuild it with `url.UserPassword(u.User.Username(), "REDACTED")` ([4:47:04](https://youtu.be/jhS_VD247Qo?t=17224)).
- Prefer replacing over deleting: seeing `REDACTED` tells you where code tried to log a secret, so you can fix it there ([4:46:03](https://youtu.be/jhS_VD247Qo?t=17163)).

## Encrypting log values
- Rarely needed (the instructor used it once or twice in a career). Use it when you **must** log sensitive data, e.g. debugging an intermittent third-party financial API, and authorized people must read it later ([4:53:11](https://youtu.be/jhS_VD247Qo?t=17591)).
- `filippo.io/age`: encrypt the value to every authorized developer's public key. Remove a key when someone leaves. Output is longer base64 (not compression) ([4:54:12](https://youtu.be/jhS_VD247Qo?t=17652)).
