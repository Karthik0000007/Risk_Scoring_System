# Architecture Decisions

## Decision
The system is a single stateless HTTP inference service with no database, prioritizing simplicity, predictability, and safe failure over scalability.

## Context
- The system performs synchronous risk scoring on user-submitted text.
- Latency requirements are strict but throughput is moderate.
- Failure would involve hidden coupling, complex deployment paths, or unclear operational behavior.

## Options Considered
1. Single stateless inference service
2. Microservices split (API, feature service, model service)
3. Event-driven asynchronous pipeline

## Choice & Rationale
**Option 1 was selected.**

- Stateless service simplifies scaling and rollback.
- Fewer services reduce operational failure modes.
- No database: each request is scored independently and nothing is persisted. The model is a file baked into the image and loaded once at startup.
- The same image runs locally, in Docker Compose (with Prometheus) and in Kubernetes.

## Why Alternatives Were Rejected
- Microservices introduce coordination overhead without clear benefit at this scale.
- Asynchronous pipelines complicate failure semantics and latency guarantees.
- Event-driven designs increase observability and retry complexity, which is out of scope.

## Trade-offs Accepted
- Vertical scaling over horizontal specialization
- Limited independent component evolution
- Single deployment unit
- No record of past scores (callers must store results if they need them)

## Revisit Conditions
- Sustained throughput above 500 RPS
- Multiple models requiring independent lifecycle management
- A need to persist scores for audit or retraining
- Separate platform and ML ownership teams
