---
name: go-observability
description: Reviews and builds observability for Go services (logs, metrics, alerts, profiles, traces) using Jonathan Hall's Boot.dev course. Covers log/slog setup, log-once error handling with stack traces and attributes carried on errors, request/build/user context, log security (redaction, sanitized HTTP errors, PII), Prometheus counters with RED/USE, Grafana alerts that people can act on, pprof CPU/heap/goroutine profiling, and OpenTelemetry tracing with Jaeger. Use when adding or reviewing logging in Go, switching from log/fmt to slog, writing request-logging or metrics middleware, deciding log levels, hunting duplicate or noisy logs, keeping secrets or PII out of logs, setting up Prometheus/Grafana dashboards or alerts, profiling a slow or memory-hungry Go service, adding OTel spans, or explaining observability basics (logs vs metrics vs traces), or when the user says "observability", "structured logging", "slog", "pprof", "alert fatigue", or "distributed tracing".
---

# Go observability

Distilled from "Logging & Observability Full Course (Prometheus, Grafana, OpenTelemetry)" (Boot.dev, author Jonathan Hall, 2026-10-29). New to this? Start with [references/basics.md](references/basics.md) (what logs, metrics, traces and profiles are). Detail in [references/logging.md](references/logging.md), [references/log-security.md](references/log-security.md), [references/metrics-alerting.md](references/metrics-alerting.md), [references/profiling-tracing.md](references/profiling-tracing.md).

## Core mental model
Build a system that helps you debug it. Logs say **what happened** (one event), metrics show **trends across thousands of events**, traces show **how it happened and what took so long**, profiles show **where CPU and memory go**, and alerts tell you **when a person must act** ([0:14:06](https://youtu.be/jhS_VD247Qo?t=846)) ([6:31:56](https://youtu.be/jhS_VD247Qo?t=23516)). Every log has readers (developers, operators, support, end users, auditors); write for the one who will read it ([1:50:48](https://youtu.be/jhS_VD247Qo?t=6648)). Good logs are discoverable, clear, specific, carry context, and respect privacy ([1:54:52](https://youtu.be/jhS_VD247Qo?t=6892)).

## Workflow: instrument a Go service
1. **Logger first.** Build it before parsing config. If the logger fails to start or close, write to stderr with `fmt.Fprintf` (the only place that's allowed) and exit ([0:57:33](https://youtu.be/jhS_VD247Qo?t=3453)). Return a close function that flushes buffers ([1:06:45](https://youtu.be/jhS_VD247Qo?t=4005)).
2. **Inject the logger** (no package globals, don't touch the default logger) ([0:41:12](https://youtu.be/jhS_VD247Qo?t=2472)). Use `log/slog`: text handler on stderr for people, JSON handler to file or cloud. Use `slog.NewMultiHandler` (Go 1.26+) to send each level to its own place ([1:27:00](https://youtu.be/jhS_VD247Qo?t=5220)).
3. **Add context once, at the edges:** build info via `-ldflags -X` ([3:07:50](https://youtu.be/jhS_VD247Qo?t=11270)), instance (env, hostname) ([3:13:56](https://youtu.be/jhS_VD247Qo?t=11636)), and per request (duration, status, bytes, user, request ID) in one request-logging middleware ([3:18:03](https://youtu.be/jhS_VD247Qo?t=11883)).
4. **Errors:** wrap with context and return. Log once, at the top. Carry slog attributes and stack traces on the error and expand them in `ReplaceAttr` ([2:40:13](https://youtu.be/jhS_VD247Qo?t=9613)).
5. **Security pass:** redact at the source, sanitize client-facing 401/403/500 bodies, and add key/URL filtering only as a backstop ([4:44:02](https://youtu.be/jhS_VD247Qo?t=17042)).
6. **Metrics:** expose `/metrics` with promhttp and add RED counters/histograms in a metrics middleware ([5:24:38](https://youtu.be/jhS_VD247Qo?t=19478)). Graph `rate()`, not raw totals ([5:34:50](https://youtu.be/jhS_VD247Qo?t=20090)).
7. **Alerts:** only on things a person must act on (5xx, not 401s), with threshold + window + pending period ([5:50:23](https://youtu.be/jhS_VD247Qo?t=21023)).
8. **When something is slow or leaking:** profile with pprof (behind auth), fix only the hot spot ([5:56:17](https://youtu.be/jhS_VD247Qo?t=21377)). Add OTel spans at handlers and slow dependencies ([6:52:23](https://youtu.be/jhS_VD247Qo?t=24743)).

## Quick checks (code review)
| Look for | Why / where |
|---|---|
| `log.Printf` then `return err` (log and rethrow) | Logging counts as handling; handle each error once → logging.md |
| `log.Fatal` / `log.Panic` anywhere | Couples logging with exit/panic; skips defers, can't recover. Log, then `os.Exit` ([0:59:35](https://youtu.be/jhS_VD247Qo?t=3575)) |
| `fmt.Print*` used as logging | Only OK when the logger itself failed. Enforce with golangci-lint `forbidigo` ([0:32:01](https://youtu.be/jhS_VD247Qo?t=1921)) |
| `Warn` level | Usually an undecided level: pick info or error ([1:24:58](https://youtu.be/jhS_VD247Qo?t=5098)) |
| 4xx logged at error | Client mistake, system working: debug/info. Error = an admin must know ([1:36:05](https://youtu.be/jhS_VD247Qo?t=5765)) |
| "entering X" / several logs for one event / logging every retry | Collapse to one log per event; log only the final retry failure ([2:15:15](https://youtu.be/jhS_VD247Qo?t=8115)) |
| Committed ad-hoc debug logs | Keep only if a teammate would want them later ([1:34:05](https://youtu.be/jhS_VD247Qo?t=5645)) |
| Buffered file writer without flush on exit; buffered stderr | Lost logs on exit; bursty console → logging.md |
| Error passed as `slog.String("error", err.Error())` | Skips `ReplaceAttr` expansion: pass the error value (`slog.Any`) ([3:48:42](https://youtu.be/jhS_VD247Qo?t=13722)) |
| Middleware reassigning a captured `logger` | Closure leak: one request's attrs land on later ones. Use a local copy ([3:39:27](https://youtu.be/jhS_VD247Qo?t=13167)) |
| Log context stored by value in `context` | Must be a pointer, set before the logger middleware runs ([3:33:20](https://youtu.be/jhS_VD247Qo?t=12800)) |
| Raw DSN, full request/response body, URL with key, full IP in logs | Secret/PII leak → log-security.md |
| Raw error text in 401/403/500 response bodies | User enumeration and internals leak; log the full error, send a generic one ([4:28:40](https://youtu.be/jhS_VD247Qo?t=16120)) |
| `import _ "net/http/pprof"` on the public mux | Exposes profiles to everyone; register handlers explicitly behind auth ([6:02:25](https://youtu.be/jhS_VD247Qo?t=21745)) |
| Dashboard on a raw counter; alert on 401s; pending period 0 | Use `rate()`; alert on 5xx; add a pending period → metrics-alerting.md |
| New span ctx not passed down (`r.Context()` reused) | Child spans detach from the trace ([6:57:26](https://youtu.be/jhS_VD247Qo?t=25046)) |
| `defer shutdown(context.Background())` for OTel | Could hang on exit; use a timeout ([6:48:16](https://youtu.be/jhS_VD247Qo?t=24496)) |

## Rules of thumb
- Prefer `slog.String`/`slog.Int` attrs over alternating key/value args: an odd count shifts every key after it ([1:40:09](https://youtu.be/jhS_VD247Qo?t=6009)).
- Info = useful in a log search; debug = rarely needed; error = an admin should look. Startup/shutdown can be debug ([1:36:05](https://youtu.be/jhS_VD247Qo?t=5765)).
- Too much log beats none, but logs cost storage and, worse, search time. Ask "who will read this?" before adding one ([2:07:04](https://youtu.be/jhS_VD247Qo?t=7624)).
- For multi-errors (`errors.Join`), solve only the shapes your app actually produces, not the general tree ([2:53:25](https://youtu.be/jhS_VD247Qo?t=10405)).
- Log filtering is a safety net, never the main defense ([4:44:02](https://youtu.be/jhS_VD247Qo?t=17042)).
- Profile when there is a real problem, not before ([5:58:19](https://youtu.be/jhS_VD247Qo?t=21499)).
- A span error status is not a failed request; spans are not stack frames, so trace the interesting work only ([6:42:06](https://youtu.be/jhS_VD247Qo?t=24126)).

## Known gaps
- On-screen code (Docker Compose/Prometheus YAML, PromQL for the alerts and bar chart, the course's `argsToAttr`, spy writers, `ReplaceAttr` bodies) is not in the transcript. References describe the APIs; any snippet there is written for this skill, not copied from the video.
- Grafana menu paths and defaults vary by version (the instructor says so); treat them as "per the video (2026)".
- Captions were auto-generated; names (Jaeger, Grafana, forbidigo, lmittmann/tint) were fixed from context.
- Examples are Go-only; the principles (log once, RED/USE, actionable alerts) carry to other languages.

## Sources
| Video | Channel | Date | Used for |
|---|---|---|---|
| [Logging & Observability Full Course (Prometheus, Grafana, OpenTelemetry)](https://www.youtube.com/watch?v=jhS_VD247Qo) | Boot dev | 2026-10-29 | Whole skill (course by Jonathan Hall); transcript in `data/raw/jhS_VD247Qo.json` |
| [Go 1.26 release notes](https://go.dev/doc/go1.26) / [Go 1.27 release notes](https://go.dev/doc/go1.27) | go.dev | 2026 | Verified `slog.NewMultiHandler` (1.26) and `goroutineleak` profile (1.27) |
