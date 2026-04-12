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

The CI workflow also needs Graphviz installed on the runner
(`sudo apt install graphviz`) for NR tests to pass.
