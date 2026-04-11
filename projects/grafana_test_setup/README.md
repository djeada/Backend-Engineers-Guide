# Grafana Alert Test Environment

A hands-on learning environment for **Grafana alerting, Prometheus metrics, and alert suppression**. Run a complete alerting stack locally, trigger simulated failures, and observe how alert rules, notification policies, and PromQL suppression work together.

## What you will learn

1. **Prometheus metrics** — how Gauges work, what the `/metrics` endpoint looks like, how labels create dimensions
2. **Grafana alert rules** — how rules query Prometheus, apply thresholds, and transition through Pending → Firing → Resolved states
3. **PromQL suppression** — using `unless on(...)` to suppress a child alert when the parent (root cause) is already firing
4. **Notification policies** — how `group_by`, `group_wait`, and `group_interval` reduce alert spam
5. **Provisioning as code** — managing data sources, alert rules, contact points, and policies from YAML files (not the UI)

## Architecture

```
┌──────────────┐    scrape /metrics     ┌──────────────┐
│  metricgen   │◄───────────────────────│  Prometheus  │
│  (Python)    │   every 15 seconds     │  :9090       │
│  :8000       │                        └──────┬───────┘
└──────────────┘                               │ PromQL queries
       ▲                                       ▼
       │ /set?parent=1&child=0          ┌──────────────┐
       │ (you trigger failures)         │   Grafana    │
       │                                │   :3000      │
       │                                │  evaluates   │
       │                                │  alert rules │
       │                                └──────┬───────┘
       │                                       │ webhook POST
       │                                       ▼
       │                                ┌──────────────┐
       │                                │  webhook     │
       └────────────────────────────────│  receiver    │
                                        │  :8080       │
                                        └──────────────┘
```

**Data flow:** You call `/set` on metricgen → Prometheus scrapes the new values → Grafana evaluates alert rules against Prometheus → alert fires → notification policy groups and routes → webhook contact point delivers → webhook receiver logs the payload.

## Quick start

```bash
# 1. Install Grafana, Prometheus, and Python dependencies
./scripts/install.sh

# 2. Start all four services
./scripts/start.sh

# 3. Verify everything is running
./scripts/status.sh
```

Grafana UI: [http://127.0.0.1:3000](http://127.0.0.1:3000) — login with `admin` / `admin`

## Guided walkthrough

### Experiment 1: Both parent and child fail (suppression in action)

This demonstrates the core concept — when the root cause fires, the symptom alert is suppressed.

```bash
# Open a second terminal to watch live notifications:
./scripts/watch-alerts.sh

# Trigger both parent and child failures:
./scripts/trigger-alert.sh --parent 1 --child 1
```

**What to observe:**
- In Grafana UI → Alerting → Alert rules: both rules go to **Pending**, then **Firing** within ~30s
- In the webhook log: you should see **only the parent alert** (`tier=parent`, `severity=critical`)
- The child alert fires in Grafana but its PromQL query returns empty thanks to `unless on(...)`, so it does NOT fire

**Why:** The child alert query is:
```promql
demo_child_failure unless on(env, service, dependency_group) (demo_parent_failure > 0)
```
When `demo_parent_failure > 0` with matching labels, the `unless` removes those series from the result — the child threshold sees nothing, so it stays OK.

### Experiment 2: Only child fails (no suppression)

```bash
./scripts/trigger-alert.sh --parent 0 --child 1
```

**What to observe:**
- Only the child alert fires (`tier=child`, `severity=warning`)
- The parent stays OK because `demo_parent_failure` is 0
- The `unless` has no effect because there's nothing to suppress

### Experiment 3: Reset and observe resolution

```bash
./scripts/reset-alerts.sh
```

**What to observe:**
- Within ~30s, firing alerts transition to **Resolved**
- The webhook receives a `"status": "resolved"` payload
- This shows the full alert lifecycle: Normal → Pending → Firing → Resolved

## Key files to study

Read these files in order for the best learning experience:

| File | What it teaches |
|------|----------------|
| `metricgen/app.py` | Prometheus Gauges, labels, `/metrics` endpoint, simulating failures |
| `prometheus/prometheus.yml` | Scrape configuration, pull-based monitoring model |
| `grafana/provisioning/datasources/datasource.yml` | How Grafana finds Prometheus |
| `grafana/provisioning/alerting/alerts.yml` | **⭐ The most important file** — alert rules, PromQL queries, `unless on()` suppression, threshold expressions |
| `grafana/provisioning/alerting/policies.yml` | Notification grouping and timing |
| `grafana/provisioning/alerting/contactpoints.yml` | Webhook delivery configuration |
| `webhook_receiver/app.py` | Grafana webhook payload structure |

> 💡 **Tip:** Every config file has inline comments explaining what each field does and why.

## Concept glossary

| Term | Meaning |
|------|---------|
| **Gauge** | A Prometheus metric that can go up or down (e.g., 0 = healthy, 1 = failing) |
| **Labels** | Key-value pairs on a metric (e.g., `env="uat"`) that create separate time series |
| **PromQL** | Prometheus Query Language — used in alert rule expressions |
| **`unless on(...)`** | PromQL set operator: returns the left side EXCEPT where the right side has matching labels |
| **`__expr__`** | Grafana's built-in expression engine for thresholds and math (not Prometheus) |
| **`for` duration** | How long a condition must be true before the alert fires (prevents flapping) |
| **Contact point** | Where alert notifications go (webhook, Slack, PagerDuty, email, etc.) |
| **Notification policy** | Rules for grouping, routing, and timing alert notifications |
| **`group_by`** | Labels used to bundle multiple alerts into a single notification |
| **Provisioning** | Loading Grafana config from files (YAML) instead of the UI — enables version control |

## Useful scripts

| Script | Purpose |
|--------|---------|
| `./scripts/install.sh` | Download Grafana and Prometheus, create Python virtualenv |
| `./scripts/start.sh` | Start all four services |
| `./scripts/stop.sh` | Stop all services |
| `./scripts/status.sh` | Show process and endpoint health |
| `./scripts/trigger-alert.sh` | Simulate failures with `--parent 1 --child 1` flags |
| `./scripts/reset-alerts.sh` | Set all metrics back to 0 |
| `./scripts/watch-alerts.sh` | Live-stream webhook alert notifications |
| `./scripts/tail-logs.sh` | Tail all service logs at once |

## Directory layout

```
grafana_test_setup/
├── grafana/provisioning/       # Grafana config-as-code (data sources, alert rules, etc.)
│   ├── datasources/            #   How Grafana connects to Prometheus
│   └── alerting/               #   Alert rules, policies, contact points
├── prometheus/prometheus.yml   # What Prometheus scrapes and how often
├── metricgen/app.py            # Fake metrics service (the thing being "monitored")
├── webhook_receiver/app.py     # Catches and displays alert notifications
├── scripts/                    # Lifecycle scripts (install, start, stop, trigger, etc.)
├── bin/                        # Downloaded Grafana + Prometheus binaries (gitignored)
└── runtime/                    # Logs, PID files, data (gitignored)
```

## Notes

- The install script pins explicit versions (Grafana 10.4.3, Prometheus 2.52.0) for reproducibility. Override with `GRAFANA_VERSION` and `PROMETHEUS_VERSION` environment variables.
- The child alert uses PromQL suppression (`unless on(...)`) which works on any Grafana version. For Grafana 13+, you could alternatively use native inhibition rules.
- All services bind to `127.0.0.1` by default. Override with the `HOST` environment variable.
