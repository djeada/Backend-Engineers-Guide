#!/usr/bin/env bash

# Pagination token/offset walkthrough.
# Usage:
#   bash pagination_example.sh

set -euo pipefail

records=(u1 u2 u3 u4 u5 u6 u7)
page_size=3
offset=0
page=1

while (( offset < ${#records[@]} )); do
  echo "Page ${page} (offset=${offset}, limit=${page_size})"
  for ((i = offset; i < offset + page_size && i < ${#records[@]}; i++)); do
    echo "  ${records[i]}"
  done
  echo
  offset=$((offset + page_size))
  page=$((page + 1))
done

echo "Key takeaway: pagination prevents large responses."
