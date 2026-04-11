#!/usr/bin/env bash
# start.sh — launch all four services and verify they're healthy
# Services: metricgen → prometheus → grafana, plus webhook-receiver
# Check status anytime with: ./scripts/status.sh

set -euo pipefail
  printf 'Grafana is not installed. Run ./scripts/install.sh first.\n' >&2
  exit 1
fi

if [[ ! -x "${PROMETHEUS_HOME}/prometheus" ]]; then
  printf 'Prometheus is not installed. Run ./scripts/install.sh first.\n' >&2
  exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  printf 'Python virtualenv is missing. Run ./scripts/install.sh first.\n' >&2
  exit 1
fi

mkdir -p \
  "${DATA_DIR}/grafana" \
  "${DATA_DIR}/prometheus" \
  "${LOG_DIR}" \
  "${PID_DIR}" \
  "${ROOT_DIR}/grafana/provisioning/plugins" \
  "${ROOT_DIR}/grafana/provisioning/notifiers"

start_background \
  "metricgen" \
  "${VENV_DIR}/bin/python" "${ROOT_DIR}/metricgen/app.py" \
  --host "${HOST}" \
  --port "${METRICGEN_PORT}"

start_background \
  "webhook-receiver" \
  "${VENV_DIR}/bin/python" "${ROOT_DIR}/webhook_receiver/app.py" \
  --host "${HOST}" \
  --port "${WEBHOOK_PORT}"

start_background \
  "prometheus" \
  "${PROMETHEUS_HOME}/prometheus" \
  --config.file="${ROOT_DIR}/prometheus/prometheus.yml" \
  --storage.tsdb.path="${DATA_DIR}/prometheus" \
  --web.listen-address="${HOST}:${PROMETHEUS_PORT}"

start_background \
  "grafana" \
  env \
  GF_SECURITY_ADMIN_USER=admin \
  GF_SECURITY_ADMIN_PASSWORD=admin \
  GF_PATHS_DATA="${DATA_DIR}/grafana" \
  GF_PATHS_LOGS="${LOG_DIR}/grafana-internal" \
  GF_PATHS_PROVISIONING="${ROOT_DIR}/grafana/provisioning" \
  GF_SERVER_HTTP_ADDR="${HOST}" \
  GF_SERVER_HTTP_PORT="${GRAFANA_PORT}" \
  "${GRAFANA_HOME}/bin/grafana" server \
  --homepath "${GRAFANA_HOME}"

wait_for_http "http://${HOST}:${METRICGEN_PORT}/" 20 1 || {
  printf 'metric generator did not start successfully\n' >&2
  exit 1
}

wait_for_http "http://${HOST}:${WEBHOOK_PORT}/health" 20 1 || {
  printf 'webhook receiver did not start successfully\n' >&2
  exit 1
}

wait_for_http "http://${HOST}:${PROMETHEUS_PORT}/-/ready" 30 1 || {
  printf 'prometheus did not start successfully\n' >&2
  exit 1
}

wait_for_http "http://${HOST}:${GRAFANA_PORT}/api/health" 60 1 || {
  printf 'grafana did not start successfully\n' >&2
  exit 1
}

curl -fsS \
  "http://${HOST}:${METRICGEN_PORT}/set?env=uat&service=checkout&dependency_group=payments&parent=0&child=0" \
  >/dev/null

curl -fsS \
  "http://${HOST}:${METRICGEN_PORT}/set?env=prod&service=checkout&dependency_group=payments&parent=0&child=0" \
  >/dev/null

log "all services are up"
