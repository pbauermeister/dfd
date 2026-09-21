#!/bin/bash
#
# Install the package into a fresh venv and smoke-test it.
#
# Usage:
#   ./tools/test-installation.sh from-wheel      # the wheel from dist/
#   ./tools/test-installation.sh from-testpypi   # the version on TestPyPI
#
# Checks that `--version` reports the version from pyproject.toml and that
# rendering an NR fixture with `-f dot` matches its golden file. No
# Graphviz needed. Run from the repository root.

set -e -u -o pipefail

SOURCE=${1:?usage: $0 from-wheel|from-testpypi}
VERSION=$(python3 tools/changelog.py print-version)
FIXTURE=tests/non-regression/001-items
TESTPYPI_INDEX=https://test.pypi.org/simple/

echo; echo "--- Test the installation of $VERSION $SOURCE ---"

# create a throwaway venv, removed on exit
SMOKE_VENV=$(mktemp -d)
trap 'rm -rf "$SMOKE_VENV" "$FIXTURE.tmp"' EXIT
uv venv --quiet "$SMOKE_VENV"
PIP=(uv pip install --quiet --python "$SMOKE_VENV/bin/python")
DFD="$SMOKE_VENV/bin/data-flow-diagram"

echo; echo "-- install"
case "$SOURCE" in
    from-wheel)
        "${PIP[@]}" dist/data_flow_diagram-"$VERSION"-*.whl
        ;;
    from-testpypi)
        # The index lags a few seconds after an upload. No
        # --extra-index-url: the package has no dependencies, and
        # --no-deps guards against a stray declaration resolving there.
        ./tools/wait-for.sh testpypi-version "$VERSION"
        "${PIP[@]}" --no-deps --no-cache \
            --default-index "$TESTPYPI_INDEX" \
            "data-flow-diagram==$VERSION"
        ;;
    *)
        echo "ERROR: unknown source '$SOURCE' (expected from-wheel|from-testpypi)"
        exit 1
        ;;
esac

echo; echo "-- check version"
[ "$("$DFD" --version)" = "data-flow-diagram $VERSION" ]

echo; echo "-- check rendering"
"$DFD" "$FIXTURE.dfd" -f dot -o "$FIXTURE.tmp"
diff -u "$FIXTURE.dot" "$FIXTURE.tmp"

echo; echo "--- Installation OK: $VERSION $SOURCE ---"
