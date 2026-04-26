# Credentials Management and Secrets in Production

Applications almost always need some form of secret: database passwords, API keys, TLS private keys, OAuth client secrets, and similar values. How those secrets are created, stored, distributed, rotated, and revoked determines the overall security posture of the system. Hardcoded secrets and loose environment-variable handling are among the most common causes of production data breaches. This document describes the risks, patterns, and tooling for safely managing credentials across the full application lifecycle.

## Why Credentials Management Is Hard

```
+------------------+       +------------------+       +-----------------+
|  Development     |       |  CI/CD Pipeline  |       |  Production     |
|  .env files      | ----> |  Build secrets   | ----> |  Runtime env    |
|  local configs   |       |  test tokens     |       |  DB passwords   |
+------------------+       +------------------+       +-----------------+
                                  |
                                  | Any one of these surfaces
                                  | can leak credentials
```

Common mistakes include:

- Committing `.env` files or config files containing real secrets to version control.
- Logging secrets accidentally (e.g., printing all environment variables during debugging).
- Storing secrets in plaintext in build artefacts, container images, or deployment scripts.
- Sharing a single long-lived credential across many services, so one breach compromises everything.
- Never rotating credentials, so a leaked token remains valid indefinitely.

## What Not To Do

### Hardcoding Secrets in Source Code

```python
# Never do this
DB_PASSWORD = "s3cur3P@ssw0rd!"
API_KEY = "sk-prod-abc123xyz"
```

Once a secret is committed to version control it should be treated as compromised—git history is permanent and is often shared widely.

### Storing Secrets in Docker Images

```dockerfile
# Never do this
ENV DATABASE_URL="postgres://user:password@db:5432/prod"
```

Any party that can pull the image can read the environment variable from the image manifest or with `docker inspect`.

### Unprotected Environment Variables

Plain environment variables are a step up from hardcoded values but are still visible to any process running on the same host (`/proc/<pid>/environ`), to log aggregators that capture startup output, and to container introspection tools.

## Secrets Management Patterns

### Secrets at Build Time vs. Runtime

Prefer injecting secrets at **runtime** rather than at build time. Build-time secrets become part of the image and its cache layers. Runtime injection means the container starts clean and receives its secrets only when it is actually scheduled to run.

```
Build time (avoid for secrets)       Runtime (preferred)
+------------------+                 +------------------+
| docker build     |                 | Secret Store     |
| --build-arg      |                 |  (Vault, SSM,    |
|   SECRET=...     |                 |   K8s Secrets)   |
+------------------+                 +--------+---------+
                                              |
                                              | injected at pod/container start
                                              v
                                     +------------------+
                                     |   Running App    |
                                     +------------------+
```

### The Twelve-Factor App Approach

The [Twelve-Factor App](https://12factor.net/config) methodology recommends storing configuration—including secrets—in the environment, separate from code. This is a useful baseline but environment variables alone are not sufficient for sensitive production secrets; use a dedicated secrets manager to populate them.

## Dedicated Secrets Managers

A secrets manager is a centralised service that stores, audits, rotates, and controls access to secrets. Applications retrieve secrets at startup (or on demand) through an authenticated API call.

### HashiCorp Vault

Vault is a widely-used open-source secrets manager. It supports dynamic secrets (short-lived credentials generated on the fly), fine-grained policies, and audit logging.

```
+----------+   AppRole / K8s Auth   +-----------+
|  App Pod |  --------------------> |   Vault   |
|          |  <------------------- |  (secret  |
|          |   short-lived token   |   engine)  |
+----------+                        +-----------+
```

**Workflow example:**

1. Application authenticates to Vault using a Kubernetes service account JWT.
2. Vault verifies the JWT against the Kubernetes API server.
3. Vault issues a short-lived token scoped to specific secret paths.
4. Application reads the secret and discards the token after use.

```bash
# Read a secret from Vault using the CLI
vault kv get -field=password secret/production/database

# Read a secret programmatically (Python)
import hvac
client = hvac.Client(url="https://vault.internal:8200", token=os.environ["VAULT_TOKEN"])
secret = client.secrets.kv.v2.read_secret_version(path="production/database")
db_password = secret["data"]["data"]["password"]
```

### AWS Secrets Manager and Parameter Store

AWS Secrets Manager stores secrets as JSON blobs and supports automatic rotation of RDS passwords, API keys, and custom secrets via Lambda.

```python
import boto3
import json

client = boto3.client("secretsmanager", region_name="us-east-1")
response = client.get_secret_value(SecretId="prod/myapp/database")
creds = json.loads(response["SecretString"])
db_password = creds["password"]
```

AWS Systems Manager (SSM) Parameter Store is a lighter-weight alternative, suitable for non-secret configuration values and lower-sensitivity secrets. Use SecureString parameters backed by KMS for anything sensitive.

### GCP Secret Manager

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = "projects/my-project/secrets/db-password/versions/latest"
response = client.access_secret_version(request={"name": name})
db_password = response.payload.data.decode("utf-8")
```

### Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)
db_password = client.get_secret("db-password").value
```

## Kubernetes Secrets

Kubernetes provides a built-in `Secret` resource. By default, secrets are base64-encoded (not encrypted) in etcd—additional steps are required to secure them properly.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: production
type: Opaque
stringData:
  username: appuser
  password: "<supplied-by-automation-never-by-hand>"
```

Mount secrets as files rather than environment variables to reduce exposure:

```yaml
spec:
  containers:
    - name: api
      image: myapp:1.2.3
      volumeMounts:
        - name: db-creds
          mountPath: "/run/secrets/db"
          readOnly: true
  volumes:
    - name: db-creds
      secret:
        secretName: db-credentials
```

Application code reads the secret from the file:

```python
with open("/run/secrets/db/password") as f:
    db_password = f.read().strip()
```

### Encrypt etcd at Rest

Enable encryption of Kubernetes secrets at rest so that even direct access to etcd storage does not reveal plaintext values:

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

### Use an External Secrets Operator

Tools such as External Secrets Operator (ESO) or Secrets Store CSI Driver bridge Kubernetes with external secrets managers (Vault, AWS Secrets Manager, GCP Secret Manager), so the canonical copy of the secret lives in the dedicated store rather than in etcd.

```
+------------------+         +-------------------+         +------------+
| External Secrets |  sync   |  K8s Secret       |  mount  | App Pod    |
| Operator         | ------> | (auto-populated)  | ------> |            |
+------------------+         +-------------------+         +------------+
         |
         | reads
         v
+------------------+
| HashiCorp Vault  |
| AWS Secrets Mgr  |
| GCP Secret Mgr   |
+------------------+
```

## Credential Rotation

Long-lived credentials are high-value targets. Rotating them regularly limits the window of exposure if a secret is leaked.

### Automatic Rotation

Many secrets managers support automatic rotation. For example, AWS Secrets Manager can trigger a Lambda function that:

1. Creates new database credentials.
2. Updates the secret in Secrets Manager.
3. Tests the new credentials.
4. Invalidates the old credentials.

Applications that retrieve secrets on each connection (or cache them with a short TTL) pick up the new credentials transparently.

### Dynamic Secrets

Vault's dynamic secret engines generate short-lived, per-application credentials on demand. The database secret engine creates a unique PostgreSQL user with a configurable TTL for each request:

```
App requests DB creds
       |
       v
+------+-------+     CREATE ROLE app_abc123     +-----------+
|     Vault    | -----------------------------> | PostgreSQL|
|              | <----------------------------- |           |
| issues lease |     credentials returned        +-----------+
+--------------+
       |
       | returns username + password (TTL: 1 hour)
       v
   Application connects, uses creds, lease expires, creds deleted
```

This eliminates the need to rotate secrets manually—they expire automatically.

## CI/CD Pipeline Secrets

### Use Native CI Secret Storage

CI/CD platforms provide encrypted secret storage that injects values as environment variables at runtime. Never print these in logs.

```yaml
# GitHub Actions example
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          API_KEY: ${{ secrets.API_KEY }}
        run: ./scripts/deploy.sh
```

### Prevent Secrets from Leaking in Logs

Configure your CI runner to mask secrets in log output. Avoid `set -x` in shell scripts that handle secrets.

```bash
# Safe: read into a variable, do not echo
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id prod/db --query SecretString --output text | jq -r .password)
```

### Short-Lived OIDC Tokens for Cloud Access

Instead of storing long-lived cloud credentials in CI, use OpenID Connect (OIDC) federation. The CI provider mints a short-lived JWT, which the cloud provider exchanges for temporary credentials.

```
GitHub Actions runner
        |
        | OIDC JWT (signed by GitHub)
        v
  AWS / GCP / Azure
  (validates JWT, issues temporary credentials scoped to job)
        |
        v
  Temporary role credentials (TTL: 15 minutes)
```

```yaml
# GitHub Actions – AWS OIDC (no static credentials stored)
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-deploy
      aws-region: us-east-1
```

## Preventing Accidental Leaks

### Pre-commit Hooks

Use tools like `detect-secrets` or `gitleaks` as pre-commit hooks to block commits that contain suspicious patterns.

```bash
# Install gitleaks
brew install gitleaks

# Scan the repository
gitleaks detect --source . --verbose

# Use as a pre-commit hook (via .pre-commit-config.yaml)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks
```

### Rotating Leaked Secrets Immediately

If a secret is committed accidentally:

1. **Revoke** the secret immediately at the issuing service.
2. **Remove** it from git history using `git filter-repo` or BFG Repo-Cleaner (be aware that forks and clones may already have copies).
3. **Notify** affected parties if the secret granted access to data.
4. **Post-mortem** to understand how it happened and prevent recurrence.

## Access Control for Secrets

Apply the principle of least privilege to secret access:

- Services should only be able to read the secrets they actually need.
- Separate secrets by environment (development / staging / production).
- Audit all access: who read which secret, when.

```
+------------------+        allowed paths         +----------+
|  frontend-svc    | ---------------------------> | Vault    |
|  (read only)     |   secret/frontend/*           | policies |
+------------------+                              +----------+
                                                       |
+------------------+        allowed paths             |
|  payment-svc     | ---------------------------> |  (RBAC)  |
|  (read only)     |   secret/payment/*            +----------+
+------------------+
```

## Summary

| Concern | Recommended Approach |
|---------|---------------------|
| Storage | Dedicated secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager) |
| Kubernetes | External Secrets Operator + encrypted etcd; secrets mounted as files |
| Rotation | Automatic rotation or dynamic short-lived credentials |
| CI/CD | Native CI secret storage; OIDC federation for cloud access |
| Leak prevention | Pre-commit hooks (gitleaks, detect-secrets), no secrets in image layers |
| Access control | Least-privilege policies, per-environment separation, audit logging |
