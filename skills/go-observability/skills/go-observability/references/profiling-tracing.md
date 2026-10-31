# Go observability: profiling and tracing

Source: Logging & Observability Full Course, Boot.dev / Jonathan Hall (youtube.com/watch?v=jhS_VD247Qo, 2026-10-29), chapters 11-12. Details are as the video describes them; Go 1.27 goroutine-leak profile checked against go.dev/doc/go1.27. Code shown here is written for this skill, not copied from the video.

## Contents
- When to profile
- Exposing pprof safely
- CPU profile
- Heap (memory) profile
- Goroutine profile and leaks
- Tracing concepts (OpenTelemetry)
- Adding tracing to a Go service
- Reading a trace
- Distributed tracing

## When to profile
Watch: ([5:53:14](https://youtu.be/jhS_VD247Qo?t=21194))
- Profile types:
  - CPU;
  - heap (memory);
  - goroutines;
  - blocking I/O;
  - execution trace.
- Go ships `pprof`; `testing` benchmarks are the other built-in tool ([5:55:17](https://youtu.be/jhS_VD247Qo?t=21317)).
- **Profile-driven development**: find a real problem (slow, OOM, rising CPU bill), profile to find the hot spot, and fix only that. Don't trade readability for speed where nothing is slow ([5:56:17](https://youtu.be/jhS_VD247Qo?t=21377)).
- **Exceptions**: CI performance checks for a few critical functions (e.g. crypto), comparing candidate designs for such code, and checking a perf fix in review ([5:58:19](https://youtu.be/jhS_VD247Qo?t=21499)).
- **PGO** (profile-guided optimization): feed a production CPU profile to the compiler for a free speedup ([5:57:18](https://youtu.be/jhS_VD247Qo?t=21438)).

## Exposing pprof safely
- `import _ "net/http/pprof"` registers every profile on `http.DefaultServeMux`. Avoid that on anything public ([6:01:22](https://youtu.be/jhS_VD247Qo?t=21682)).
- With your own mux, import `net/http/pprof` normally and register only what you need, e.g. `pprof.Index` at `GET /debug/pprof/` and `pprof.Profile` at `GET /debug/pprof/profile`. Put them **behind auth**, dev-only, or on a VPN/private port ([6:02:25](https://youtu.be/jhS_VD247Qo?t=21745)).

## CPU profile
- Profiling runs only on request, not all the time. Capture while generating load:
  - `curl -u user:pass "http://host/debug/pprof/profile?seconds=30" -o cpu.prof`
  - or `go tool pprof <url>` ([6:07:36](https://youtu.be/jhS_VD247Qo?t=22056)).
- Read: `go tool pprof <binary> cpu.prof`, then `top`. Build with `go build` so pprof can match the binary ([6:08:37](https://youtu.be/jhS_VD247Qo?t=22117)).
- Graph view (needs Graphviz): `go tool pprof -http=:0 cpu.prof`, or `go tool pprof -dot mem.prof | dot -Tsvg > mem.svg`. Box size = cost; follow the arrows up to your own function ([6:18:47](https://youtu.be/jhS_VD247Qo?t=22727)).
- **Worked example (Linko)**: 95% of CPU in `blowfish.encryptBlock`. Following callers up through `bcrypt` led to the redirect handler, which ran `bcrypt.GenerateFromPassword` on the long URL and threw the result away. Delete that call ([6:13:40](https://youtu.be/jhS_VD247Qo?t=22420)).

## Heap (memory) profile
- `curl ... "/debug/pprof/heap?seconds=30" -o mem.prof`. **flat** = memory allocated by the function itself; **cum** = itself plus everything it calls ([6:17:46](https://youtu.be/jhS_VD247Qo?t=22666)).
- **Worked example (Linko)**: the biggest allocation, `strings.Builder.grow` ← `strings.Repeat` ← redirect handler, appended a URL repeated 1,024 times to a package-level slice on every request. A slice that only grows looks like a leak ([6:22:50](https://youtu.be/jhS_VD247Qo?t=22970)).

## Goroutine profile and leaks
- `/debug/pprof/goroutine` is a **snapshot** (no `seconds`). To see growth, take several and compare them ([6:24:53](https://youtu.be/jhS_VD247Qo?t=23093)).
- Leaks show up only in busy, long-running systems because goroutines are cheap. The classic cause is **starting a goroutine with an infinite loop per request** ([6:26:55](https://youtu.be/jhS_VD247Qo?t=23215)).
- Go 1.27 (Aug 2026) adds a `goroutineleak` profile (`/debug/pprof/goroutineleak`). It finds goroutines blocked forever on unreachable channels or locks; it was a `GOEXPERIMENT` in 1.26. Use it before diffing raw goroutine dumps.

## Tracing concepts (OpenTelemetry)
- A log answers **what happened**; a trace answers **how, in what order, and what took so long**. A trace could in principle be rebuilt from logs, but it would be crowded and hard to read ([6:31:56](https://youtu.be/jhS_VD247Qo?t=23516)).
- OpenTelemetry (OTel) collects traces (and can also do logs and metrics); Jaeger displays them. Like Prometheus + Grafana, roughly ([6:30:54](https://youtu.be/jhS_VD247Qo?t=23454)).
- **Trace** = one request, possibly across services and frontend → backend. **Span** = a timed piece of work with ID, name, start/end, attributes, events and status. Spans are like stack frames but not one-to-one; you choose them ([6:36:00](https://youtu.be/jhS_VD247Qo?t=23760)).
- **Span status**: Unset (default), Ok, Error. An Error span doesn't mean the request failed (a coupon lookup can fail and the request still succeed). Unset means "not set", not success ([6:40:04](https://youtu.be/jhS_VD247Qo?t=24004)) ([6:42:06](https://youtu.be/jhS_VD247Qo?t=24126)).

## Adding tracing to a Go service
1. `initTracing(ctx)`: create an OTLP gRPC exporter (`otlptracegrpc.New`), then a `sdktrace.NewTracerProvider` with a batcher (e.g. 2 s timeout, so traces show up with a small delay). Call `otel.SetTracerProvider`, set a package-level `tracer = tp.Tracer("<scope name>")`, and return `tp.Shutdown` ([6:44:07](https://youtu.be/jhS_VD247Qo?t=24247)) ([6:56:26](https://youtu.be/jhS_VD247Qo?t=24986)).
2. Call it before the logger and `defer` shutdown so the last spans are flushed. Use a **timeout context**, not a bare `context.Background()`, so a stuck exporter can't block exit. Log if it fails ([6:48:16](https://youtu.be/jhS_VD247Qo?t=24496)).
3. Wrap the root handler with `otelhttp.NewHandler(mux, "name")` (`go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`). It creates a root span per request and puts it in the request context ([6:46:10](https://youtu.be/jhS_VD247Qo?t=24370)).
4. Local config through environment: `OTEL_EXPORTER_OTLP_INSECURE=true` (no TLS) and `OTEL_SERVICE_NAME=<svc>`. The default endpoint is `localhost:4317` ([6:46:10](https://youtu.be/jhS_VD247Qo?t=24370)).
5. Add child spans: `ctx, span := tracer.Start(r.Context(), "handler.shortenLink"); defer span.End()`. Then pass **that** `ctx` down. Tip: start every handler with `ctx := r.Context()` so adding a span later is a one-line change ([6:58:28](https://youtu.be/jhS_VD247Qo?t=25108)).
6. If a callee takes `*http.Request`, put the new ctx back with `r = r.WithContext(ctx)`, or its spans detach ([6:59:31](https://youtu.be/jhS_VD247Qo?t=25171)).
- **What to span**: handlers, auth that does real lookups, slow dependencies (DB, outbound HTTP, password hashing). Skip middleware that runs on every request with nothing interesting (request ID, logging, metrics) ([6:52:23](https://youtu.be/jhS_VD247Qo?t=24743)).

## Reading a trace
- In Jaeger, filter by service, then open the long traces (the short ones are often Prometheus scrapes) ([7:03:37](https://youtu.be/jhS_VD247Qo?t=25417)).
- Thick dark segments = the span is working; thin = waiting on a child. In the example, `auth.validatePassword` (bcrypt) took more than half the request **on purpose** (a slow hash slows attackers), and `shortenLink` mostly waited on `http.verifyDestination` (an outbound request checking the URL isn't a 404) ([7:06:39](https://youtu.be/jhS_VD247Qo?t=25599)).
- Use traces over logs when you need fine-grained timing of the parts of a request ([7:07:40](https://youtu.be/jhS_VD247Qo?t=25660)).

## Distributed tracing
- The trace context (trace ID + parent span ID) is propagated in HTTP headers or gRPC metadata. OTel SDKs in other languages speak the same protocol ([7:09:41](https://youtu.be/jhS_VD247Qo?t=25781)).
- Outbound HTTP needs `&http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}`, and requests built with `http.NewRequestWithContext(ctx, ...)` using the span's ctx ([7:10:41](https://youtu.be/jhS_VD247Qo?t=25841)).
- Every service must export to the **same** tracing backend for the spans to join up ([7:12:42](https://youtu.be/jhS_VD247Qo?t=25962)).
