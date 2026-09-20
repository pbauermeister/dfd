#!/bin/sh

set -ex

clean() {
    $1 rm -rf \
       build/ dist/ src/*.egg-info/ \
       $(find -name __pycache__) \
       $(find tests/non-regression/ -name "*.svg")
}

clean || clean sudo
