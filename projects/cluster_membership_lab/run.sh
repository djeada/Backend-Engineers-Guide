#!/usr/bin/env bash
# run.sh — run the Cluster Membership Lab demo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Cluster Membership Lab ==="
echo ""

echo "--- Gossip Protocol ---"
python3 "$REPO_ROOT/scripts/distributed_systems/gossip_protocol_example.py"
echo ""

echo "=== All demos complete ==="
