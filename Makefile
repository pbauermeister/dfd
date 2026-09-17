# Just type 'make' to get help.

SHELL := /bin/bash
# Created by `uv sync`; also hosts prettier, installed there by `make require`
VENV := .venv
# Supported Python versions, checked by test-matrix and CI
PYTHONS := 3.11 3.12 3.13

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

venv: ## create or update the local .venv and tell how to activate it
	uv sync
	@echo "Now please run:"
	@echo ". $(VENV)/bin/activate"

venv-activate: ## activate .venv and start an interactive shell
	@bash --rcfile <(echo "unset MAKELEVEL"; cat ~/.bashrc $(VENV)/bin/activate)

require-system: ## install system packages (graphviz, npm) and uv
	@case "$$(uname -s)" in \
	  Linux)  which apt >/dev/null 2>&1 && \
	          sudo apt install -y graphviz npm || \
	          echo "Non-Debian Linux: install graphviz and npm manually" ;; \
	  Darwin) which brew >/dev/null 2>&1 && \
	          brew install graphviz node uv || \
	          echo "macOS without Homebrew: install graphviz, node and uv manually" ;; \
	  *)      echo "Unknown OS: install graphviz, node and uv manually" ;; \
	esac
	@which uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

require: ## install dev tools: Python ones in .venv (uv sync), prettier (npm)
	uv sync
	npm install --prefix $(VENV) --no-audit --no-fund prettier@3

all: require-system require format lint test doc clean ## make all, except publish

################################################################################
# Quality:: ##

format: ## format source files (changes shall be committed)
	uv run ruff format .

black: format ## alias of format

lint: ## lint source files, check CI lists the same Python versions
	uv run ./tools/lint.sh
	uv run ./tools/check-python-versions.py $(PYTHONS)

test: ## run unit tests and non-regression tests
	uv run pytest
	$(MAKE) nr-test

test-matrix: ## run test and lint on every supported Python (uv-managed)
	for py in $(PYTHONS); do \
	  UV_PYTHON=$$py UV_PROJECT_ENVIRONMENT=$(VENV)-$$py $(MAKE) test lint \
	  || exit 1; \
	done

nr-review: ## gen. pre-goldens (SVG + error msg) for review before regen.
	uv run ./tests/nr-review.sh

nr-regenerate: ## regen. golden files (.dot + .stderr) from NR fixtures
	uv run ./tests/nr-regenerate.sh

nr-test: ## NR tests: verify fixtures still match their golden files
	uv run ./tests/nr-test.sh

################################################################################
# Local:: ##

install: ## install user-wide as a uv tool (isolated venv, no sudo)
	uv tool install --reinstall .

uninstall: ## remove the user-wide uv tool install
	uv tool uninstall data-flow-diagram

################################################################################
# Release:: ##

readme: ## regenerate auto-updatable sections of README.md and doc/*.md
	VENV=$(VENV) uv run ./tools/update-docs.sh

doc: readme ## remake doc
	uv run ./tools/make-doc.sh

smoke-test-wheel: clean ## build wheel, install in a fresh venv, check
	uv build
	./tools/smoke-test-install.sh wheel

publish-to-testpypi: clean ## release rehearsal: upload to TestPyPI, install, check
	./tools/publish-to-testpypi.sh

publish-to-pypi: clean ## rehearse on TestPyPI, then publish to Pypi
	./tools/publish-to-pypi.sh

publish-to-gh: clean ## create GitHub Release (standalone)
	uv run ./tools/publish-to-github.py

################################################################################
# Cleanup:: ##
clean: ## clean
	./tools/clean.sh
