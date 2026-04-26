
## Deployment Strategies

A deployment strategy defines how a new version of an application is released to production. The right strategy balances risk, speed, infrastructure cost, and rollback complexity.

### Rolling Update

A rolling update replaces instances of the old version one at a time (or in small batches), keeping the cluster available throughout.

```
  Before   Step 1       Step 2       Step 3   After
  ──────   ──────────   ──────────   ──────   ─────
  [v1]     [v2]         [v2]         [v2]     [v2]
  [v1]  →  [v1]    →   [v2]    →   [v2]  →  [v2]
  [v1]     [v1]         [v1]         [v2]     [v2]
```

**Characteristics:**

- Zero downtime when `maxUnavailable = 0`.
- Old and new versions coexist during the rollout — API changes must be backward-compatible.
- Rollback requires re-deploying the previous version, which takes as long as the original deploy.
- Default strategy for Kubernetes Deployments.

**When to use:** Most stateless services with backward-compatible changes.

**Kubernetes configuration:**

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # extra pods allowed during update
    maxUnavailable: 0  # no pods removed until replacement is ready
```

### Blue-Green Deployment

Two identical production environments exist simultaneously. Only one environment (blue) receives live traffic. The new version is deployed to the idle environment (green), tested, then traffic is switched over instantly.

```
         Load Balancer
              |
    ┌─────────┴─────────┐
    ▼                   ▼
  [Blue v1]          [Green v2]  ← new version deployed here
  (live traffic)     (idle)

        ──── switch ────►

         Load Balancer
              |
    ┌─────────┴─────────┐
    ▼                   ▼
  [Blue v1]          [Green v2]
  (idle / standby)  (live traffic)
```

**Characteristics:**

- Instant cutover with zero downtime.
- Instant rollback — flip traffic back to blue.
- Requires double the infrastructure (both environments must be production-grade).
- Both environments must stay in sync with configuration and database state.

**When to use:** High-stakes releases where instant rollback is essential; when infrastructure cost of running two environments is acceptable.

### Canary Release

A small percentage of traffic is gradually shifted to the new version. Metrics and error rates are monitored before widening the rollout.

```
                    ┌──► [v2] 5% of traffic
  Load Balancer ───►│
                    └──► [v1] 95% of traffic

              ... watch metrics ...

                    ┌──► [v2] 50%
  Load Balancer ───►│
                    └──► [v1] 50%

              ... watch metrics ...

                    ┌──► [v2] 100%
  Load Balancer ───►│
                    └──► [v1] 0%  (decommissioned)
```

**Characteristics:**

- Real production traffic validates the new version before full rollout.
- Limits the blast radius of a bug to a small percentage of users.
- Requires traffic-splitting support (Nginx, Istio, AWS ALB weighted target groups).
- More complex monitoring and routing setup than a rolling update.

**When to use:** High-traffic services where bugs have a large customer impact; machine learning model updates; significant user-facing changes.

**Kubernetes with Nginx Ingress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"  # 10% to canary
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-v2-svc
                port:
                  number: 80
```

### Feature Flags

Feature flags (also called feature toggles) decouple deployment from release. Code is shipped to production in a disabled state, then enabled independently of a deployment.

```
  Deploy (always)                 Release (controlled)
  ──────────────────              ──────────────────────
  git push → CI → prod    +       Feature Flag ON/OFF
                                  (per user, group, %)
```

**Types:**

| Type | Lifespan | Purpose |
|------|----------|---------|
| Release toggle | Short | Hide incomplete features until ready |
| Experiment toggle | Medium | A/B testing, canary experiments |
| Ops toggle | Long | Kill switch for expensive or risky code paths |
| Permission toggle | Long | Grant features to specific user groups |

**Simple implementation:**

```python
import os

FEATURE_FLAGS = {
    "new_checkout_flow": os.getenv("FF_NEW_CHECKOUT", "false").lower() == "true",
    "recommendations_v2": os.getenv("FF_RECS_V2", "false").lower() == "true",
}

def is_enabled(flag: str) -> bool:
    return FEATURE_FLAGS.get(flag, False)
```

In production, tools like **LaunchDarkly**, **Unleash**, or **Flagsmith** provide dynamic flag evaluation, user targeting, and percentage rollouts without redeployment.

**Benefits:**

- Decouple feature release from code deployment.
- Quickly disable a problematic feature without rollback.
- Target new features at internal users or beta groups first.

**Risks:**

- Flag proliferation — clean up flags once a feature is fully released.
- Combinatorial complexity — many flags increase the number of code paths to test.

### Recreate (Big Bang)

All old instances are terminated before new instances start. Results in a brief outage.

```
  [v1] [v1] [v1]  →  (down)  →  [v2] [v2] [v2]
```

**When to use:** Development or staging environments where downtime is acceptable; breaking database schema changes that cannot be run side-by-side.

### Comparison

| Strategy | Downtime | Rollback Speed | Resource Cost | Risk Scope |
|----------|----------|----------------|---------------|------------|
| Recreate | Brief outage | Fast (redeploy old) | Low | 100% |
| Rolling | None | Slow (redeploy) | Low (+1 surge) | Decreasing |
| Blue-Green | None | Instant (traffic flip) | 2× | 0% after switch |
| Canary | None | Fast (reroute) | Low (+canary) | Small % |
| Feature Flag | None | Instant (toggle off) | None | Configurable |

### Choosing a Strategy

1. **Is downtime acceptable?** If no, rule out Recreate.
2. **Are the changes backward-compatible?** If no, Blue-Green avoids mixed-version coexistence.
3. **Is production traffic the only way to validate?** If yes, use Canary.
4. **Is infrastructure cost a constraint?** If yes, prefer Rolling over Blue-Green.
5. **Should release be decoupled from deployment?** If yes, add Feature Flags.

### Rollback Planning

Every deployment strategy must have a tested rollback procedure before the change goes to production.

- **Rolling / Recreate** – rerun the pipeline with the previous image tag.
- **Blue-Green** – redirect traffic back to the previous environment instantly.
- **Canary** – reduce canary weight to 0% or delete the canary Ingress.
- **Feature Flag** – disable the flag in the feature flag service.

Document the rollback steps in a runbook and test them in staging before each significant release.
