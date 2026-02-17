#!/bin/bash
# Compare generated DOT against golden .dot files.

set -e

NR_DIR=tests/non-regression
fail=0

for dfd in "$NR_DIR"/*.dfd; do
    dot="${dfd%.dfd}.dot"
    [ -f "$dot" ] || continue
    tmp="${dfd%.dfd}.tmp"
    ./data-flow-diagram "$dfd" -f dot -o "$tmp"
    if diff -u "$dot" "$tmp" > /dev/null 2>&1; then
        echo "  PASS: $dfd"
    else
        echo "  FAIL: $dfd"
        diff -u "$dot" "$tmp" || true
        fail=1
    fi
    rm -f "$tmp"
done

[ $fail -eq 0 ] || { echo "Non-regression test(s) FAILED"; exit 1; }
