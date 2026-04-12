# Just type 'make' to get help.

PYTHON3 := python3
SHELL := /bin/bash
VENV ?= .venv

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
	@echo ". $(VENV)/bin/activate"

venv-activate: ## activate .venv and start an interactive shell
	@bash --rcfile <(echo "unset MAKELEVEL"; cat ~/.bashrc $(VENV)/bin/activate)

_venv:
	$(PYTHON3) -m venv $(VENV)

require-system: ## install system packages (graphviz, python3-venv)
	@case "$$(uname -s)" in \
	  Linux)  which apt >/dev/null 2>&1 && \
	          sudo apt install -y graphviz python3-venv || \
	          echo "Non-Debian Linux: install graphviz manually" ;; \
	  Darwin) which brew >/dev/null 2>&1 && \
	          brew install graphviz python3 || \
	          echo "macOS without Homebrew: install graphviz manually" ;; \
	  *)      echo "Unknown OS: install graphviz manually" ;; \
	esac

require: ## install needed dev+install tools, in venv
	. $(VENV)/bin/activate && \
	pip install setuptools twine pytest typing_extensions

all: require-system venv require black lint test doc clean ## make all, except publish

################################################################################
# Quality:: ##

black: ## run black (changes shall be committed)
	. $(VENV)/bin/activate && \
	black --skip-string-normalization --line-length 80 .

lint: ## lint source files
	. $(VENV)/bin/activate && \
	./tools/lint.sh

test: ## run unit tests and non-regression tests
	. $(VENV)/bin/activate && \
	pytest
	$(MAKE) nr-test

nr-review: ## gen. pre-goldens (SVG + error msg) for review before regen.
	. $(VENV)/bin/activate && \
	./tests/nr-review.sh

nr-regenerate: ## regen. golden files (.dot + .stderr) from NR fixtures
	. $(VENV)/bin/activate && \
	./tests/nr-regenerate.sh

nr-test: ## NR tests: verify fixtures still match their golden files
	. $(VENV)/bin/activate && \
	./tests/nr-test.sh

################################################################################
# Local:: ##

install: ## install locally
	pip install . --break-system-packages

################################################################################
# Release:: ##

readme: ## regenerate auto-updatable sections of README.md
	. $(VENV)/bin/activate && \
	./tools/update-readme.sh

doc: readme ## remake doc
	. $(VENV)/bin/activate && \
	./tools/make-doc.sh

publish-to-pypi: venv clean ## publish to Pypi and create GitHub Release
	. $(VENV)/bin/activate && \
	./tools/publish-to-pypi.sh
	. $(VENV)/bin/activate && \
	python3 ./tools/publish-to-github.py

publish-to-gh: venv clean ## create GitHub Release (standalone)
	. $(VENV)/bin/activate && \
	python3 ./tools/publish-to-github.py

################################################################################
# Cleanup:: ##
clean: ## clean
	./tools/clean.sh
