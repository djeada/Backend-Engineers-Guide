# Projects

Hands-on projects complement the notes and standalone scripts with guided labs that focus on a specific backend engineering theme.

| Project | Focus | Run style |
|---------|-------|-----------|
| [`api_reliability_lab`](api_reliability_lab/README.md) | API versioning, idempotency, and webhook trust | Python standard library scripts |
| [`database_reliability_lab`](database_reliability_lab/README.md) | Transactions, migrations, indexes, and pooling | Python standard library scripts |
| [`cache_patterns_lab`](cache_patterns_lab/README.md) | Cache eviction, TTLs, and write strategies | Python standard library scripts |
| [`messaging_reliability_lab`](messaging_reliability_lab/README.md) | Pub/sub, batching, streaming, and DLQs | Python standard library scripts |
| [`distributed_coordination_lab`](distributed_coordination_lab/README.md) | Elections, vector clocks, quorums, and hashing | Python standard library scripts |
| [`grafana_test_setup`](grafana_test_setup/README.md) | Grafana alerting, Prometheus metrics, and notification policies | Multi-service local environment |
| [`reverse_proxy_lab`](reverse_proxy_lab/README.md) | Reverse proxy routing and load-balancing strategies | Python standard library scripts |
| [`deployment_rollout_lab`](deployment_rollout_lab/README.md) | Rolling deploys, canary releases, and readiness checks | Python standard library scripts |

> Most projects can be run directly from the repository root with `python scripts/...`. The Grafana setup is the only project that downloads external tooling.
