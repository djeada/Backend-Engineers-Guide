# Supply Chain Attacks

A supply chain attack targets the tools, dependencies, build systems, or distribution channels that an application relies on, rather than attacking the application directly. By compromising a trusted component upstream, an adversary can inject malicious code into many downstream consumers at once. High-profile incidents—SolarWinds, the XZ Utils backdoor, the npm `event-stream` compromise, and dozens of typosquatting campaigns—show that supply chain attacks are a realistic and growing threat to backend systems.

## What Is a Software Supply Chain?

```
Developer workstation
        |
        | git push
        v
+------------------+     fetch deps      +------------------+
|  Source Repo     | -----------------> | Package Registry |
| (GitHub, GitLab) |                    | (npm, PyPI, Maven|
+------------------+                    |  crates.io, etc.)|
        |                               +------------------+
        | triggers
        v
+------------------+     pull base image  +------------------+
|  CI/CD Pipeline  | ------------------> | Container Registry|
| (Actions, Jenkins|                     | (Docker Hub, ECR)|
+------------------+                     +------------------+
        |
        | push artefact
        v
+------------------+
| CD / Deployment  |
| (K8s, ECS, VM)   |
+------------------+
        |
        v
+------------------+
|  Production      |
+------------------+
```

Every arrow in this diagram is a potential attack surface. A supply chain attack exploits trust at any one of these links.

## Common Attack Vectors

### Dependency Confusion

An attacker publishes a malicious package to a **public** registry (npm, PyPI, RubyGems) with the same name as a **private** internal package, but with a higher version number. Package managers that check both private and public feeds may silently fetch the public (malicious) one.

```
Internal registry:   acme-internal-utils @ 1.2.0
Public npm registry: acme-internal-utils @ 9.9.9  <-- attacker-controlled
                                                       (higher version wins)
```

**Mitigation**: Use a private registry proxy (Artifactory, AWS CodeArtifact, Nexus) configured to **only** serve specific scopes from the public registry. For npm, set the package scope in `.npmrc`:

```
@acme:registry=https://registry.acme.internal
```

For pip, pin exact hashes in `requirements.txt`:

```
acme-internal-utils==1.2.0 \
    --hash=sha256:abcdef1234...
```

### Typosquatting

Attackers register packages with names that closely resemble popular legitimate packages, hoping developers will mistype them.

Examples of real typosquatting campaigns:

| Legitimate package | Typosquat package |
|--------------------|-------------------|
| `requests` (Python) | `reqeusts`, `request` |
| `lodash` (npm) | `lodahs`, `lodash_` |
| `boto3` (Python) | `bot03`, `botto3` |

**Mitigation**:
- Verify the package owner and download counts before adding a new dependency.
- Lock dependencies to exact versions with integrity hashes.
- Use a private proxy that has an allow-list of approved packages.

### Compromised Maintainer Account

An attacker gains access to a legitimate maintainer's account (through phishing, credential stuffing, or buying an abandoned package) and publishes a new version containing malicious code. The `event-stream` npm package compromise (2018) is a well-known example.

```
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
                              | @3.3.6 (malicious)|
                              +------------------+
                                         |
                                         | millions of apps install it
                                         v
                              Malicious code executes in production
```

**Mitigation**:
- Enable MFA on all package registry accounts.
- Set up alerts for new versions of critical dependencies (Dependabot, Renovate, socket.dev).
- Review changelogs and diffs before upgrading; prefer automated PRs over manual upgrades.

### Build System Compromise

An attacker targets the CI/CD pipeline itself—via a compromised build agent, a malicious GitHub Action, or a tampered build script—to inject code into artefacts during the build phase. The SolarWinds SUNBURST attack modified the build system to insert a backdoor into signed software updates.

```
+-------------------+
| Source code (OK)  |
+-------------------+
         |
         v
+-------------------+
| Build System      |  <-- attacker modifies build scripts / runner
| (compromised)     |      injects malicious code into artefact
+-------------------+
         |
         v
+-------------------+
| Signed Artefact   |  <-- signature is valid (signed by legitimate key)
| (contains payload)|       but the content has been tampered with
+-------------------+
         |
         v
+-------------------+
| Production        |
| (executes payload)|
+-------------------+
```

**Mitigation**:
- Use ephemeral, hermetic build environments.
- Pin GitHub Actions versions to a full commit SHA rather than a tag.
- Audit third-party Actions before using them; prefer actions from verified publishers.
- Implement binary authorisation: only deploy artefacts whose provenance can be cryptographically verified.

### Malicious Pull Requests and Code Injection

Open-source projects with automated CI pipelines can be targeted with pull requests that contain subtle backdoors. The XZ Utils incident (2024) involved a patient, multi-year social engineering campaign to gain maintainer trust before inserting a backdoor.

**Mitigation**:
- Require code review from multiple maintainers for security-sensitive changes.
- Apply code-owner rules that enforce reviews from domain experts for critical paths.
- Run CI in a sandboxed environment that cannot access production secrets.
- Use `pull_request_target` carefully in GitHub Actions; prefer `pull_request` from forks (which has no secret access by default).

### Protestware and Intentional Sabotage by Package Authors

Some authors have intentionally introduced destructive code into their own packages to make a political statement (`colors.js`, `node-ipc`). This highlights that even legitimate maintainers can become threats.

**Mitigation**: Treat all third-party code as potentially hostile; pin versions and require approval for upgrades.

## Software Bill of Materials (SBOM)

An SBOM is a machine-readable inventory of all software components—direct and transitive dependencies—and their versions, licences, and vulnerability status. SBOMs enable rapid identification of affected components when a new CVE is disclosed.

```
+------------------+
|  Your Application|
|  v2.4.1          |
+------------------+
  Contains:
  - express 4.18.2
    - accepts 1.3.8
    - depd 2.0.0
    - ...
  - lodash 4.17.21
  - pg 8.11.3
    - pg-connection-string 2.6.2
    - ...
```

Common SBOM formats:
- **SPDX** (ISO/IEC 5962:2021) – widely supported, used by Linux Foundation projects.
- **CycloneDX** – designed specifically for security use cases; supports VEX (Vulnerability Exploitability eXchange).

Generate an SBOM with Syft:

```bash
syft myapp:1.2.3 -o spdx-json > sbom.spdx.json
syft myapp:1.2.3 -o cyclonedx-json > sbom.cyclonedx.json
```

Store the SBOM as a build artefact and scan it against vulnerability databases (OSV, NVD) with Grype:

```bash
grype sbom:sbom.spdx.json --fail-on high
```

## Dependency Pinning and Integrity Verification

### Lock Files

Always commit lock files. They record the exact resolved versions and (in many ecosystems) the content hashes of every dependency.

| Ecosystem | Lock file |
|-----------|-----------|
| Node.js | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python | `requirements.txt` (with hashes) or `poetry.lock` |
| Go | `go.sum` |
| Rust | `Cargo.lock` |
| Ruby | `Gemfile.lock` |
| Java | resolved via BOM + dependency checksums |

### Hash Pinning

For high-assurance environments, pin dependencies to their SHA-256 hash:

```bash
# pip — generate hashed requirements
pip-compile --generate-hashes requirements.in -o requirements.txt

# requirements.txt entry produced:
requests==2.31.0 \
    --hash=sha256:58cd2187423839b8e... \
    --hash=sha256:942c5a758f98d790...
```

```json
// npm — sub-resource integrity in package-lock.json (automatic)
{
  "node_modules/lodash": {
    "version": "4.17.21",
    "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
    "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZkGLZqJZFYjsLumBKg=="
  }
}
```

## Artefact Signing and Provenance

### Sigstore and Cosign

[Sigstore](https://www.sigstore.dev/) provides free, transparent signing for open-source packages. Cosign signs container images and other artefacts using short-lived keys tied to an OIDC identity (no long-lived key material to manage).

```bash
# Sign a container image from a CI job (keyless signing)
cosign sign --yes myregistry.io/myapp:1.2.3

# Verify the image, checking it was signed by a specific GitHub Actions workflow
cosign verify \
  --certificate-identity "https://github.com/acme/myapp/.github/workflows/release.yml@refs/tags/v1.2.3" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:1.2.3
```

### SLSA Framework

[SLSA](https://slsa.dev/) (Supply-chain Levels for Software Artefacts) defines graduated security levels for build provenance:

| Level | Key requirement |
|-------|----------------|
| SLSA 1 | Provenance exists (build system generates it) |
| SLSA 2 | Hosted build; provenance is signed |
| SLSA 3 | Hardened build; provenance prevents tampering |
| SLSA 4 | Hermetic, reproducible build; two-party review |

GitHub's `slsa-github-generator` can produce SLSA level 3 provenance directly from GitHub Actions:

```yaml
jobs:
  build:
    uses: slsa-framework/slsa-github-generator/.github/workflows/builder_go_slsa3.yml@v1.9.0
    with:
      go-version: "1.22"
```

### Reproducible Builds

A reproducible build produces bit-for-bit identical output from the same source code, regardless of the machine or time of build. This allows independent parties to verify that a distributed binary matches the claimed source.

## Dependency Auditing and Automated Updates

### Automated Vulnerability Alerts

| Tool | Ecosystem | What it does |
|------|-----------|-------------|
| Dependabot | npm, pip, Go, Maven, etc. | Opens PRs to upgrade vulnerable dependencies |
| Renovate | Same + more | Highly configurable; groups updates, auto-merges patch releases |
| socket.dev | npm | Analyses package behaviour, flags suspicious patterns |
| OSV-Scanner | All major ecosystems | Scans lock files against the OSV database |

```bash
# OSV-Scanner
osv-scanner --lockfile package-lock.json
osv-scanner --lockfile requirements.txt
osv-scanner --sbom sbom.cyclonedx.json
```

### Manual Dependency Review

Before adding a new package:

1. Check download counts and recent activity (abandoned packages are risky).
2. Review the list of maintainers and whether they have MFA enabled (npm badge, PyPI trusted publishers).
3. Read the changelog for any recent suspicious changes.
4. Prefer packages with a clear security policy and a history of CVE fixes.
5. Run `socket scan npm install <package>` or equivalent to detect risky patterns.

## Network-Level Mitigations

Use a private package proxy to enforce an allow-list of approved packages and versions, and to prevent dependency confusion attacks:

```
Developer / CI runner
         |
         | all package requests
         v
+------------------+
| Private Proxy    |  (Artifactory, AWS CodeArtifact, Nexus)
| - allow-list     |  - cache approved packages
| - audit log      |  - block unapproved names/scopes
| - CVE scan       |  - scan packages on first fetch
+------------------+
         |
         | only allowed packages
         v
+------------------+
| Public Registry  |
| (npm, PyPI, etc.)|
+------------------+
```

## Incident Response for Supply Chain Compromises

1. **Identify blast radius**: Use the SBOM to determine which services include the affected component and which version range is vulnerable.
2. **Isolate**: If a service is actively exploiting the malicious package, take it out of rotation.
3. **Patch**: Pin to a clean version and redeploy. If no clean version is available, fork and patch internally.
4. **Verify**: Confirm the new deployment does not include the compromised version.
5. **Rotate**: Assume all secrets the compromised process could have accessed are leaked; revoke and rotate them.
6. **Post-mortem**: Determine how the dependency was introduced without review, and close the gap (better alerting, stricter allow-lists, required review for new dependencies).

## Summary

| Threat | Mitigation |
|--------|-----------|
| Dependency confusion | Private registry proxy with scope/name allow-lists |
| Typosquatting | Verify package identity, hash-pin dependencies |
| Compromised maintainer | Version pinning, automated diff review, MFA on registry accounts |
| Compromised build system | Ephemeral CI, pinned Action versions (full SHA), binary authorisation |
| Unknown vulnerabilities in transitive deps | SBOM generation, automated CVE scanning, Dependabot/Renovate |
| Tampered artefacts | Cosign image signing, SLSA provenance, reproducible builds |
| Widespread blast radius after disclosure | SBOM enables rapid inventory; automated update PRs speed remediation |
