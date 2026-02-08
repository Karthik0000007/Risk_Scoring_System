# Project Scope: Real-Time Content Risk Scoring System

## Decision
The system will provide synchronous, probabilistic risk scoring for text content at submission time and will not perform enforcement, moderation workflows, or human review.

## Context
- Modern platforms require fast, explainable risk signals before content is persisted or published.
- Failure would mean building a demo that optimizes accuracy instead of reliability, or a system with unclear ownership boundaries.

## In Scope
- Text-only content risk scoring
- Synchronous API-based inference
- Offline, reproducible model training
- Containerized deployment on Kubernetes
- Observability (logs, metrics)
- CI/CD gates preventing unsafe deployment

## Explicit Non-Goals
- No multimedia (image/video/audio)
- No online or continuous learning
- No human-in-the-loop moderation
- No policy rule engine
- No multi-region or active-active setup
- No state-of-the-art NLP optimization

## Success Criteria
- p95 inference latency < 50ms
- Safe failure behavior under partial outages
- Reproducible model training
- Clear deployment rollback path
- Design clarity suitable for senior engineering review

## Trade-offs Accepted
- Lower model accuracy in exchange for predictability
- Single-region deployment
- Manual model promotion

## Revisit Conditions
- Sustained traffic > 500 RPS
- Regulatory or policy enforcement requirements
- Dedicated Trust & Safety team involvement
