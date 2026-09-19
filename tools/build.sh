#!/bin/bash
. ./init-tracing.sh

make require clean lint test doc
