# General Devlog

Analysis outcomes and informal notes that are not yet tracked by a dedicated
`NNN-short-description.md` file. Owned by Claude; entries are append-only.

---

## 1. 2026-04-12 — Add GitHub Actions CI with multi-version testing [PENDING]

**Prompt:** Set up GitHub Actions CI with a Python version matrix (3.10, 3.11,
3.12, 3.13) using tox and the `setup-python` action. This would:

- Verify the declared Python 3.10+ support (currently only tested on 3.12).
- Replace the stale `tox.ini` boilerplate (copied from PyPA sample project,
  never customized) with a working configuration.
- Enable a CI/build status badge in the README badge row, signaling project
  health to new visitors.

### Plan

**1. Rewrite `tox.ini`** for this project:
- `envlist = py{310,311,312,313}`
- Dependencies: `pytest` (from `pyproject.toml` or inline)
- Commands: `pytest` + `make nr-test` (NR tests use shell scripts, not
  pytest — need to verify they work under tox)
- `isolated_build = true` (PEP 517/518)
- Remove stale flake8/check-manifest config

**2. Create `.github/workflows/ci.yml`:**
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

**3. Add CI badge to README:**
- `[![CI](https://github.com/pbauermeister/dfd/actions/workflows/ci.yml/badge.svg)](https://github.com/pbauermeister/dfd/actions/workflows/ci.yml)`
- Place in the badge row after PyPI version

**4. Verify and fix compatibility:**
- Run tox locally (requires pyenv or deadsnakes to have multiple Python
  versions installed) or push to a branch and let GH Actions run it
- Fix any 3.10/3.11/3.13-specific failures (likely none, but verify)
- The NR test scripts (`tests/nr-test.sh`, etc.) shell out to
  `./data-flow-diagram` — need to verify this works inside tox's
  virtualenv where the package is installed, not run from the repo root

**5. Clean up:**
- Delete or update any references to the old tox.ini config
- Verify `make test` and `tox` don't conflict
