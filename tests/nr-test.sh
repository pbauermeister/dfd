#!/bin/bash
# Compare generated DOT against golden .dot files.

set -e

NR_DIR=tests/non-regression
fail=0

# Test .dfd files (error fixtures have their own loop below). A render
# that fails is a FAIL line, not an abort of the run.
for dfd in "$NR_DIR"/*.dfd; do
    case "$dfd" in *-err-*) continue ;; esac
    dot="${dfd%.dfd}.dot"
    [ -f "$dot" ] || continue
    tmp="${dfd%.dfd}.tmp"
    if ! ./data-flow-diagram "$dfd" -f dot -o "$tmp" 2> "$tmp.stderr"; then
        echo "  FAIL: $dfd (render failed)"
        cat "$tmp.stderr"
        fail=1
        rm -f "$tmp" "$tmp.stderr"
        continue
    fi
    rm -f "$tmp.stderr"
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

# Test error fixtures (*-err-*.dfd -> .stderr). An error fixture has no
# golden .dot: one lying next to it is a leftover of a run where the
# fixture succeeded, and is reported. The DOT of the run goes to a
# scratch path and is deleted, so that this script leaves none.
for dfd in "$NR_DIR"/*-err-*.dfd; do
    [ -f "$dfd" ] || continue
    stderr="${dfd%.dfd}.stderr"
    stray="${dfd%.dfd}.dot"
    tmp="${dfd%.dfd}.tmp"
    tmp_stderr="${dfd%.dfd}.tmp.stderr"
    if [ -f "$stray" ]; then
        echo "  FAIL: $dfd (stray $stray: an error fixture has no golden .dot, remove it)"
        fail=1
    fi
    if ./data-flow-diagram "$dfd" -f dot -o "$tmp" 2> "$tmp_stderr"; then
        echo "  FAIL: $dfd (expected to fail but succeeded)"
        fail=1
    elif diff -u "$stderr" "$tmp_stderr" > /dev/null 2>&1; then
        echo "  PASS: $dfd"
    else
        echo "  FAIL: $dfd"
        diff -u "$stderr" "$tmp_stderr" || true
        fail=1
    fi
    rm -f "$tmp" "$tmp_stderr"
done

# Final result
[ $fail -eq 0 ] || { echo "Non-regression test(s) FAILED"; exit 1; }
