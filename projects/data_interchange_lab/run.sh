#!/usr/bin/env bash
# run.sh — run all Data Interchange Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Data Interchange Lab ==="
echo ""

echo "--- 1. Format Conversion (JSON / XML / YAML) ---"
python3 "$REPO_ROOT/scripts/data_formats/format_conversion.py"
echo ""

echo "--- 2. Binary Serialization (Protocol Buffers) ---"
python3 "$REPO_ROOT/scripts/data_formats/protocol_buffer_example.py"
echo ""

echo "=== All demos complete ==="
