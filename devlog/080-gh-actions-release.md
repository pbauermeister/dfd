# 080 — Release from GitHub Actions

Date: 2026-09-17
Status: PENDING

Issue: https://github.com/pbauermeister/dfd/issues/80

Depends on #79 (branch created from `refactor/79-python-m-build`;
rebase on `main` once PR #81 is merged).

## Requirement

Today `make publish-to-pypi` and `make publish-to-gh` are independent:
each builds its own sdist/wheel, only the GH path checks branch and tree
cleanliness and tags, only the PyPI path runs tests and the TestPyPI
rehearsal, and tokens live on disk (echoed by `set -x`).

Goal: one manually triggered GitHub Actions workflow that releases to
PyPI and GitHub from a single build, after the full test suite passes.

- Trigger: `workflow_dispatch` only (via `make release` or the Actions
  UI), on `main`. No automatic release on tag push or merge. The
  decision to release is manual; a release typically gathers several
  merged PRs.
- Gate: `ci.yml` made reusable (`workflow_call`) and called as the first
  job, so the release runs the same tox matrix, lint and wheel smoke
  test as CI on the released commit. All later jobs depend on it.
- Preflight: ref is `main`; version from CHANGES.md has no tag yet and
  is not on PyPI.
- Build once (`python -m build`), pass the artifact to all later jobs.
- Order: TestPyPI upload + install smoke test → tag `vX.Y.Z` → PyPI
  upload → GitHub release (changelog section as notes, same files
  attached).
- Uploads use PyPI trusted publishing (OIDC), no API tokens.
- Local `make publish-to-*` targets kept as a documented emergency
  fallback, reordered to match the workflow.
- Task closing process (CLAUDE.md): after switching back to `main` and
  pulling, the agent lists the PRs merged since the last release tag
  and asks whether to release now.

Prerequisites:

- #79 (python -m build).
- One-time manual setup by the maintainer: register the workflow as a
  trusted publisher on pypi.org and test.pypi.org.

PATCH bump.

## Design

To be agreed.
