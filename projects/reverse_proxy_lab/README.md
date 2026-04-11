# Reverse Proxy Lab

This mini-project packages two existing server-technology demos into a short learning path for **request routing** and **traffic distribution**.

## What you will practice

1. How a reverse proxy exposes one public entry point while forwarding traffic to different backends
2. How path-based routing works for `/api/*` and `/static/*` style requests
3. How load-balancing strategies change request distribution across upstream servers

## Quick start

Run these commands from the repository root:

```bash
python scripts/server_technologies/reverse_proxy_example.py
python scripts/server_technologies/load_balancer_example.py
```

## Suggested walkthrough

### 1. Follow the proxy flow

Start with:

```bash
python scripts/server_technologies/reverse_proxy_example.py
```

Observe:

- requests to `/api/users` are forwarded to Backend A
- requests to `/static/index.html` are forwarded to Backend B
- unmatched paths return a `502` response

Read next:

- [`scripts/server_technologies/reverse_proxy_example.py`](../../scripts/server_technologies/reverse_proxy_example.py)
- [`notes/03_server_technologies/07_reverse_proxies.md`](../../notes/03_server_technologies/07_reverse_proxies.md)

### 2. Compare balancing strategies

Then run:

```bash
python scripts/server_technologies/load_balancer_example.py
```

Compare the output for:

- round robin
- weighted round robin
- least connections

Read next:

- [`scripts/server_technologies/load_balancer_example.py`](../../scripts/server_technologies/load_balancer_example.py)
- [`notes/03_server_technologies/08_load_balancing.md`](../../notes/03_server_technologies/08_load_balancing.md)

## Extension ideas

- Add a third backend route and verify how the proxy resolves it
- Change backend weights and compare how the weighted strategy shifts traffic
- Introduce a health flag in the load balancer so unhealthy backends stop receiving requests
