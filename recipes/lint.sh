#!/bin/bash
# Lint the Python sources: ruff check and format check, then mypy in
# strict mode with the options below.
set -ex

MYPY_OPTS=""
MYPY_OPTS+=" --warn-redundant-casts"
MYPY_OPTS+=" --warn-return-any"
#MYPY_OPTS+=" --warn-unreachable"
MYPY_OPTS+=" --strict-equality"
MYPY_OPTS+=" --strict --namespace-packages"

ruff check .
ruff format --check .

SRCS=$(find src tests -name "*.py")
mypy --ignore-missing-imports --pretty $MYPY_OPTS --no-strict-optional $SRCS
