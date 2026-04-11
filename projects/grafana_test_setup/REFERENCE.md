# Advanced Reference — Grafana Alerting Concepts

This document covers advanced concepts for students who want to go deeper after working through the hands-on demo in [README.md](README.md).

---

## How alert evaluation works (step by step)

1. **Metricgen** exposes `demo_parent_failure` and `demo_child_failure` Gauges on `/metrics`
2. **Prometheus** scrapes these every 15 seconds and stores them as time series
3. **Grafana** evaluates alert rules every 10 seconds (configured in `alerts.yml` → `interval: 10s`)
4. Each rule has a **PromQL query** (step A) and a **threshold expression** (step C)
5. If the threshold is exceeded, the alert enters **Pending** state
6. After the **`for` duration** (30s in our setup), if still true, it transitions to **Firing**
7. Grafana's **notification policy** groups the firing alert with others sharing the same `group_by` labels
8. After **`group_wait`** (10s), the grouped notification is sent to the **contact point** (our webhook)
9. When the metric drops back to 0, the alert transitions to **Resolved** and a resolution notification is sent

### Alert state machine

```
              condition true          for duration elapsed
  Normal ────────────────► Pending ────────────────────────► Firing
    ▲                         │                                │
    │     condition false      │         condition false        │
    └─────────────────────────┘                                │
    ▲                                                          │
    │              resolved notification sent                   │
    └──────────────────────────────────────────────────────────┘
```

---

## The `unless on(...)` suppression pattern

This is the core teaching concept of the demo. The child alert query is:

```promql
demo_child_failure unless on(env, service, dependency_group) (demo_parent_failure > 0)
```

### How it works

- `unless` is a PromQL **set difference** operator
- It takes two sets of time series (left and right)
- For each series on the left, if there's a matching series on the right (matched by the labels in `on(...)`), it's **removed** from the result
- `on(env, service, dependency_group)` means matching happens on these three labels

### Truth table

| `demo_parent_failure` | `demo_child_failure` | Query result | Child alert fires? |
|:---------------------:|:--------------------:|:------------:|:-----------------:|
| 0 | 0 | empty | No |
| 0 | 1 | `demo_child_failure` | **Yes** |
| 1 | 0 | empty | No |
| 1 | 1 | empty (suppressed) | **No** ← this is the key case |

### Why this matters

In real systems, a database going down (parent) causes many downstream services to fail (children). Without suppression, you'd get N+1 alerts. With suppression, you get exactly one: the root cause.

---

## Alternative approaches to alert suppression

### 1. Grafana inhibition rules (Grafana 13+)

Native feature that suppresses alerts based on label matching without changing PromQL:

```yaml
inhibitRules:
  - sourceMatchers:
      - ["tier", "=", "parent"]
    targetMatchers:
      - ["tier", "=", "child"]
    equal:
      - service
      - dependency_group
      - env
```

**Pros:** Cleaner separation of concerns — alert queries stay simple.
**Cons:** Only available in Grafana 13+.

### 2. Routing to different contact points

Route child alerts to a low-noise channel (e.g., email) while parent alerts go to PagerDuty:

```yaml
policies:
  - orgId: 1
    receiver: pagerduty
    routes:
      - receiver: email-only
        object_matchers:
          - ["tier", "=", "child"]
```

### 3. Informational child alerts

Keep child alerts but make them less urgent:
- Set `severity: info` instead of `severity: warning`
- Increase `for` duration to 5m
- Increase `repeat_interval` to 24h

---

## Notification policy timing explained

```yaml
group_wait: 10s        # Collect alerts for 10s before first notification
group_interval: 1m     # Wait 1m between updates to the same group
repeat_interval: 4h    # Re-notify every 4h for a still-firing alert
```

**Example timeline:**
- `T+0s` — Alert A fires (checkout/payments/uat)
- `T+5s` — Alert B fires (same group labels)
- `T+10s` — `group_wait` expires → ONE notification with alerts A+B
- `T+70s` — `group_interval` expires → next update can be sent if group changed
- `T+4h` — `repeat_interval` expires → re-notify even if nothing changed

---

## Scaling this approach

To add a new environment or service, you don't copy alert rules. Instead:

1. **Add new metric labels** in metricgen (e.g., `env=staging`, `service=inventory`)
2. **Seed them** in `seed_defaults()` so Prometheus sees them immediately
3. **The alert rules automatically create new instances** — Grafana's multi-dimensional alerting creates one alert instance per unique label combination

This is why the PromQL queries don't hardcode `env="uat"` — they match ALL environments, and labels carry the context.

---

## Further reading

- [Grafana alerting documentation](https://grafana.com/docs/grafana/latest/alerting/)
- [Provisioning alerting resources from files](https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/file-provisioning/)
- [Notification policies](https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/notification-policies/)
- [PromQL operators (including `unless`)](https://prometheus.io/docs/prometheus/latest/querying/operators/)
- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
