# Scripts

A collection of small, self-contained Python scripts that demonstrate key backend engineering concepts covered in the [notes](../notes). Every script uses only the Python standard library so no extra dependencies are needed.

## Prerequisites

- Python 3.8 or later

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
| `network_communications/` | `tcp_udp_example.py` | TCP vs UDP echo server/client comparison |
| `databases/` | `transaction_example.py` | SQLite transactions and ACID properties |
| `caching/` | `lru_cache_example.py` | LRU cache implementation and eviction |
| `data_formats/` | `format_conversion.py` | JSON, XML, and YAML conversion |
| `data_processing/` | `pub_sub_example.py` | In-process publish/subscribe broker |
| `security/` | `hashing_example.py` | Password hashing, token generation |
| `distributed_systems/` | `gossip_protocol_example.py` | Gossip protocol cluster simulation |
| `server_technologies/` | `load_balancer_example.py` | Load balancing strategy simulation |
| `deployment/` | `health_check_example.py` | Health-check and readiness endpoints |
