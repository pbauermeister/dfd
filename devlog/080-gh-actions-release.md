# 080 — Release from GitHub Actions

Date: 2026-09-17
Status: ONGOING

Issue: https://github.com/pbauermeister/dfd/issues/80

## Requirement

Today `make publish-to-pypi` and `make publish-to-gh` are independent:
each builds its own sdist/wheel, only the GH path checks branch and tree
cleanliness and tags, only the PyPI path runs tests and the TestPyPI
rehearsal, and tokens live on disk.

Goal: one manually triggered GitHub Actions workflow that releases to
PyPI and GitHub from a single build, after the full test suite passes.

- Trigger: `workflow_dispatch` only (via `make release` or the Actions
  UI), on `main`. No automatic release on tag push or merge. The
  decision to release is manual; a release typically gathers several
  merged PRs.
- Gate: `ci.yml` made reusable (`workflow_call`) and called as the first
  job, so the release runs the same Python matrix, lint and wheel smoke
  test as CI on the released commit. All later jobs depend on it.
- Preflight: ref is `main`; version from CHANGES.md has no tag yet and
  is on neither PyPI nor TestPyPI.
- Build once (`uv build`), pass the artifact to all later jobs.
- Order: TestPyPI upload + install smoke test → PyPI upload → GitHub
  release, which creates the tag `vX.Y.Z` on the released commit
  (changelog section as notes, same files attached).
- Uploads use PyPI trusted publishing (OIDC), no API tokens.
- Local `make publish-to-*` targets kept as a documented emergency
  fallback, reordered to match the workflow.
- Task closing process (CLAUDE.md): after switching back to `main` and
  pulling, the agent lists the PRs merged since the last release tag
  and asks whether to release now.

Prerequisites:

- #79 (uv build/publish): merged.
- One-time manual setup by the maintainer: register the workflow as a
  trusted publisher on pypi.org and test.pypi.org.

PATCH bump (goes into the pending 1.17.6 entry).

## Design

### Workflow `.github/workflows/release.yml`

`on: workflow_dispatch`, with one boolean input `dry_run` (default
false): stop after the TestPyPI rehearsal, and accept any ref. This is
the only way to exercise the workflow before it lands on `main`.
`concurrency: release` forbids two runs at once. Jobs, each `needs` the
previous one:

1. `ci` — `uses: ./.github/workflows/ci.yml` (`ci.yml` gets an extra
   `workflow_call:` trigger; nothing else changes).
2. `preflight` — ref is `refs/heads/main` (unless `dry_run`); version
   read from CHANGES.md; `git ls-remote` finds no tag `vX.Y.Z`; the
   JSON API of PyPI and of TestPyPI both 404 for that version. Outputs
   `version`.
3. `build` — `uv build`, `tools/smoke-test-install.sh wheel`, upload
   `dist/` as artifact `dist`.
4. `testpypi` — environment `testpypi`, `id-token: write`; download
   `dist`; `uv publish --trusted-publishing always --publish-url
   https://test.pypi.org/legacy/`; `tools/smoke-test-install.sh
   testpypi`.
5. `pypi` — environment `pypi`, `id-token: write`; `uv publish
   --trusted-publishing always`. Skipped on `dry_run`.
6. `github-release` — `contents: write`; `gh release create vX.Y.Z
   --target $GITHUB_SHA --title vX.Y.Z --notes-file` with the changelog
   section, attaching `dist/*.whl dist/*.tar.gz`. `gh` creates the
   (lightweight) tag on that commit, so there is no separate tag job.
   Skipped on `dry_run`.

Top-level `permissions: contents: read`; each job raises only what it
needs.

### Scripts and Makefile

- `tools/changelog.py version|notes` (Python: CHANGES.md parsing) prints
  the latest version, or its changelog section. Used by the workflow
  (preflight, release notes) and by `publish-to-github.py`, which
  imports it instead of carrying its own regexes.
- `tools/release.sh` (bash: `gh` sequencing), behind `make release`:
  checks the checkout is `main`, clean and equal to `origin/main`,
  runs `gh workflow run release.yml --ref main`, then `gh run watch
  --exit-status` on the new run.
- Local fallback, in workflow order: `make publish-to-pypi` (unchanged:
  build, wheel smoke, TestPyPI, TestPyPI smoke, PyPI) then
  `make publish-to-gh`, which no longer cleans and rebuilds but tags
  and attaches the `dist/` just published. `--no-check` and the forced
  tag stay for backfilling.

### Setup, docs, process

- GitHub environments `testpypi` and `pypi` (created with `gh api`).
  Trusted publishers registered by Pascal on test.pypi.org and pypi.org
  for `pbauermeister/dfd`, workflow `release.yml`, matching environment
  name.
- New `doc/RELEASING.md`: how to release (`make release`), what the
  workflow checks, recovery after a failed run (version already on
  TestPyPI → `.postN` bump; on PyPI but no GitHub release → "Re-run
  failed jobs" in the Actions UI, which reuses the run's artifact, else
  `make publish-to-gh`), dry run from a branch, local fallback,
  one-time trusted publisher setup. Linked from the README development section.
- CLAUDE.md "Task closing": step 4, list PRs merged since the last
  release tag and ask whether to release.
- CHANGES.md: bullet in 1.17.6. TODO.md item 6 → DONE.

### Decisions to confirm

1. Version already on TestPyPI (failed earlier run) → preflight refuses;
   recovery is a `.postN` bump, as with the local rehearsal (#77).
2. No tag job: the GitHub release creates the tag (decided 2026-09-17,
   replacing "tag before PyPI upload" from the issue). PyPI is the only
   irreversible step; a failed later job is re-run in place.
3. `dry_run` input: worth its few lines to test the workflow from the
   PR branch, if `gh workflow run` accepts a workflow file that is not
   yet on `main` (to be verified at step 3; otherwise the first real
   release is the test, and 1.17.6 gets a `.post1` if it fails).
4. Preflight checks live inline in the workflow, not in a script: the
   local fallback keeps its own checks (`publish-to-github.py`).

### Implementation steps

1. `ci.yml`: add `workflow_call`; `tools/changelog.py`;
   `publish-to-github.py` imports it and stops building; Makefile
   `publish-to-gh` drops `clean`. Verify `make publish-to-gh --dry`-style
   locally by running the script functions on a scratch build.
2. `release.yml` (all jobs), GitHub environments. Push; try a dry run
   from the branch with a throwaway `1.17.6.dev1` heading in
   CHANGES.md. **Checkpoint:** Pascal registers the trusted publishers
   before the dry run (TestPyPI) and before the first release (PyPI).
3. `tools/release.sh` + `make release`; `doc/RELEASING.md`; README link;
   CLAUDE.md step; CHANGES.md; TODO.md.
4. Self-review, `make format lint test`, PR ready.
5. After merge: `make release` publishes 1.17.6, the first release
   through the workflow.
