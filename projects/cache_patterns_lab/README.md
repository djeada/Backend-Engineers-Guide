# Cache Patterns Lab

This mini-project groups the caching demos into a focused lab on **latency reduction**, **eviction**, and **staleness control**.

## What you will practice

1. How LRU eviction keeps a cache bounded
2. How TTL expiration prevents stale data from living forever
3. How write-through, write-back, and cache-aside strategies differ

## Quick start

Run these commands from the repository root:

```bash
python scripts/caching/lru_cache_example.py
python scripts/caching/ttl_cache_example.py
python scripts/caching/cache_strategies_example.py
```

## Suggested walkthrough

### 1. LRU eviction

```bash
python scripts/caching/lru_cache_example.py
```

Focus on:

- which entries get evicted when the cache is full
- how hit rate changes when hot keys are reused
- why bounded caches need an eviction policy

Read next:

- [`scripts/caching/lru_cache_example.py`](../../scripts/caching/lru_cache_example.py)
- [`notes/05_caching/01_caching_strategies.md`](../../notes/05_caching/01_caching_strategies.md)

### 2. TTL expiration

```bash
python scripts/caching/ttl_cache_example.py
```

Focus on:

- how entries expire lazily on access
- why different keys may need different TTLs
- when an eager purge helps control memory usage

Read next:

- [`scripts/caching/ttl_cache_example.py`](../../scripts/caching/ttl_cache_example.py)

### 3. Compare write strategies

```bash
python scripts/caching/cache_strategies_example.py
```

Focus on:

- which strategy gives the fastest writes
- where consistency risk appears in write-back caching
- why cache-aside is common in application code

Read next:

- [`scripts/caching/cache_strategies_example.py`](../../scripts/caching/cache_strategies_example.py)
- [`notes/05_caching/04_database_caching.md`](../../notes/05_caching/04_database_caching.md)

## Extension ideas

- Add cache-hit metrics to each strategy
- Simulate a cache crash before write-back flush completes
- Compare small and large cache capacities on the same workload
