#!/bin/sh

set -ex

clean() {
    $1 rm -rf build/ dist/ src/*.egg-info/ $(find -name __pycache__)
}

clean || clean sudo
