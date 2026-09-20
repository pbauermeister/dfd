#!/bin/bash
# Rebuild the documentation: renumber the titles of doc/README.md, then
# render every diagram of doc/ and README.md with the dev wrapper.
. ./tools/init-tracing.sh

OPTS=--debug
OPTS=

tools/doc-renumber-md-titles.py doc/README.md

# rebuild in doc/
(
    cd doc

    rm -f */*.svg

    for doc in *.md; do
	../data-flow-diagram $OPTS $doc --markdown
    done

    for dfd in dfd/*.dfd; do
	../data-flow-diagram $OPTS $dfd
    done
)

# rebuild in top level
./data-flow-diagram $OPTS README.md --markdown
