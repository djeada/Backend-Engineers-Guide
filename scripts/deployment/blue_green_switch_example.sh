#!/usr/bin/env bash

# Blue/green traffic switch simulation.
# Usage:
#   bash blue_green_switch_example.sh

set -euo pipefail

current="blue"
next="green"

echo "Current production: ${current}"
echo "Deploying ${next} environment..."
echo "Running health checks on ${next}..."
echo "Switching load balancer traffic to ${next}"
echo "Keeping ${current} for quick rollback"
echo "Key takeaway: blue/green reduces deployment risk."
