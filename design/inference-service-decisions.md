# Inference Service Decisions

## Decision
The inference layer will be implemented as a stateless HTTP service exposing a synchronous REST API with strict input validation, bounded latency, and explicit failure behavior.

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
- This aligns with conservative production choices common in Japanese platforms.

## API Contract Principles
- Inputs are strictly validated at the boundary.
- Invalid requests fail fast with explicit error codes.
- Responses always include model version and confidence metadata.

## Model Loading Strategy
- Model artifacts are loaded once at process startup.
- Readiness probes fail until model loading succeeds.
- Model is treated as immutable during runtime.

## Latency Control
- Inference execution is bounded by request-level timeouts.
- No retries are performed within the service.
- Slow requests are terminated to protect tail latency.

## Failure Behavior
- If model loading fails, the service does not accept traffic.
- If inference fails, the request returns an explicit error response.
- If persistence fails, inference still succeeds with degraded metadata.

## Trade-offs Accepted
- Service restart required for model update
- No per-request model switching
- Limited flexibility in experimentation

## Revisit Conditions
- Multiple models required concurrently
- Dynamic model routing or A/B testing
- Sub-10ms latency requirements
