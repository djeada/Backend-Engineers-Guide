#!/usr/bin/env bash
# reset-alerts.sh — set all metrics back to 0 (healthy state)
# After resetting, active alerts will resolve within ~30 seconds.

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

curl -fsS \
  "http://${HOST}:${METRICGEN_PORT}/set?env=uat&service=checkout&dependency_group=payments&parent=0&child=0"
printf '\n'
curl -fsS \
  "http://${HOST}:${METRICGEN_PORT}/set?env=prod&service=checkout&dependency_group=payments&parent=0&child=0"
printf '\n'
