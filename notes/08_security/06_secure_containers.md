# Secure Containers

Containers package an application together with its dependencies, providing portability and reproducibility. That same packaging surface can, however, introduce security risks if images are built carelessly, runtimes are misconfigured, or containers run with unnecessary privileges. This document covers the key areas of container security: hardening images, locking down the runtime, isolating workloads at the network level, and integrating security scanning into CI/CD pipelines.

## Why Container Security Matters

A container shares the host kernel with all other containers on the same machine. A successful container-escape exploit gives an attacker access to the host and every other container on it. Even without a full escape, a compromised container can exfiltrate secrets, pivot to internal services, or consume resources that disrupt neighboring workloads.

```
+--------------------------------------+
|              Host OS / Kernel        |
|   +-----------+   +-----------+      |
|   | Container |   | Container |      |
|   |   App A   |   |   App B   |      |
|   +-----------+   +-----------+      |
|   shared kernel syscall interface    |
+--------------------------------------+
```

Because the kernel boundary is thinner than a full virtual-machine hypervisor, every layer of defence matters.

## Image Hardening

### Start from a Minimal Base Image

Prefer distroless or minimal base images (such as `gcr.io/distroless/static`, `alpine`, or `debian-slim`) over full general-purpose distributions. Fewer packages mean a smaller attack surface and fewer CVEs to patch.

```dockerfile
# Avoid
FROM ubuntu:latest

# Prefer
FROM gcr.io/distroless/base-debian12
```

### Do Not Run as Root

By default many images run processes as `root` (UID 0). If an attacker exploits the application they immediately have root privileges inside the container, which makes container-escape much easier.

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

# Create a non-root user and switch to it
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

### Use Multi-Stage Builds

Multi-stage builds let you compile or build in a full-featured environment and then copy only the final artefacts into a lean runtime image, excluding compilers, build tools, and source code.

```dockerfile
# --- Build stage ---
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

# --- Runtime stage ---
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
```

### Pin Image Versions

Using `latest` tags causes silent, potentially breaking or vulnerable image updates. Pin to a specific digest or version tag and update it deliberately.

```dockerfile
# Avoid
FROM python:latest

# Prefer
FROM python:3.12.3-slim-bookworm
# or pin to SHA digest for maximum reproducibility:
# FROM python:3.12.3-slim-bookworm@sha256:<digest>
```

### Remove Secrets and Sensitive Files from Images

Never bake credentials, private keys, or `.env` files into a Docker image—they are visible to anyone with read access to the image.

```dockerfile
# Wrong — the secret is baked into a layer even if deleted later
RUN echo "MY_SECRET=abc123" > /app/.env

# Right — supply secrets at runtime via environment variables or secret mounts
```

Use `.dockerignore` to prevent sensitive files from ever entering the build context:

```
.env
.env.*
*.pem
*.key
secrets/
.git/
```

### Scan Images for Known Vulnerabilities

Integrate a vulnerability scanner such as Trivy, Grype, or Snyk into the CI pipeline so builds fail when high-severity CVEs are detected.

```bash
# Scan with Trivy (https://github.com/aquasecurity/trivy)
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:1.2.3
```

## Runtime Security

### Apply the Principle of Least Privilege

Drop all Linux capabilities and add back only those required by the application.

```bash
docker run \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --read-only \
  --tmpfs /tmp \
  myapp:1.2.3
```

| Flag | Purpose |
|------|---------|
| `--cap-drop ALL` | Remove all Linux capabilities |
| `--cap-add NET_BIND_SERVICE` | Re-add only the capability needed to bind ports < 1024 |
| `--read-only` | Mount the root filesystem read-only |
| `--tmpfs /tmp` | Provide a writable in-memory temp directory |

### Prevent Privilege Escalation

Set `no-new-privileges` so a container process cannot gain extra privileges via `setuid`/`setgid` binaries.

```bash
docker run --security-opt no-new-privileges:true myapp:1.2.3
```

In Kubernetes, this is expressed in the `securityContext`:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

### Use Seccomp and AppArmor Profiles

Seccomp filters the set of system calls a container may make; AppArmor restricts file, network, and capability access via mandatory access-control rules.

```bash
# Apply the default Docker seccomp profile
docker run --security-opt seccomp=/path/to/seccomp.json myapp:1.2.3

# Apply an AppArmor profile
docker run --security-opt apparmor=docker-default myapp:1.2.3
```

Docker applies a default seccomp profile that already blocks ~44 dangerous syscalls. Custom profiles can be even more restrictive.

### Limit Container Resources

Without resource limits a misbehaving or compromised container can starve the host. Always set CPU and memory limits.

```yaml
# Kubernetes resource limits
resources:
  requests:
    cpu: "250m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

```bash
# Docker equivalent
docker run --cpus="0.5" --memory="256m" myapp:1.2.3
```

### Avoid Privileged Containers

Running with `--privileged` gives the container nearly full access to the host. Never use it in production; redesign the workload so it does not require it.

```
+------------------+       +------------------+
| Privileged       |       | Unprivileged     |
| Container        |       | Container        |
|                  |       |                  |
| Full host access |       | Scoped, least-   |
| kernel devices   |       | privilege access |
+------------------+       +------------------+
     High risk                  Recommended
```

## Network Isolation

### Use Private Networks

Define explicit Docker networks so containers communicate only with the services they need. Avoid attaching all containers to the default bridge network.

```bash
docker network create --internal backend-net
docker run --network backend-net myapp:1.2.3
docker run --network backend-net postgres:16
```

### Apply Kubernetes Network Policies

In a Kubernetes cluster, `NetworkPolicy` resources restrict which pods can talk to which other pods.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-only-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

This allows only pods labelled `app: frontend` to reach `backend-api` on port 8080, and blocks all other inbound traffic.

### Encrypt Inter-Container Traffic

For sensitive data flowing between services inside the cluster, use a service mesh (Istio, Linkerd) to enforce mutual TLS (mTLS) automatically.

```
+------------+   mTLS   +-------------+
| Service A  | <------> |  Service B  |
+------------+          +-------------+
  cert: A.crt             cert: B.crt
```

## Container Registry Security

### Use a Private Registry

Host images in a private registry (AWS ECR, GCP Artifact Registry, Harbor) instead of public Docker Hub, so you control who can push or pull.

### Sign Images

Sign container images with Cosign or Notary so the runtime can verify the image was produced by a trusted build system and has not been tampered with.

```bash
# Sign an image with Cosign
cosign sign --key cosign.key myregistry.io/myapp:1.2.3

# Verify before deploying
cosign verify --key cosign.pub myregistry.io/myapp:1.2.3
```

### Enable Vulnerability Scanning in the Registry

Registries such as ECR and Harbor support automatic scanning on push. Block deployments of images that contain unresolved critical CVEs by coupling registry scan results to your admission controller.

## CI/CD Pipeline Integration

```
Code Push
    |
    v
+-------------------+
| Build Image       |
+-------------------+
    |
    v
+-------------------+
| Lint Dockerfile   |  <- hadolint, dockerfile-lint
+-------------------+
    |
    v
+-------------------+
| Scan for CVEs     |  <- Trivy, Grype, Snyk
+-------------------+
    |   (fail on HIGH/CRITICAL)
    v
+-------------------+
| Sign Image        |  <- Cosign
+-------------------+
    |
    v
+-------------------+
| Push to Registry  |
+-------------------+
    |
    v
+-------------------+
| Deploy (with      |
| admission check)  |  <- OPA/Gatekeeper, Kyverno
+-------------------+
```

Enforce that containers may only be deployed if the image passes a signature verification and has no open high/critical vulnerabilities, using an admission controller such as OPA Gatekeeper or Kyverno.

## Summary

| Area | Key Practice |
|------|-------------|
| Image | Minimal base, non-root user, multi-stage build, pinned tags |
| Image | No secrets baked in; scan for CVEs before push |
| Runtime | Drop all capabilities, read-only filesystem, no-new-privileges |
| Runtime | Seccomp / AppArmor profiles, resource limits |
| Network | Explicit networks, Kubernetes NetworkPolicy, mTLS |
| Registry | Private registry, image signing, scan on push |
| Pipeline | Lint → scan → sign → deploy with admission control |
