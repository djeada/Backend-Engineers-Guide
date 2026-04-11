#!/usr/bin/env bash
# run.sh — run all Deployment Rollout Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Deployment Rollout Lab ==="
echo ""

echo "--- 1. Rolling Deployment ---"
python3 "$REPO_ROOT/scripts/deployment/rolling_deploy_example.py"
echo ""

echo "--- 2. Canary Deployment ---"
python3 "$REPO_ROOT/scripts/deployment/canary_deploy_example.py"
echo ""

echo "--- 3. Health Checks ---"
python3 "$REPO_ROOT/scripts/deployment/health_check_example.py"
echo ""

echo "=== All demos complete ==="
