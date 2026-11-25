from prometheus_client import Counter, Gauge, Histogram

# Request metrics. `path` is the route template (e.g. /score), never the raw URL,
# so label cardinality stays bounded. Unknown URLs share the "unmatched" label.
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["path"],
)

# Model metrics.
PREDICTIONS = Counter(
    "predictions_total",
    "Scoring responses by risk label",
    ["label"],
)

FALLBACKS = Counter(
    "fallback_total",
    "Requests scored by the keyword fallback because the model failed",
)

MODEL_LOADED = Gauge(
    "model_loaded",
    "1 if the model is loaded and the service is ready, else 0",
)
