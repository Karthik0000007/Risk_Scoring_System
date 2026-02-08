# CI/CD Decisions

## Decision
The system will use a gated CI/CD pipeline that blocks deployment unless code, configuration, and model artifacts pass explicit validation checks, with manual promotion required for production.

## Context
- Content risk systems can cause platform-wide harm if deployed incorrectly.
- ML failures are often silent and difficult to roll back.
- The project simulates a small, risk-averse production team.
- Failure would involve unvalidated models or broken services reaching production.

## Options Considered
1. Fully automated CI/CD with auto-deploy to production
2. CI with automated deploy to staging and manual production promotion
3. Manual deployment without CI enforcement

## Choice & Rationale
**Option 2 was selected.**

- CI enforces correctness and repeatability.
- Staging deployment validates runtime behavior.
- Manual promotion provides a final human safety check.
- This reflects conservative deployment practices common in Japanese consumer platforms.

## Pipeline Stages
1. Code linting and static analysis
2. Unit and integration tests
3. Model validation checks
4. Container image build
5. Security scanning
6. Deployment to staging
7. Manual promotion to production

## Deployment Gates
- Test failures block all deployments.
- Model metrics below baseline block promotion.
- Schema or configuration mismatches block deployment.
- Failed staging health checks block promotion.

## Failure Visibility
- CI failures are surfaced immediately in pull requests.
- Deployment failures are visible via pipeline status.
- No silent fallback to previous versions without notification.

## Trade-offs Accepted
- Slower deployment velocity
- Increased manual steps
- Higher operational overhead for small changes

## Revisit Conditions
- Dedicated on-call rotation established
- Proven rollback automation
- Strong confidence in automated validation coverage
