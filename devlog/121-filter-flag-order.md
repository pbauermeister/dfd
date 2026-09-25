# 121 — Filter flags on either side of the span

Date: 2026-09-25
Status: ONGOING
Issue: #121 · PR: #122 · Branch: `fix/121-filter-flag-order`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 21 (removed in the first commit), found at the stop 0 review
of #104. Second of the filter batch of 2026-09-25 (20, 21, 22, 23),
stacked on #119 (PR #120). Before: README § 7.3.3 said
`DIRECTION[SPAN][FLAGS]`, while SYNTAX.md § 7.3, the regex and the six
examples (README § 7.4.1.8 and § 7.4.1.9, fixtures 032, 033, 043, 044)
put the flags first.

### 1.2 Goal

The parser accepts the flags on either side of the span; the docs give
the documented order `DIRECTION SPAN [FLAGS]` and say the former one
stays accepted; the six examples read `<>2x` and `<>2xf`; one fixture
locks the former order.

### 1.3 Design decisions

| #   | Decision                                                                          | Basis                                                                          | Alternatives considered                            |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------- |
| 1   | Two flag groups in the regex, before and after the span, concatenated             | TODO 21: the documented order is the logical one; the former must keep working | Reject the former order (breaks existing diagrams) |
| 2   | A split (`<>x2f`) is accepted, undocumented                                       | user (the go): a rule against it costs code for nothing                        | An error on the split                              |
| 3   | The six examples migrate; fixture 090 keeps the former order, same picture as 033 | rule: fixtures lock both accepted forms                                        | Leave the fixtures as they were                    |

### 1.4 Acceptance criteria

1. Unit: `<>2xf`, `<>xf2`, `<>x2f` parse to the same neighbors.
2. Goldens of 032, 033, 043, 044 unchanged by the migration; 090 equals
   033's but for the title; on the pre-fix parser the migrated fixtures
   fail (mutation smoke-test).
3. `make format lint test` green; `tests/RULES.md` next number 091.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 21 removed, filed as #121.
- `f80238a` fix: the regex (`flags_before`, `flags`), the docs (README
  § 7.3.3 note, SYNTAX.md § 7.3 grammar, note and example), the six
  migrations, fixture 090, the unit case per order.
- This devlog.

## 3. Delivery

### 3.1 Test report

1. `test_parse_filter_flags_either_side_of_span`, three cases green
   (criterion 1).
2. `make nr-regenerate`: the four `.dot` goldens untouched; `diff 033
090`: the title line only. Pre-fix parser: `make nr-test` stops at
   032 with `Name(s) unknown: <>2x`, exit 2 (criterion 2).
3. 134 pytest, 97 NR fixtures; lint and format clean; RULES.md 091+
   (criterion 3).

### 3.2 Verdict

**Recommendation:** accept

- Both orders proven by fixtures, the docs agree with each other and
  with the parser.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                         | Agent | User |
| --- | --------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track; the doc discrepancy listed in the TODO made it one pass | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source           | Rule                                         | Verb (applied / created) |
| ---------------- | -------------------------------------------- | ------------------------ |
| `tests/RULES.md` | Mutation smoke-test after adding NR fixtures | applied                  |
