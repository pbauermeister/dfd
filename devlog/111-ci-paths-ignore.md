# 111 — Skip CI on commits confined to bookkeeping paths

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
on #107 (PR #108), whose `bookkeeping_paths` (in `pyproject.toml` since the review of #108) is the list this task
filters on; the PR is retargeted to `main` when #108 merges.

### 1.2 Goal

`ci.yml` runs nothing for a push to `main` or a PR confined to the
bookkeeping paths; `merge-gate.yml` and `pr-title.yml`, required
checks of the ruleset, keep running on every event; `workflow_call`
stays unfiltered so `release.yml` gates on the suite. `make lint`
keeps the `paths-ignore` lists equal to `bookkeeping_paths`.

### 1.3 Design decisions

| #   | Decision                                                                                            | Basis                                                                                                           | Alternatives considered                                     |
| --- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 1   | The list equals #107's set; directories as `dir/**`                                                 | user (the go)                                                                                                   | A wider list (`.gitignore`, `LICENSE`): marginal, not asked |
| 2   | Two explicit copies in `ci.yml`, no YAML anchor                                                     | rule: measure, don't estimate — anchor support in workflows is unverified, the lint check makes the copies safe | One anchor for both triggers                                |
| 3   | `check-bookkeeping-paths` in the tool, run by `make lint`, as `check-type-lists` for the type lists | rule: single source of truth, the pattern of #88                                                                | Prose only                                                  |
| 4   | Only `ci.yml` is filtered                                                                           | verified: the ruleset requires `conventional` and `gate` only; a filtered required check never reports          | Filter the gate too (would block the merge button)          |

### 1.4 Acceptance criteria

1. `make lint` runs the check, green; a broken glob fails it.
2. After the retarget to `main`: a push of this devlog alone starts no
   CI run; the branch's `ci.yml` commit does.
3. `make format lint test` green.

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- First commit: TODO 18 removed, filed as #111.
- Second commit: `paths-ignore` on both triggers with a comment,
  `bookkeeping_globs()`, `load_ci_paths_ignore()` (`on:` reads as the
  key `True` in PyYAML), `check_bookkeeping_paths()`, the Makefile
  line, one unit case; the sentence in RELEASING.md "Bookkeeping
  commits". A first attempt used a YAML anchor and was lost to a
  `git checkout` of the file during the negative trial; redone
  without the anchor (decision 2).
- This devlog, with the RELEASING.md sentence refined: a PR is judged
  on all its files (GitHub evaluates `pull_request` path filters on
  the whole PR), so the saving is on bookkeeping-only PRs and pushes.

## 3. Delivery

### 3.1 Test report

1. `make lint`: `Bookkeeping paths consistent: TODO.md CLAUDE.md
.claude/** devlog/** discussions/** engineering/** templates/**`;
   with `devlog/**` misspelt: two `ERROR:` lines, exit 1 (criterion 1).
2. Pending the retarget: while the base is the #107 branch, the
   `branches: ["main"]` filter alone keeps CI off, which proves
   nothing. To read at the review, once #108 is merged and `main`
   merged in: `gh run list -b ci/111-ci-paths-ignore` shows a CI run
   for the branch update and none for a devlog-only push (criterion 2).
3. `make test`: 118 pytest, 95 NR fixtures; lint and format clean
   (criterion 3).

### 3.2 Verdict

**Recommendation:** accept with reservations

- The lint check and the YAML are proven locally.

Reservations:

1. Criterion 2 is observed only after the retarget; the reviewer reads
   the run list of the branch before merging.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                           | Agent    | User |
| --- | ------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track, stacked PR; the stacking hides the live try until the retarget                            | tension  |      |
| 2   | A negative trial that edits a tracked file must be reverted by re-applying, not by `git checkout`, before the work is committed | not well |      |

Process: 1 round before the go; no loop; rework after the go: the ci.yml edit redone.

Closed: pending

### 4.2 Rule trace

| Source                                                  | Rule                                                                     | Verb (applied / created) |
| ------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------ |
| `engineering/RELEASING.md` "Bookkeeping commits" (#107) | CI skips a push or a PR confined to the bookkeeping paths                | created (sentence added) |
| `engineering/PROCESS.md` "Established tool vs bespoke"  | Measure, don't estimate (no unverified YAML anchor)                      | applied                  |
| `engineering/PROCESS.md` "Branching and PR workflow" 6  | A bookkeeping-only PR has no CI to wait for (asked at the merge of #108) | created (sentence added) |

