#!/usr/bin/env bash
# run.sh — run all Network Resilience Lab demos in sequence
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Network Resilience Lab ==="
echo ""

echo "--- 1. TCP vs UDP ---"
python3 "$REPO_ROOT/scripts/network_communications/tcp_udp_example.py"
echo ""

echo "--- 2. HTTP Request/Response ---"
python3 "$REPO_ROOT/scripts/network_communications/http_request_example.py"
echo ""

echo "--- 3. DNS Resolution ---"
python3 "$REPO_ROOT/scripts/network_communications/dns_resolver_example.py"
echo ""

echo "--- 4. Circuit Breaker ---"
python3 "$REPO_ROOT/scripts/network_communications/circuit_breaker_example.py"
echo ""

echo "=== All demos complete ==="
