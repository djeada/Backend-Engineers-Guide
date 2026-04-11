#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

show_service() {
  local name="$1"
  local url="$2"
  local reachable="false"

  if curl -fsS "${url}" >/dev/null 2>&1; then
    reachable="true"
  fi

  if is_running "${name}" || [[ "${reachable}" == "true" ]]; then
    printf '%-18s running  ' "${name}"
  else
    printf '%-18s stopped  ' "${name}"
  fi

  if [[ "${reachable}" == "true" ]]; then
    printf 'http ok  %s\n' "${url}"
  else
    printf 'http down %s\n' "${url}"
  fi
}

show_service "metricgen" "http://${HOST}:${METRICGEN_PORT}/"
show_service "webhook-receiver" "http://${HOST}:${WEBHOOK_PORT}/health"
show_service "prometheus" "http://${HOST}:${PROMETHEUS_PORT}/-/ready"
show_service "grafana" "http://${HOST}:${GRAFANA_PORT}/api/health"
