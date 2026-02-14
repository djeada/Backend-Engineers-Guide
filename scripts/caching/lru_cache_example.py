"""
LRU (Least Recently Used) cache demonstration.

Implements a simple LRU cache from scratch and compares it with
Python's built-in functools.lru_cache to illustrate common caching
strategies discussed in backend engineering.

No external dependencies required.

Usage:
    python lru_cache_example.py
"""

import time
from collections import OrderedDict
from functools import lru_cache


class LRUCache:
    """A minimal LRU cache built on OrderedDict."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.hits += 1
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            evicted = self.cache.popitem(last=False)
            print(f"    Evicted key={evicted[0]}")

    def stats(self):
        total = self.hits + self.misses
        ratio = (self.hits / total * 100) if total else 0
        return f"hits={self.hits}, misses={self.misses}, hit_rate={ratio:.1f}%"


# ---------- Simulated slow lookup ----------

def slow_lookup(key: int) -> str:
    """Simulate a slow database or network call."""
    time.sleep(0.05)
    return f"value_for_{key}"


def demo_manual_cache():
    """Demonstrate the hand-rolled LRU cache."""
    print("=" * 55)
    print("1) Hand-Rolled LRU Cache (capacity=3)")
    print("=" * 55)

    cache = LRUCache(capacity=3)

    keys = [1, 2, 3, 1, 4, 2, 5, 1]
    for k in keys:
        result = cache.get(k)
        if result is None:
            result = slow_lookup(k)
            cache.put(k, result)
            print(f"  key={k}  MISS  -> fetched '{result}'")
        else:
            print(f"  key={k}  HIT   -> cached  '{result}'")

    print(f"\n  Cache stats: {cache.stats()}")
    print()


def demo_functools_cache():
    """Demonstrate Python's built-in functools.lru_cache."""
    print("=" * 55)
    print("2) functools.lru_cache (maxsize=3)")
    print("=" * 55)

    @lru_cache(maxsize=3)
    def cached_lookup(key: int) -> str:
        time.sleep(0.05)
        return f"value_for_{key}"

    keys = [1, 2, 3, 1, 4, 2, 5, 1]
    for k in keys:
        start = time.perf_counter()
        result = cached_lookup(k)
        elapsed = time.perf_counter() - start
        status = "MISS" if elapsed > 0.01 else "HIT "
        print(f"  key={k}  {status} -> '{result}'  ({elapsed*1000:.1f} ms)")

    info = cached_lookup.cache_info()
    print(f"\n  Cache info: {info}")
    print()


def main():
    demo_manual_cache()
    demo_functools_cache()
    print("Key takeaway: Caching avoids repeated expensive lookups;")
    print("LRU eviction keeps the cache bounded by removing the least-recently-used entries.")


if __name__ == "__main__":
    main()
