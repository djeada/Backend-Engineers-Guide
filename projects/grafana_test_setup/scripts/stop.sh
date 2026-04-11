#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

stop_background grafana
stop_background prometheus
stop_background webhook-receiver
stop_background metricgen
