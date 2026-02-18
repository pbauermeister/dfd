#!/bin/bash
# Compare generated DOT against golden .dot files.

set -e

NR_DIR=tests/non-regression
fail=0

# Test .dfd files
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

# Test .md files with fenced code blocks
for md in "$NR_DIR"/*.md; do
    [ -f "$md" ] || continue
    subdir="${md%.md}"
    tmp_md="${md%.md}.tmp.md"

    # Rewrite fence output paths: .dot -> .tmp
    sed 's/\.dot$/.tmp/g' "$md" > "$tmp_md"
    ./data-flow-diagram --markdown -f dot "$tmp_md"
    for dot in "$subdir"/*.dot; do
        tmp="${dot%.dot}.tmp"
        [ -f "$tmp" ] || continue
        if diff -u "$dot" "$tmp" > /dev/null 2>&1; then
            echo "  PASS: $dot"
        else
            echo "  FAIL: $dot"
            diff -u "$dot" "$tmp" || true
            fail=1
        fi
        rm -f "$tmp"
    done
    rm -f "$tmp_md"
done

# Final result
[ $fail -eq 0 ] || { echo "Non-regression test(s) FAILED"; exit 1; }
