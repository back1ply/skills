# Go observability: beginner basics

Source: Logging & Observability Full Course, Boot.dev / Jonathan Hall (youtube.com/watch?v=jhS_VD247Qo, 2026-10-29), mostly the intro and chapters 1-3, 9 and 12. Details are as the video describes them. Read this first if logs, metrics, traces or profiling are new to you; the other reference files assume it.

## Contents
- Why observability matters
- What observability is: three pillars plus alerting
- Logs
- Why use a logger instead of print
- Structured logs
- Log levels
- Timestamps and context
- Metrics
- Logs vs metrics
- Where metrics live: Prometheus and Grafana
- Traces
- Profiling
- Glossary

## Why observability matters
- The course opens with a scenario: your store returns 500 errors to 10% of visitors. You know something is broken, but not which requests trigger it, which of four servers is responsible, or whether it hits everyone or one country ([0:00:00](https://youtu.be/jhS_VD247Qo?t=0)).
- Every back-end developer eventually has to answer two questions: **how do I know something is going wrong**, and **how do I find the problem as fast as possible** ([0:00:00](https://youtu.be/jhS_VD247Qo?t=0)).
- One difference between junior and senior developers is whether they build systems that help debug themselves, or carry the whole debugging burden themselves ([0:05:58](https://youtu.be/jhS_VD247Qo?t=358)).

## What observability is: three pillars plus alerting
- **Observability** is the ability to know what a running application is doing, both right now and in the past ([0:13:05](https://youtu.be/jhS_VD247Qo?t=785)).
- It is usually described as three pillars plus a fourth piece built on them ([0:14:06](https://youtu.be/jhS_VD247Qo?t=846)):

| Piece | What it is | Example |
|---|---|---|
| **Logs** | A historical record of events in the system | "user 9284 failed to log in from 102.x.x.x" |
| **Metrics** | Aggregate numbers about the system over time | requests per second, errors in the last hour, % memory used |
| **Traces** | The path of one request through the system, maybe across several services, with timings | a request spent 72 ms checking the password and 40 ms calling another site |
| **Alerts** | Proactive messages when something needs attention, usually based on logs or metrics | "more than 5% of requests failed in the last 5 minutes" |

- Logs and metrics often describe the same information from different angles; they complement each other ([0:14:06](https://youtu.be/jhS_VD247Qo?t=846)).
- A stack trace is a simple kind of trace. Request tracing goes further and follows a request through the whole system ([0:15:06](https://youtu.be/jhS_VD247Qo?t=906)).
- A program that prints nothing when it starts is the least observable kind: you can't even tell it's running without sending it a request. The first fix is a "server started on :8899" log and a "shutting down" log ([0:16:08](https://youtu.be/jhS_VD247Qo?t=968)).

## Logs
- A log is a line of text (or a structured record) that a program writes when something happens: a request served, a login failed, a file couldn't be opened.
- Logs answer **"what happened?"** for a single event ([6:31:56](https://youtu.be/jhS_VD247Qo?t=23516)).
- People read logs to debug, operate, support users, and audit. Each of them wants different details (see logging.md, "consider the consumer") ([1:50:48](https://youtu.be/jhS_VD247Qo?t=6648)).

## Why use a logger instead of print
`fmt.Println` works, so why bother with a logging library ([0:20:50](https://youtu.be/jhS_VD247Qo?t=1250))?
1. **One switch for where logs go.** With print calls you'd have to edit thousands of lines to send output to a file or the network; a logger changes it in one place ([0:21:51](https://youtu.be/jhS_VD247Qo?t=1311)).
2. **Timestamps for free** on every line ([0:21:51](https://youtu.be/jhS_VD247Qo?t=1311)).
3. **Levels** (debug, info, warn, error) so you can filter. Go's old `log` package has no levels; its `Fatal` and `Panic` only change what happens after printing (exit or panic) ([0:21:51](https://youtu.be/jhS_VD247Qo?t=1311)).
4. Each logger call is one full line, so you don't add `\n` yourself ([0:24:54](https://youtu.be/jhS_VD247Qo?t=1494)).
- Go's `log` package flags control what each line starts with: `Ldate`, `Ltime`, `Lmicroseconds`, `Llongfile`/`Lshortfile` (caller's file), `LUTC`, `Lmsgprefix`, and `LstdFlags` (date + time) ([0:29:59](https://youtu.be/jhS_VD247Qo?t=1799)).

## Structured logs
- Plain logs are free-form strings. **Structured logs** add key-value pairs: `user_id=9284 ip=102.0.0.1 msg="login failed"` or the same as JSON ([1:11:41](https://youtu.be/jhS_VD247Qo?t=4301)).
- Why it matters: searching plain text for `9284` also matches file sizes and timestamps that contain those digits. Searching `user_id=9284` matches only that user ([1:13:43](https://youtu.be/jhS_VD247Qo?t=4423)).
- Nearly every cloud log service understands structured logs natively. Plain-text logs have to be parsed into fields first ([1:12:42](https://youtu.be/jhS_VD247Qo?t=4362)).
- The trade-off: structured logs are built for machines first and are slightly harder for people to read ([1:14:45](https://youtu.be/jhS_VD247Qo?t=4485)).
- Keys only help if they stay consistent across the codebase (`user_id` everywhere, not `uid` in one place) ([1:12:42](https://youtu.be/jhS_VD247Qo?t=4362)).
- In Go, the standard structured logger is `log/slog` ([1:15:46](https://youtu.be/jhS_VD247Qo?t=4546)).

## Log levels
- A level says how important a log is. slog has four: **Debug**, **Info**, **Warn**, **Error** ([1:23:58](https://youtu.be/jhS_VD247Qo?t=5038)).
- You set a minimum level per destination: e.g. show debug and up on your laptop, info and up in production ([1:25:58](https://youtu.be/jhS_VD247Qo?t=5158)).
- Rough meaning, per the course ([1:36:05](https://youtu.be/jhS_VD247Qo?t=5765)):
  - **Debug**: detail you rarely need, turned on while investigating.
  - **Info**: normal things worth finding later (a login, a request served).
  - **Error**: something an operator or developer should look at.
  - **Warn**: the course advises picking info or error instead.

## Timestamps and context
- A timestamp is the one piece of context that applies to every event. Without anything else, you can at least line up logs that happened at the same moment ([1:59:54](https://youtu.be/jhS_VD247Qo?t=7194)).
- On a busy server thousands of lines share a second, so timestamps alone aren't enough. Logs also need context: who, what, where, why (user, file name, request ID, server, app version) ([2:00:55](https://youtu.be/jhS_VD247Qo?t=7255)) ([1:55:52](https://youtu.be/jhS_VD247Qo?t=6952)).

## Metrics
- A metric is a **measurement** of something about your system, recorded over time ([4:57:06](https://youtu.be/jhS_VD247Qo?t=17826)).
- Three types ([4:57:06](https://youtu.be/jhS_VD247Qo?t=17826)):

| Type | Behaves like | Example | Not this |
|---|---|---|---|
| **Counter** | Only goes up (resets on restart) | number of failed logins since start | open DB connections (goes down too) |
| **Gauge** | Goes up and down | % memory used, current open connections | |
| **Histogram** | Counts values in buckets to show a distribution | how many requests took < 1 s, 1-2 s, 2-3 s… | |

- Example histogram from the course: 432 requests under 1 s, 976 between 1 and 2 s, 301 between 2 and 3 s. Most requests take 1-3 s, and a tail is slower ([5:09:23](https://youtu.be/jhS_VD247Qo?t=18563)).
- Percentiles come from histograms: "95% of requests finished in under 10 ms" ([4:57:06](https://youtu.be/jhS_VD247Qo?t=17826)).
- **System metrics** describe the machine (CPU, memory, disk, network). Most cloud providers show them without any setup ([5:01:13](https://youtu.be/jhS_VD247Qo?t=18073)).
- **Service metrics** describe your app (requests, errors, response times). You add these yourself in code ([5:17:34](https://youtu.be/jhS_VD247Qo?t=19054)).

## Logs vs metrics
- Logs tell you what happened in **one specific event**; metrics show you something odd happening **across tens of thousands of events** ([0:02:01](https://youtu.be/jhS_VD247Qo?t=121)).
- A typical flow: a metric or alert says "errors jumped at 14:05", then you search the logs around 14:05 to see which requests failed and why.
- Some information fits better as a log, some as a metric, and some works as both ([0:14:06](https://youtu.be/jhS_VD247Qo?t=846)).

## Where metrics live: Prometheus and Grafana
- **Prometheus** is a time-series database: it stores numbers with timestamps, and you query them with its own language (PromQL) ([4:59:09](https://youtu.be/jhS_VD247Qo?t=17949)).
- Unlike most databases it **pulls**: it visits each target's `/metrics` page on a schedule. An **exporter** is anything that serves such a page (Node Exporter for the host, your app for itself) ([5:03:15](https://youtu.be/jhS_VD247Qo?t=18195)).
- **Grafana** turns those numbers into dashboards and sends alerts. It can read many sources, not only Prometheus ([5:12:27](https://youtu.be/jhS_VD247Qo?t=18747)) ([5:14:29](https://youtu.be/jhS_VD247Qo?t=18869)).

## Traces
- A log is one moment in time; a trace is a two-dimensional view of several steps, their order, and how long each took. Logs answer "what happened"; traces answer "how did it happen and what took so long" ([6:31:56](https://youtu.be/jhS_VD247Qo?t=23516)).
- A **trace** is one request. It is made of **spans**: named, timed pieces of work such as "check password" or "call the other service". Spans nest inside each other ([6:36:00](https://youtu.be/jhS_VD247Qo?t=23760)).
- **OpenTelemetry** collects traces; **Jaeger** shows them as a timeline. This is roughly like Prometheus collecting metrics and Grafana showing them ([6:30:54](https://youtu.be/jhS_VD247Qo?t=23454)).

## Profiling
- Profiling measures where a running program spends resources: CPU time, memory, goroutines, waiting on I/O ([5:53:14](https://youtu.be/jhS_VD247Qo?t=21194)).
- Use it when something is slow or using too much memory, to find the one function to fix ([5:56:17](https://youtu.be/jhS_VD247Qo?t=21377)).
- Go's built-in profiler is **pprof** ([5:55:17](https://youtu.be/jhS_VD247Qo?t=21317)).

## Glossary
- **Alert fatigue**: so many unimportant alerts that people stop paying attention and miss the real ones ([5:47:21](https://youtu.be/jhS_VD247Qo?t=20841)).
- **Exporter**: a program or endpoint that exposes metrics for Prometheus to collect ([5:03:15](https://youtu.be/jhS_VD247Qo?t=18195)).
- **Handler (slog)**: the part of the logger that formats and writes logs (text, JSON, a cloud service) ([1:15:46](https://youtu.be/jhS_VD247Qo?t=4546)).
- **Middleware**: code that wraps every HTTP request, the natural place to log or measure all requests ([0:35:04](https://youtu.be/jhS_VD247Qo?t=2104)).
- **PII**: personally identifiable information (names, addresses, often IP addresses) that should stay out of logs ([1:56:53](https://youtu.be/jhS_VD247Qo?t=7013)).
- **Request ID**: a unique ID attached to a request so its logs can be found across services ([3:51:51](https://youtu.be/jhS_VD247Qo?t=13911)).
- **Span**: one timed step inside a trace ([6:36:00](https://youtu.be/jhS_VD247Qo?t=23760)).
