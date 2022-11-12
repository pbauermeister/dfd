#!/bin/sh
. ./set-ex.sh

./build.sh

pip3 uninstall data-flow-diagram || true
sudo pip3 uninstall data-flow-diagram

python3 setup.py build

sudo python3 setup.py install
