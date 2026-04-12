# 063 — GitHub Actions CI with tox Multi-version Testing

**Date:** 2026-04-12
**Status:** DONE

## Requirement

Set up GitHub Actions CI with a Python version matrix (3.10, 3.11, 3.12,
3.13) using tox and the `setup-python` action.

1. **Verify the declared Python 3.10+ support** — currently only tested on
   3.12 locally.
2. **Replace the stale `tox.ini` boilerplate** (copied from PyPA sample
   project, never customized) with a working configuration.
3. **Add a CI/build status badge** to the README badge row, signaling project
   health to new visitors.

## Design

### Key design decision: tox delegates to Makefile

All tests continue to go through the Makefile — tox is just the
orchestrator that selects which Python version runs them. tox passes
its venv path to Make via a configurable `VENV` variable:

**Makefile** (top):
```makefile
VENV ?= .venv
```

All targets use `$(VENV)` instead of hardcoded `.venv`:
```makefile
test:
    . $(VENV)/bin/activate && pytest
    $(MAKE) nr-test
nr-test:
    . $(VENV)/bin/activate && ./tests/nr-test.sh
```

**tox.ini:**
```ini
[testenv]
commands =
    make test VENV={envdir}
    make lint VENV={envdir}
```

Locally: `make test` uses `.venv` as before (default). In tox: each
Python version passes its own venv path via `{envdir}`.

**NR test fix:** the `nr-test` target currently does not activate the
venv — `./data-flow-diagram` runs with whatever Python is on PATH.
This must be fixed: `nr-test` must activate `$(VENV)` so the correct
Python version is used. Similarly for `nr-review` and `nr-regenerate`.

### Implementation steps

1. **Make venv path configurable in Makefile:**
   - Add `VENV ?= .venv` at the top.
   - Replace all `. .venv/bin/activate` with `. $(VENV)/bin/activate`.
   - Add venv activation to `nr-test`, `nr-review`, `nr-regenerate`
     targets (currently missing — they use system Python).

2. **Rewrite `tox.ini`:**
   - `envlist = py{310,311,312,313}`
   - Dependencies: `pytest` (plus any test deps)
   - Commands: `make test VENV={envdir}` and `make lint VENV={envdir}`
   - `isolated_build = true` (PEP 517/518)
   - Remove stale flake8/check-manifest config

3. **Create `.github/workflows/ci.yml`:**
   - Triggers: `push` to `main`, `pull_request` targeting `main`
   - Matrix: `python-version: ["3.10", "3.11", "3.12", "3.13"]`
   - Steps:
     1. Checkout
     2. Install Graphviz (`sudo apt-get install -y graphviz`)
     3. `setup-python` with matrix version
     4. `pip install tox`
     5. `tox -e py` (tox auto-selects the matching env)
   - Consider: also run `make lint` (mypy) as a separate job or tox env,
     since type-checking only needs one Python version

4. **Add CI badge to README:**
   - Place in the badge row after PyPI version

5. **Verify and fix compatibility:**
   - Push to branch and let GH Actions run the matrix
   - Fix any 3.10/3.11/3.13-specific failures (likely none, but verify)

6. **Clean up:**
   - Verify `make test` still works locally with `.venv` (default path)
