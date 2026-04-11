# Request Pipeline Lab

This mini-project focuses on the **middleware pipeline** that sits between an incoming request and your application handler.

## What you will practice

1. How middleware layers compose around a core handler
2. How logging, tracing, CORS, and auth fit into the same request path
3. Why cross-cutting concerns belong in reusable wrappers instead of business logic

## Quick start

Run this command from the repository root:

```bash
python scripts/server_technologies/middleware_chain_example.py
```

## Suggested walkthrough

### 1. Follow a request through the chain

```bash
python scripts/server_technologies/middleware_chain_example.py
```

Focus on:

- how request IDs are added before the response is returned
- why auth can short-circuit a request before it reaches the route handler
- how response headers are enriched on the way back out

Read next:

- [`scripts/server_technologies/middleware_chain_example.py`](../../scripts/server_technologies/middleware_chain_example.py)
- [`notes/03_server_technologies/`](../../notes/03_server_technologies/)

## Extension ideas

- Add a metrics middleware that tracks status-code counts
- Insert a rate-limiting middleware before auth and compare behavior
- Add request timing to the response body for debugging
