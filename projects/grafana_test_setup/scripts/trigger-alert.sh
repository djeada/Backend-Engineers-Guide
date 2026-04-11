#!/usr/bin/env bash
# trigger-alert.sh — simulate a failure by setting metric values
#
# WHAT THIS DOES:
#   Calls the metricgen /set endpoint to change Prometheus gauge values.
#   Within ~15 seconds Prometheus scrapes the new values, and within
#   ~30 seconds (the "for" duration) Grafana fires the alert.
#
# EXAMPLES:
#   # Both parent and child fail → only parent alert should notify
#   ./scripts/trigger-alert.sh --parent 1 --child 1
#
#   # Only child fails → child alert should notify
#   ./scripts/trigger-alert.sh --parent 0 --child 1

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

ENV_NAME="uat"
SERVICE="checkout"
DEPENDENCY_GROUP="payments"
PARENT="1"
CHILD="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="$2"
      shift 2
      ;;
    --service)
      SERVICE="$2"
      shift 2
      ;;
    --dependency-group)
      DEPENDENCY_GROUP="$2"
      shift 2
      ;;
    --parent)
      PARENT="$2"
      shift 2
      ;;
    --child)
      CHILD="$2"
      shift 2
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

curl -fsS \
  "http://${HOST}:${METRICGEN_PORT}/set?env=${ENV_NAME}&service=${SERVICE}&dependency_group=${DEPENDENCY_GROUP}&parent=${PARENT}&child=${CHILD}"
printf '\n'
