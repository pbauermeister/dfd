# 117 — The merge gate blocks a bumping title on a bookkeeping-only PR

Date: 2026-09-25
Status: ONGOING
Issue: #117 · PR: #118 · Branch: `ci/117-gate-bookkeeping-pr`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 27 (removed in the first commit), deferred by #107: the
`commit-msg` hook checks each commit's staged paths, but the PR title
is the type that reaches `main` at squash, and a title is edited on
GitHub out of the hook's reach. Builds on #107 (`bookkeeping_paths`,
`bookkeeping_verdict()`) and on the gate of #88.

### 1.2 Goal

The `Merge gate` check blocks a PR whose title bumps while every file
it changes is bookkeeping, with the hook's message; the level gate is
unchanged and runs first.

### 1.3 Design decisions

| #   | Decision                                                                                                           | Basis                                                                                                  | Alternatives considered                      |
| --- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| 1   | The files come from `git diff --name-only origin/main...HEAD` on the PR checkout, written to a file the tool reads | rule: the workflow already has the full history and the checkout; no API call, no token scope          | `gh api pulls/N/files` (a token, pagination) |
| 2   | One subcommand, `gate-pr-against-main --changed-files FILE`, optional: without the file the level gate alone runs  | rule: one concern per tool call site; the option keeps the local use (`make show-release-plan`) intact | A second subcommand                          |
| 3   | `pr_verdict()` composes the two verdicts, level first; `bookkeeping_verdict()` reused as is                        | rule: the same message as the hook, one implementation                                                 | A gate-specific message                      |

### 1.4 Acceptance criteria

1. Locally: a `docs:` title with bookkeeping files only is BLOCKED; a
   `chore:` title on the same passes; `docs:` with one shipping file
   passes; no file list keeps the former behavior.
2. The gate run of this PR prints the file count and passes.
3. `make format lint test` green; unit cases for the composition.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 27 removed, filed as #117.
- `984b3a6` ci: `pr_verdict()`, the `--changed-files` option, the
  workflow step, the sentence in RELEASING.md "Merge gate", five unit
  cases (level gate first, then files, no list).
- This devlog.

## 3. Delivery

### 3.1 Test report

1. Local trials with `--current 1.18.0 --next 1.18.0`: `docs: x` on
   `TODO.md` + `devlog/x.md` → `BLOCKED: a patch type on bookkeeping
paths only (TODO.md, devlog/x.md): use a type that bumps nothing`,
   exit 1; `chore: x` → `allowed: none level`; `docs: x` with
   `src/a.py` → `allowed: ships src/a.py`; no list → `allowed: patch
level` (criterion 1).
2. Run 36125951323 on this PR: `pending on main: patch (1.18.0 ->
1.18.1)`, `incoming PR: none`, `changed files: 5`, `allowed: none
level` (criterion 2).
3. 130 pytest, 95 NR fixtures, lint and format clean (criterion 3).

### 3.2 Verdict

**Recommendation:** accept with reservations

- The composition is unit-tested and the workflow line is proven by
  the PR's own run.

Reservations:

1. The BLOCKED path is not observed in a live run: this PR ships
   files, so it cannot provoke it. The first bookkeeping-only PR with
   a wrong title will; TODO 12's checklist could carry the case.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                         | Agent | User |
| --- | --------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track for a deferred, fully specified item; one round, no loop | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                                           | Rule                                                            | Verb (applied / created) |
| ------------------------------------------------ | --------------------------------------------------------------- | ------------------------ |
| `engineering/RELEASING.md` "Merge gate"          | A bumping title on a bookkeeping-only PR is blocked at the gate | created (sentence added) |
| `engineering/RELEASING.md` "Bookkeeping commits" | `chore:` for TODO.md and this devlog; `ci:` for the PR          | applied                  |
