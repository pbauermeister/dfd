# 107 — Bookkeeping commits must not bump the version

Date: 2026-09-24
Status: ONGOING
Issue: #107 · PR: #108 · Branch: `fix/107-bookkeeping-commits-no-bump`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 24 (removed in `c1937c9`), found at the delivery of #104: a
`docs:` commit on `TODO.md` alone (80e97b3) bumped patch, blocked the
`feat:` PR #105 at the merge gate and forced the empty release
1.17.10. First of a batch of five build-related tasks (24, 26, 18,
19, 25) decided in one conversation on 2026-09-24; its rule sets the
commit types of the four that follow.

### 1.2 Goal

A commit or a PR confined to paths that ship nothing carries a type
that bumps nothing. The rule is written in `engineering/RELEASING.md`
"Bookkeeping commits", echoed where `engineering/PROCESS.md` describes
TODO and direct commits, and enforced by the `commit-msg` hook.

### 1.3 Design decisions

| #   | Decision                                                                                                                                   | Basis                                                                                | Alternatives considered                                                                                                  |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | Non-shipping set: `TODO.md`, `CLAUDE.md`, `.claude/`, `devlog/`, `discussions/`, `engineering/`, `templates/`; `doc/` and `README.md` ship | user (the go)                                                                        | `tests/`, `tools/` as bookkeeping: they do not ship either, but `test:`/`build:` are the honest types and were not asked |
| 2   | Enforced by a path-aware local `commit-msg` hook, a subcommand of `tools/conventional-commits.py` (the bump map's owner)                   | user (the go): the direct-to-main commit that hurt has no PR, only a hook catches it | Rule in prose only; a merge-gate check of the title against the PR's files (TODO 27)                                     |
| 3   | `docs:` keeps bumping patch                                                                                                                | user (the go): the manual is the product's user-facing surface                       | `docs` to none, doc fixes waiting for the next code release                                                              |
| 4   | The list lives once, `BOOKKEEPING_PATHS` in the tool; the prose cites it                                                                   | rule: single source of truth (as the bump map in `pyproject.toml`)                   | A second copy in the docs                                                                                                |
| 5   | An empty staged set (empty or merge commit) is allowed                                                                                     | rule: nothing says what the commit is about                                          | Refuse                                                                                                                   |

### 1.4 Acceptance criteria

1. `docs:` on `TODO.md` alone is refused at commit time; `chore:` on
   the same passes; `docs:` on `TODO.md` plus a shipping path passes.
2. Unit tests for the path predicate, the verdict and the message
   reading; `make format lint test` green.
3. The rule is readable in `engineering/RELEASING.md` and pointed to
   from `engineering/PROCESS.md`.

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- `c1937c9` chore: TODO 24 removed, filed as #107.
- `803e603` chore: `check-bookkeeping-commit` subcommand
  (`BOOKKEEPING_PATHS`, `is_bookkeeping()`, `bookkeeping_verdict()`,
  staged paths from `git diff --cached`, comment lines of the message
  file dropped), local hook in `.pre-commit-config.yaml` at the
  `commit-msg` stage, 15 unit cases. A first live trial passed by
  mistake: the staged set held the tool itself, a shipping path, and
  the verdict was right; the trial commit was undone and redone on
  `TODO.md` alone.
- `d01703c` chore: "Bookkeeping commits" section in RELEASING.md,
  the sentence in PROCESS.md "Branching and PR workflow", TODO 27
  (the merge-gate check on the PR's files, deferred).
- This devlog.
- Follow-up found at #113's dry run: the hook's `uv run` re-synced
  the venv when `pyproject.toml`'s version changed, rewrote `uv.lock`
  and pre-commit failed the commit ("files were modified by this
  hook"). The entry is now `uv run --no-sync`: the hook never touches
  the environment (`make require` keeps it in sync).

## 3. Delivery

### 3.1 Test report

1. Live: `echo "# trial" >> TODO.md; git add TODO.md; git commit -m
"docs: trial"` → `BLOCKED: a patch type on bookkeeping paths only
(TODO.md): use a type that bumps nothing`, exit 1; the hook command
   on `chore: trial` exits 0; the same `docs:` with the tool staged
   passed (criterion 1).
2. `make test`: 117 pytest (102 + 15), 95 NR fixtures green; `make
format lint` clean (criterion 2).
3. Sections written (criterion 3); prettier clean.

### 3.2 Verdict

**Recommendation:** accept

- The three criteria are proven by a run; the hook is on for every
  commit of the four tasks that follow.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                    | Agent    | User |
| --- | ------------------------------------------------------------------------------------------------------------------------ | -------- | ---- |
| 1   | Process and template fit: fast track, decisions taken from disposable mandate drafts in one round for five tasks at once | well     |      |
| 2   | The first hook trial proved nothing (the tool's own files were staged); a trial must isolate the case                    | not well |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                                           | Rule                                                              | Verb (applied / created) |
| ------------------------------------------------ | ----------------------------------------------------------------- | ------------------------ |
| `engineering/RELEASING.md` "Bookkeeping commits" | A commit confined to non-shipping paths carries a none-level type | created                  |
| `engineering/CONVENTIONS.md` Type safety         | Keyword-only parameters, `Verdict` dataclass reused               | applied                  |
