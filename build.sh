#!/bin/bash
. ./set-ex.sh

banner2 "Cleaning up"
./clean.sh

banner2 "Linting"
./lint.sh

banner2 "Testing"
./test.sh

banner2 "Making doc"
./make-doc.sh
