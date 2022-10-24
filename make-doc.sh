#!/bin/bash
. ./set-ex.sh

(cd doc && ../data-flow-diagram README.md --markdown)
./data-flow-diagram README.md --markdown
