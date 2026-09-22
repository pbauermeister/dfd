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
	./recipes/require-system.sh

require: ## install dev tools: Python ones in .venv (uv sync), prettier (npm), git hook
	uv sync
	npm install --prefix $(VENV) --no-audit --no-fund prettier@3
	uv run pre-commit install --hook-type commit-msg

all: require-system require format lint test doc clean ## make all, except publish

################################################################################
# Quality:: ##

format: ## format source files (changes shall be committed)
	uv run ruff format .

black: format ## alias of format

lint: ## lint source files, check CI and hooks agree with pyproject.toml
	uv run ./recipes/lint.sh
	uv run ./tools/check-python-versions.py $(PYTHONS)
	uv run ./tools/conventional-commits.py check-type-lists

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

build: require clean lint test doc ## full local build, before a local install

install: ## install user-wide as a uv tool (isolated venv, no sudo)
	uv tool install --reinstall .

uninstall: ## remove the user-wide uv tool install
	uv tool uninstall data-flow-diagram

################################################################################
# Release:: ##

doc-sections: ## regenerate auto-updatable sections of README.md and doc/*.md
	VENV=$(VENV) uv run ./tools/doc-update-sections.py

doc: doc-sections ## remake doc
	uv run ./recipes/doc.sh

smoke-test-wheel: clean ## build wheel, install in a fresh venv, check
	uv build
	./tools/test-installation.sh from-wheel

show-release-plan: ## print the next version and the commits since the last release with their bump levels
	@uv run ./tools/print-release-plan.py

help-cc: ## print the conventional commit type to version bump map
	@uv run ./tools/conventional-commits.py print-bump-table

release: ## release to PyPI and GitHub via GitHub Actions (see engineering/RELEASING.md)
	./recipes/release.sh

publish-to-testpypi: build ## release rehearsal: upload to TestPyPI, install, check
	./recipes/publish-to-testpypi.sh

publish-to-pypi: publish-to-testpypi ## fallback: rehearse on TestPyPI, then publish to PyPI
	./recipes/publish-to-pypi.sh

publish-to-gh: ## fallback: GitHub Release from dist/ (after publish-to-pypi)
	uv run ./tools/publish-to-github.py

################################################################################
# Cleanup:: ##
clean: ## remove build artifacts, caches and generated NR SVGs
	rm -rf build/ dist/ src/*.egg-info/
	find . -name __pycache__ -exec rm -rf {} +
	find tests/non-regression -name '*.svg' -delete
