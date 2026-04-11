#!/usr/bin/env bash
# run.sh — run the Request Pipeline Lab demo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Request Pipeline Lab ==="
echo ""

echo "--- Middleware Chain ---"
python3 "$REPO_ROOT/scripts/server_technologies/middleware_chain_example.py"
echo ""

echo "=== All demos complete ==="
