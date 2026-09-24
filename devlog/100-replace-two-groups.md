# 100 — Replacement flows between two replaced groups

Date: 2026-09-23
Status: DONE
Issue: #100 · PR: #101 · Branch: `fix/100-replace-two-groups`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Issue #100: with two `~=` replacements in one diagram (`~=AB A B`,
`~=CD C D`), the flows between the two groups vanish instead of
becoming flows between the replacers. The issue suspects a single-pass
implementation; reading `src/data_flow_diagram/dsl/filters.py` shows
the mapping is collected in phase 1 and applied in phase 2 already.
The cause is the guard in `_apply_filters()` that skips a connection
whose two endpoints are both replaced, meant to drop the self-loop of
an intra-group flow, but written without checking that both map to
the same replacer.

### 1.2 Goal

A flow between two items of different replaced groups is rendered
between their replacers. A flow whose two ends collapse to one item
after replacement is dropped, as before. Two NR fixtures lock it in;
both fail on the code before the fix.

### 1.3 Design decisions

| #   | Decision                                                                                                           | Basis                                                                                 | Alternatives considered                                                   |
| --- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | Rewrite the endpoints first, then skip when `src == dst`: one condition covers same-group and replacer-as-endpoint | rule: simplest correct condition; self-loop avoidance confirmed by the user at Try it | Compare `replacement.get(src) == replacement.get(dst)` (misses `A -> AB`) |
| 2   | Fixtures committed before the fix, so that the history shows them failing                                          | user (this conversation)                                                              | Fixtures and fix in one commit                                            |
| 3   | Two fixtures: 077 the issue's example verbatim, 078 the edge cases (intra-group flows, flow to a replacer)         | taste                                                                                 | One fixture with everything (less legible as a repro)                     |

| 5 | Fixture 079 dedicated to the self-loop avoidance: the three collapse cases and a genuine self-loop kept | user (at Try it) | Leave the case inside 078 |

## 2. Execution

### 2.1 Account

- `f614d86` docs: this devlog, opened at scaffolding on the user's ask
  (the fast form writes it at closure; here a Try it stop was wanted).
- `4572f3a` test: fixtures 077 (the issue's example) and 078 (edge
  cases), goldens generated with the fix in place; `make nr-test` at
  this commit fails on both (077: cross flows missing; 078: the same,
  plus an `AB -> AB` self-loop rendered). `tests/RULES.md` next number 079. This failing run is the mutation smoke-test.
- `bc349e9` fix: `_apply_filters()` rewrites the ends first, then
  skips when they collapsed to one item. `make format lint test`
  green: 97 pytest, 85 NR fixtures; no existing golden changed.
- `f60add5` test: labels on the flows of both fixtures, asked at the
  review; the fail-before trial redone: both fail at `4572f3a`'s
  code, pass at HEAD. A separate commit rather than a rewrite of
  `4572f3a`, since the branch was pushed (squash is the user's).
- `d1de5f5` test: fixture 079, asked at Try it once the self-loop
  avoidance was confirmed as desired; fails on the pre-fix code (two
  `AB -> AB` rendered). `tests/RULES.md` next number 080. 86 NR
  fixtures green.

Approved: 2026-09-23

## 3. Delivery

### 3.1 Try it

```bash
make nr-review     # SVGs next to the fixtures
xdg-open tests/non-regression/077-filter-replace-two-groups.svg
xdg-open tests/non-regression/078-filter-replace-two-groups-edge.svg
xdg-open tests/non-regression/079-filter-replace-self-loop.svg
git show bc349e9   # the fix, 7 lines changed
git checkout 4572f3a -- src && make nr-test; git checkout HEAD -- src
                   # the fixtures fail before the fix
```

077 renders the issue's expected picture, labels carried: `AB -> CD`,
`AB <- CD`, `AB -> E`, `CD -> E`. 078 renders `AB -> CD` twice ("same
label" once, "other label") and `CD -> AB` ("back"); the four
collapsing flows are gone. 079 renders `E -> E` and `AB -> E` only.

Tried: 2026-09-24 (the demo and a diagram of the user's own)

### 3.2 Verdict

**Recommendation:** accept

- The issue's example now produces the flows it expected; the three
  fixtures fail before the fix and pass after; no other golden moved.

The reservation that stood here (the fix drops the self-loop of a
flow to the replacer, one case beyond the issue) was settled at Try
it: desired, and locked in by fixture 079.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                        | Agent   | User       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---------- |
| 1   | Process and template fit: fast track with a Try it stop added, a hybrid the template does not name; it cost nothing and caught two additions | well    | well       |
| 2   | The issue's hypothesis (a single pass) was wrong; reading the code before scaffolding set the frame right in one round                       | well    | well       |
| 3   | Two loops at Try it (labels, fixture 079) grew the tests in conversation, as the fast track intends                                          | well    | well       |
| 4   | Commits pushed as they came, not squashed per step: nine commits for three steps in the PR list                                              | tension | don't care |

Process: 1 round before the go; 2 loops at Try it; rework after the go: none.

Pascal's note: very satisfied how it went. The "try it" scenario and stop place were very proper.

Closed: 2026-09-24

### 4.2 Rule trace

| Source           | Rule                                         | Verb (applied / created) |
| ---------------- | -------------------------------------------- | ------------------------ |
| `tests/RULES.md` | Mutation smoke-test after adding NR fixtures | applied                  |
