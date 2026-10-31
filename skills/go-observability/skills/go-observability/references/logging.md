# Go observability: logging detail

Source: Logging & Observability Full Course, Boot.dev / Jonathan Hall (youtube.com/watch?v=jhS_VD247Qo, 2026-10-29). Details are as the video describes them; API names checked against the Go docs. Code shown here is written for this skill, not copied from the video.

## Contents
- Logger setup and ownership
- Buffered file output and closing
- slog: handlers, levels, attributes, formats
- Levels: what goes where
- Minimal logging: one log per event
- Errors: log once, stack traces, attributes on errors, multi-errors
- Context: build, instance, request, user, request ID
- Storage: console, files, rotation, syslog
- Testing log output

## Logger setup and ownership
- **What**: Use a logger, not `fmt.Print*`. One place controls where every log goes, and you get timestamps and levels ([0:20:50](https://youtu.be/jhS_VD247Qo?t=1250)).
- **Detect**: `fmt.Print*`/`log.Print*` scattered through code; changes made to the default global logger.
- **Do**:
  - Send logs to **stderr**, not stdout ([0:28:58](https://youtu.be/jhS_VD247Qo?t=1738)).
  - Create your own logger instead of changing the default one, because third-party libraries share the default ([0:28:58](https://youtu.be/jhS_VD247Qo?t=1738)).
  - Then inject it (struct fields, constructor args), no package globals. This lets tests run in parallel and lets parts of the app wrap the logger with extra attrs ([0:41:12](https://youtu.be/jhS_VD247Qo?t=2472)).
  - Pick output by environment, e.g. `LINKO_LOG_FILE` set → file + stderr, unset → stderr only ([0:50:25](https://youtu.be/jhS_VD247Qo?t=3025)).
- **Bootstrapping exception**: create the logger first, before full config parsing, so config errors can be logged. If the logger itself fails, `fmt.Fprintf(os.Stderr, ...)` and return a non-zero exit code ([0:57:33](https://youtu.be/jhS_VD247Qo?t=3453)).
- **Never `log.Fatal` / `log.Panic`**: they couple logging with control flow. `Fatal` exits without running defers (unflushed logs, open DB connections) and callers can't recover. Write two lines instead: log, then `os.Exit(1)` ([0:59:35](https://youtu.be/jhS_VD247Qo?t=3575)).
- **Migrating a team off fmt**: golangci-lint's `forbidigo` with a rule such as `^fmt\.Print.*$` → "use the logger" ([0:32:01](https://youtu.be/jhS_VD247Qo?t=1921)).
- **Request logging**: one middleware wrapping the whole mux, not each route. Skip noisy endpoints (e.g. `/healthz`) inside the middleware with an early return ([0:37:08](https://youtu.be/jhS_VD247Qo?t=2228)).
- **First action**: grep for `fmt.Print`, `log.Fatal`, `log.Panic`, and the default `log.`/`slog.` package functions.

## Buffered file output and closing
- **What**: `bufio.NewWriterSize(file, 8<<10)` batches small writes to cut syscalls ([1:03:41](https://youtu.be/jhS_VD247Qo?t=3821)).
- **Do**: buffer the **file only**. A buffered stderr makes console output bursty ([1:04:42](https://youtu.be/jhS_VD247Qo?t=3882)).
- **Bug it brings**: if the buffer isn't flushed on exit, the last logs are lost ([1:06:45](https://youtu.be/jhS_VD247Qo?t=4005)). The logger constructor should return a `close func() error` that flushes, then closes the file (a no-op for stderr-only), and `run()` should `defer` it. If close fails, report it with `fmt.Fprintf(os.Stderr, ...)`, since the logger can no longer be trusted ([1:08:50](https://youtu.be/jhS_VD247Qo?t=4130)).
- **First action**: every constructor that returns a logger writing to a file also returns a close function, and the caller defers it.

## slog: handlers, levels, attributes, formats
- slog has a frontend (`*slog.Logger`) and a backend (`slog.Handler`), like `database/sql` and its drivers. The standard library ships `NewTextHandler` and `NewJSONHandler`; others write to clouds, syslog, and so on ([1:15:46](https://youtu.be/jhS_VD247Qo?t=4546)). slog shipped in Go 1.21 (the video says "June 2023"). Prefer it over Logrus/Zerolog/Zap unless you have a strong reason ([1:15:46](https://youtu.be/jhS_VD247Qo?t=4546)).
- There is no `Printf`; use attributes. While migrating, `logger.Info(fmt.Sprintf(...))` is a stopgap only ([1:17:49](https://youtu.be/jhS_VD247Qo?t=4669)).
- **Levels**: Debug −4, Info 0, Warn 4, Error 8. The gaps leave room for custom levels, which are logged with `logger.Log(ctx, level, ...)` ([1:23:58](https://youtu.be/jhS_VD247Qo?t=5038)). Filter with `&slog.HandlerOptions{Level: slog.LevelDebug}` ([1:25:58](https://youtu.be/jhS_VD247Qo?t=5158)).
- **Fan-out by level**: build one handler per destination (stderr text at Debug, file JSON at Info) and combine them with `slog.NewMultiHandler(h1, h2)` (Go 1.26+). Move the fan-out from `io.MultiWriter` to the handler level when the destinations need different levels or formats ([1:27:00](https://youtu.be/jhS_VD247Qo?t=5220)). Define the stderr handler once and reuse it in both code paths so they can't drift ([1:31:03](https://youtu.be/jhS_VD247Qo?t=5463)).
- **Attributes**: `slog.String("method", r.Method)` and alternating `"method", r.Method` give identical output. Typed attrs are safer, because an odd number of alternating args shifts every key after the gap (`!BADKEY`) ([1:40:09](https://youtu.be/jhS_VD247Qo?t=6009)).
- **Groups**: `slog.Group("error", slog.String("message", ...), slog.String("stack_trace", ...))` nests related fields ([2:27:55](https://youtu.be/jhS_VD247Qo?t=8875)).
- **Format**: text (or a colored handler such as `github.com/lmittmann/tint`) on the console for people; JSON for files and cloud ingestion. Most cloud providers ingest JSON from stderr ([1:47:19](https://youtu.be/jhS_VD247Qo?t=6439)).
- **Color only on a TTY**: set tint's `NoColor` to `!(isatty.IsTerminal(fd) || isatty.IsCygwinTerminal(fd))` (`github.com/mattn/go-isatty`) so redirected output has no escape codes ([4:05:15](https://youtu.be/jhS_VD247Qo?t=14715)).

## Levels: what goes where
- **Error**: something an admin or developer must know; can route to Sentry, Slack or alerts ([1:25:58](https://youtu.be/jhS_VD247Qo?t=5158)).
- **Info**: what you want in a log search (logins, requests served) ([1:36:05](https://youtu.be/jhS_VD247Qo?t=5765)).
- **Debug**: low operational value; startup/shutdown can live here ([1:36:05](https://youtu.be/jhS_VD247Qo?t=5765)).
- **Warn**: on servers, usually a sign nobody decided. Choose info or error ([1:24:58](https://youtu.be/jhS_VD247Qo?t=5098)).
- **4xx responses are not errors**: the system worked and the client made a mistake (debug/info). 5xx usually are, though an upstream 502 you can't fix may not be ([1:37:07](https://youtu.be/jhS_VD247Qo?t=5827)).
- **Debug logs**: most committed ones were ad-hoc debugging leftovers. Keep one only if a teammate turning on debug would want it ([1:34:05](https://youtu.be/jhS_VD247Qo?t=5645)).

## Minimal logging: one log per event
Logs cost storage and, more importantly, search time ([2:07:04](https://youtu.be/jhS_VD247Qo?t=7624)). Rules ([2:08:05](https://youtu.be/jhS_VD247Qo?t=7685)):
1. Don't log the same event twice (handler + middleware + elsewhere).
2. Don't log what no reader cares about; think before "might be useful someday".
3. Don't log events that may resolve themselves: in a retry loop, log only the final failure.
4. Log at the right level, so debug noise stays out of prod.
5. Use structured logs and timestamps.
- **Redundant pairs**: "calling GetUser" + "entering GetUser" is ad-hoc tracing. Use tracing instead ([2:11:08](https://youtu.be/jhS_VD247Qo?t=7868)).
- **One log per event**: replace "open file / reading / read ok / closing" with a single log per outcome. A failure log implies the earlier steps succeeded ([2:15:15](https://youtu.be/jhS_VD247Qo?t=8115)). Before deleting a log, check its fields are already on the surviving one ([2:19:20](https://youtu.be/jhS_VD247Qo?t=8360)).
- Don't log all user metadata on every action ([2:11:08](https://youtu.be/jhS_VD247Qo?t=7868)).

## Errors: log once, stack traces, attributes on errors, multi-errors
- **Not every error value is an error state** (e.g. an expected file-not-found). Some logs are errors; most errors get logged ([2:20:49](https://youtu.be/jhS_VD247Qo?t=8449)).
- **Handle once** (Dave Cheney, "Don't just check errors, handle them gracefully"). Handling means making one decision, and logging is a decision. Log-and-return gives duplicate logs ([2:33:04](https://youtu.be/jhS_VD247Qo?t=9184)). Fix: the inner function wraps with `fmt.Errorf("validate item %d: %w", i, err)` and returns; the top level logs once ([2:35:07](https://youtu.be/jhS_VD247Qo?t=9307)).
- **Stack traces**: the standard library doesn't add them (dropped from Go 1.13 for performance). The course uses `github.com/pkg/errors` (`pkgerr.WithStack(err)`, printed with `%+v`), imported as `pkgerr` to avoid confusion with `errors` ([2:23:52](https://youtu.be/jhS_VD247Qo?t=8632)). Note: that repo has been archived (read-only) since 2021; it still works, and alternatives exist. Stack traces cost CPU and space, so skip them on very hot paths ([2:21:50](https://youtu.be/jhS_VD247Qo?t=8510)).
- **Expand in `ReplaceAttr`**: when `a.Key == "error"` and the value is an `error`, return a group with `message`, plus `stack_trace` when it implements the (unexported, define-it-yourself) `StackTrace() errors.StackTrace` interface ([2:29:59](https://youtu.be/jhS_VD247Qo?t=8999)).
- **Keep fields structured on errors**: wrapping with `fmt.Errorf` turns `path=...` into text. Instead, define an `errorWithAttrs{error; attrs []slog.Attr}` with `Unwrap()` and `Attrs()`, a `WithAttrs(err, args...)` constructor (key/value parsing copied from slog's internal argsToAttr), and an `Attrs(err)` helper that walks the whole chain ([2:40:13](https://youtu.be/jhS_VD247Qo?t=9613)). That walk uses a direct type assertion plus `errors.Unwrap` in a loop, because `errors.As` stops at the first match ([2:44:16](https://youtu.be/jhS_VD247Qo?t=9856)). Put these in an app-level errors package ([2:45:18](https://youtu.be/jhS_VD247Qo?t=9918)).
- **Multi-errors** (`errors.Join`, batch or fan-out): by default they render as newline-joined text. In `ReplaceAttr`, detect `interface{ Unwrap() []error }` and emit an `errors` group with numbered entries, each expanded like a single error ([2:53:25](https://youtu.be/jhS_VD247Qo?t=10405)). Solve only the nesting your app produces ([2:53:25](https://youtu.be/jhS_VD247Qo?t=10405)).
- **First action**: search for `logger.Error(...)` followed by `return err`; delete the log and wrap the error.

## Context: build, instance, request, user, request ID
- **Build info on every log**: version/commit and build time, so you know which deploy produced a log ([3:05:48](https://youtu.be/jhS_VD247Qo?t=11148)). `-buildvcs`/`debug.ReadBuildInfo` needs `.git` in the build (awkward in Docker). The course prefers `go build -ldflags "-X <module>/internal/build.GitSHA=$(git rev-parse HEAD) -X <module>/internal/build.BuildTime=..."` with placeholder defaults like `"unknown"` ([3:07:50](https://youtu.be/jhS_VD247Qo?t=11270)), then `logger = logger.With(...)` in the constructor ([3:09:51](https://youtu.be/jhS_VD247Qo?t=11391)). `-X` doesn't apply through a plain `go run`; build the binary to test it ([3:12:56](https://youtu.be/jhS_VD247Qo?t=11576)).
- **Instance context**: environment (`ENV`), hostname (`os.Hostname`), region, pod/container, kernel, OS. Choose what varies in your fleet ([3:13:56](https://youtu.be/jhS_VD247Qo?t=11636)).
- **Request context** (any request: HTTP, gRPC, cron, CLI) ([3:18:03](https://youtu.be/jhS_VD247Qo?t=11883)): start with duration, status, response size, and request size. Don't log all headers by default ([3:19:04](https://youtu.be/jhS_VD247Qo?t=11944)).
  - Request bytes: wrap `r.Body` in a counting `ReadCloser`. It counts only bytes the handler **read**; to count unread bytes, drain in `Close`, at a latency cost ([3:21:07](https://youtu.be/jhS_VD247Qo?t=12067)).
  - Response: wrap `ResponseWriter` to record status and bytes. `Write` without `WriteHeader` means 200; a handler that never writes leaves status 0, so default it to 200 ([3:25:11](https://youtu.be/jhS_VD247Qo?t=12311)).
- **User context (chicken-and-egg)**: auth runs below the logger. In the logger middleware, put a **pointer** to a `logContext{User string; Error error}` into the request context **before** `next.ServeHTTP`. Auth middleware fills it in, and the logger reads it after ([3:30:17](https://youtu.be/jhS_VD247Qo?t=12617)). A value instead of a pointer appears to work but loses every write ([3:33:20](https://youtu.be/jhS_VD247Qo?t=12800)). Add `user` only when it isn't empty ([3:36:25](https://youtu.be/jhS_VD247Qo?t=12985)).
- **Closure bug**: inside the returned handler, `logger = logger.With(...)` rewrites the captured variable for all later requests. Use `lg := logger` per request ([3:39:27](https://youtu.be/jhS_VD247Qo?t=13167)).
- **Errors reach the request log**: replace `http.Error` with a helper `httpError(ctx, w, status, err)` that stores `err` in the log context and then calls `http.Error`. The request logger then adds it once, with `slog.Any("error", err)` so `ReplaceAttr` can expand it ([3:40:28](https://youtu.be/jhS_VD247Qo?t=13228)) ([3:48:42](https://youtu.be/jhS_VD247Qo?t=13722)).
- **Request ID across services**: middleware reads `X-Request-ID`, generates one if missing (`crypto/rand.Text()`, Go 1.24+), sets it on the **response** header, and logs it on every request. Run it before the request logger and keep the header name in a constant ([3:51:51](https://youtu.be/jhS_VD247Qo?t=13911)).

## Storage: console, files, rotation, syslog
- **Console**: fine for dev and quick checks, and often the actual prod path (cloud agents ingest stdout/stderr). **Files**: non-distributed apps that haven't scaled. **Cloud logging**: large or distributed systems needing indexed search and central access control. Cloud moves permission checks, it doesn't remove them ([4:00:06](https://youtu.be/jhS_VD247Qo?t=14406)).
- **Rotation**: current → `.0` → `.1` … with older files gzipped. Use distro `logrotate`, or for a single-binary Go app `gopkg.in/natefinch/lumberjack.v2`. `&lumberjack.Logger{Filename, MaxSize (MB), MaxAge (days), MaxBackups, LocalTime, Compress}` is an `io.Writer` that replaces your own `os.OpenFile`/bufio. Call its `Close` in the logger's close function ([4:10:22](https://youtu.be/jhS_VD247Qo?t=15022)).
- **Syslog**: treat the standard library `log/syslog` as deprecated; it has no structured logging. Use an slog adapter such as `github.com/samber/slog-syslog` ([4:16:30](https://youtu.be/jhS_VD247Qo?t=15390)).

## Testing log output
- Write logs to a `bytes.Buffer` and compare strings. Timestamps change, so in tests use `ReplaceAttr` to set `slog.TimeKey` to a fixed time (this proves a timestamp exists), or drop it ([2:04:02](https://youtu.be/jhS_VD247Qo?t=7442)).
- Assert the timestamp once per logger; drop it everywhere else to keep assertions simple ([2:06:03](https://youtu.be/jhS_VD247Qo?t=7563)).
