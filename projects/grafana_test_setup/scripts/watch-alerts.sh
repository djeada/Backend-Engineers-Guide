#!/usr/bin/env bash
# watch-alerts.sh — live-stream webhook notifications
# Shows the alert payloads Grafana sends when alerts fire or resolve.
# This is the best way to verify suppression behavior in real time.

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

touch "${LOG_DIR}/webhook-receiver.log"

tail -n 50 -f "${LOG_DIR}/webhook-receiver.log"
