# 125 — Filters after a replacement work on the rewired graph

Date: 2026-09-25
Status: ONGOING
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

Tried: pending

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

**Recommendation:** accept with reservations

- The three rules are each locked by a fixture that fails without them.

Reservations:

1. Decision 4 (no neighbor specification on a leading `~=`) was mine,
   not in the draft; it closes a case rather than defining it, and can
   be reopened if a use appears.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                        | Agent | User |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track for a design agreed at a previous task's Try it; the rules were written before the code | well  |      |
| 2   | The batch order paid: 20 and 21 cleared the parser, 22 the doc section, so this task touched `filters.py` and § 7.4 only     | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                | Rule                                                             | Verb (applied / created) |
| --------------------- | ---------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`      | Mutation smoke-test after adding NR fixtures                     | applied                  |
| `doc/SYNTAX.md` § 7.4 | Rules 3 and 4: replaced anchors, replacement does not initialise | created                  |
