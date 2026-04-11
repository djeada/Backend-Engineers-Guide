# Network Resilience Lab

This mini-project groups networking demos into a short lab for studying **transport choices**, **HTTP behavior**, **name resolution**, and **downstream failure protection**.

## What you will practice

1. How TCP and UDP differ in delivery guarantees and overhead
2. How HTTP requests combine methods, headers, bodies, and status codes
3. How DNS resolution walks the hierarchy and benefits from caching
4. How circuit breakers fail fast during downstream outages

## Quick start

Run these commands from the repository root:

```bash
python scripts/network_communications/tcp_udp_example.py
python scripts/network_communications/http_request_example.py
python scripts/network_communications/dns_resolver_example.py
python scripts/network_communications/circuit_breaker_example.py
```

## Suggested walkthrough

### 1. Compare TCP and UDP

```bash
python scripts/network_communications/tcp_udp_example.py
```

Focus on:

- why TCP performs a connection handshake before sending data
- why UDP has lower overhead but weaker delivery guarantees
- which protocol is a better fit for APIs, streaming, and telemetry

Read next:

- [`scripts/network_communications/tcp_udp_example.py`](../../scripts/network_communications/tcp_udp_example.py)
- [`notes/02_network_communications/02_tcp_and_udp.md`](../../notes/02_network_communications/02_tcp_and_udp.md)

### 2. Inspect HTTP request/response flow

```bash
python scripts/network_communications/http_request_example.py
```

Focus on:

- how GET and POST differ in semantics
- where custom headers and content types show up in requests
- how servers communicate success and failure with status codes

Read next:

- [`scripts/network_communications/http_request_example.py`](../../scripts/network_communications/http_request_example.py)
- [`notes/02_network_communications/03_http_protocol.md`](../../notes/02_network_communications/03_http_protocol.md)

### 3. Trace DNS lookups

```bash
python scripts/network_communications/dns_resolver_example.py
```

Focus on:

- how recursive resolution moves from root to TLD to authoritative servers
- why TTL-based caching reduces repeated lookups
- what kinds of failures lead to NXDOMAIN or missing answers

Read next:

- [`scripts/network_communications/dns_resolver_example.py`](../../scripts/network_communications/dns_resolver_example.py)
- [`notes/02_network_communications/`](../../notes/02_network_communications/)

### 4. Protect callers with a circuit breaker

```bash
python scripts/network_communications/circuit_breaker_example.py
```

Focus on:

- when the breaker transitions from CLOSED to OPEN
- why OPEN state blocks calls instead of letting failures pile up
- how HALF_OPEN probes a dependency before normal traffic resumes

Read next:

- [`scripts/network_communications/circuit_breaker_example.py`](../../scripts/network_communications/circuit_breaker_example.py)

## Extension ideas

- Add retries with backoff ahead of the circuit breaker
- Simulate packet loss in the UDP example
- Reduce DNS TTLs and compare cache-hit behavior
