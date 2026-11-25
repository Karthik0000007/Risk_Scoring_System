# Kubernetes Deployment Decisions

## Decision
The system is deployed as a stateless Kubernetes Deployment with explicit resource limits and health probes, prioritizing predictable behavior and safe rollback.

## Context
- The inference service is synchronous and latency-sensitive.
- The system must be easy to restart, scale, and roll back.
- The project simulates a small team operating a service.
- Failure would involve traffic routed to unhealthy pods or unsafe rollouts.

## Options Considered
1. Kubernetes Deployment with rolling updates
2. StatefulSet-based deployment
3. Bare container or VM-based deployment

## Choice & Rationale
**Option 1 was selected.**

- Stateless Deployments are easy to scale horizontally.
- Rolling updates provide controlled rollout, and `kubectl rollout undo` gives a rollback path.
- No persistent state is stored in pods.

## Namespace Strategy
- The manifests define one namespace, `content-risk-staging`.
- A separate production namespace is planned but not defined.

## Resource Management
- Requests: 200m CPU, 512Mi memory. Limits: 500m CPU, 1Gi memory.
- Hard limits prevent noisy-neighbor issues.
- One replica; there is no autoscaler yet.

## Health Probes
- Liveness (`/healthz`) always returns 200 while the process runs, so a bad model file does not cause a restart loop.
- Readiness (`/readyz`) returns 503 until the model has loaded, so the Service sends no traffic to the pod. The response includes the load error.
- Startup probe is avoided to reduce configuration complexity.

## Configuration Management
- The only setting is `MODEL_PATH`, set as a plain env var in `deployment.yaml` (and as a default in the Dockerfile).
- The model artifact is baked into the image, so an image tag fully identifies the code and model.
- No ConfigMaps or Secrets are used; the service has no credentials.

## Rollout Strategy
- The Deployment uses the default `RollingUpdate` strategy.
- A new pod only receives traffic once its readiness probe passes, so a version whose model fails to load never takes traffic. The rollout stalls rather than rolling back automatically; rollback is `kubectl rollout undo`.
- No canary or blue-green deployment.

## Trade-offs Accepted
- Slower deployments
- Limited rollout flexibility
- No advanced traffic splitting
- Model updates require a new image

## Revisit Conditions
- Multi-region deployment
- Multiple concurrent model versions
- Dedicated SRE ownership
