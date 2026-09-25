#!/bin/bash
#
# Install the working tree user-wide as a uv tool, its version a
# stamp of the branch and the revision (tools/print-dev-version.py,
# `0+<branch>.git<hash>[.dirty]`), so that `data-flow-diagram
# --version` tells a development install from any release. The tree
# is staged in a scratch directory (tools/stage-dev-tree.sh): the
# checkout is never touched, the release path keeps the bare version.
# `uv tool upgrade` cannot follow a removed scratch copy: run `make
# install` again instead.

. ./tools/init-tracing.sh

SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT

step "stage the tree"
./tools/stage-dev-tree.sh "$SCRATCH"

step "install the copy as a uv tool"
uv tool install --reinstall "$SCRATCH"
data-flow-diagram --version
