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

| #   | Decision                                                                                                             | Basis                          | Alternatives considered                   |
| --- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------- |
| 1   | `[]` sets both directions with `layout_direction`; one alternative in `RX_FILTER_ARG`, one case in the match         | TODO 30 (rule)                 | A second regex group for the layout forms |
| 2   | Nothing else in the grammar moves: an unknown direction (`<]`) still fails as an unknown item name                   | TODO 30 (rule)                 | A dedicated error for a bad direction     |
| 3   | Parser unit test over the five directions, one parametrized case each; NR fixture 110 `![]2 S2` on the filter master | `tests/README.md` (rule)       | The fixture alone                         |
| 4   | Distance 2 for the fixture: at 1, `[]` and `<>` keep the same set (every adjacent item), the reversals show at 2     | measured (see Account)         | Distance 1, `*`                           |
| 5   | README § 7.3.3 gains the form in the list and the "counts as one" sentence; SYNTAX.md § 7.4 the table cell           | TODO 30 (taste): no new figure | An example in § 7.4.1.2                   |

### 1.4 Acceptance criteria

1. `![]2 S2` on the filter master keeps `[2 S2` ∪ `]2 S2` and differs
   from `<>2 S2`.
2. Flags and span apply as with `<>`: `[]xf*` parses to both sides,
   anchors suppressed, frames suppressed, unlimited.
3. `<]2` and `[]` with a second specification fail as before.
4. `make format`, `make lint`, `make test` pass; the mutation
   smoke-test fails fixture 110 and the unit test.

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

Process: 1 round before the go (the batch assessment); 0 loops.

Closed: pending

### 4.2 Rule trace

| Source            | Rule                                                      | Verb (applied / created) |
| ----------------- | --------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`  | Mutation smoke-test after adding an NR fixture            | applied                  |
| `tests/README.md` | Unit test for the parser, NR fixture for the nominal case | applied                  |
