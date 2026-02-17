#!/bin/bash
. ./set-ex.sh

banner2 "Cleaning up"
./tools/clean.sh

banner2 "Linting"
./tools/lint.sh

banner2 "Testing"
./test.sh

banner2 "Making doc"
./tools/make-doc.sh
