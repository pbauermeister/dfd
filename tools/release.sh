#!/bin/bash
#
# Release the next version. semantic-release derives it from the
# conventional commits since the last tag and makes the release commit
# (version in pyproject.toml and uv.lock, CHANGES.md entry) and the tag
# locally; both are shown and confirmed before the push. The tag push
# triggers the release workflow (.github/workflows/release.yml), which
# runs CI, rehearses on TestPyPI, publishes to PyPI and creates the
# GitHub release. See doc/RELEASING.md.

. ./init-tracing.sh

WORKFLOW=release.yml

step "check the checkout is main, clean and equal to origin/main"
[ "$(git branch --show-current)" = main ] \
    || { echo "ERROR: releases are made from main"; exit 1; }
[ -z "$(git status --porcelain)" ] \
    || { echo "ERROR: working tree is not clean"; exit 1; }
git fetch origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
    || { echo "ERROR: local main differs from origin/main"; exit 1; }

step "show the release plan"
uv run ./tools/print-release-plan.py

step "make the release commit and the tag, locally"
# the release commit is authored by the operator, not by the tool
export GIT_COMMIT_AUTHOR="$(git config user.name) <$(git config user.email)>"
uv run semantic-release version --no-push --no-vcs-release
NEXT=$(uv run ./tools/changelog.py print-version)
git --no-pager show --stat HEAD
echo
uv run ./tools/changelog.py print-notes
echo

step "confirm"
read -r -p "Push main and v$NEXT to origin, releasing $NEXT? [y/N] " ANSWER
if [ "$ANSWER" != y ]; then
    git tag -d "v$NEXT"
    git reset --hard origin/main
    echo "Aborted: local release commit and tag removed"
    exit 1
fi

step "push main and the tag"
git push origin main "v$NEXT"

step "watch the run"
RUN_ID=$(./tools/wait-for.sh workflow-run "$WORKFLOW" "v$NEXT")
gh run watch "$RUN_ID" --exit-status
