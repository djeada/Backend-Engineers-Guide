#!/usr/bin/env bash
# run.sh — run all Reverse Proxy Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Reverse Proxy Lab ==="
echo ""

echo "--- 1. Reverse Proxy Routing ---"
python3 "$REPO_ROOT/scripts/server_technologies/reverse_proxy_example.py"
echo ""

echo "--- 2. Load Balancing Strategies ---"
python3 "$REPO_ROOT/scripts/server_technologies/load_balancer_example.py"
echo ""

echo "=== All demos complete ==="
