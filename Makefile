# Just type 'make' to get help.

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
	| awk 'BEGIN {FS = ":[^:]*?##"}; {printf "  %-24s %s\n", $$1, $$2}' \
	| sed -E 's/^ *#+/\n/g' \
	| sed -E 's/ +$$//g'

	@# capture notes:
	@grep -E '^##[^#]*$$' Makefile | sed -E 's/^## ?//g'

venv: # setup a local .venv and tell how to activate it
	python3 -m venv .venv || \
	(apt install python3.12-venv && python3 -m venv .venv)
	@echo "Now please run:"
	@echo ". .venv/bin/activate"

require: ## install needed dev+install tools, in venv
	. .venv/bin/activate && \
	pip install setuptools twine

all: venv require black lint test doc clean ## make all, except publish

################################################################################
# Quality:: ##

black: ## run black (changes shall be committed)
	. .venv/bin/activate && \
	black --skip-string-normalization --line-length 80 .

lint: ## lint source files
	. .venv/bin/activate && \
	./lint.sh

test: ## run tests
	. .venv/bin/activate && \
	./test.sh

################################################################################
# Local:: ##

install: ## install locally
	pip install . --break-system-packages

################################################################################
# Release:: ##

doc: ## remake doc
	. .venv/bin/activate && \
	./make-doc.sh

publish-to-pypi: venv ## publish to Pypi
	. .venv/bin/activate && \
	./publish-to-pypi.sh

################################################################################
# Cleanup:: ##
clean: ## clean
	./clean.sh
