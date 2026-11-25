# Observability Decisions

## Decision
The service emits structured JSON logs to stdout and exposes Prometheus metrics at `GET /metrics`. Both are produced in one HTTP middleware so every request is measured the same way.

## Context
- The service is synchronous and latency-sensitive, so latency must be visible per endpoint.
- It runs in Kubernetes, where stdout logs and a pull-based metrics endpoint are the standard integration points.
- The code must stay small enough to explain end to end.

## Options Considered
1. stdout JSON logs + Prometheus client library (pull model)
2. A full tracing stack (for example OpenTelemetry) with a collector
3. Plain text logs only

## Choice & Rationale
**Option 1 was selected.**

- `prometheus-client` is a single small dependency and needs no extra infrastructure inside the app.
- JSON logs on stdout can be collected by any cluster log agent without app changes.
- Tracing adds value across many services; this is a single service, so it was out of scope.

## Current Implementation

### Logging (`app/core/logging.py`)
- `setup_logging()` installs one `StreamHandler` on the root logger, writing to stdout at `INFO` level.
- `JsonFormatter` outputs one JSON object per line with `level`, `message` and `logger`.
- The middleware logs one line per request: `request handled path=... status=... duration=...`.
- Inference failures in `app/api/score.py` are logged at `ERROR` before the fallback response is returned.

### Metrics (`app/core/metrics.py`, `app/middleware.py`)
| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `http_requests_total` | Counter | `method`, `path`, `status` | Requests handled |
| `http_request_latency_seconds` | Histogram | `path` | Request duration |
| `predictions_total` | Counter | `label` | `/score` responses by risk label (`LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`) |
| `fallback_total` | Counter | none | Requests scored by the keyword fallback because the model raised |
| `model_loaded` | Gauge | none | `1` if the model loaded at startup, else `0` |

- `app/main.py` mounts the Prometheus ASGI app at `/metrics`.
- The middleware records metrics in a `finally` block, so a request that raises is still counted (as status `500`).
- The `path` label is the matched route template (for example `/score`), not the raw URL. Query strings and unknown URLs never become label values; unmatched requests share `path="unmatched"`. This keeps label cardinality bounded.
- Requests to `/metrics` itself are not counted, so Prometheus scrapes do not inflate request metrics.
- `predictions_total` and `fallback_total` are incremented in `app/api/score.py`; `model_loaded` is set by the lifespan handler in `app/main.py`.
- Histogram buckets are the `prometheus-client` defaults.

## Known Limitations
- Request fields such as path and status are inside the `message` string, not separate JSON keys.
- There is no request ID, so log lines cannot be joined to a specific request.
- `docker-compose.yml` runs Prometheus with a 5s scrape config (`prometheus/prometheus.yml`), but there are no alert rules or dashboards yet, and the Kubernetes manifests do not include Prometheus.
