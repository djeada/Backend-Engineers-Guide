# Credentials Management and Secrets in Production

Applications almost always need some form of secret. These secrets may include database passwords, API keys, TLS private keys, OAuth client secrets, webhook signing keys, encryption keys, and credentials for third-party services.

How these secrets are created, stored, distributed, rotated, and revoked has a major impact on the security of the whole system. A strong application can still be compromised if its database password is leaked, its API key is committed to Git, or its cloud credentials are exposed in CI logs.

Secrets should never be treated like ordinary configuration values. They need controlled access, secure storage, audit trails, rotation plans, and clear ownership. Hardcoded secrets and poorly managed environment variables are among the most common causes of production security incidents.

---

## Why Credentials Management Is Hard

Credentials management is difficult because secrets pass through many parts of the software lifecycle. A secret might be used during local development, injected into a CI/CD pipeline, deployed into a container, mounted into a Kubernetes pod, read by an application, and rotated later in production.

Each stage creates a possible leak point. A secret may be accidentally committed to source control, printed in logs, included in a Docker image layer, copied into a build artifact, exposed through debugging output, or shared too broadly between services.

```text
+------------------+       +------------------+       +-----------------+
|  Development     |       |  CI/CD Pipeline  |       |  Production     |
|  .env files      | ----> |  Build secrets   | ----> |  Runtime env    |
|  local configs   |       |  test tokens     |       |  DB passwords   |
+------------------+       +------------------+       +-----------------+
                                  |
                                  | Any one of these surfaces
                                  | can leak credentials
```

Example leak scenario:

```text
Developer adds .env file locally
.env contains production database password
.env is accidentally committed to Git
CI pipeline pushes repository to remote hosting
Secret is now visible in repository history
```

Example incident output:

```json
{
  "secretType": "database_password",
  "location": "git_history",
  "status": "compromised",
  "requiredAction": "rotate immediately"
}
```

Common mistakes include:

* Committing `.env` files or config files containing real secrets to version control.
* Logging secrets accidentally, such as printing all environment variables during debugging.
* Storing secrets in plaintext in build artifacts, container images, or deployment scripts.
* Sharing a single long-lived credential across many services.
* Never rotating credentials, allowing a leaked token to remain valid indefinitely.

The goal of secrets management is to reduce both the chance of leakage and the damage caused if a secret is exposed.

---

## What Not To Do

Some patterns are especially risky and should be avoided in production systems. These patterns may seem convenient during development, but they create long-term security problems.

---

### Hardcoding Secrets in Source Code

Hardcoding secrets means placing credentials directly in the application code. This is dangerous because source code is usually copied, reviewed, tested, built, deployed, and stored in version control systems.

```python
# Never do this
DB_PASSWORD = "s3cur3P@ssw0rd!"
API_KEY = "sk-prod-abc123xyz"
```

Example risk output:

```json
{
  "problem": "hardcoded_secret",
  "risk": "anyone with repository access can read the secret",
  "recommendedAction": "remove from code and rotate the credential"
}
```

Once a secret is committed to version control, it should be treated as compromised. Even if the line is deleted later, the secret may still exist in Git history, forks, logs, caches, backups, or local clones.

A safer pattern is to load secrets from a managed secret source at runtime:

```python
import os

db_password = os.environ["DB_PASSWORD"]
```

This is better than hardcoding, but environment variables still need to be populated securely by a secrets manager or deployment platform.

---

### Storing Secrets in Docker Images

Secrets should not be baked into Docker images. Docker images are often stored in registries, shared between environments, inspected by operators, and cached in build layers.

```dockerfile
# Never do this
ENV DATABASE_URL="postgres://user:password@db:5432/prod"
```

Example risk output:

```json
{
  "problem": "secret_in_container_image",
  "risk": "anyone who can pull or inspect the image may read the secret",
  "recommendedAction": "inject secret at runtime instead"
}
```

The secret may be visible through image metadata, build history, registry layers, or commands such as `docker inspect`.

A safer pattern is to keep the image generic and inject secrets only when the container starts:

```dockerfile
# Better: image contains application code, not production secrets
ENV NODE_ENV=production
CMD ["node", "server.js"]
```

Then the runtime platform supplies the secret securely.

---

### Unprotected Environment Variables

Environment variables are common and useful, but they are not a complete secrets management solution by themselves. They can be exposed through process inspection, crash dumps, logs, debugging tools, startup output, or container introspection.

Example risky debugging command:

```bash
env
```

Example unsafe output:

```text
DB_PASSWORD=prod-password-123
API_KEY=sk-prod-abc123xyz
```

Example risk output:

```json
{
  "problem": "secret_exposed_in_environment_output",
  "risk": "logs or debugging output may capture credentials",
  "recommendedAction": "avoid printing environment variables and use secret masking"
}
```

Environment variables may still be acceptable as a delivery mechanism if they are populated from a dedicated secrets manager and protected from logging. For highly sensitive secrets, mounting secrets as files or fetching them directly from a secrets manager may reduce exposure.

---

## Secrets Management Patterns

Secrets management patterns define when secrets are introduced, where they are stored, how applications receive them, and how access is controlled. The safest pattern is usually to keep secrets out of source code and build artifacts, then inject or retrieve them at runtime.

---

### Secrets at Build Time vs. Runtime

Secrets should usually be injected at **runtime** rather than **build time**. Build-time secrets are risky because they may become part of image layers, build cache, compiled artifacts, or deployment packages.

Runtime injection means the application image can be built without sensitive production values. The container receives secrets only when it is scheduled to run in a specific environment.

```text
Build time (avoid for secrets)       Runtime (preferred)
+------------------+                 +------------------+
| docker build     |                 | Secret Store     |
| --build-arg      |                 |  Vault, SSM,     |
|   SECRET=...     |                 |  K8s Secrets     |
+------------------+                 +--------+---------+
                                              |
                                              | injected at pod/container start
                                              v
                                     +------------------+
                                     |   Running App    |
                                     +------------------+
```

Example build-time risk:

```bash
docker build --build-arg DB_PASSWORD=prod-password .
```

Example risk output:

```json
{
  "stage": "build",
  "risk": "secret may remain in image layers or build cache",
  "preferredStage": "runtime"
}
```

Example runtime pattern:

```bash
docker run --env DB_PASSWORD_FILE=/run/secrets/db_password myapp:1.2.3
```

Example output:

```json
{
  "stage": "runtime",
  "secretSource": "/run/secrets/db_password",
  "status": "secret provided only to running container"
}
```

Runtime injection limits where the secret appears and makes it easier to rotate secrets without rebuilding the application image.

---

### The Twelve-Factor App Approach

The Twelve-Factor App methodology recommends storing configuration separately from code. This includes values such as database URLs, service endpoints, feature flags, and credentials.

This approach is a useful baseline because it prevents applications from hardcoding environment-specific values. The same application code can run in development, staging, and production with different configuration values.

Example environment-based configuration:

```bash
DATABASE_HOST=db.internal
DATABASE_NAME=myapp
DATABASE_USER=myapp_user
DATABASE_PASSWORD=from_secret_manager
```

Example output:

```json
{
  "configuration": "separated_from_code",
  "environment": "production",
  "status": "application can be deployed without code changes"
}
```

However, environment variables alone are not enough for sensitive production secrets. A dedicated secrets manager should store the canonical secret and securely populate the runtime environment, file mount, or application secret cache.

---

## Dedicated Secrets Managers

A secrets manager is a centralized service for storing, retrieving, auditing, rotating, and controlling access to secrets. Instead of scattering secrets across code, scripts, servers, and build systems, teams store them in one controlled system.

Applications authenticate to the secrets manager using an identity, such as a cloud role, Kubernetes service account, workload identity, or machine identity. The secrets manager then decides which secrets the application can access.

Example generic flow:

```text
Application starts
Application authenticates to secrets manager
Secrets manager checks policy
Application receives only the secrets it is allowed to read
Application connects to database or external service
```

Example output:

```json
{
  "service": "orders-api",
  "secretPath": "production/orders/database",
  "access": "allowed",
  "auditLogged": true
}
```

Secrets managers improve security because they provide central policy enforcement, access logs, rotation workflows, and integration with cloud or platform identities.

---

### HashiCorp Vault

HashiCorp Vault is a widely used secrets manager. It supports static secrets, dynamic secrets, encryption as a service, fine-grained policies, authentication methods, leases, and audit logs.

Vault is especially powerful because it can issue short-lived credentials dynamically. For example, instead of storing one permanent database password, Vault can create temporary database credentials for each application instance.

```text
+----------+   AppRole / K8s Auth   +-----------+
|  App Pod |  --------------------> |   Vault   |
|          |  <-------------------  |  secret   |
|          |   short-lived token    |  engine   |
+----------+                        +-----------+
```

Workflow example:

1. The application authenticates to Vault using a Kubernetes service account JWT.
2. Vault verifies the JWT against the Kubernetes API server.
3. Vault issues a short-lived token scoped to specific secret paths.
4. The application reads the secret.
5. Vault records the access in an audit log.

Example CLI command:

```bash
vault kv get -field=password secret/production/database
```

Example CLI output:

```text
prod-db-password-value
```

Example Python access:

```python
import os
import hvac

client = hvac.Client(
    url="https://vault.internal:8200",
    token=os.environ["VAULT_TOKEN"]
)

secret = client.secrets.kv.v2.read_secret_version(
    path="production/database"
)

db_password = secret["data"]["data"]["password"]
```

Example application output:

```json
{
  "secretPath": "production/database",
  "readStatus": "success",
  "passwordLoaded": true
}
```

The application should avoid printing the actual secret. Logs should show that the secret was loaded, not reveal its value.

---

### AWS Secrets Manager and Parameter Store

AWS Secrets Manager stores secrets as encrypted values and can represent them as JSON objects. It supports integration with AWS IAM, AWS KMS, CloudTrail audit logs, and automatic rotation for some services.

It is commonly used for database credentials, API keys, OAuth secrets, and application credentials.

```python
import boto3
import json

client = boto3.client("secretsmanager", region_name="us-east-1")

response = client.get_secret_value(
    SecretId="prod/myapp/database"
)

creds = json.loads(response["SecretString"])
db_password = creds["password"]
```

Example secret value shape:

```json
{
  "username": "appuser",
  "password": "prod-db-password",
  "host": "db.example.internal",
  "port": 5432
}
```

Example safe application output:

```json
{
  "secretId": "prod/myapp/database",
  "loadedFields": ["username", "password", "host", "port"],
  "status": "success"
}
```

AWS Systems Manager Parameter Store is a lighter-weight option. It can store configuration values and sensitive values as `SecureString` parameters backed by AWS KMS.

Example Parameter Store output:

```json
{
  "parameter": "/prod/myapp/api-base-url",
  "type": "String",
  "useCase": "non-secret configuration"
}
```

For sensitive values, use encrypted parameters and strict IAM permissions.

---

### GCP Secret Manager

GCP Secret Manager stores versioned secrets and controls access through IAM. Applications can access secrets using service accounts and Google Cloud client libraries.

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

name = "projects/my-project/secrets/db-password/versions/latest"

response = client.access_secret_version(
    request={"name": name}
)

db_password = response.payload.data.decode("utf-8")
```

Example safe output:

```json
{
  "secret": "db-password",
  "version": "latest",
  "accessStatus": "success"
}
```

Secret versioning is useful during rotation. The application can move from an older version to a newer one while maintaining a rollback option.

---

### Azure Key Vault

Azure Key Vault stores secrets, keys, and certificates. It integrates with Azure Active Directory and managed identities, allowing applications to authenticate without storing static credentials.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

client = SecretClient(
    vault_url="https://myvault.vault.azure.net",
    credential=credential
)

db_password = client.get_secret("db-password").value
```

Example safe output:

```json
{
  "vault": "myvault",
  "secret": "db-password",
  "accessStatus": "success"
}
```

Managed identities reduce the need for long-lived credentials because the cloud platform provides the application identity.

---

## Kubernetes Secrets

Kubernetes provides a built-in `Secret` resource. A Kubernetes Secret can hold passwords, tokens, certificates, and other sensitive values for workloads running in the cluster.

By default, Kubernetes Secret values are base64-encoded, not automatically encrypted in a strong security sense. Base64 is only an encoding format. Anyone with permission to read the Secret can decode it.

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

Example decoded secret risk:

```text
base64 value can be decoded back into plaintext
```

Example risk output:

```json
{
  "resource": "Kubernetes Secret",
  "defaultProtection": "base64 encoding",
  "additionalProtectionNeeded": "etcd encryption and RBAC restrictions"
}
```

Kubernetes Secrets are useful, but they should be protected with RBAC, namespace boundaries, encryption at rest, and careful access policies.

---

### Mount Secrets as Files

Mounting secrets as files can reduce exposure compared with passing them as environment variables. Environment variables can be captured in process listings, crash reports, or logs. File mounts can be scoped to specific paths and read only by the application process.

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

Application code reads the secret from the mounted file:

```python
with open("/run/secrets/db/password") as f:
    db_password = f.read().strip()
```

Example safe application output:

```json
{
  "secretLocation": "/run/secrets/db/password",
  "readStatus": "success",
  "secretPrinted": false
}
```

The application should read the file value but avoid logging it.

---

### Encrypt etcd at Rest

Kubernetes stores cluster state in etcd. If Secrets are not encrypted at rest, someone with access to etcd storage may be able to read them.

Encryption at rest protects Kubernetes Secret values inside etcd.

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

Example output after enabling encryption:

```json
{
  "resource": "secrets",
  "etcdEncryption": "enabled",
  "provider": "aescbc"
}
```

This protects against direct access to etcd storage, but it does not replace Kubernetes RBAC. Users and service accounts with permission to read Secrets through the Kubernetes API can still access them.

---

### Use an External Secrets Operator

External Secrets Operator and Secrets Store CSI Driver connect Kubernetes workloads to external secrets managers such as Vault, AWS Secrets Manager, GCP Secret Manager, and Azure Key Vault.

This pattern keeps the canonical copy of the secret in the dedicated secrets manager. Kubernetes can then sync or mount the secret into the application environment.

```text
+------------------+         +-------------------+         +------------+
| External Secrets |  sync   |  K8s Secret       |  mount  | App Pod    |
| Operator         | ------> | auto-populated    | ------> |            |
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

Example sync result:

```json
{
  "externalSecret": "prod-db-credentials",
  "provider": "AWS Secrets Manager",
  "kubernetesSecret": "db-credentials",
  "syncStatus": "success"
}
```

This approach improves central control and can simplify rotation because the external secrets manager remains the source of truth.

---

## Credential Rotation

Long-lived credentials are high-value targets. If a long-lived secret leaks, an attacker may be able to use it until someone discovers and revokes it. Rotation limits the window of exposure.

Credential rotation means replacing an old credential with a new one and ensuring applications switch safely to the new value.

Good rotation plans include:

```text
Create new credential
Deploy or reload applications with new credential
Verify new credential works
Disable old credential
Monitor for failures
```

Example rotation output:

```json
{
  "secret": "prod/database/password",
  "oldVersion": "v4",
  "newVersion": "v5",
  "rotationStatus": "completed",
  "oldCredentialRevoked": true
}
```

Applications should be designed to reload or refresh secrets safely, otherwise rotations may require downtime.

---

### Automatic Rotation

Many secrets managers support automatic rotation. For example, AWS Secrets Manager can trigger a Lambda function to rotate an RDS password.

A typical rotation function may:

1. Create new database credentials.
2. Update the secret in the secrets manager.
3. Test the new credentials.
4. Invalidate the old credentials.

Example automatic rotation flow:

```text
Secrets Manager starts rotation
Rotation function creates new password
Database password is updated
Application reads new secret
Old password is revoked
```

Example output:

```json
{
  "secret": "prod/myapp/database",
  "rotationType": "automatic",
  "testConnection": "passed",
  "oldCredentialStatus": "revoked"
}
```

Applications that retrieve secrets on each connection, or cache them with a short TTL, can pick up rotated credentials more smoothly.

---

### Dynamic Secrets

Dynamic secrets are credentials generated on demand with a limited lifetime. Instead of every application instance sharing the same database password, each instance can receive a unique temporary credential.

Vault’s database secret engine is a common example. It can create a temporary PostgreSQL user with a configured TTL.

```text
App requests DB creds
       |
       v
+------+-------+     CREATE ROLE app_abc123     +-----------+
|     Vault    | -----------------------------> | PostgreSQL|
|              | <----------------------------- |           |
| issues lease |     credentials returned       +-----------+
+--------------+
       |
       | returns username + password TTL: 1 hour
       v
   Application connects, uses creds, lease expires, creds deleted
```

Example dynamic credential output:

```json
{
  "username": "app_abc123",
  "password": "temporary-password",
  "ttl": "1h",
  "leaseId": "database/creds/app/abcd"
}
```

Dynamic secrets reduce the need for manual rotation because credentials expire automatically. If a credential leaks, its lifetime is limited.

---

## CI/CD Pipeline Secrets

CI/CD systems often need secrets for deployment, testing, signing artifacts, publishing containers, or accessing cloud infrastructure. These secrets must be handled carefully because CI logs, runners, artifacts, and build scripts can expose sensitive values.

---

### Use Native CI Secret Storage

Most CI/CD platforms provide encrypted secret storage. Secrets are injected into jobs at runtime and can be masked in logs.

Example GitHub Actions workflow:

```yaml
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

Example safe output:

```text
Deploy started
Connecting to production database
Deployment completed
```

Unsafe output would include the secret value itself. Build scripts should avoid printing secrets or dumping full environment variables.

---

### Prevent Secrets from Leaking in Logs

CI logs are often accessible to many people in an organization. A secret printed in CI logs may be copied, indexed, retained, or exposed through build artifacts.

Avoid shell debugging modes such as `set -x` when handling secrets because they may print commands and variable values.

Example safer shell pattern:

```bash
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id prod/db \
    --query SecretString \
    --output text | jq -r .password)
```

Example safe log output:

```text
Database password loaded from secrets manager
```

Example unsafe log output:

```text
DB_PASSWORD=prod-db-password
```

CI systems should use secret masking, restricted log access, and short-lived credentials whenever possible.

---

### Short-Lived OIDC Tokens for Cloud Access

Instead of storing long-lived cloud credentials in CI, modern pipelines can use OpenID Connect federation. The CI provider issues a short-lived signed token. The cloud provider validates it and returns temporary credentials scoped to the job.

```text
GitHub Actions runner
        |
        | OIDC JWT signed by GitHub
        v
  AWS / GCP / Azure
  validates JWT, issues temporary credentials scoped to job
        |
        v
  Temporary role credentials TTL: 15 minutes
```

Example GitHub Actions configuration for AWS OIDC:

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-deploy
      aws-region: us-east-1
```

Example output:

```json
{
  "credentialType": "temporary",
  "source": "OIDC",
  "ttl": "short-lived",
  "staticCloudKeysStoredInCI": false
}
```

This reduces the risk of long-lived access keys leaking from CI/CD systems.

---

## Preventing Accidental Leaks

Preventing leaks is easier than responding to them. Teams should use tools and processes that catch secrets before they reach repositories, logs, images, or production artifacts.

---

### Pre-commit Hooks

Pre-commit hooks can scan files before they are committed. Tools such as `gitleaks`, `detect-secrets`, and similar scanners look for patterns that resemble API keys, tokens, private keys, passwords, and other sensitive values.

Example installation and scan:

```bash
brew install gitleaks

gitleaks detect --source . --verbose
```

Example finding:

```json
{
  "file": ".env",
  "line": 3,
  "rule": "generic-api-key",
  "status": "blocked"
}
```

Example pre-commit configuration:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks
```

Example safe output:

```text
No leaks found
Commit allowed
```

These tools should also run in CI because developers may bypass local hooks.

---

### Rotating Leaked Secrets Immediately

If a secret is committed or exposed, assume it is compromised. Removing it from the visible file is not enough because copies may already exist in Git history, forks, logs, or caches.

Recommended response:

1. **Revoke** the secret immediately at the issuing service.
2. **Create** a replacement secret.
3. **Update** applications and deployment systems to use the new value.
4. **Remove** the secret from Git history using tools such as `git filter-repo` or BFG Repo-Cleaner.
5. **Notify** affected parties if the secret granted access to sensitive data.
6. **Review** how the leak happened and add controls to prevent recurrence.

Example incident response output:

```json
{
  "secret": "API_KEY",
  "revokeStatus": "completed",
  "replacementCreated": true,
  "gitHistoryCleaned": true,
  "postMortemRequired": true
}
```

Even after cleaning history, old clones or forks may still contain the secret. Revocation is the most important step.

---

## Access Control for Secrets

Secrets should follow the principle of least privilege. Each service should be able to read only the secrets it actually needs. A frontend service should not be able to read payment processor credentials. A reporting service should not be able to read production database admin passwords.

Access should also be separated by environment. Development, staging, and production should use different secrets and different access policies.

```text
+------------------+        allowed paths         +----------+
|  frontend-svc    | ---------------------------> | Vault    |
|  read only       |   secret/frontend/*           | policies |
+------------------+                              +----------+
                                                       |
+------------------+        allowed paths             |
|  payment-svc     | ---------------------------> |  RBAC    |
|  read only       |   secret/payment/*            +----------+
+------------------+
```

Example access policy result:

```json
{
  "service": "payment-svc",
  "allowedSecrets": ["secret/payment/stripe", "secret/payment/database"],
  "deniedSecrets": ["secret/admin/root-db-password"],
  "audit": "enabled"
}
```

Access policies should be reviewed regularly. Audit logs should record who or what accessed each secret, when, and from where.

Example audit log:

```json
{
  "timestamp": "2026-04-25T12:00:00Z",
  "principal": "payment-svc",
  "action": "read",
  "secret": "secret/payment/stripe",
  "result": "allowed"
}
```

This audit trail helps detect misuse and supports incident investigations.

