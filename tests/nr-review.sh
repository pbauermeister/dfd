#!/bin/bash
# Generate SVGs from NR test DFDs for visual inspection.

set -e

NR_DIR=tests/non-regression

for dfd in "$NR_DIR"/*.dfd; do
    case "$dfd" in *-err-*) continue ;; esac
    svg="${dfd%.dfd}.svg"
    echo "  $dfd -> $svg"
    ./data-flow-diagram "$dfd" -f svg -o "$svg"
done

# Error fixtures: show stderr output for inspection
for dfd in "$NR_DIR"/*-err-*.dfd; do
    [ -f "$dfd" ] || continue
    echo "  $dfd (error output):"
    ./data-flow-diagram "$dfd" -f dot 2>&1 || true
done

for md in "$NR_DIR"/*.md; do
    [ -f "$md" ] || continue
    tmp_md="${md%.md}.tmp.md"
    # Flatten subdir/file -> subdir--file and .dot -> .svg
    sed -e 's|\(tests/non-regression/[^/]*\)/|\1--|g' \
        -e 's/\.dot$/.svg/g' "$md" > "$tmp_md"
    echo "  $md (markdown)"
    ./data-flow-diagram --markdown -f svg "$tmp_md"
    rm -f "$tmp_md"
done
