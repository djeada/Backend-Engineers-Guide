#!/usr/bin/env bash

# Cache warming simulation.
# Usage:
#   bash cache_warming_example.sh

set -euo pipefail

hot_keys=("homepage" "pricing" "dashboard")

echo "Warming cache with expected hot keys..."
for key in "${hot_keys[@]}"; do
  echo "  priming ${key}"
done

echo "Warm-up complete. First user requests avoid cold misses."
