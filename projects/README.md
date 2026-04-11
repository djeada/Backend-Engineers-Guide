# Projects

Hands-on projects complement the notes and standalone scripts with guided labs that focus on a specific backend engineering theme.

## Prerequisites

- **Python 3.8+** and **Bash** — required by all projects
- **Docker** and **Docker Compose** — optional, only needed for `grafana_test_setup`

## Quick start

Every lab project includes a `run.sh` script that runs all its demos in sequence:

```bash
cd projects/<project_name>
./run.sh
```

The `grafana_test_setup` project uses Docker Compose for external dependencies (Prometheus, Grafana):

```bash
cd projects/grafana_test_setup
docker compose up -d
```

## Project index

| Project | Focus | Run style |
|---------|-------|-----------|
| [`api_reliability_lab`](api_reliability_lab/README.md) | API versioning, idempotency, and webhook trust | Python standard library scripts |
| [`network_resilience_lab`](network_resilience_lab/README.md) | TCP/UDP trade-offs, HTTP flow, DNS, and circuit breakers | Python standard library scripts |
| [`security_controls_lab`](security_controls_lab/README.md) | Hashing, tokens, encryption, and rate limiting | Python standard library scripts |
| [`data_interchange_lab`](data_interchange_lab/README.md) | Text vs binary serialization formats | Python standard library scripts |
| [`request_pipeline_lab`](request_pipeline_lab/README.md) | Middleware layering for logging, auth, tracing, and CORS | Python standard library scripts |
| [`cluster_membership_lab`](cluster_membership_lab/README.md) | Gossip-based cluster membership and propagation | Python standard library scripts |
| [`database_reliability_lab`](database_reliability_lab/README.md) | Transactions, migrations, indexes, and pooling | Python standard library scripts |
| [`cache_patterns_lab`](cache_patterns_lab/README.md) | Cache eviction, TTLs, and write strategies | Python standard library scripts |
| [`messaging_reliability_lab`](messaging_reliability_lab/README.md) | Pub/sub, batching, streaming, and DLQs | Python standard library scripts |
| [`distributed_coordination_lab`](distributed_coordination_lab/README.md) | Elections, vector clocks, quorums, and hashing | Python standard library scripts |
| [`grafana_test_setup`](grafana_test_setup/README.md) | Grafana alerting, Prometheus metrics, and notification policies | Docker Compose or local binaries |
| [`reverse_proxy_lab`](reverse_proxy_lab/README.md) | Reverse proxy routing and load-balancing strategies | Python standard library scripts |
| [`deployment_rollout_lab`](deployment_rollout_lab/README.md) | Rolling deploys, canary releases, and readiness checks | Python standard library scripts |

> Most projects can be run directly with `./run.sh` inside the project directory. The Grafana setup additionally supports Docker Compose for external services.
