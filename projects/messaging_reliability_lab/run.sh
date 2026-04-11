#!/usr/bin/env bash
# run.sh — run all Messaging Reliability Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Messaging Reliability Lab ==="
echo ""

echo "--- 1. Pub/Sub ---"
python3 "$REPO_ROOT/scripts/data_processing/pub_sub_example.py"
echo ""

echo "--- 2. Batch Processing ---"
python3 "$REPO_ROOT/scripts/data_processing/batch_processing_example.py"
echo ""

echo "--- 3. Stream Processing ---"
python3 "$REPO_ROOT/scripts/data_processing/stream_processing_example.py"
echo ""

echo "--- 4. Dead-Letter Queue ---"
python3 "$REPO_ROOT/scripts/data_processing/dead_letter_queue_example.py"
echo ""

echo "=== All demos complete ==="
