#!/bin/bash
#
# Release the next version. semantic-release derives it from the
# conventional commits since the last tag and makes the release commit
# (version in pyproject.toml, CHANGES.md entry) and the tag locally;
# both are shown and confirmed before the push. The tag push triggers
# the release workflow (.github/workflows/release.yml), which runs CI,
# rehearses on TestPyPI, publishes to PyPI and creates the GitHub
# release. See doc/RELEASING.md.

. ./set-ex.sh

WORKFLOW=release.yml
RETRIES=12  # The run appears a few seconds after the push.
DELAY=5

step "check the checkout is main, clean and equal to origin/main"
[ "$(git branch --show-current)" = main ] \
    || { echo "ERROR: releases are made from main"; exit 1; }
[ -z "$(git status --porcelain)" ] \
    || { echo "ERROR: working tree is not clean"; exit 1; }
git fetch origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
    || { echo "ERROR: local main differs from origin/main"; exit 1; }

step "compute the next version"
CURRENT=$(uv run ./tools/changelog.py version)
NEXT=$(uv run semantic-release --noop version --print 2>/dev/null)
[ "$NEXT" != "$CURRENT" ] \
    || { echo "ERROR: nothing to release since v$CURRENT"; exit 1; }

step "list the commits since v$CURRENT with their levels"
# A lower level before a higher one means the merge gate was bypassed:
# warn, the operator decides at the confirmation.
rank() {
    case "$1" in
        patch) echo 1;; minor) echo 2;; major) echo 3;; *) echo 0;;
    esac
}
MAX=0
WARN=
for SHA in $(git rev-list --reverse "v$CURRENT..HEAD"); do
    LEVEL=$(git log -1 --format=%B "$SHA" \
            | uv run ./tools/conventional-commits.py level 2>/dev/null \
            || printf none)
    R=$(rank "$LEVEL")
    if [ "$R" -gt "$MAX" ]; then
        [ "$MAX" -eq 0 ] || WARN=1
        MAX=$R
    fi
    echo "  $(git log -1 --format='%h %s' "$SHA")  [$LEVEL]"
done
[ -z "$WARN" ] || echo "WARNING: a lower level precedes a higher one: v$NEXT closes both"

step "make the release commit and the tag v$NEXT, locally"
uv run semantic-release version --no-push --no-vcs-release
git --no-pager show --stat HEAD
echo
uv run ./tools/changelog.py notes
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
for i in $(seq "$RETRIES"); do
    RUN_ID=$(gh run list --workflow "$WORKFLOW" --branch "v$NEXT" --limit 1 \
             --json databaseId,status \
             -q '.[] | select(.status != "completed") | .databaseId')
    [ -n "$RUN_ID" ] && break
    sleep "$DELAY"
done
[ -n "$RUN_ID" ] || { echo "ERROR: no run found after the push"; exit 1; }
gh run watch "$RUN_ID" --exit-status
