# Risk and Failure Analysis

## Decision
The system fails safely and visibly: it prefers a clearly marked degraded response over a hard failure for one bad request, and refuses to score at all when it has no model.

## Context
- Content risk systems influence downstream enforcement decisions.
- Silent failures are more dangerous than explicit errors.
- The system must behave predictably under partial outages.

## Identified Risks

### Model Loading Failure
- Cause: Corrupt or missing model artifact (simulate with `FAIL_MODEL_LOAD=true`)
- Impact: Inference unavailable on that instance
- Mitigation: Process stays up; `/readyz` and `/score` return 503 with the reason, so Kubernetes routes no traffic to it. `model_loaded` gauge is 0. No fallback scoring is attempted.

### Prediction Error
- Cause: An exception inside the loaded model for a specific request
- Impact: One request cannot be scored by the model
- Mitigation: Whole-word keyword rules score the text; response has `degraded: true` and `model_version: "keyword-fallback-1.0"`; `fallback_total` rises. If the rules fail too, `UNKNOWN` with score 0.5.

### Latency Degradation
- Cause: CPU contention under concurrent load (one worker)
- Impact: User-visible delay; at concurrency 10 on a laptop, p99 was about 60 ms with local uvicorn and 70 to 440 ms across four runs in Docker
- Mitigation: Measured with `scripts/loadtest.py` and visible in `http_request_latency_seconds`. There is no request timeout yet.

### Bad Model Deployment
- Cause: Inadequate validation or human error
- Impact: Systemic misclassification
- Mitigation: Versioned artifacts with metrics in `models/risk-v1.json`, manual review before committing a model, CI tests on loading and prediction. There is no automatic metric gate yet.

### Data Drift
- Cause: Upstream content distribution changes
- Impact: Gradual accuracy decay
- Mitigation (partial): `predictions_total{label}` shows shifts in the label mix over time. No alert rules exist yet.

## Failure Principles
- No silent correctness failures: a fallback score is always marked `degraded`
- Degrade functionality before availability
- Prefer explicit errors (503) over scoring without a model

## Trade-offs Accepted
- Reduced availability during model load failure
- Keyword fallback is much less accurate than the model
- Conservative rollback behavior

## Revisit Conditions
- Regulatory or legal enforcement coupling
- Introduction of automated moderation actions
- On-call rotation with multiple responders
