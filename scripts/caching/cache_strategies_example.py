"""
Cache-strategy demonstration: write-through, write-back, and cache-aside.

Builds simple cache and "database" (dict) abstractions, then shows how
each caching strategy handles reads and writes differently with
step-by-step output.

No external dependencies required.

Usage:
    python cache_strategies_example.py
"""

import time
import threading


# ---------------------------------------------------------------------------
# Simulated slow database
# ---------------------------------------------------------------------------

class FakeDatabase:
    """Dict-backed store with artificial latency to simulate I/O."""

    def __init__(self, name="DB", latency=0.05):
        self.name = name
        self._store = {}
        self._latency = latency

    def read(self, key):
        time.sleep(self._latency)
        value = self._store.get(key)
        return value

    def write(self, key, value):
        time.sleep(self._latency)
        self._store[key] = value

    def snapshot(self):
        return dict(self._store)


# ---------------------------------------------------------------------------
# Cache layer
# ---------------------------------------------------------------------------

class SimpleCache:
    """A plain dict cache with hit/miss tracking."""

    def __init__(self):
        self._store = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self._store:
            self.hits += 1
            return self._store[key], True
        self.misses += 1
        return None, False

    def put(self, key, value):
        self._store[key] = value

    def invalidate(self, key):
        self._store.pop(key, None)

    def snapshot(self):
        return dict(self._store)

    def stats(self):
        total = self.hits + self.misses
        ratio = (self.hits / total * 100) if total else 0
        return f"hits={self.hits}, misses={self.misses}, hit_rate={ratio:.1f}%"


# ---------------------------------------------------------------------------
# Strategy 1 — Write-Through
# ---------------------------------------------------------------------------

def write_through_write(cache, db, key, value):
    """Write to cache AND database synchronously."""
    cache.put(key, value)
    db.write(key, value)


def write_through_read(cache, db, key):
    """Read from cache; on miss, load from DB and populate cache."""
    value, hit = cache.get(key)
    if hit:
        return value, "HIT"
    value = db.read(key)
    if value is not None:
        cache.put(key, value)
    return value, "MISS"


def demo_write_through():
    print("=" * 60)
    print("1) Write-Through Strategy")
    print("=" * 60)
    print("  Writes go to BOTH cache and DB at the same time.")
    print("  + Data is always consistent")
    print("  - Every write has DB latency\n")

    db = FakeDatabase("WriteThrough-DB")
    cache = SimpleCache()

    ops = [
        ("WRITE", "user:1", "Alice"),
        ("WRITE", "user:2", "Bob"),
        ("READ",  "user:1", None),
        ("READ",  "user:2", None),
        ("WRITE", "user:1", "Alice-v2"),
        ("READ",  "user:1", None),
        ("READ",  "user:3", None),
    ]

    for op, key, val in ops:
        if op == "WRITE":
            start = time.perf_counter()
            write_through_write(cache, db, key, val)
            elapsed = time.perf_counter() - start
            print(f"  WRITE {key}={val:10s}  ({elapsed*1000:.1f} ms)")
        else:
            start = time.perf_counter()
            result, status = write_through_read(cache, db, key)
            elapsed = time.perf_counter() - start
            print(f"  READ  {key} -> {str(result):10s}  {status}  ({elapsed*1000:.1f} ms)")

    print(f"\n  Cache: {cache.snapshot()}")
    print(f"  DB:    {db.snapshot()}")
    print(f"  Stats: {cache.stats()}\n")


# ---------------------------------------------------------------------------
# Strategy 2 — Write-Back (Write-Behind)
# ---------------------------------------------------------------------------

class WriteBackCache:
    """Cache that buffers writes and flushes to DB asynchronously."""

    def __init__(self, db, flush_interval=0.2):
        self._cache = {}
        self._dirty = {}
        self._db = db
        self._flush_interval = flush_interval
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self._running = True
        self._thread = threading.Thread(target=self._flusher, daemon=True)
        self._thread.start()

    def get(self, key):
        with self._lock:
            if key in self._cache:
                self.hits += 1
                return self._cache[key], True
            self.misses += 1
        # cache miss — read from DB
        value = self._db.read(key)
        if value is not None:
            with self._lock:
                self._cache[key] = value
        return value, False

    def put(self, key, value):
        with self._lock:
            self._cache[key] = value
            self._dirty[key] = value  # mark dirty for async flush

    def flush_now(self):
        """Force-flush all dirty entries to the database."""
        with self._lock:
            dirty = dict(self._dirty)
            self._dirty.clear()
        for k, v in dirty.items():
            self._db.write(k, v)
        return len(dirty)

    def stop(self):
        self._running = False
        self._thread.join(timeout=2)
        self.flush_now()

    def _flusher(self):
        while self._running:
            time.sleep(self._flush_interval)
            self.flush_now()

    def snapshot(self):
        with self._lock:
            return dict(self._cache)

    def stats(self):
        total = self.hits + self.misses
        ratio = (self.hits / total * 100) if total else 0
        return f"hits={self.hits}, misses={self.misses}, hit_rate={ratio:.1f}%"


def demo_write_back():
    print("=" * 60)
    print("2) Write-Back (Write-Behind) Strategy")
    print("=" * 60)
    print("  Writes go to cache immediately; a background thread flushes")
    print("  dirty entries to the DB periodically.")
    print("  + Very fast writes (no DB latency on the hot path)")
    print("  - Risk of data loss if the cache crashes before flush\n")

    db = FakeDatabase("WriteBack-DB")
    wb = WriteBackCache(db, flush_interval=0.3)

    # Fast writes — only touch cache
    for key, val in [("order:1", "pending"), ("order:2", "shipped"), ("order:1", "confirmed")]:
        start = time.perf_counter()
        wb.put(key, val)
        elapsed = time.perf_counter() - start
        print(f"  WRITE {key}={val:12s}  ({elapsed*1000:.1f} ms)  [cache only]")

    print(f"\n  Cache: {wb.snapshot()}")
    print(f"  DB (before flush): {db.snapshot()}")

    # Wait for background flush
    print("\n  Waiting for background flush …")
    time.sleep(0.5)

    print(f"  DB (after flush):  {db.snapshot()}")

    # Read back
    val, hit = wb.get("order:2")
    tag = "HIT" if hit else "MISS"
    print(f"\n  READ  order:2 -> {val}  {tag}")
    print(f"  Stats: {wb.stats()}\n")

    wb.stop()


# ---------------------------------------------------------------------------
# Strategy 3 — Cache-Aside (Lazy Loading)
# ---------------------------------------------------------------------------

def cache_aside_read(cache, db, key):
    """Application checks cache first; on miss loads from DB."""
    value, hit = cache.get(key)
    if hit:
        return value, "HIT"
    value = db.read(key)
    if value is not None:
        cache.put(key, value)
    return value, "MISS"


def cache_aside_write(cache, db, key, value):
    """Application writes to DB, then invalidates the cache entry."""
    db.write(key, value)
    cache.invalidate(key)


def demo_cache_aside():
    print("=" * 60)
    print("3) Cache-Aside (Lazy Loading) Strategy")
    print("=" * 60)
    print("  On read-miss the app loads from DB and fills the cache.")
    print("  On write the app updates DB and INVALIDATES the cache entry,")
    print("  so the next read fetches fresh data.")
    print("  + Simple and flexible")
    print("  - First read after a write is always a miss\n")

    db = FakeDatabase("CacheAside-DB")
    cache = SimpleCache()

    # Pre-populate the database (as if data already exists)
    db._store = {"product:1": "$9.99", "product:2": "$19.99", "product:3": "$29.99"}

    ops = [
        ("READ",  "product:1", None),
        ("READ",  "product:1", None),
        ("WRITE", "product:1", "$12.99"),
        ("READ",  "product:1", None),
        ("READ",  "product:2", None),
        ("READ",  "product:4", None),
    ]

    for op, key, val in ops:
        if op == "READ":
            start = time.perf_counter()
            result, status = cache_aside_read(cache, db, key)
            elapsed = time.perf_counter() - start
            print(f"  READ  {key} -> {str(result):10s}  {status}  ({elapsed*1000:.1f} ms)")
        else:
            start = time.perf_counter()
            cache_aside_write(cache, db, key, val)
            elapsed = time.perf_counter() - start
            print(f"  WRITE {key}={val:10s}  (invalidate cache)  ({elapsed*1000:.1f} ms)")

    print(f"\n  Cache: {cache.snapshot()}")
    print(f"  DB:    {db.snapshot()}")
    print(f"  Stats: {cache.stats()}\n")


# ---------------------------------------------------------------------------
# Comparison summary
# ---------------------------------------------------------------------------

def print_comparison():
    print("=" * 60)
    print("Strategy Comparison")
    print("=" * 60)
    rows = [
        ("", "Write-Through", "Write-Back", "Cache-Aside"),
        ("Write speed", "Slow (DB sync)", "Fast (cache only)", "Slow (DB sync)"),
        ("Read miss", "Load + cache", "Load + cache", "Load + cache"),
        ("Consistency", "Strong", "Eventual", "Eventual"),
        ("Data-loss risk", "Low", "Higher", "Low"),
        ("Complexity", "Low", "Medium", "Low"),
    ]
    col_w = [16, 16, 18, 16]
    for row in rows:
        line = "  ".join(cell.ljust(w) for cell, w in zip(row, col_w))
        print(f"  {line}")
    print()


def main():
    demo_write_through()
    demo_write_back()
    demo_cache_aside()
    print_comparison()
    print("Key takeaway: The right caching strategy depends on your workload;")
    print("write-through ensures consistency, write-back maximizes write speed,")
    print("and cache-aside keeps the logic simple with lazy population.")


if __name__ == "__main__":
    main()
