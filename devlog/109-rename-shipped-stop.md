# 109 — Rename the `Shipped:` stop to `Ready:`

Date: 2026-09-24
Status: ONGOING
Issue: #109 · PR: #110 · Branch: `doc/109-rename-shipped-stop`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 26 (removed in the first commit), raised at stop 3 of #104
and decided there: `Ready:`, as in `gh pr ready`. Second of the batch
of five build-related tasks of 2026-09-24 (24, 26, 18, 19, 25); the
PR type `chore:` follows the rule of #107.

### 1.2 Goal

The third stop reads `Ready:` in `templates/devlog.md` and in
`engineering/PROCESS.md`; the prose around it says "the ready
decision". Earlier devlogs keep `Shipped:` (nine files), history being
history.

### 1.3 Design decisions

| #   | Decision                                                  | Basis                                                                  | Alternatives considered                                          |
| --- | --------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------- |
| 1   | `Ready:`                                                  | user (TODO 26, decided at #104 stop 3)                                 | `Reviewable:`, `Done:`, `Delivered:` (as confusing as "shipped") |
| 2   | Prose: "the ready decision", one wording everywhere       | user (the go)                                                          | "readiness decision", "delivery decision"                        |
| 3   | "the step that ships it" (Set-based design comment) stays | rule: it speaks of a convention reaching the codebase, not of the stop | Rename it too                                                    |

### 1.4 Acceptance criteria

1. `grep -i shipped templates/devlog.md engineering/PROCESS.md` is
   empty; five mentions in the template and two in the process read
   `Ready`.
2. Devlogs under `devlog/` unchanged.
3. `make test` green (the doc-sync tests read the template).

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- First commit: TODO 26 removed, filed as #109.
- Second commit: the seven lines, by `sed` on the exact lines;
  prettier clean.
- This devlog.

## 3. Delivery

### 3.1 Test report

1. The grep is empty; the seven `Ready` lines listed (criterion 1).
2. `git status` shows no `devlog/` change but this file (criterion 2).
3. `make test`: 102 pytest, 95 NR fixtures green (criterion 3).

### 3.2 Verdict

**Recommendation:** accept

- A rename with no reading left ambiguous; the memory notes are
  updated at closure.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                           | Agent | User |
| --- | --------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track for a decided rename; fits | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                                                  | Rule                                      | Verb (applied / created) |
| ------------------------------------------------------- | ----------------------------------------- | ------------------------ |
| `engineering/PROCESS.md` Phase 4                        | Third stop `Ready:`; the ready decision   | created                  |
| `engineering/RELEASING.md` "Bookkeeping commits" (#107) | `chore:` for `templates/`, `engineering/` | applied                  |
