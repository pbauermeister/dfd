# 102 — Removing a node linked to a replacement group

Date: 2026-09-24
Status: DONE
Issue: #102 · PR: #103 · Branch: `fix/102-remove-node-linked-to-group`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Issue #102: `~ P3` leaves P3 rendered, unlabelled, when P3 is linked
to a `~=` replacement group; without the group it is removed. In
`_apply_filters()` (`src/data_flow_diagram/dsl/filters.py`) a
connection with no replaced end is dropped when either end is not in
the kept set, but a connection with a replaced end is rewritten and
kept with no kept-set check at all. `Group -> P3` survives and
Graphviz creates P3 implicitly. The gap predates #101 (devlog 100),
which reshaped that branch without adding the check; the filter
order does not matter.

### 1.2 Goal

A rewired connection is subject to the same kept-set check as any
other: a flow to a removed node is dropped whether or not its other
end was replaced. Two NR fixtures lock it in; both fail on the code
before the fix.

### 1.3 Design decisions

| #   | Decision                                                                                                        | Basis                                       | Alternatives considered                                          |
| --- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------- |
| 1   | Rewrite first, then one kept-set check for every connection; the self-loop skip and the dedup registration stay | rule: one check, one code path, no branches | Add the check inside the replaced branch (duplicates the check)  |
| 2   | Fixtures committed before the fix, goldens generated with the fix, so that the history shows them failing       | devlog 100, decision 2                      | Fixtures and fix in one commit                                   |
| 3   | Two fixtures: 080 the issue's example verbatim, 081 the filter order reversed                                   | taste                                       | One fixture (the order is the natural doubt, worth its own file) |

## 2. Execution

### 2.1 Account

- `b1d233c` test: fixtures 080 (the issue's example) and 081 (order
  reversed), goldens generated with the fix in place; `make nr-test`
  with the fix stashed fails on both (`Group -> P3` rendered). This
  failing run is the mutation smoke-test. `tests/RULES.md` next
  number 082.
- `6d4a755` fix: the kept-set check moved out of the non-replaced
  branch and applied after the rewrite. `make format lint test`
  green: 97 pytest, 88 NR fixtures; no existing golden changed.

Approved: 2026-09-24 ("Go")

## 3. Delivery

### 3.1 Try it

```bash
make nr-review     # SVGs next to the fixtures
xdg-open tests/non-regression/080-filter-replace-then-remove-neighbor.svg
xdg-open tests/non-regression/081-filter-remove-neighbor-then-replace.svg
git show 6d4a755   # the fix, 11 lines in, 8 out
git stash push -- src; make nr-test; git stash pop
                   # not applicable once merged: use
                   # git checkout b1d233c -- src && make nr-test; git checkout HEAD -- src
```

080 and 081 both render `Group` alone, as the issue's first example
minus P3.

Tried: 2026-09-24 (the two fixtures and a diagram of the user's own)

### 3.2 Verdict

**Recommendation:** accept

- The issue's example renders as expected; both fixtures fail before
  the fix and pass after; no other golden moved.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                    | Agent | User |
| --- | -------------------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Sibling of #100 in the same ten lines; the assessment before the go named cause, fix and fixtures in one | well  | well |
| 2   | Fast track, one go, fixtures then fix as in devlog 100; the devlog written at closure as the track says  | well  | well |

Process: 1 round before the go; loops at Try it: none; rework after the go: none.

Closed: 2026-09-24

### 4.2 Rule trace

| Source           | Rule                                         | Verb (applied / created) |
| ---------------- | -------------------------------------------- | ------------------------ |
| `tests/RULES.md` | Mutation smoke-test after adding NR fixtures | applied                  |
