#!/usr/bin/env bash

# Tiny NGINX access-log parsing demonstration.
# Usage:
#   bash nginx_log_parse_example.sh

set -euo pipefail

log_lines=(
  '127.0.0.1 - - [14/Feb/2026:16:00:00 +0000] "GET /health HTTP/1.1" 200 12'
  '127.0.0.1 - - [14/Feb/2026:16:00:01 +0000] "GET /api/users HTTP/1.1" 200 120'
  '127.0.0.1 - - [14/Feb/2026:16:00:02 +0000] "GET /api/users HTTP/1.1" 500 42'
)

total=${#log_lines[@]}
errors=0
for line in "${log_lines[@]}"; do
  status=$(awk '{print $(NF-1)}' <<< "${line}")
  if [[ "${status}" == "500" ]]; then
    errors=$((errors + 1))
  fi
done

echo "Total requests: ${total}"
echo "5xx responses: ${errors}"
echo "Key takeaway: log parsing helps detect error spikes quickly."
