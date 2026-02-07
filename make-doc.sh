#!/bin/bash
. ./set-ex.sh

OPTS=--debug
OPTS=

# rebuild in doc/
(
    cd doc

    rm -f img/*.svg

    for doc in *.md; do
	../data-flow-diagram $OPTS $doc --markdown
    done

    for dfd in *.dfd; do
	../data-flow-diagram $OPTS $dfd
    done
)

# rebuild in top level
./data-flow-diagram $OPTS README.md --markdown
