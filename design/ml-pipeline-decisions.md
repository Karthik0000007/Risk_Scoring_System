# ML Pipeline Decisions

## Decision
The system uses an offline, batch-trained text classification model with explicit versioning, reproducible training, and manual promotion (committing a new artifact).

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
- Clear separation between training (`training/train.py`) and serving (`app/`) reduces operational risk.
- Manual promotion ensures that a person reviews the metrics before a model is committed.

## Why Alternatives Were Rejected
- Online learning complicates debugging and rollback.
- Continuous retraining increases the risk of silent regressions.
- Automated promotion removes human judgment during failure-prone stages.

## Model Characteristics
- scikit-learn `Pipeline`: `TfidfVectorizer` (word 1 and 2 grams) then `LogisticRegression`.
- The vectorizer is saved inside the same joblib file as the classifier, so training and serving always use identical preprocessing (no training-serving skew).
- Output is the spam-class probability, used directly as `risk_score`.

## Data Management
- Dataset: SMS Spam Collection (UCI), 5,574 messages, kept in `data/` and not committed.
- Stratified 80/20 split with a fixed seed (42) makes training reproducible.
- `models/risk-v1.json` records version, training date, dataset name, row count, scikit-learn version and test metrics.

## Validation Strategy
- Current: `train.py` prints precision, recall and F1 for the spam class on the held-out 20%, and writes them to the metadata file. `risk-v1`: precision 1.00, recall 0.75, F1 0.86.
- Current: inference latency is measured separately with `scripts/loadtest.py`.
- Not yet automated: there is no baseline check that blocks a worse model. A person compares metrics before committing.

## Trade-offs Accepted
- Slower iteration speed
- Manual intervention in model lifecycle
- Lower peak model accuracy
- The model only knows SMS-style spam; link-based phishing and threats score low

## Revisit Conditions
- Dedicated ML platform support
- Strong monitoring and alerting maturity
- Regulatory approval for automated model deployment
