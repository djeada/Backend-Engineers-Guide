#!/usr/bin/env bash

# API key rotation sequence demonstration.
# Usage:
#   bash api_key_rotation_example.sh

set -euo pipefail

old_key="key_v1_old"
new_key="key_v2_new"

echo "Step 1: Create new key: ${new_key}"
echo "Step 2: Deploy service accepting both ${old_key} and ${new_key}"
echo "Step 3: Update clients to use ${new_key}"
echo "Step 4: Revoke ${old_key} after migration window"
echo "Key takeaway: overlap old/new keys to avoid downtime."
