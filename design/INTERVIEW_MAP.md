# Interview Map - Real-Time Content Risk Scoring System

## System Design
- Architecture choice: [architecture-decisions.md](architecture-decisions.md)
- Service boundaries: [system-boundaries.md](system-boundaries.md)
- Failure semantics: [risk-and-failure-analysis.md](risk-and-failure-analysis.md)

## ML System Design
- Training vs inference separation: [ml-pipeline-decisions.md](ml-pipeline-decisions.md)
- Model lifecycle and promotion: [ci-cd-decisions.md](ci-cd-decisions.md)
- Why accuracy was not optimized: [project-scope.md](project-scope.md)

## Backend / API Design
- REST vs gRPC decision: [inference-service-decisions.md](inference-service-decisions.md)
- Input validation and contracts: [inference-service-decisions.md](inference-service-decisions.md)

## Kubernetes & Infra
- Deployment vs StatefulSet: [kubernetes-decisions.md](kubernetes-decisions.md)
- Readiness and liveness behavior: [kubernetes-decisions.md](kubernetes-decisions.md)
- Pod replacement and rollout: [kubernetes-decisions.md](kubernetes-decisions.md)

## Reliability & Operations
- Observability strategy: [observability-decisions.md](observability-decisions.md)
- Degraded responses vs hard failures: [risk-and-failure-analysis.md](risk-and-failure-analysis.md)
- Load limits and behavior: [README.md](../README.md)

## What I Would Improve
- Future scalability and team growth: [what-i-would-change.md](what-i-would-change.md)

## Questions to Answer Without Notes
| Question | Short answer | Where it is written |
|---|---|---|
| Why logistic regression and not BERT? | 1.3 MB model, about 5 ms per prediction on CPU, output is already a probability, word weights can be inspected. 5,574 messages is too little data to justify a transformer's size and latency. | README, Design decisions |
| What is your F1, and what does a false positive cost here? | F1 0.86 (precision 1.00, recall 0.75) on 1,115 test messages: 0 false positives, 37 of 149 spam missed. A false positive could block or delay a real user's message, which costs trust; a false negative lets spam through. 3 of 966 normal test messages score `MEDIUM` or higher, none `HIGH`. | README, The model; `models/risk-v1.json` |
| Liveness vs readiness: what does Kubernetes do with each? | A failing liveness probe makes the kubelet restart the container. A failing readiness probe removes the pod from the Service endpoints, so it gets no traffic but keeps running. `/healthz` is liveness, `/readyz` is readiness and depends on the model. | README, Design decisions; [kubernetes-decisions.md](kubernetes-decisions.md) |
| Why return 200 with `degraded=true` instead of 500? | One failed prediction should not force the caller to guess or retry. The keyword score is still a signal, and `degraded`, `model_version` and `fallback_total` make the lower quality visible. A model that never loaded gives 503, not a fake score. | README, Design decisions |
| How would you roll out model v2 safely? | Train `risk-v2`, compare its metrics JSON with v1, bake it into a new image tag, and roll it out. The readiness probe keeps a v2 that fails to load away from traffic. Watch `fallback_total` and the `predictions_total` label mix, and `kubectl rollout undo` if they move. Next step: a canary or shadow run. | [kubernetes-decisions.md](kubernetes-decisions.md), [ml-pipeline-decisions.md](ml-pipeline-decisions.md) |
| Why label metrics by route template? | Raw URLs (IDs, query strings, scanners hitting random paths) would create a new time series per value and can exhaust Prometheus memory. The template keeps the label set small and fixed; unknown paths share `unmatched`. | [observability-decisions.md](observability-decisions.md) |
