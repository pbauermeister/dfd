#!/bin/bash
. ./set-ex.sh

(cd doc && ../data_flow_diagram README.md --markdown)
./data_flow_diagram README.md --markdown
