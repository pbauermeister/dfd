#!/bin/bash
#
# Wait for a condition, polling every DELAY seconds up to RETRIES times
# (WAIT_RETRIES and WAIT_DELAY override them).
#
# Usage:
#   ./tools/wait-for.sh workflow-run <workflow> <ref>   # prints the id of
#                                                       # the in-progress run
#   ./tools/wait-for.sh testpypi-version <version>      # the TestPyPI index
#                                                       # serves the version
#
# Each condition is a function taking the remaining arguments and
# succeeding when the condition holds. Progress goes to stderr.

set -e -o pipefail

RETRIES=${WAIT_RETRIES:-12}
DELAY=${WAIT_DELAY:-5}
PACKAGE=data-flow-diagram

workflow_run() {  # <workflow> <ref>
    local run_id
    run_id=$(gh run list --workflow "$1" --branch "$2" --limit 1 \
             --json databaseId,status \
             -q '.[] | select(.status != "completed") | .databaseId')
    [ -n "$run_id" ] && echo "$run_id"
}

testpypi_version() {  # <version>
    curl -s "https://test.pypi.org/simple/$PACKAGE/" \
        | grep -q "${PACKAGE//-/_}-$1[-.]"
}

CONDITION=${1:?usage: $0 workflow-run <workflow> <ref> | testpypi-version <version>}
shift
case "$CONDITION" in
    workflow-run)     CHECK=workflow_run ;;
    testpypi-version) CHECK=testpypi_version ;;
    *) echo "ERROR: unknown condition '$CONDITION'" >&2; exit 2 ;;
esac

for i in $(seq "$RETRIES"); do
    if $CHECK "$@"; then
        exit 0
    fi
    if [ "$i" -ge "$RETRIES" ]; then
        echo "ERROR: $CONDITION $* not met after $RETRIES tries" >&2
        exit 1
    fi
    echo "waiting for $CONDITION $* ($i/$RETRIES, ${DELAY}s)" >&2
    sleep "$DELAY"
done
