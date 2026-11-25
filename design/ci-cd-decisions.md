# CI/CD Decisions

## Decision
Every push and pull request runs a CI pipeline that fails on any lint error, test failure or broken image build. Deployment is manual. Automated staging deployment and production promotion are planned, not implemented.

## Context
- Content risk systems can cause platform-wide harm if deployed incorrectly.
- ML failures are often silent and difficult to roll back.
- The project simulates a small, risk-averse team.
- Failure would involve unvalidated code or models reaching users.

## Options Considered
1. Fully automated CI/CD with auto-deploy to production
2. CI with automated deploy to staging and manual production promotion
3. CI only, with manual deployment

## Choice & Rationale
**Option 3 is implemented now; option 2 is the target.**

- CI enforces correctness and repeatability on every change.
- Manual deployment (`kubectl apply`) keeps a person in control while there is no staging cluster.
- Option 1 was rejected: without strong automated model validation, auto-deploy is unsafe.

## Pipeline Stages (`.github/workflows/ci.yml`)
1. Install pinned dependencies (`requirements.txt`, `requirements-dev.txt`) with pip caching
2. Lint: `ruff check .`
3. Tests: `pytest` (API, fallback, readiness, metrics, loader, training, UI)
4. Container image build: `docker build`

Any failing step fails the run. There is no `|| true` style fallback.

## Not Yet Implemented
- Model validation gate (fail if a retrained model's F1 is below the current one)
- Security scanning of the image
- Image push to a registry and deployment to staging
- Manual promotion to production

## Failure Visibility
- CI failures are surfaced immediately in pull requests and in the README badge.

## Trade-offs Accepted
- Deployment is manual and depends on the operator
- No automated rollback

## Revisit Conditions
- A staging cluster and image registry are available
- Proven rollback automation
- Strong confidence in automated validation coverage
