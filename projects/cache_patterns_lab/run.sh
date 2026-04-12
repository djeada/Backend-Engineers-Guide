#!/usr/bin/env bash
# run.sh — run all Cache Patterns Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Cache Patterns Lab ==="
echo ""

echo "--- 1. LRU Eviction ---"
python3 "$REPO_ROOT/scripts/caching/lru_cache_example.py"
echo ""

echo "--- 2. TTL Expiration ---"
python3 "$REPO_ROOT/scripts/caching/ttl_cache_example.py"
echo ""

echo "--- 3. Write Strategies ---"
python3 "$REPO_ROOT/scripts/caching/cache_strategies_example.py"
echo ""

echo "=== All demos complete ==="
