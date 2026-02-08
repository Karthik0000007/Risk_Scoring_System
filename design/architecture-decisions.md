# Architecture Decisions

## Decision
The system will be implemented as a single stateless HTTP inference service backed by a relational database, prioritizing simplicity, predictability, and safe failure over scalability.

## Context
- The system performs synchronous risk scoring on user-submitted text.
- Latency requirements are strict but throughput is moderate.
- Failure would involve hidden coupling, complex deployment paths, or unclear operational behavior.

## Options Considered
1. Single stateless inference service + database
2. Microservices split (API, feature service, model service)
3. Event-driven asynchronous pipeline

## Choice & Rationale
**Option 1 was selected.**

- Stateless service simplifies scaling and rollback.
- Fewer services reduce operational failure modes.
- Database is used only for metadata persistence, not online inference.
- Architecture mirrors conservative production systems commonly used in Japanese consumer platforms.

## Why Alternatives Were Rejected
- Microservices introduce coordination overhead without clear benefit at this scale.
- Asynchronous pipelines complicate failure semantics and latency guarantees.
- Event-driven designs increase observability and retry complexity, which is out of scope.

## Trade-offs Accepted
- Vertical scaling over horizontal specialization
- Limited independent component evolution
- Single deployment unit

## Revisit Conditions
- Sustained throughput above 500 RPS
- Multiple models requiring independent lifecycle management
- Separate platform and ML ownership teams
