# Real-Time Content Risk Scoring System

## Overview
This is a production-grade, synchronous text risk scoring service.
It exposes a REST API that assigns probabilistic risk scores under strict latency constraints.

The key design goal was reliability over model sophistication. Training is offline and versioned, inference is stateless, and deployment is gated through CI/CD.

Failures are handled explicitly: model load failures block traffic via readiness probes, runtime errors degrade responses instead of crashing, and all behavior is observable via logs and metrics.

The system is containerized, deployed on Kubernetes, and intentionally scoped for a small team operating a risk-sensitive service.

## Non-Goals
- State-of-the-art NLP accuracy
- Multimedia content
- Automated moderation actions
- Online learning

## Architecture Summary
- Stateless FastAPI inference service
- Offline, versioned model training
- Containerized deployment on Kubernetes
- Explicit readiness and health probes
- Structured logging and Prometheus metrics

## Failure Behavior
- Model load failure blocks traffic via readiness probes
- Runtime inference errors return degraded responses
- Process crashes trigger Kubernetes pod replacement
- All failures are visible via logs and metrics

## Load Characteristics
- Designed for moderate synchronous traffic (~10 concurrent requests per pod)
- Predictable latency degradation under load
- No autoscaling configured intentionally

## Repository Structure
- `app/` – inference service
- `k8s/` – Kubernetes manifests
- `design/` – decision-focused design documentation

## How This Would Scale
- Horizontal scaling via replicas
- Separate training pipeline
- Canary deployments for models
- Dedicated monitoring and alerting
