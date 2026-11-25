# System Boundaries and Ownership

## Decision
The system acts as a stateless inference service with clearly defined upstream and downstream dependencies, owning only risk scoring.

## Context
- Ambiguous ownership leads to brittle systems.
- This project simulates a small, focused platform team.
- Failure would involve hidden coupling to external systems or unclear responsibilities during incidents.

## Owned Components
- HTTP inference API and the one-page UI
- Input validation and schema enforcement
- Model loading and inference (feature extraction is inside the model pipeline)
- Keyword fallback scoring
- Risk score computation
- Observability instrumentation (JSON logs, Prometheus metrics)
- Offline training script

## External Dependencies
- Upstream content submission service (caller)
- Kubernetes runtime (or Docker Compose locally)
- Prometheus (included in Docker Compose; not in the Kubernetes manifests)

## Explicitly Not Owned
- Content policy definition
- Enforcement decisions
- Storing scores or content (no database)
- User identity management
- Abuse investigation workflows

## Trust Boundaries
- External caller to inference API
- Prometheus scraping `/metrics`

## Failure Definition
- Returning incorrect risk scores silently
- Blocking content submission due to internal errors
- Deploying unvalidated models

## Trade-offs Accepted
- No persistence of scores
- No asynchronous retries
- No authentication on the API (expected to run on an internal network)

## Revisit Conditions
- Introduction of moderation workflows
- Multi-team ownership
- High availability requirements beyond single-region
