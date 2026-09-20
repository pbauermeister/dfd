#!/bin/sh
# Remove build artifacts, caches and generated NR SVGs; retry with sudo
# when a root-owned artifact is in the way.

set -ex

clean() {
    $1 rm -rf \
       build/ dist/ src/*.egg-info/ \
       $(find -name __pycache__) \
       $(find tests/non-regression/ -name "*.svg")
}

clean || clean sudo
