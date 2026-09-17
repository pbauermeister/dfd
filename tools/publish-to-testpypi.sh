#!/bin/sh
#
# Release rehearsal: build, smoke-test the wheel, upload to TestPyPI,
# install from there into a fresh venv and smoke-test again.
#
# Getting a token:
#   https://test.pypi.org/manage/account/token/
#
# TestPyPI refuses re-uploads of a version: a failed rehearsal needs a
# version bump before retrying.

. ./set-ex.sh

./tools/build.sh


banner2 "Building distributions"

uv build


banner2 "Smoke-testing the wheel"

./tools/smoke-test-install.sh wheel


banner2 "Publishing to TestPyPI"

if [ ! -f .token-test ]; then
    echo "ERROR: please have a file named '.token-test' containing your TestPyPI token"
    exit 1
fi

# read the token without tracing it; the token is the only credential
# (a UV_PUBLISH_USERNAME inherited from the shell would conflict with it)
unset UV_PUBLISH_USERNAME UV_PUBLISH_PASSWORD
{ set +x; UV_PUBLISH_TOKEN=$(cat .token-test); export UV_PUBLISH_TOKEN; set -x; } 2>/dev/null
uv publish --publish-url https://test.pypi.org/legacy/ dist/*


banner2 "Smoke-testing the TestPyPI install"

./tools/smoke-test-install.sh testpypi
