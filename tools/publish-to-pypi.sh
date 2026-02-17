#!/bin/sh
#
# Pip packaging:
#   https://packaging.python.org/tutorials/packaging-projects/
#
# Entry point:
#   https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
#
# Getting a token:
#   https://pypi.org/manage/account/token/
#
# Version info: please update the file
#   setup.py
#

. ./set-ex.sh

./tools/build.sh


banner2 "Publishing to Pypi"

if [ ! -f .token ]; then
    echo "ERROR: please have a file named '.token' containing your pypi token"
    exit 1
fi

python3 setup.py sdist
python3 -m twine upload --username __token__ dist/* \
	--password $(cat .token) --verbose
