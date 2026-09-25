#!/bin/bash
#
# Copy the working tree into a directory and stamp its version.
#
# Usage:
#   ./tools/stage-dev-tree.sh DEST   # DEST exists and is empty
#
# Tracked and untracked files go, .gitignore respected, deleted files
# skipped: the tree as it is, not the last commit. The version line of
# the copy's pyproject.toml becomes the stamp of print-dev-version.py;
# the checkout is never touched. Run from the repository root.

set -e -u -o pipefail

DEST=${1:?usage: $0 DEST}
[ -d "$DEST" ] || { echo "ERROR: $DEST is not a directory"; exit 1; }

VERSION=$(uv run ./tools/changelog.py print-version)
STAMP=$(uv run ./tools/print-dev-version.py)

echo "--- Stage the tree in $DEST ---"

echo "-- copy"
git ls-files -z --cached --others --exclude-standard \
    | tar --null --files-from - --ignore-failed-read -cf - \
    | tar -C "$DEST" -xf -

echo "-- stamp: $VERSION -> $STAMP"
sed -i "s|^version = \"$VERSION\"$|version = \"$STAMP\"|" "$DEST/pyproject.toml"
grep -q "^version = \"$STAMP\"$" "$DEST/pyproject.toml" \
    || { echo "ERROR: version line not rewritten in pyproject.toml"; exit 1; }
