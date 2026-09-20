#!/bin/bash
. ./tools/init-tracing.sh

make require clean lint test doc
