#!/bin/sh
. ./set-ex.sh

./tools/build.sh

yes | pip3 uninstall data-flow-diagram 2>/dev/null || true
yes | sudo pip3 uninstall data-flow-diagram

python3 setup.py build

sudo python3 setup.py install
