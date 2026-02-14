#!/usr/bin/env bash

# Rolling restart simulation for a backend service fleet.
# Usage:
#   bash rolling_restart_example.sh

set -euo pipefail

instances=("api-1" "api-2" "api-3")

echo "Starting rolling restart..."
echo

for instance in "${instances[@]}"; do
  echo "Draining traffic from ${instance}"
  sleep 0.2
  echo "Restarting ${instance}"
  sleep 0.2
  echo "Waiting for ${instance} to pass health checks"
  sleep 0.2
  echo "${instance} is healthy and back in rotation"
  echo
done

echo "Rolling restart completed with zero-downtime sequencing."
