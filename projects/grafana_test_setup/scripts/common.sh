#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# common.sh — shared variables and helper functions for all scripts
#
# This file is "sourced" (not executed directly) by every other script.
# It sets up paths, ports, and reusable functions for process management.
# ─────────────────────────────────────────────────────────────────────

# Safety flags:
#   -e  Exit immediately if any command fails
#   -u  Treat unset variables as errors (catches typos)
#   -o pipefail  A pipeline fails if ANY command in it fails (not just the last)
set -euo pipefail

# ── Directory layout ─────────────────────────────────────────────────
# Resolve the project root relative to this script's location.
# BASH_SOURCE[0] is the path to THIS file, even when sourced from another script.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${ROOT_DIR}/runtime"       # Generated data (not checked into git)
BIN_DIR="${ROOT_DIR}/bin"               # Downloaded Grafana and Prometheus binaries
DOWNLOAD_DIR="${RUNTIME_DIR}/downloads" # Cached tar.gz archives
PID_DIR="${RUNTIME_DIR}/pids"           # PID files for background processes
LOG_DIR="${RUNTIME_DIR}/logs"           # Log files for all services
DATA_DIR="${RUNTIME_DIR}/data"          # Prometheus TSDB and Grafana data

# ── Network configuration ────────────────────────────────────────────
# All ports are configurable via environment variables.
HOST="${HOST:-127.0.0.1}"
GRAFANA_PORT="${GRAFANA_PORT:-3000}"
PROMETHEUS_PORT="${PROMETHEUS_PORT:-9090}"
METRICGEN_PORT="${METRICGEN_PORT:-8000}"
WEBHOOK_PORT="${WEBHOOK_PORT:-8080}"

# ── Version pinning ──────────────────────────────────────────────────
GRAFANA_VERSION="${GRAFANA_VERSION:-10.4.3}"
PROMETHEUS_VERSION="${PROMETHEUS_VERSION:-2.52.0}"

GRAFANA_ARCHIVE="grafana-${GRAFANA_VERSION}.linux-amd64.tar.gz"
PROMETHEUS_ARCHIVE="prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz"

GRAFANA_HOME="${BIN_DIR}/grafana-${GRAFANA_VERSION}"
PROMETHEUS_HOME="${BIN_DIR}/prometheus-${PROMETHEUS_VERSION}"
VENV_DIR="${RUNTIME_DIR}/venv"

# Create directories on source (idempotent)
mkdir -p "${RUNTIME_DIR}" "${BIN_DIR}" "${DOWNLOAD_DIR}" "${PID_DIR}" "${LOG_DIR}" "${DATA_DIR}"

# ── Helper functions ─────────────────────────────────────────────────

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "${cmd}" >&2
    exit 1
  fi
}

# PID file helpers — each background service writes its process ID to a file.
# This lets stop.sh and status.sh find and manage them later.
pid_file() {
  printf '%s/%s.pid' "${PID_DIR}" "$1"
}

is_running() {
  local name="$1"
  local file
  file="$(pid_file "${name}")"

  if [[ ! -f "${file}" ]]; then
    return 1
  fi

  local pid
  pid="$(<"${file}")"
  # "kill -0" doesn't actually send a signal — it just checks if the process exists
  kill -0 "${pid}" >/dev/null 2>&1
}

# Poll an HTTP endpoint until it responds (used to wait for services to start)
wait_for_http() {
  local url="$1"
  local retries="${2:-30}"
  local delay="${3:-1}"
  local attempt=1

  while (( attempt <= retries )); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep "${delay}"
    ((attempt++))
  done

  return 1
}

# Start a process in the background with nohup.
# nohup prevents the process from dying when the terminal closes.
# Output is appended to a log file for later inspection.
start_background() {
  local name="$1"
  shift

  local logfile="${LOG_DIR}/${name}.log"
  local pidfile
  pidfile="$(pid_file "${name}")"

  if is_running "${name}"; then
    log "${name} is already running"
    return 0
  fi

  nohup "$@" >>"${logfile}" 2>&1 &
  echo "$!" >"${pidfile}"
  log "started ${name} (pid $(<"${pidfile}"))"
}

# Gracefully stop a background process (SIGTERM first, then SIGKILL after timeout)
stop_background() {
  local name="$1"
  local pidfile
  pidfile="$(pid_file "${name}")"

  if [[ ! -f "${pidfile}" ]]; then
    log "${name} is not running"
    return 0
  fi

  local pid
  pid="$(<"${pidfile}")"

  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill "${pid}"
    for _ in $(seq 1 20); do
      if ! kill -0 "${pid}" >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done
    # Force-kill if graceful shutdown didn't work within 20 seconds
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
  fi

  rm -f "${pidfile}"
  log "stopped ${name}"
}
