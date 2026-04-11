#!/usr/bin/env bash
# install.sh — download Grafana + Prometheus, set up Python virtualenv
# Run this once before start.sh. Safe to re-run (skips cached downloads).

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cmd curl
require_cmd tar
require_cmd python3

download_if_missing() {
  local url="$1"
  local archive="$2"

  if [[ ! -f "${DOWNLOAD_DIR}/${archive}" ]]; then
    log "downloading ${archive}"
    curl -fL "${url}" -o "${DOWNLOAD_DIR}/${archive}"
  else
    log "using cached archive ${archive}"
  fi
}

extract_if_missing() {
  local archive="$1"
  local dest_dir="$2"
  local extracted_name="$3"

  if [[ ! -d "${dest_dir}" ]]; then
    log "extracting ${archive}"
    tar -xzf "${DOWNLOAD_DIR}/${archive}" -C "${BIN_DIR}"
    mv "${BIN_DIR}/${extracted_name}" "${dest_dir}"
  else
    log "using existing directory ${dest_dir}"
  fi
}

download_if_missing \
  "https://dl.grafana.com/oss/release/${GRAFANA_ARCHIVE}" \
  "${GRAFANA_ARCHIVE}"

download_if_missing \
  "https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/${PROMETHEUS_ARCHIVE}" \
  "${PROMETHEUS_ARCHIVE}"

extract_if_missing \
  "${GRAFANA_ARCHIVE}" \
  "${GRAFANA_HOME}" \
  "grafana-v${GRAFANA_VERSION}"

extract_if_missing \
  "${PROMETHEUS_ARCHIVE}" \
  "${PROMETHEUS_HOME}" \
  "prometheus-${PROMETHEUS_VERSION}.linux-amd64"

if [[ ! -d "${VENV_DIR}" ]]; then
  log "creating python virtualenv"
  python3 -m venv "${VENV_DIR}"
fi

log "installing python dependencies"
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${ROOT_DIR}/metricgen/requirements.txt"

mkdir -p \
  "${DATA_DIR}/grafana" \
  "${DATA_DIR}/prometheus" \
  "${LOG_DIR}" \
  "${PID_DIR}" \
  "${ROOT_DIR}/grafana/provisioning/plugins" \
  "${ROOT_DIR}/grafana/provisioning/notifiers"

log "installation complete"
