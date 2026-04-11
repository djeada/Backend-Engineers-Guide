#!/usr/bin/env bash
# run.sh — run all Security Controls Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Security Controls Lab ==="
echo ""

echo "--- 1. Password Hashing ---"
python3 "$REPO_ROOT/scripts/security/hashing_example.py"
echo ""

echo "--- 2. JWT Tokens ---"
python3 "$REPO_ROOT/scripts/security/jwt_example.py"
echo ""

echo "--- 3. Encryption ---"
python3 "$REPO_ROOT/scripts/security/encryption_example.py"
echo ""

echo "--- 4. Rate Limiting ---"
python3 "$REPO_ROOT/scripts/security/rate_limiter_example.py"
echo ""

echo "=== All demos complete ==="
