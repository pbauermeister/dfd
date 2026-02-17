#!/bin/bash
# Generate SVGs from NR test DFDs for visual inspection.

set -e

NR_DIR=tests/non-regression

for dfd in "$NR_DIR"/*.dfd; do
    svg="${dfd%.dfd}.svg"
    echo "  $dfd -> $svg"
    ./data-flow-diagram "$dfd" -f svg -o "$svg"
done
