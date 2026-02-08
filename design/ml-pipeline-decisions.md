# ML Pipeline Decisions

## Decision
The system will use an offline, batch-trained text classification model with explicit versioning, reproducible training, and manual promotion into production.

## Context
- The system provides synchronous risk scoring with strict latency guarantees.
- Training and inference have fundamentally different failure characteristics.
- Failure would involve training-serving skew, unreproducible models, or unsafe automatic promotion.

## Options Considered
1. Offline batch training with versioned artifacts
2. Online or incremental learning
3. Continuous retraining with automated deployment

## Choice & Rationale
**Option 1 was selected.**

- Offline training allows deterministic, reproducible experiments.
- Clear separation between training and serving reduces operational risk.
- Manual promotion ensures that only validated models reach production.
- This mirrors production ML practices in risk-sensitive systems.

## Why Alternatives Were Rejected
- Online learning complicates debugging and rollback.
- Continuous retraining increases the risk of silent regressions.
- Automated promotion removes human judgment during failure-prone stages.

## Model Characteristics
- Lightweight text model (e.g., linear or shallow neural model)
- Deterministic preprocessing
- Fixed feature schema shared between training and inference

## Data Management
- Training datasets are immutable once created.
- Dataset versions are explicitly recorded.
- Feature extraction logic is shared and versioned.

## Validation Strategy
- Model performance must meet or exceed a fixed baseline.
- Sanity checks on output distributions are required.
- Inference latency is measured as part of validation.

## Trade-offs Accepted
- Slower iteration speed
- Manual intervention in model lifecycle
- Lower peak model accuracy

## Revisit Conditions
- Dedicated ML platform support
- Strong monitoring and alerting maturity
- Regulatory approval for automated model deployment
