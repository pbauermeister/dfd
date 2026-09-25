# 125 — Filters after a replacement work on the rewired graph

Date: 2026-09-25
Status: REJECTED
Issue: #125 · PR: #126 · Branch: `fix/125-filters-after-replacement`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 23 (removed in the first commit), found at the stop 1
discussion of #104, its direction agreed at that task's Try it (block
J of `devlog/104-try-it.dfd`). Last of the filter batch of 2026-09-25,
stacked on #123 (PR #124). Before: the traversal read the original
flows, so `~=G B C` then `!<2 D` re-added B and C as orphans next to
G; `! B` after the replacement did the same for an anchor; and the
group-first order could not be expressed at all.

### 1.2 Goal

Three rules, decided from the draft: the traversal and the anchors
read the flows as rewired so far; an anchor naming a replaced item is
an error; a replacement before any other filter records the rewiring
without initialising the kept set, so that the keep filter that
follows selects on the grouped graph. Both orders keep a meaning, the
doc says which.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                           | Basis                                                                                                                | Alternatives considered                                              |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | `_collect_connected_names()` reads each flow with its ends replaced so far and skips a collapsed one; `replacement` flows down from `find_neighbors()`             | user (the go), rule 1                                                                                                | Rewrite the statements after each `~=` (a second pass over the list) |
| 2   | Error "Name(s) no longer available, replaced: B (by G)", checked before the kept-set check, for `!` and `~` alike                                                  | user (the go), rule 2, wording confirmed                                                                             | The existing "due to previous filters" message                       |
| 3   | A `~=` while the kept set is `None` records the rewiring and does nothing else; initialisation, by a plain `~` or at the end, is all names minus the replaced ones | user (the go), rule 3                                                                                                | `~=` initialises as today and `!` after `~` narrows                  |
| 4   | A `~=` before any other filter takes no neighbor specification (error)                                                                                             | agent: removing neighbors from a set that does not exist yet has no meaning; deferring them is code for no known use | Defer the removals to the initialisation                             |
| 5   | Doc: README § 7.4.2.2 gains the group-first example with its picture; SYNTAX.md § 7.4 rules 3 and 4                                                                | rule: the doc's `!`-first example stays valid and is now contrasted                                                  | A new section                                                        |

### 1.4 Acceptance criteria

1. Fixtures: 093 (`~=G B C` then `!<2 D` gives A → G → D), 094 (anchor
   replaced, error), 095 (block J: A1–A3, Z, C1–C3, no orphan), 096
   (`~=` alone: A → G → D); 093, 094, 095 fail on the pre-fix code.
2. No older golden moves.
3. Unit: the replaced-anchor error, the neighbor-spec error.
4. `make format lint test doc` green; `tests/RULES.md` next number 097.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 23 removed, filed as #125.
- Second commit, fix: `filters.py` as decided (`_check_not_replaced()`,
  the `replacement` parameter down the traversal, the rewiring-only
  branch of `Without`, the initialisation minus replaced); fixtures
  093–096; two unit cases in `test_dfd.py`.
- Third commit, docs: README § 7.4.2.2 (example rendered by `make
doc`, one new image, no other image changed), SYNTAX.md § 7.4.
- This devlog.

## 3. Delivery

### 3.1 Try it

```bash
xdg-open doc/img/filter-replace-first.svg     # the group-first picture
make nr-review && xdg-open tests/non-regression/095-filter-replace-first-then-keep.svg
```

Tried: 2026-09-25 (the try-it pictures of `devlog/125-try-it/`, case 2 wrong on both code bases)

### 3.2 Test report

1. Goldens read: 093 and 096 hold A, D, G and the flows A→G, G→D; 094
   ends with the message; 095 holds the seven items and twelve flows,
   all through Z. Pre-fix `filters.py`: `FAIL:` 093, 095, 094; 096
   passes, as it should (criterion 1).
2. `git status` after `make nr-regenerate`: the four new files only
   (criterion 2).
3. Two unit cases green (criterion 3).
4. 141 pytest, 103 NR fixtures; lint, format and doc clean; RULES.md
   097+ (criterion 4).

### 3.3 Verdict

**Recommendation:** reject

- The fixes hold, each locked by a fixture, but the review found the
  flaw upstream of them: `~=` conflates a substitution with a filter,
  and rules 3 and 4 of this task were decrees covering that. Shipping
  the fixes would ship a still broken concept. The concept and the
  material go to #127 (the substitution statement `=G B C`, `~=`
  desugared and deprecated); nothing is merged from here.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                    | Agent      | User       |
| --- | -------------------------------------------------------------------------------------------------------- | ---------- | ---------- |
| 1   | Process fit: the review became a design round the fast track cannot hold; the stop rule was applied late | not well   | ended well |
| 2   | The flaw was in the concept: `~=` conflates a substitution with a filter, so every rule here was decreed | surprise   | surprise   |
| 3   | The joint effort to solve it in place (alternatives, mutations, a deferred implementation, renders)      | not well   | not well   |
| 4   | The decision to abort: nothing shipped on a broken concept, the material carried to a new task           | ended well | ended well |
| 5   | The pictures decided what prose could not; the reviewer's reading of case 2 named the concept            | well       | well       |

Process: 1 round before the go; 3 loops at the review; rework after the go: abandoned, the task stopped.

Pascal's note: on row 1, more lenient than the agent, because the
process permitted to realign: there is a valve.

Closed: 2026-09-25

### 4.2 Forward-looking

- Issue #127: the substitution statement, full track, this file and
  the review of PR #126 as its brief. Fixtures 093–096, the traversal
  through the rewiring, `_check_not_replaced()`, the README § 7.4.2.2
  example and the try-it cases are its material, on the branch
  `fix/125-filters-after-replacement`, left on origin unmerged.
- Found on the way and carried into #127's brief: chained
  substitutions lose their flows on `main` (`~=G B C` then `~=H G D`
  renders A and H with no flow); the strict flow collector reads raw
  ends; `~ X` then `! X` re-adds X against SYNTAX.md § 7.4 rule 3.
- This file reaches `main` by a direct commit, with the try-it
  folder: the record of a stopped task.

### 4.3 Rule trace

| Source                | Rule                                                             | Verb (applied / created) |
| --------------------- | ---------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`      | Mutation smoke-test after adding NR fixtures                     | applied                  |
| `doc/SYNTAX.md` § 7.4 | Rules 3 and 4: replaced anchors, replacement does not initialise | created                  |
