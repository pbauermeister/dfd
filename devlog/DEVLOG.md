# General Devlog

Analysis outcomes and informal notes that are not yet tracked by a dedicated
`NNN-short-description.md` file. Owned by Claude; entries are append-only.

---

## 1. 2026-04-12 — Add GitHub Actions CI with multi-version testing [DONE]

**Prompt:** Set up GitHub Actions CI with a Python version matrix using tox.

Promoted to issue #63 and tracked in
[`devlog/063-ci-tox.md`](063-ci-tox.md).

## 2. 2026-04-12 — Evaluate ruff as linter/formatter [PENDING]

**Prompt:** CI lint job takes 16s (mypy). Evaluate ruff as a faster
alternative or complement. ruff handles style/import linting (10-100x faster
than flake8/pylint) but does not replace mypy's type checking. Consider:
ruff for style + mypy for types, or ruff alone if type checking is deemed
low-value for this project.
