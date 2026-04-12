#!/usr/bin/env bash
# run.sh — run all API Reliability Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== API Reliability Lab ==="
echo ""

echo "--- 1. API Versioning ---"
python3 "$REPO_ROOT/scripts/api_design/versioning_example.py"
echo ""

echo "--- 2. Idempotency Keys ---"
python3 "$REPO_ROOT/scripts/api_design/idempotency_example.py"
echo ""

echo "--- 3. Webhook Signatures ---"
python3 "$REPO_ROOT/scripts/api_design/webhook_signature_example.py"
echo ""

echo "=== All demos complete ==="
