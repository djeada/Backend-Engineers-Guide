# Database Reliability Lab

This mini-project packages the database demos into a learning path for **consistency**, **schema evolution**, and **query performance**.

## What you will practice

1. How transactions preserve correctness when multiple statements must succeed together
2. How schema migrations evolve a database predictably across environments
3. How indexes trade write overhead for faster reads
4. Why connection pooling protects a database from unbounded concurrency

## Quick start

Run these commands from the repository root:

```bash
python scripts/databases/transaction_example.py
python scripts/databases/migration_example.py
python scripts/databases/index_example.py
python scripts/databases/connection_pool_example.py
```

## Suggested walkthrough

### 1. Transactions and rollback

```bash
python scripts/databases/transaction_example.py
```

Focus on:

- how a successful money transfer commits as one unit
- how a failed transfer rolls back to preserve consistency
- why uncommitted writes stay invisible to other readers

Read next:

- [`scripts/databases/transaction_example.py`](../../scripts/databases/transaction_example.py)
- [`notes/04_databases/02_transactions.md`](../../notes/04_databases/02_transactions.md)

### 2. Schema migrations

```bash
python scripts/databases/migration_example.py
```

Focus on:

- how a schema version table tracks applied changes
- why migrations should be ordered and repeatable
- how applications avoid drift between development and production schemas

Read next:

- [`scripts/databases/migration_example.py`](../../scripts/databases/migration_example.py)

### 3. Index performance

```bash
python scripts/databases/index_example.py
```

Focus on:

- how query plans change before and after index creation
- why composite and covering indexes speed up specific access patterns
- when extra index maintenance cost is worth paying

Read next:

- [`scripts/databases/index_example.py`](../../scripts/databases/index_example.py)
- [`notes/04_databases/03_indexes.md`](../../notes/04_databases/03_indexes.md)

### 4. Connection pooling

```bash
python scripts/databases/connection_pool_example.py
```

Focus on:

- what happens when all pooled connections are busy
- why applications must release connections promptly
- how pool limits protect databases under load

Read next:

- [`scripts/databases/connection_pool_example.py`](../../scripts/databases/connection_pool_example.py)

## Extension ideas

- Add a migration that backfills data as well as changing schema
- Compare two different index definitions for the same workload
- Simulate a pool timeout instead of immediate exhaustion
