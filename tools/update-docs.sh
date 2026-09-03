#!/usr/bin/env bash
#
# Regenerate auto-updatable sections of README.md and doc/*.md.
#
# Each section is demarcated by HTML comment markers:
#   <!-- AUTO:section-name -->
#   ...generated content...
#   <!-- /AUTO:section-name -->
#
# The script replaces everything between the markers, then reformats the
# touched files with prettier so that editor auto-formatting (VSCode +
# prettier) produces no further diff. Hand-edited content outside markers
# is never touched.
#
# Environment: VENV (default .venv) locates prettier, installed there by
# `make require`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="${VENV:-$ROOT_DIR/.venv}"
README="$ROOT_DIR/README.md"
DOC_README="$ROOT_DIR/doc/README.md"
DOC_SYNTAX="$ROOT_DIR/doc/SYNTAX.md"

# ── section generators ───────────────────────────────────────────────

generate_cli_help() {
    # activate venv if present, so the local entry point works
    if [[ -f "$VENV/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source "$VENV/bin/activate"
    fi

    echo '````'
    "$ROOT_DIR/data-flow-diagram" --help 2>&1
    echo '````'
}

generate_doc_toc() {
    # extract level-2 headings from doc/README.md and build a linked list
    grep -n '^## ' "$DOC_README" | while IFS=: read -r _ line; do
        # strip the "## " prefix and any trailing whitespace
        title="${line#\#\# }"
        title="${title%"${title##*[![:space:]]}"}"
        # build a GitHub-compatible anchor
        anchor=$(echo "$title" \
            | tr '[:upper:]' '[:lower:]' \
            | sed 's/[^a-z0-9 _-]//g' \
            | tr ' ' '-')
        echo "- [$title](doc/README.md#$anchor)"
    done
}

generate_style_table() {
    # $1: readme|syntax
    "$SCRIPT_DIR/gen-style-tables.py" "$1"
}

# ── generic marker replacement ───────────────────────────────────────

replace_section() {
    local file="$1"
    local section_name="$2"
    local new_content="$3"

    local open_marker="<!-- AUTO:${section_name} -->"
    local close_marker="<!-- /AUTO:${section_name} -->"

    if ! grep -qF "$open_marker" "$file"; then
        echo "warning: marker $open_marker not found in $file — skipping" >&2
        return
    fi

    # build the replacement block (markers + blank line + content + blank line)
    local replacement
    replacement=$(printf '%s\n\n%s\n\n%s' "$open_marker" "$new_content" "$close_marker")

    # replace everything between (and including) the markers
    # use awk for reliable multi-line replacement
    awk -v open_m="$open_marker" -v close_m="$close_marker" -v repl="$replacement" '
        $0 == open_m { print repl; skip=1; next }
        $0 == close_m { skip=0; next }
        skip { next }
        { print }
    ' "$file" > "${file}.tmp"

    mv "${file}.tmp" "$file"
    echo "  - $(realpath --relative-to="$ROOT_DIR" "$file"): $section_name done"
}

# ── prettier ─────────────────────────────────────────────────────────

reformat() {
    local prettier="$VENV/node_modules/.bin/prettier"
    if [[ ! -x "$prettier" ]]; then
        echo "warning: $prettier not found (run 'make require') — skipping reformat" >&2
        return
    fi
    "$prettier" --log-level warn --write "$@"
    echo "  - prettier: done"
}

# ── main ─────────────────────────────────────────────────────────────

echo "Updating auto-generated sections..."

replace_section "$README" "cli-help" "$(generate_cli_help)"
replace_section "$README" "doc-toc" "$(generate_doc_toc)"
replace_section "$DOC_README" "style-table" "$(generate_style_table readme)"
replace_section "$DOC_SYNTAX" "style-table" "$(generate_style_table syntax)"

reformat "$README" "$DOC_README" "$DOC_SYNTAX"

echo "Done."
