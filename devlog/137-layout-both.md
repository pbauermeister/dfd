# 137 — A symmetrical layout neighborhood `[]`

Date: 2026-09-26
Status: ONGOING
Issue: #137 · PR: #140 · Branch: `feature/137-layout-both`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 30 (raised at the review of #124, removed by the filing
commit of the batch). First of the batch 30, 28, 36 of 2026-09-26,
off `main`, reviewed first. Since #123 a filter takes one
neighborhood specification, and `[1` then `]1` on the same items are
two `Only` filters that intersect, so the two-sided layout
neighborhood had no form at all.

### 1.2 Goal

`[]` is to `[` and `]` what `<>` is to `<` and `>`: one filter keeps
the items and their neighbors on both sides in the layout direction,
with the same flags and span. Documented next to `<>`.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                                                                                                                                                                                                                                           | Basis                                                    | Alternatives considered                   |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------- |
| 1   | `[]` sets both directions with `layout_direction`; one alternative in `RX_FILTER_ARG`, one case in the match                                                                                                                                                                                                                                                                       | TODO 30 (rule)                                           | A second regex group for the layout forms |
| 2   | Nothing else in the grammar moves: an unknown direction (`<]`) still fails as an unknown item name                                                                                                                                                                                                                                                                                 | TODO 30 (rule)                                           | A dedicated error for a bad direction     |
| 3   | Parser unit test over the five directions, one parametrized case each; NR fixture 110 `![]2 S2` on the filter master                                                                                                                                                                                                                                                               | `tests/README.md` (rule)                                 | The fixture alone                         |
| 4   | Distance 2 for the fixture: at 1, `[]` and `<>` keep the same set (every adjacent item), the reversals show at 2                                                                                                                                                                                                                                                                   | measured (see Account)                                   | Distance 1, `*`                           |
| 5   | README § 7.3.3 gains the form in the list and the "counts as one" sentence; SYNTAX.md § 7.4 the table cell                                                                                                                                                                                                                                                                         | TODO 30 (taste): no new figure                           | An example in § 7.4.1.2                   |
| 6   | Review loop: a matrix master (111 part) of five A→B→C chains drawn in the four arrow combinations plus a constraint, fixtures 111 (`[]2`) and 112 (`<>2` twin), 110 kept; span 2 because span 1 keeps every adjacent item in both forms                                                                                                                                            | review of #140 (rule); measured before writing           | Distance-1 cases; one fixture per chain   |
| 7   | Second loop: the master is a fixture itself, `111-filter-layout-matrix.master.dfd` with its golden, so that the review renders it; the rule codified in `tests/RULES.md` and `tests/README.md` (028 stays a `.part`, 093 predates the name)                                                                                                                                        | review of #140, the same remark at #127 (rule created)   | Keep the `.part` and render it by hand    |
| 8   | Third loop: the matrix replaced by a 5 x 5 grid master (111) in the vertical style of the #104 playground, columns constrained, rows relaxed, rows 2 and 4 and columns 2 and 4 flowing against the drawing, the two diagonals through N33; nine fixtures 112 to 120: `[]` keep and remove at spans `*`, 1, 2 from the center, the `<>2` twin, keep and remove from the two corners | review of #140 (rule); layout measured over ten variants | All diagonals (busy); labels on 48 flows  |

### 1.4 Acceptance criteria

1. `![]2 S2` on the filter master keeps `[2 S2` ∪ `]2 S2` and differs
   from `<>2 S2`.
2. Flags and span apply as with `<>`: `[]xf*` parses to both sides,
   anchors suppressed, frames suppressed, unlimited.
3. `<]2` and `[]` with a second specification fail as before.
4. `make format`, `make lint`, `make test` pass; the mutation
   smoke-test fails fixture 110 and the unit test.
5. Third loop: the grid master renders as a 5 x 5 grid (no order
   violation in the node positions); from N33, `[]*` and `[]2` keep
   all but N25 and N41, `[]1` the 3 x 3 around the center, the
   removals are their complements; `<>2` keeps 21 items, a different
   set; the mutation fails every `[]` fixture and leaves 118.

Approved: 2026-09-26 (the go for the batch)

## 2. Execution

### 2.1 Account

- `f504ae5` feat: parser, unit test, fixture 110, both docs. Kept sets
  measured before choosing the fixture's span, `S2` as anchor:

  | Spec  | Kept                                |
  | ----- | ----------------------------------- |
  | `[]1` | P2 P3 P4 P5 S2 (same as `<>1`)      |
  | `[2`  | P2 S1 S2                            |
  | `]2`  | E2 P3 P4 P5 P6 S2                   |
  | `[]2` | E2 P2 P3 P4 P5 P6 S1 S2 (the union) |
  | `<>2` | C1 C2 E2 P2 P3 P4 P5 S2             |

  The render of 110 read: the frame-1 channels are out, reachable
  only against the drawing. Mutation (`case "[]"` renamed): fixture
  110 FAIL, two unit cases fail; reverted. A first README paragraph
  restating the two kinds of neighborhood was dropped, § 7.4.1.2
  has it with a figure.

- This devlog.
- Review loop (2026-09-26): prettier pass on `doc/SYNTAX.md` (the
  table); the matrix master and fixtures 111 and 112, kept sets
  measured in the scratchpad first (111: A1..A5 B1..B5 C1 C4; 112:
  the same plus C2 C3); TODO item 37 for the combinatorial matrix of
  all filters, with the reservation that expected outputs cannot be
  generated without re-implementing the search. Mutation reverted by
  its inverse `sed` this time, parser diff against HEAD empty after.
- Second loop (2026-09-26): the master renamed to a `.master.dfd`
  fixture with its golden, the rule written in `tests/RULES.md` and
  `tests/README.md`; the devlog lines of this loop landed one commit
  late, an edit script stopped on a table re-padded by prettier.
- Third loop (2026-09-26): the review asked for a 5 x 5 matrix with
  horizontal, vertical and diagonal flows, some inverted, the
  vertical and diagonal ones relaxed, filters on the center at three
  spans and on several items. Measured first: relaxed verticals and
  diagonals in the horizontal layout let Graphviz permute the rows as
  soon as one diagonal exists (10 order violations with the four
  center diagonals, 5 with the two full ones); all 32 diagonals
  relaxed keep the shape by symmetry but the render is unreadable;
  the vertical style with constrained columns, relaxed rows and
  constrained diagonals (a diagonal to the next row agrees with the
  ranks) keeps the shape, as the #104 grid did; relaxed diagonals in
  that style break the columns. So the diagonals are constrained,
  against the letter of the request and for its intent. A filtered
  render is no longer a grid (#104 noted it). Fixtures 111 and 112 of
  the second loop deleted, numbers reused since never merged; the
  disposable folder refreshed with the goldens rendered by `dot`.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- Criteria 1 to 4 met: the table above, the parametrized test, the
  unchanged error paths, 154 tests green and the mutation caught.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                               | Agent    | User |
| --- | ------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track, three files of substance, one commit                                          | well     |      |
| 2   | Measuring the kept sets first chose the span; the item's "two filters" wording was wrong, `Only` filters intersect  | well     |      |
| 3   | Reverting the mutation with `git checkout` took the feature edit with it; a mutation is reverted by its own inverse | not well |      |

| 4 | The review asked for the cases the item did not name (drawn with and against the flow, a constraint); the matrix master answered them in one diagram that reads as rows | well | |

Process: 1 round before the go (the batch assessment); 3 loops at the review (the matrix fixtures, the master as a fixture, the 5 x 5 grid).

Closed: pending

### 4.2 Rule trace

| Source            | Rule                                                                          | Verb (applied / created) |
| ----------------- | ----------------------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`  | Mutation smoke-test after adding an NR fixture                                | applied                  |
| `tests/README.md` | Unit test for the parser, NR fixture for the nominal case                     | applied                  |
| `tests/RULES.md`  | A shared master is a fixture itself, `NNN-<topic>.master.dfd` with its golden | created                  |
