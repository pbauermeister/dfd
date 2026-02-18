#!/bin/bash
. ./set-ex.sh

make venv require clean lint test doc
