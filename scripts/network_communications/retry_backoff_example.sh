#!/usr/bin/env bash

# Exponential-backoff retry simulation for outbound HTTP calls.
# Usage:
#   bash retry_backoff_example.sh

set -euo pipefail

attempt=0
max_attempts=5

simulate_request() {
  # Fail the first two attempts, then succeed.
  if [[ $attempt -lt 3 ]]; then
    return 1
  fi
  return 0
}

echo "Starting request with retries..."
while (( attempt < max_attempts )); do
  attempt=$((attempt + 1))
  echo "Attempt ${attempt}/${max_attempts}"

  if simulate_request; then
    echo "Request succeeded."
    exit 0
  fi

  delay=$((2 ** (attempt - 1)))
  echo "Request failed, backing off for ${delay}s"
  sleep "${delay}"
done

echo "Request failed after ${max_attempts} attempts."
exit 1
