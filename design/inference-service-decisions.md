# Inference Service Decisions

## Decision
The inference layer is a stateless HTTP service exposing a synchronous REST API with strict input validation and explicit failure behavior.

## Context
- The service is invoked synchronously by upstream content submission systems.
- Latency directly impacts user experience.
- The service must be safe to scale horizontally and safe to roll back.
- Failure would involve unpredictable response times, hidden state, or silent correctness errors.

## Options Considered
1. REST-based synchronous HTTP service
2. gRPC-based inference service
3. Asynchronous inference via message queue

## Choice & Rationale
**Option 1 was selected.**

- REST is widely understood and easier to debug operationally.
- JSON payloads allow explicit schema validation and logging.
- Synchronous responses simplify failure semantics for callers.

## API Contract Principles
- Inputs are validated at the boundary by Pydantic: `content` must be 1 to 5000 characters.
- Invalid requests fail fast with `422`.
- Every `200` response includes `risk_score`, `risk_label`, `model_version` and a `degraded` flag, so callers can tell a model score from a fallback score.

## Model Loading Strategy
- The model artifact (`MODEL_PATH`, default `models/risk-v1.joblib`) is loaded once by the FastAPI lifespan handler at startup.
- If loading fails, the process stays up, `/readyz` returns `503` with the reason, and `/score` returns `503`.
- The model is treated as immutable during runtime.

## Latency Control
- No retries are performed within the service.
- There is no per-request timeout yet. Latency is measured with `scripts/loadtest.py` (p95 at concurrency 10 on a laptop: about 42 ms with local uvicorn, about 58 ms in Docker) and exposed as `http_request_latency_seconds`.

## Failure Behavior
- If model loading fails, the service reports not ready and does not score (`503`).
- If a prediction raises, the text is scored by whole-word keyword rules and the response is marked `degraded: true` with `model_version: "keyword-fallback-1.0"`.
- If the keyword rules also fail, the response is `risk_score: 0.5`, `risk_label: "UNKNOWN"`, `degraded: true`.

## Trade-offs Accepted
- Service restart required for model update
- No per-request model switching
- Limited flexibility in experimentation
- No request timeout: a slow prediction holds its worker thread until it finishes

## Revisit Conditions
- Multiple models required concurrently
- Dynamic model routing or A/B testing
- Sub-10ms latency requirements
