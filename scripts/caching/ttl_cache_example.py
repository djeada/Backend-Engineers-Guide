"""
TTL-based cache with automatic expiration.

Implements a cache where each entry has a time-to-live (TTL).  Expired
entries are lazily evicted on access and eagerly purged by an optional
sweep.  Demonstrates how backends avoid serving stale data without manual
invalidation.

No external dependencies required.

Usage:
    python ttl_cache_example.py
"""

import time


class TTLCache:
    """Dictionary-backed cache with per-entry TTL."""

    def __init__(self, default_ttl: float = 5.0):
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[object, float]] = {}
        self.hits = 0
        self.misses = 0
        self.expirations = 0

    def put(self, key: str, value: object, ttl: float | None = None):
        expires_at = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = (value, expires_at)

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None, False
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            self.expirations += 1
            self.misses += 1
            return None, False
        self.hits += 1
        return value, True

    def purge_expired(self) -> int:
        now = time.monotonic()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired_keys:
            del self._store[k]
        self.expirations += len(expired_keys)
        return len(expired_keys)

    def size(self) -> int:
        return len(self._store)

    def stats(self) -> str:
        total = self.hits + self.misses
        ratio = (self.hits / total * 100) if total else 0
        return (
            f"hits={self.hits} misses={self.misses} "
            f"hit_rate={ratio:.1f}% expirations={self.expirations}"
        )


def main():
    print("=" * 60)
    print("TTL Cache Demo")
    print("=" * 60)
    print()

    cache = TTLCache(default_ttl=0.5)

    print("--- Populate cache (TTL=0.5s default, session has TTL=1.0s) ---")
    cache.put("user:1", {"name": "Alice", "role": "admin"})
    cache.put("user:2", {"name": "Bob", "role": "viewer"})
    cache.put("session:abc", "token-xyz", ttl=1.0)
    print(f"  Cache size: {cache.size()}")
    print()

    print("--- Immediate reads (all should hit) ---")
    for key in ["user:1", "user:2", "session:abc"]:
        value, hit = cache.get(key)
        print(f"  {key}: {'HIT' if hit else 'MISS'} -> {value}")
    print(f"  Stats: {cache.stats()}")
    print()

    print("--- Wait 0.6s (user entries expire, session still alive) ---")
    time.sleep(0.6)
    for key in ["user:1", "user:2", "session:abc"]:
        value, hit = cache.get(key)
        print(f"  {key}: {'HIT' if hit else 'MISS (expired)'} -> {value}")
    print(f"  Stats: {cache.stats()}")
    print()

    print("--- Wait another 0.5s (session also expires) ---")
    time.sleep(0.5)
    value, hit = cache.get("session:abc")
    print(f"  session:abc: {'HIT' if hit else 'MISS (expired)'} -> {value}")
    print(f"  Stats: {cache.stats()}")
    print()

    print("--- Eager purge demo ---")
    cache.put("temp:1", "a", ttl=0.2)
    cache.put("temp:2", "b", ttl=0.2)
    cache.put("temp:3", "c", ttl=10.0)
    print(f"  Cache size before purge: {cache.size()}")
    time.sleep(0.3)
    removed = cache.purge_expired()
    print(f"  Purged {removed} expired entries")
    print(f"  Cache size after purge: {cache.size()}")
    print(f"  Final stats: {cache.stats()}")
    print()

    print("Key takeaway: TTL caches automatically expire stale data,")
    print("reducing the need for explicit invalidation while keeping")
    print("memory usage bounded.")


if __name__ == "__main__":
    main()
