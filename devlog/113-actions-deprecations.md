# 113 — Clear the GitHub Actions deprecation annotations

Date: 2026-09-24
Status: ONGOING
Issue: #113 · PR: #114 · Branch: `ci/113-actions-deprecations`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 19 (removed in the first commit). Fourth of the batch of
five build-related tasks of 2026-09-24 (24, 26, 18, 19, 25). Stacked
on #111 (PR #112), which edits the same `ci.yml`. Run 36051160152
(release 1.18.0) ended with 10 Node 20 warnings, 9 Ubuntu 26 notices
and 2 setup-uv warnings from the `pypi` job, which has no checkout.

### 1.2 Goal

The three workflows use the current majors of the four actions; the
`pypi` job's setup-uv is silent; the suite is known to pass on
Ubuntu 26.04 before `ubuntu-latest` migrates (2026-10-19 to
2026-11-19); the `release.yml` dry run has been exercised once.

### 1.3 Design decisions

| #   | Decision                                                                                                         | Basis                                                                                          | Alternatives considered                                                |
| --- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1   | Latest majors: `checkout@v7`, `upload-artifact@v7`, `download-artifact@v8`, `setup-uv@v10.2.0`                   | user (the go); the release notes of every major since v4 read, none touches this usage         | The lowest Node 24 majors (v5/v6/v7/v7): the same cycle returns sooner |
| 2   | `setup-uv` by exact tag `v10.2.0`: immutable releases since v8, no moving major tag past v7                      | measured: `@v10` does not resolve (run 36054836843)                                            | A commit SHA (the immutable release makes the tag as safe)             |
| 3   | Keep `ubuntu-latest`; the try is one matrix run on `ubuntu-26.04`                                                | user (the go): a pin is a debt; the suite depends on graphviz only                             | Pin `ubuntu-24.04` and migrate on purpose later                        |
| 4   | `pypi` job: `enable-cache: false`, `ignore-empty-workdir: true` (both inputs in v10.2.0's `action.yml`)          | user (the go): the job only publishes                                                          | Add a checkout                                                         |
| 5   | Dry run on a throwaway commit (version `1.18.1.dev1`, matrix on `ubuntu-26.04`), undone by a conventional revert | rule: TestPyPI refuses re-uploads, the version must be fresh; the tree must return to `1.18.0` | Two dry runs (one per change)                                          |

### 1.4 Acceptance criteria

1. A `release.yml` dry run from the branch is green through TestPyPI
   with no Node 20 warning.
2. The CI matrix passes on `ubuntu-26.04`.
3. `pyproject.toml`, `uv.lock` and `ci.yml`'s `runs-on` are back to
   `main`'s values; `make format lint test` green.

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- First commit: TODO 19 removed, filed as #113.
- `0e78b2f` ci: the four actions bumped, the two inputs on the `pypi`
  job. A dispatch on this commit (run 36054836843) failed in CI at
  "Set up job": `astral-sh/setup-uv@v10` does not exist as a tag.
- `41d7a0e` ci: `setup-uv@v10.2.0`.
- `2085331` ci: throwaway dry-run commit. Its first attempt did not
  commit: the bookkeeping hook of #107 ran `uv run`, which re-synced
  the venv on the version change and rewrote `uv.lock`; fixed on
  #107's branch (`--no-sync`), then a second defect (a merge commit's
  subject refused) fixed there too, both merged forward into #111 and
  this branch (`adaa8dd`, `15dcdbf`).
- Dispatch on `2085331`: run 36054992654, green: CI on `ubuntu-26.04`
  for 3.11, 3.12, 3.13 and the wheel smoke test; preflight, build,
  TestPyPI publish and install of `1.18.1.dev1`; `pypi` and
  `github-release` skipped as designed. Annotations left: three
  Ubuntu 26 notices from the release jobs on `ubuntu-latest`.
- `3bef6af` ci: the throwaway commit undone (`git revert --no-commit`,
  conventional subject). `dee8347` chore: TODO 12's first box ticked.
- This devlog.

## 3. Delivery

### 3.1 Test report

1. Run 36054992654: all jobs green through `testpypi`; no Node 20 or
   setup-uv annotation (criterion 1). The `pypi` job's inputs are not
   exercised by a dry run: the next real release proves them.
2. Same run, `ci / test (3.11, 3.12, 3.13)` and `ci / smoke-test-wheel`
   on `ubuntu-26.04`: success (criterion 2).
3. `git diff main -- pyproject.toml uv.lock` empty; `ci.yml` has
   `ubuntu-latest` twice; 119 pytest, 95 NR fixtures, lint and format
   clean (criterion 3).

### 3.2 Verdict

**Recommendation:** accept with reservations

- The rehearsal proves the majors and the image; the notices left are
  GitHub's until the migration.

Reservations:

1. The `pypi` job's setup-uv inputs are proven at the next release
   only (the job runs on a tag push).

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                               | Agent    | User |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track with a measured rehearsal; the dry run doubled as the try for two decisions                    | well     |      |
| 2   | The TODO's majors were a year stale; reading the release notes first replaced them in one pass                                      | well     |      |
| 3   | A dispatched run on the wrong commit (the hook had aborted the throwaway commit silently to me): check `git log` before dispatching | not well |      |
| 4   | The dry run was the first real use of #107's hook and found two defects; the batch order (24 first) paid off                        | surprise |      |

Process: 1 round before the go; no loop; rework after the go: the setup-uv ref, the hook fixes on #107.

Closed: pending

### 4.2 Rule trace

| Source                                                 | Rule                                     | Verb (applied / created) |
| ------------------------------------------------------ | ---------------------------------------- | ------------------------ |
| `engineering/PROCESS.md` "Established tool vs bespoke" | Measure, don't estimate (notes, dry run) | applied                  |
| `engineering/RELEASING.md` "Bookkeeping commits"       | `chore:` for TODO.md and this devlog     | applied                  |
