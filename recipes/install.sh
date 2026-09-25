#!/bin/bash
#
# Install the working tree user-wide as a uv tool, its version a
# stamp of the branch and the revision (tools/print-dev-version.py,
# `0+<branch>.git<hash>[.dirty]`), so that `data-flow-diagram
# --version` tells a development install from any release. The tree is copied to a scratch directory
# (tracked and untracked files, .gitignore respected) and the version
# rewritten there: the checkout is never touched, the release path
# keeps the bare version. `uv tool upgrade` cannot follow a removed
# scratch copy: run `make install` again instead.

. ./tools/init-tracing.sh

VERSION=$(uv run ./tools/changelog.py print-version)
DEV_VERSION=$(uv run ./tools/print-dev-version.py)
SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT

step "copy the tree to $SCRATCH"
git ls-files -z --cached --others --exclude-standard \
    | tar --null --files-from - --ignore-failed-read -cf - \
    | tar -C "$SCRATCH" -xf -

step "stamp the copy: $VERSION -> $DEV_VERSION"
sed -i "s|^version = \"$VERSION\"$|version = \"$DEV_VERSION\"|" "$SCRATCH/pyproject.toml"
grep -q "^version = \"$DEV_VERSION\"$" "$SCRATCH/pyproject.toml" \
    || { echo "ERROR: version line not rewritten in pyproject.toml"; exit 1; }

step "install the copy as a uv tool"
uv tool install --reinstall "$SCRATCH"
data-flow-diagram --version
