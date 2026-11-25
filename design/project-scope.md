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
- CI gates (lint, tests, image build) that block broken changes

## Explicit Non-Goals
- No multimedia (image/video/audio)
- No online or continuous learning
- No human-in-the-loop moderation
- No policy rule engine
- No multi-region or active-active setup
- No state-of-the-art NLP optimization

## Success Criteria
- Target: p95 latency under 50 ms at concurrency 10. Measured: 42 ms with local uvicorn (met), 58 ms in Docker Compose (not met yet). See the README Performance section.
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
