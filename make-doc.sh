#!/bin/bash
. ./set-ex.sh

(
    cd doc

    rm -f *.svg

    for doc in *.md; do
	../data-flow-diagram $doc --markdown
    done

    for dfd in *.dfd; do
	../data-flow-diagram $dfd
    done
)

./data-flow-diagram README.md --markdown
