#!/usr/bin/env bash
# tail-logs.sh — stream all service logs in one terminal
# Useful for debugging startup issues or watching the full system.

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

touch \
  "${LOG_DIR}/metricgen.log" \
  "${LOG_DIR}/webhook-receiver.log" \
  "${LOG_DIR}/prometheus.log" \
  "${LOG_DIR}/grafana.log"

tail -n 50 -f \
  "${LOG_DIR}/metricgen.log" \
  "${LOG_DIR}/webhook-receiver.log" \
  "${LOG_DIR}/prometheus.log" \
  "${LOG_DIR}/grafana.log"
