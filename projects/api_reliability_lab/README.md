# API Reliability Lab

This mini-project groups a few API-design demos into a short lab for studying **backward compatibility**, **safe retries**, and **trusted event delivery**.

## What you will practice

1. How versioning strategies let APIs evolve without breaking existing clients
2. How idempotency keys prevent duplicate side effects during retries
3. How webhook signatures protect receivers from tampered payloads

## Quick start

Run all demos at once:

```bash
cd projects/api_reliability_lab
./run.sh
```

Or run individual demos from the repository root:

```bash
python scripts/api_design/versioning_example.py
python scripts/api_design/idempotency_example.py
python scripts/api_design/webhook_signature_example.py
```

## Suggested walkthrough

### 1. Version API responses safely

```bash
python scripts/api_design/versioning_example.py
```

Focus on:

- how URL, header, and query-parameter versioning differ
- how older and newer response shapes can coexist
- why choosing one versioning strategy consistently reduces client confusion

Read next:

- [`scripts/api_design/versioning_example.py`](../../scripts/api_design/versioning_example.py)
- [`notes/01_api_design/`](../../notes/01_api_design/)

### 2. Make retries safe

```bash
python scripts/api_design/idempotency_example.py
```

Focus on:

- how retries can create duplicate payments without an idempotency key
- why servers should store and reuse the first successful response
- where idempotency keys are most useful in real payment and order APIs

Read next:

- [`scripts/api_design/idempotency_example.py`](../../scripts/api_design/idempotency_example.py)

### 3. Verify inbound webhooks

```bash
python scripts/api_design/webhook_signature_example.py
```

Focus on:

- how HMAC signing proves payload integrity
- why receivers should reject tampered webhook bodies
- why signature verification should happen before any business logic

Read next:

- [`scripts/api_design/webhook_signature_example.py`](../../scripts/api_design/webhook_signature_example.py)

## Extension ideas

- Add an expiration window to the idempotency-key store
- Extend the versioning demo with a deprecation notice for old clients
- Include a timestamp header in the webhook signature to reduce replay risk
