#!/bin/bash
#
# Release the version in CHANGES.md: dispatch the release workflow
# (.github/workflows/release.yml) on main and watch it. The workflow
# runs CI, rehearses on TestPyPI, publishes to PyPI and creates the
# GitHub release and tag. See doc/RELEASING.md.

. ./set-ex.sh

WORKFLOW=release.yml
RETRIES=12  # The run appears a few seconds after the dispatch.
DELAY=5

step "check the checkout is main, clean and pushed"
[ "$(git branch --show-current)" = main ] \
    || { echo "ERROR: releases are made from main"; exit 1; }
[ -z "$(git status --porcelain)" ] \
    || { echo "ERROR: working tree is not clean"; exit 1; }
git fetch origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
    || { echo "ERROR: local main differs from origin/main"; exit 1; }

step "dispatch $WORKFLOW on main"
gh workflow run "$WORKFLOW" --ref main

step "watch the run"
for i in $(seq "$RETRIES"); do
    RUN_ID=$(gh run list --workflow "$WORKFLOW" --branch main --limit 1 \
             --json databaseId,status \
             -q '.[] | select(.status != "completed") | .databaseId')
    [ -n "$RUN_ID" ] && break
    sleep "$DELAY"
done
[ -n "$RUN_ID" ] || { echo "ERROR: no run found after dispatch"; exit 1; }
gh run watch "$RUN_ID" --exit-status
