#!/bin/bash
. ./set-ex.sh

#OPTS=--debug
OPTS=

(
    cd doc

    rm -f *.svg

    for doc in *.md; do
	../data-flow-diagram $OPTS $doc --markdown
    done

    for dfd in *.dfd; do
	../data-flow-diagram $OPTS $dfd
    done
)

./data-flow-diagram README.md --markdown
