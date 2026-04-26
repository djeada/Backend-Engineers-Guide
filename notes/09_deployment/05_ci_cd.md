
## CI/CD Pipelines

Continuous Integration (CI) and Continuous Delivery/Deployment (CD) automate the path from a code commit to running software in production. CI catches integration problems early by building and testing on every commit. CD takes those validated artifacts and delivers them to one or more environments automatically.

```
  Developer
     |
     | git push
     v
  +----------+     +----------+     +----------+     +------------+
  |  Source  | --> |   CI     | --> |  CD      | --> | Production |
  |  Control |     |  Build   |     |  Deploy  |     | Environment|
  |  (Git)   |     |  & Test  |     |  Stage   |     |            |
  +----------+     +----------+     +----------+     +------------+
                       |                |
                  Unit Tests        Integration
                  Lint/Format       Tests
                  Security Scan     Smoke Tests
                  Build Artifact    Approval Gate
```

- **Continuous Integration** – merge frequently, build and test automatically on every push.
- **Continuous Delivery** – every passing build is a release candidate that *can* be deployed with a manual approval.
- **Continuous Deployment** – every passing build is deployed to production automatically with no manual gate.

### Core Concepts

#### Pipeline

A pipeline is a sequence of stages (jobs) that transform source code into a deployed application. Stages run sequentially; jobs within a stage may run in parallel.

#### Artifact

An artifact is the versioned, immutable output of a build stage — a Docker image, a compiled binary, or a JAR file. The same artifact is promoted through staging, QA, and production rather than rebuilt per environment.

#### Environment

An environment is a named deployment target (development, staging, production). Each environment typically has its own configuration and credentials.

#### Secrets Management

Credentials, API keys, and tokens are stored outside the repository in a secrets store (GitHub Actions Secrets, GitLab CI Variables, Vault) and injected into pipeline jobs at runtime.

### GitHub Actions Example

GitHub Actions defines pipelines in YAML files under `.github/workflows/`.

```yaml
# .github/workflows/ci-cd.yml
name: CI / CD

on:
  push:
    branches: [main]
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGE: ghcr.io/${{ github.repository }}

jobs:
  # ── CI stage ──────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint
        run: ruff check .

      - name: Unit tests
        run: pytest --tb=short

  # ── Build & push ──────────────────────────────────────
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE }}
          tags: |
            type=sha,prefix=sha-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ steps.meta.outputs.tags }}

  # ── Deploy to staging ─────────────────────────────────
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ needs.build.outputs.image_tag }} \
            -n staging
        env:
          KUBECONFIG_DATA: ${{ secrets.STAGING_KUBECONFIG }}

  # ── Deploy to production (manual approval) ────────────
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.example.com
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ needs.build.outputs.image_tag }} \
            -n production
        env:
          KUBECONFIG_DATA: ${{ secrets.PROD_KUBECONFIG }}
```

The `environment: production` setting in GitHub Actions triggers a required reviewer approval before the job runs.

### GitLab CI Example

GitLab CI defines the pipeline in `.gitlab-ci.yml` at the repository root.

```yaml
stages:
  - test
  - build
  - deploy

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

test:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt
    - pytest --tb=short

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE .
    - docker push $IMAGE

deploy-staging:
  stage: deploy
  environment: staging
  script:
    - kubectl set image deployment/myapp myapp=$IMAGE -n staging
  only:
    - main

deploy-production:
  stage: deploy
  environment: production
  script:
    - kubectl set image deployment/myapp myapp=$IMAGE -n production
  when: manual
  only:
    - main
```

### Pipeline Best Practices

#### Fail Fast

- **Run quick checks first** (lint, type-check, unit tests) before slow integration tests.
- **Cache dependencies** between runs to avoid re-downloading packages.

```yaml
# GitHub Actions – cache pip packages
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('requirements.txt') }}
```

#### Immutable Artifacts

- **Build once, promote everywhere** – never rebuild the same source for different environments.
- **Tag images with the commit SHA** rather than a mutable tag like `latest`.

#### Branch Strategy

| Branch | Purpose | Deploys to |
|--------|---------|------------|
| `feature/*` | Isolated development | No automatic deploy |
| `main` | Integration branch | Staging (automatic) |
| `release/*` | Release candidates | Production (manual approval) |

#### Security in CI/CD

- **Store secrets** in the CI/CD secrets store, never in the repository.
- **Rotate credentials** regularly and revoke them immediately if a pipeline is compromised.
- **Pin action versions** to a specific commit SHA to prevent supply-chain attacks:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

- **Scan dependencies and images** for CVEs in the pipeline before deploying.
- **Restrict which branches can deploy** to production.

### Testing in the Pipeline

| Stage | Tests |
|-------|-------|
| Pre-commit | Lint, format |
| CI (unit) | Unit tests, type checks |
| CI (integration) | Service integration tests, database migrations |
| Post-deploy (staging) | Smoke tests, contract tests |
| Post-deploy (production) | Synthetic monitoring, canary metrics |

### Notifications and Observability

- **Notify** the team in Slack or email on pipeline failure and recovery.
- **Track** deployment frequency, lead time, change failure rate, and mean time to recovery (MTTR) as DORA metrics.
- **Link** each deployment to the commit that triggered it for fast incident triage.
