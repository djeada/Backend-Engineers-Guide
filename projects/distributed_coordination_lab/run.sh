#!/usr/bin/env bash
# run.sh — run all Distributed Coordination Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Distributed Coordination Lab ==="
echo ""

echo "--- 1. Leader Election ---"
python3 "$REPO_ROOT/scripts/distributed_systems/leader_election_example.py"
echo ""

echo "--- 2. Vector Clocks ---"
python3 "$REPO_ROOT/scripts/distributed_systems/vector_clock_example.py"
echo ""

echo "--- 3. Quorum Overlap ---"
python3 "$REPO_ROOT/scripts/distributed_systems/quorum_example.py"
echo ""

echo "--- 4. Consistent Hashing ---"
python3 "$REPO_ROOT/scripts/distributed_systems/consistent_hashing_example.py"
echo ""

echo "=== All demos complete ==="
