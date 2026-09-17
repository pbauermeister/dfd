#!/bin/sh
#
# Pip packaging:
#   https://packaging.python.org/tutorials/packaging-projects/
#
# Entry point:
#   https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
#
# Getting a token:
#   https://pypi.org/manage/account/token/
#
# Version info: please update the file
#   CHANGES.md
#
# The TestPyPI rehearsal (build, wheel smoke test, TestPyPI upload and
# install smoke test) runs first; any failure stops before the real upload.

. ./set-ex.sh

./tools/publish-to-testpypi.sh


banner2 "Publishing to Pypi"

if [ ! -f .token ]; then
    echo "ERROR: please have a file named '.token' containing your pypi token"
    exit 1
fi

# read the token without tracing it
{ set +x; UV_PUBLISH_TOKEN=$(cat .token); export UV_PUBLISH_TOKEN; set -x; } 2>/dev/null
uv publish dist/*
