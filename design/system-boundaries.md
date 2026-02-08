# System Boundaries and Ownership

## Decision
The system will act as a stateless inference service with clearly defined upstream and downstream dependencies, owning only risk scoring and metadata persistence.

## Context
- Ambiguous ownership leads to brittle systems.
- This project simulates a small, focused platform team.
- Failure would involve hidden coupling to external systems or unclear responsibilities during incidents.

## Owned Components
- HTTP inference API
- Input validation and schema enforcement
- Feature extraction
- Model loading and inference
- Risk score computation
- Observability instrumentation
- Metadata persistence

## External Dependencies
- Upstream content submission service (caller)
- Kubernetes runtime
- PostgreSQL database
- Monitoring stack (Prometheus/Grafana)

## Explicitly Not Owned
- Content policy definition
- Enforcement decisions
- User identity management
- Abuse investigation workflows

## Trust Boundaries
- External caller → inference API
- API → database
- API → monitoring systems

## Failure Definition
- Returning incorrect risk scores silently
- Blocking content submission due to internal errors
- Deploying unvalidated models

## Trade-offs Accepted
- Single database instance
- No asynchronous retries

## Revisit Conditions
- Introduction of moderation workflows
- Multi-team ownership
- High availability requirements beyond single-region
