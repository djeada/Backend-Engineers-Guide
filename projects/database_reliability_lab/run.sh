#!/usr/bin/env bash
# run.sh — run all Database Reliability Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Database Reliability Lab ==="
echo ""

echo "--- 1. Transactions ---"
python3 "$REPO_ROOT/scripts/databases/transaction_example.py"
echo ""

echo "--- 2. Schema Migrations ---"
python3 "$REPO_ROOT/scripts/databases/migration_example.py"
echo ""

echo "--- 3. Index Performance ---"
python3 "$REPO_ROOT/scripts/databases/index_example.py"
echo ""

echo "--- 4. Connection Pooling ---"
python3 "$REPO_ROOT/scripts/databases/connection_pool_example.py"
echo ""

echo "=== All demos complete ==="
