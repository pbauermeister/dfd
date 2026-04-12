#!/usr/bin/env bash
#
# Regenerate auto-updatable sections of README.md.
#
# Each section is demarcated by HTML comment markers:
#   <!-- AUTO:section-name -->
#   ...generated content...
#   <!-- /AUTO:section-name -->
#
# The script replaces everything between the markers.
# Hand-edited content outside markers is never touched.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
README="$ROOT_DIR/README.md"

# ── section generators ───────────────────────────────────────────────

generate_cli_help() {
    # activate venv if present, so the local entry point works
    if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source "$ROOT_DIR/.venv/bin/activate"
    fi

    echo '````'
    "$ROOT_DIR/data-flow-diagram" --help 2>&1
    echo '````'
}

generate_doc_toc() {
    # extract level-2 headings from doc/README.md and build a linked list
    local doc="$ROOT_DIR/doc/README.md"
    grep -n '^## ' "$doc" | while IFS=: read -r _ line; do
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

# ── generic marker replacement ───────────────────────────────────────

replace_section() {
    local section_name="$1"
    local new_content="$2"
    local file="$README"

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
}

# ── main ─────────────────────────────────────────────────────────────

echo "Updating README.md auto-generated sections..."

cli_help=$(generate_cli_help)
replace_section "cli-help" "$cli_help"
echo "  - cli-help: done"

doc_toc=$(generate_doc_toc)
replace_section "doc-toc" "$doc_toc"
echo "  - doc-toc: done"

echo "README.md updated."
