# 111 — Skip CI on pushes confined to bookkeeping paths

Date: 2026-09-24
Status: ONGOING
Issue: #111 · PR: #112 · Branch: `ci/111-ci-paths-ignore`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 18 (removed in the first commit). Third of the batch of
five build-related tasks of 2026-09-24 (24, 26, 18, 19, 25). Stacked
on #107 (PR #108), whose `bookkeeping_paths` (in `pyproject.toml`
since the review of #108) is the list this task filters on. The first
version filtered the `push` and `pull_request` triggers; the review
(2026-09-25) found it of little value: a `pull_request` event is judged
on the whole PR, so a devlog-only push on a code PR still ran the
suite, the case the user wanted gone. Reworked as a push-only
trigger, the idea taken from `pikett-ai-mvp`'s `ci.yml`.

### 1.2 Goal

A push confined to the bookkeeping paths starts no CI run, on any
branch and whatever else the PR holds; a push that ships something
runs the suite on the branch tip; `merge-gate.yml` and `pr-title.yml`,
required checks of the ruleset, keep running on every PR event;
`workflow_call` stays unfiltered so `release.yml` gates on the suite.
`make lint` keeps the `paths-ignore` list equal to `bookkeeping_paths`.

### 1.3 Design decisions

| #   | Decision                                                                                            | Basis                                                                                                             | Alternatives considered                                                                                                  |
| --- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | The list equals #107's set; directories as `dir/**`                                                 | user (the go)                                                                                                     | A wider list (`.gitignore`, `LICENSE`): marginal, not asked                                                              |
| 2   | Explicit list in `ci.yml`, no YAML anchor                                                           | rule: measure, don't estimate — anchor support in workflows is unverified, the lint check makes the copy safe     | One anchor for both triggers (moot since the rework)                                                                     |
| 3   | `check-bookkeeping-paths` in the tool, run by `make lint`, as `check-type-lists` for the type lists | rule: single source of truth, the pattern of #88                                                                  | Prose only                                                                                                               |
| 4   | Only `ci.yml` is filtered                                                                           | verified: the ruleset requires `conventional` and `gate` only; a filtered required check never reports            | Filter the gate too (would block the merge button)                                                                       |
| 5   | Push-only trigger, every branch: a push event is judged on the files of the push (two-dot diff)     | user (review, 2026-09-25): a devlog-only push on a code PR must not run CI; measured on this branch, Try it       | `[skip ci]` (measured: skips the required checks too, PR BLOCKED); a head job judging the pushed delta; a private marker |
| 6   | CI tests the branch tip, not the synthetic merge; CI stays a non-required check                     | rule: the ruleset's up-to-date policy makes the tip the merge result; `release.yml` gates on CI before publishing | CI as a required check (needs an always-reporting job, so a run on every push, the cost the task removes)                |
| 7   | The squash merge of a bookkeeping-only PR runs no CI on `main`                                      | user (review): nothing shippable to test; other merges run                                                        | A `push` trigger without filter for `main`                                                                               |

### 1.4 Acceptance criteria

1. `make lint` runs the check, green; a broken glob fails it.
2. Measured on this branch: a push that ships starts a `push` CI run;
   a devlog-only push on the same PR starts none; the required checks
   run on both.
3. `make format lint test` green.

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- First commit: TODO 18 removed, filed as #111.
- Second commit: `paths-ignore` on both triggers, `bookkeeping_globs()`,
  `load_ci_paths_ignore()` (`on:` reads as the key `True` in PyYAML),
  `check_bookkeeping_paths()`, the Makefile line, one unit case; the
  sentence in RELEASING.md "Bookkeeping commits". A first attempt used
  a YAML anchor and was lost to a `git checkout` of the file during
  the negative trial; redone without the anchor (decision 2).
- Devlog, RELEASING.md sentence refined (a PR judged on all its files).
- Merges forward from #107 (hook fixes, list moved to `pyproject.toml`)
  and from `main` after #108 and #110; `check_bookkeeping_paths()`
  reads the list through `load_bookkeeping_paths()`.
- PROCESS.md step 6: a bookkeeping-only PR has no CI to wait for
  (asked at the merge of #108).
- Review loop (2026-09-25). Measured first: a devlog-only commit with
  `[skip ci]` pushed to this PR skipped every workflow, `conventional`
  and `gate` included, PR BLOCKED; the undo commit quoted the marker in
  its body and was skipped too; an empty commit restored the checks
  (three trial commits at the tip, gone at squash; a rewrite was
  refused by the session's permissions). Then `8413c64`: `on: push`
  on `branches: ["**"]` with the one `paths-ignore`, `pull_request`
  dropped, `workflow_call` kept; the check restricted to `push`; the
  two doc passages rewritten; this devlog.

## 3. Delivery

### 3.1 Try it

```bash
gh api "repos/pbauermeister/dfd/actions/runs?head_sha=8413c64" \
  --jq '.workflow_runs[] | "\(.name)\t\(.event)\t\(.conclusion)"'
   # PR title, Merge gate (pull_request) and CI (push): the rework ships
gh api "repos/pbauermeister/dfd/actions/runs?head_sha=3a8b95e" \
  --jq '.workflow_runs[] | "\(.name)\t\(.event)\t\(.conclusion)"'
   # PR title and Merge gate only: a devlog-only push
gh pr checks 112   # the CI run of 8413c64 still shown on the PR
```

Tried: pending

### 3.2 Test report

1. `make lint`: `Bookkeeping paths consistent: …`; with `devlog/**`
   misspelt, `ERROR:` and exit 1 (criterion 1).
2. `8413c64` (ships `ci.yml`): `CI push` run started, `PR title` and
   `Merge gate` completed, CI `success`. `3a8b95e` (this devlog
   only): `PR title` and `Merge gate` only, no CI run (criterion 2).
3. 119 pytest, 95 NR fixtures; lint and format clean (criterion 3).

### 3.3 Verdict

**Recommendation:** accept

- The trigger is measured on the PR itself, both ways; the required
  checks are untouched.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                            | Agent    | User |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- |
| 1   | Process and template fit: fast track; the review became a design discussion (five options, one measured), which the fast track absorbs as a loop | well     |      |
| 2   | The first version answered the TODO's words ("commits that do not need them") with the wrong event: the user's goal was the push, not the PR     | not well |      |
| 3   | A negative trial that edits a tracked file must be reverted by re-applying, not by `git checkout`, before the work is committed                  | not well |      |
| 4   | The `[skip ci]` trial left three commits at the tip: quoting a marker in a commit body is itself a marker                                        | surprise |      |
| 5   | The idea came from another repository's `ci.yml`: reading a working example beat reasoning about GitHub's filter semantics                       | well     |      |

Process: 1 round before the go; 1 loop at the review; rework after the go: the trigger redesigned.

Closed: pending

### 4.2 Rule trace

| Source                                                  | Rule                                                                          | Verb (applied / created) |
| ------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------ |
| `engineering/RELEASING.md` "Bookkeeping commits" (#107) | CI runs on pushes only and skips a push confined to the bookkeeping paths     | created (sentence added) |
| `engineering/PROCESS.md` "Branching and PR workflow" 6  | The run to wait for is the last shipping push's, plus the two required checks | created (sentence added) |
| `engineering/PROCESS.md` "Established tool vs bespoke"  | Measure, don't estimate (`[skip ci]` trial, both pushes observed)             | applied                  |
