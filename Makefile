# Just type 'make' to get help.

PYTHON3 := python3
SHELL := /bin/bash

# Special targets:
.PHONY:  * # In this makefile, targets are not built artifacts.

################################################################################
## General commands:: ##

help: ## print this help
	@echo "Usage: make [TARGET]..."
	@echo
	@echo "TARGETs:"

	@# capture section headers and documented targets:
	@grep -E '^#* *[ a-zA-Z_-]+:.*?##.*$$' Makefile \
	| awk 'BEGIN {FS = ":[^:]*?##"}; {printf "  %-16s %s\n", $$1, $$2}' \
	| sed -E 's/^ *#+/\n/g' \
	| sed -E 's/ +$$//g'

	@# capture notes:
	@grep -E '^##[^#]*$$' Makefile | sed -E 's/^## ?//g'

venv: _venv ## setup a local .venv and tell how to activate it
	@echo "Now please run:"
	@echo ". .venv/bin/activate"

venv-activate: ## activate .venv and start an interactive shell
	@bash --rcfile <(echo "unset MAKELEVEL"; cat ~/.bashrc .venv/bin/activate)

_venv:
	python3 -m venv .venv || \
	(apt install python3.12-venv && python3 -m venv .venv)
	$(PYTHON3) -m venv .venv

require: ## install needed dev+install tools, in venv
	. .venv/bin/activate && \
	pip install setuptools twine pytest typing_extensions

all: venv require black lint test doc clean ## make all, except publish

################################################################################
# Quality:: ##

black: ## run black (changes shall be committed)
	. .venv/bin/activate && \
	black --skip-string-normalization --line-length 80 .

lint: ## lint source files
	. .venv/bin/activate && \
	./tools/lint.sh

test: ## run unit tests and non-regression tests
	. .venv/bin/activate && \
	pytest
	$(MAKE) nr-test

nr-review: ## gen. pre-goldens (SVG + error msg) for review before regen.
	./tests/nr-review.sh

nr-regenerate: ## regen. golden files (.dot + .stderr) from NR fixtures
	./tests/nr-regenerate.sh

nr-test: ## NR tests: verify fixtures still match their golden files
	./tests/nr-test.sh

################################################################################
# Local:: ##

install: ## install locally
	pip install . --break-system-packages

################################################################################
# Release:: ##

doc: ## remake doc
	. .venv/bin/activate && \
	./tools/make-doc.sh

publish-to-pypi: venv ## publish to Pypi
	. .venv/bin/activate && \
	./tools/publish-to-pypi.sh

################################################################################
# Cleanup:: ##
clean: ## clean
	./tools/clean.sh
