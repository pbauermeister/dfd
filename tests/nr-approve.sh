#!/bin/bash
# (Re)generate golden .dot files from NR test DFDs.

set -e

NR_DIR=tests/non-regression

for dfd in "$NR_DIR"/*.dfd; do
    dot="${dfd%.dfd}.dot"
    echo "  $dfd -> $dot"
    ./data-flow-diagram "$dfd" -f dot -o "$dot"
done

for md in "$NR_DIR"/*.md; do
    [ -f "$md" ] || continue
    subdir="${md%.md}"
    mkdir -p "$subdir"
    echo "  $md (markdown)"
    ./data-flow-diagram --markdown -f dot "$md"
done

echo
echo "WARNING: Any git change to $NR_DIR/*.dot files must be"
echo "carefully examined. Changed golden files are either deliberate"
echo "updates or an early sign of regression."
