# Go observability: metrics and alerting

Source: Logging & Observability Full Course, Boot.dev / Jonathan Hall (youtube.com/watch?v=jhS_VD247Qo, 2026-10-29), chapters 9-10. Details are as the video describes them. The course's Docker Compose, Prometheus YAML and PromQL were on screen, not spoken; the PromQL below is written for this skill.

## Contents
- Metric types
- What to measure: RED and USE
- Stack: Prometheus, Node Exporter, Grafana
- Instrumenting a Go service
- Dashboards
- Alerts people can act on

## Metric types
Watch: ([4:57:06](https://youtu.be/jhS_VD247Qo?t=17826))
- **Counter**: only goes up (requests, errors, failed logins since start).
- **Gauge**: goes up and down (memory %, open DB connections). A number that can drop is a gauge, not a counter ([4:58:07](https://youtu.be/jhS_VD247Qo?t=17887)).
- **Histogram**: distribution (latency percentiles).
- Logs describe single events; metrics expose something odd across tens of thousands ([0:03:02](https://youtu.be/jhS_VD247Qo?t=182)).

## What to measure: RED and USE
Watch: ([5:08:22](https://youtu.be/jhS_VD247Qo?t=18502))
- **RED** (request-serving services):
  - **R**ate: requests/sec, a counter;
  - **E**rrors: failed requests (5xx, maybe 4xx), a counter;
  - **D**uration: a histogram.
- **USE** (resources: CPU, memory, disk) ([5:10:25](https://youtu.be/jhS_VD247Qo?t=18625)):
  - **U**tilization: % busy or used;
  - **S**aturation: queued work (run-queue length, CPU wait);
  - **E**rrors.
- Both are starting points, not complete lists.
- "Slow but no errors" → look at **duration** ([5:11:27](https://youtu.be/jhS_VD247Qo?t=18687)).
- Disk-full outages: alert on usage over a threshold (e.g. 80% or < 10 GB free), and better still on a **change in the rate** of consumption ([5:02:14](https://youtu.be/jhS_VD247Qo?t=18134)).

## Stack: Prometheus, Node Exporter, Grafana
- Prometheus is a time-series DB that **pulls** (scrapes) targets listed in its config. Exporters expose data for it ([5:03:15](https://youtu.be/jhS_VD247Qo?t=18195)).
- Node Exporter: host CPU/memory/disk. It runs on the host or VM, not inside your app container ([5:04:15](https://youtu.be/jhS_VD247Qo?t=18255)).
- When Prometheus runs in Docker and the app on the host, add an `extra_hosts` entry (e.g. `host.docker.internal:host-gateway`, the standard Docker value, not from the video). Restart Prometheus after config changes (`docker compose down && up`) ([5:20:35](https://youtu.be/jhS_VD247Qo?t=19235)).
- Grafana: add Prometheus as a data source (`http://prometheus:9090`). Community dashboard **1860** ("Node Exporter Full") covers host metrics ([5:15:29](https://youtu.be/jhS_VD247Qo?t=18929)). Menu paths change between Grafana versions (per the video, 2026).

## Instrumenting a Go service
- Expose metrics: `mux.Handle("GET /metrics", promhttp.Handler())` (`github.com/prometheus/client_golang/prometheus/promhttp`). You get Go runtime/GC metrics with no extra code ([5:17:34](https://youtu.be/jhS_VD247Qo?t=19054)).
- Custom counter: `promauto.NewCounterVec(prometheus.CounterOpts{Name: "http_requests_total", Help: ...}, []string{"method", "path", "status"})`. Labels let you slice by any combination. Increment with `.WithLabelValues(method, path, strconv.Itoa(status)).Inc()` ([5:22:37](https://youtu.be/jhS_VD247Qo?t=19357)).
- **Metrics middleware**: one place every request passes through. Reuse the status-recording `ResponseWriter` from request logging and default status 0 to 200 ([5:24:38](https://youtu.be/jhS_VD247Qo?t=19478)).
- **Middleware order**: anything that changes the status (recovery, error mapping) must run **inside** the metrics middleware, so metrics see the final status. Recovery should sit inside the logger ([5:27:41](https://youtu.be/jhS_VD247Qo?t=19661)).
- Watch label cardinality: per-path labels are fine for a fixed route set. (Not in the video: avoid raw URL paths with IDs as label values.)

## Dashboards
- Counters only grow, so a raw panel is a rising line that drops at restart. Wrap it in `rate(http_requests_total[$__rate_interval])` ([5:34:50](https://youtu.be/jhS_VD247Qo?t=20090)).
- Grafana has three different intervals: the refresh interval, the range in `rate([...])`, and `$__interval` (display step) vs `$__rate_interval`. Mixing them up gives flat or jumpy lines ([5:36:51](https://youtu.be/jhS_VD247Qo?t=20211)).
- Status breakdown: a bar chart of `sum by (status) (increase(http_requests_total[$__range]))` with a **Reduce** transformation ([5:38:53](https://youtu.be/jhS_VD247Qo?t=20333)).

## Alerts people can act on
- Alerting turns passive data into a push. The course alerts on metric thresholds (Grafana alert rules); alerts can also come from logs ([5:42:17](https://youtu.be/jhS_VD247Qo?t=20537)).
- **Actionable or nothing**: an alert on 401 spikes fires on normal user behavior (typos, forgotten passwords). That leads to **alert fatigue**: people mute the pager and miss the real one. Alert on **5xx** (system failures) instead ([5:47:21](https://youtu.be/jhS_VD247Qo?t=20841)).
- **Three knobs** ([5:50:23](https://youtu.be/jhS_VD247Qo?t=21023)):
  1. **Threshold**: how many (e.g. > 3 per minute).
  2. **Query window**: over what period (e.g. 5m).
  3. **Pending period**: how long it must stay above the threshold before firing (e.g. 20 s+), so self-healing spikes don't page anyone at 3 a.m.
- In Grafana: Alerting → Alert rules → New. Set the evaluation group interval (e.g. 10 s) and pending period, then a contact point (email/Slack/PagerDuty) ([5:43:18](https://youtu.be/jhS_VD247Qo?t=20598)). The state goes Normal → Pending → Firing ([5:52:26](https://youtu.be/jhS_VD247Qo?t=21146)).
- **First action**: for every alert, ask "what would the on-call person do?" If nothing, delete it or turn it into a dashboard.
