# Real-Time Content Risk Scoring System

## Overview
Production-grade, synchronous text risk scoring service designed to demonstrate
reliable ML system deployment under realistic constraints.

The system prioritizes correctness, observability, and safe failure behavior
over model sophistication.

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
