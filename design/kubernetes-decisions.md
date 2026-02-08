# Kubernetes Deployment Decisions

## Decision
The system will be deployed as a stateless Kubernetes Deployment with explicit resource limits, health probes, and conservative rollout policies, prioritizing predictable behavior and safe rollback.

## Context
- The inference service is synchronous and latency-sensitive.
- The system must be easy to restart, scale, and roll back.
- The project simulates a small team operating a production service.
- Failure would involve traffic routed to unhealthy pods or unsafe rollouts.

## Options Considered
1. Kubernetes Deployment with rolling updates
2. StatefulSet-based deployment
3. Bare container or VM-based deployment

## Choice & Rationale
**Option 1 was selected.**

- Stateless Deployments are easy to scale horizontally.
- Rolling updates provide controlled rollout and rollback.
- No persistent state is stored in pods.
- This aligns with standard production practices in consumer platforms.

## Namespace Strategy
- Separate namespaces for staging and production.
- Minimal shared resources across namespaces.
- Clear isolation for rollback and testing.

## Resource Management
- CPU and memory requests are explicitly defined.
- Hard limits prevent noisy-neighbor issues.
- Resource sizing favors stability over density.

## Health Probes
- Liveness probe ensures dead pods are restarted.
- Readiness probe blocks traffic until model loading succeeds.
- Startup probe is avoided to reduce configuration complexity.

## Configuration Management
- ConfigMaps are used for non-sensitive configuration.
- Secrets are used for credentials and API keys.
- No configuration is baked into container images.

## Rollout Strategy
- Rolling updates with limited surge and unavailable pods.
- Automatic rollback on failed readiness checks.
- No canary or blue-green deployment in initial version.

## Trade-offs Accepted
- Slower deployments
- Limited rollout flexibility
- No advanced traffic splitting

## Revisit Conditions
- Multi-region deployment
- Multiple concurrent model versions
- Dedicated SRE ownership
