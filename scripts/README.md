# Scripts

A collection of small, self-contained scripts (primarily Python, plus Bash) that demonstrate key backend engineering concepts covered in the [notes](../notes). Python scripts use only the standard library so no extra dependencies are needed.

## Prerequisites

- Python 3.8 or later
- Bash

## Quick Start

Run any script directly:

```bash
cd scripts
python api_design/rest_api_example.py
```

## Script Index

| Directory | Script | Topic |
|-----------|--------|-------|
| `api_design/` | `rest_api_example.py` | Minimal REST API server with CRUD endpoints |
| `api_design/` | `graphql_example.py` | GraphQL-like query engine with field selection |
| `api_design/` | `idempotency_example.py` | Idempotency keys for retry-safe POST operations |
| `api_design/` | `webhook_signature_example.py` | HMAC webhook signature verification for event authenticity |
| `api_design/` | `pagination_example.sh` | Offset/limit pagination walkthrough for large datasets |
| `network_communications/` | `tcp_udp_example.py` | TCP vs UDP echo server/client comparison |
| `network_communications/` | `http_request_example.py` | HTTP methods, headers, and content types |
| `network_communications/` | `retry_backoff_example.sh` | Exponential-backoff retry loop for unstable outbound calls |
| `network_communications/` | `circuit_breaker_example.py` | Circuit breaker state transitions for flaky dependencies |
| `databases/` | `transaction_example.py` | SQLite transactions and ACID properties |
| `databases/` | `index_example.py` | Index performance and EXPLAIN QUERY PLAN |
| `databases/` | `connection_pool_example.py` | Fixed-size connection pool acquisition and exhaustion |
| `caching/` | `lru_cache_example.py` | LRU cache implementation and eviction |
| `caching/` | `cache_strategies_example.py` | Write-through, write-back, and cache-aside patterns |
| `caching/` | `cache_warming_example.sh` | Cache warm-up of hot keys before traffic cutover |
| `data_formats/` | `format_conversion.py` | JSON, XML, and YAML conversion |
| `data_formats/` | `protocol_buffer_example.py` | Protocol-buffer-like binary serialization |
| `data_processing/` | `pub_sub_example.py` | In-process publish/subscribe broker |
| `data_processing/` | `batch_processing_example.py` | Batch processing pipeline with configurable batches |
| `data_processing/` | `dead_letter_queue_example.py` | Retry then route poison jobs to a DLQ |
| `security/` | `hashing_example.py` | Password hashing, token generation |
| `security/` | `jwt_example.py` | JWT-like token creation and verification |
| `security/` | `rate_limiter_example.py` | Token-bucket request throttling with burst tolerance |
| `security/` | `api_key_rotation_example.sh` | Zero-downtime API key rotation sequence |
| `distributed_systems/` | `gossip_protocol_example.py` | Gossip protocol cluster simulation |
| `distributed_systems/` | `vector_clock_example.py` | Vector clock causality tracking |
| `distributed_systems/` | `quorum_example.py` | Quorum overlap checks for replicated data consistency |
| `server_technologies/` | `load_balancer_example.py` | Load balancing strategy simulation |
| `server_technologies/` | `reverse_proxy_example.py` | Reverse proxy routing by path prefix |
| `server_technologies/` | `nginx_log_parse_example.sh` | Parse access logs to count requests and 5xx errors |
| `deployment/` | `health_check_example.py` | Health-check and readiness endpoints |
| `deployment/` | `rolling_deploy_example.py` | Rolling deployment simulation |
| `deployment/` | `rolling_restart_example.sh` | Rolling restart sequence with health-check gating |
| `deployment/` | `blue_green_switch_example.sh` | Blue/green deployment traffic switch workflow |
