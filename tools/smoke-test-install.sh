#!/bin/bash
#
# Install the package into a fresh venv and check that it works.
#
# Usage:
#   ./tools/smoke-test-install.sh wheel      # install the wheel from dist/
#   ./tools/smoke-test-install.sh testpypi   # install from TestPyPI
#
# Checks that `--version` reports the version from CHANGES.md and that
# rendering an NR fixture with `-f dot` matches its golden file. No
# Graphviz needed. Run from the repository root.

. ./set-ex.sh

MODE=${1:?usage: $0 wheel|testpypi}
VERSION=$(sed -nE 's/^## Version +([^:]+):.*/\1/p' CHANGES.md | head -1)
FIXTURE=tests/non-regression/001-items
TESTPYPI_INDEX=https://test.pypi.org/simple/
RETRIES=12  # The TestPyPI index lags a few seconds after upload.
DELAY=5

banner2 "Smoke test: install $VERSION from $MODE"

# create a throwaway venv, removed on exit
SMOKE_VENV=$(mktemp -d)
trap 'rm -rf "$SMOKE_VENV" "$FIXTURE.tmp"' EXIT
uv venv --quiet "$SMOKE_VENV"
PIP=(uv pip install --quiet --python "$SMOKE_VENV/bin/python")
DFD="$SMOKE_VENV/bin/data-flow-diagram"

step "install"
case "$MODE" in
    wheel)
        "${PIP[@]}" dist/data_flow_diagram-"$VERSION"-*.whl
        ;;
    testpypi)
        # No --extra-index-url: the package has no dependencies, and
        # --no-deps guards against a stray declaration resolving there.
        for i in $(seq "$RETRIES"); do
            "${PIP[@]}" --no-deps --no-cache \
                --default-index "$TESTPYPI_INDEX" \
                "data-flow-diagram==$VERSION" && break
            [ "$i" -lt "$RETRIES" ] || exit 1
            echo "not yet available, retrying in ${DELAY}s ($i/$RETRIES)"
            sleep "$DELAY"
        done
        ;;
    *)
        echo "ERROR: unknown mode '$MODE' (expected wheel|testpypi)"
        exit 1
        ;;
esac

step "check version"
[ "$("$DFD" --version)" = "data-flow-diagram $VERSION" ]

step "check rendering"
"$DFD" "$FIXTURE.dfd" -f dot -o "$FIXTURE.tmp"
diff -u "$FIXTURE.dot" "$FIXTURE.tmp"

banner2 "Smoke test OK: $VERSION from $MODE"
