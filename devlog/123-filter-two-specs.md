# 123 — One neighbor specification per filter

Date: 2026-09-25
Status: ONGOING
Issue: #123 · PR: #124 · Branch: `fix/123-filter-two-specs`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 22 (removed in the first commit), found at the stop 1
discussion of #104. Third of the filter batch of 2026-09-25, first
stacked on #121 (PR #122, cancelled at its review; see the Account).
`_parse_filter()` consumed every leading neighbor spec, so `!<1 >2 C`
worked, undocumented and unillustrated, and `!<1 <3 C` silently kept
the last spec. The TODO leaned to documenting the combined form; the
review reversed it.

### 1.2 Goal

A filter takes one neighbor specification, `<>` being one; a second
one is an error. The docs say so and show the two-filter form. README
§ 7.3.3 gives the grammar the parser always had.

### 1.3 Design decisions

| #   | Decision                                                                   | Basis                                                                                                                                                                                                                                                                                        | Alternatives considered                                                                                                                           |
| --- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | One specification per filter; a second is an error, whatever its direction | user (review): a stream direction and a layout direction do not compose (`>` and `]` agree only where the arrows are drawn in the stream's direction); the combined form multiplies the test combinations; two filters with the same items say the same thing; the form was never documented | Document the combined form with a repeat-direction rule (first version of this branch); four walks per filter (stream up/down, layout left/right) |
| 2   | `<>` is one specification                                                  | user (review): it is symmetrical                                                                                                                                                                                                                                                             | Count it as two                                                                                                                                   |
| 3   | README § 7.3.3 reads `DIRECTION[FLAGS]SPAN`                                | review of #122: the README described a form that never parsed                                                                                                                                                                                                                                | Accept both orders (#122, cancelled)                                                                                                              |
| 4   | The findings of the dropped seam fixtures are kept here, not the fixtures  | rule: a fixture locks accepted behavior; the combined form is refused now                                                                                                                                                                                                                    | Keep them as error fixtures (one is enough)                                                                                                       |
| 5   | `[]` is a TODO item (30), not this task                                    | rule: new syntax is a `feat`, held by the merge gate until the pending patch release                                                                                                                                                                                                         | Add it here                                                                                                                                       |

### 1.4 Acceptance criteria

1. `! <1 >2 A`, `! <1 <3 A`, `! >1 ]1 A`, `! <>1 <3 A` raise "One
   neighbor specification per filter"; `! <>1 A` parses.
2. Fixture 091 errors with the message and passes silently on the
   pre-fix parser (mutation smoke-test); fixture 092 shows the
   two-filter form.
3. `make format lint test` green; `tests/RULES.md` next number 093.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 22 removed, filed as #123.
- Second commit (first version): a repeat-direction rule, the combined
  form documented, fixtures 091 (combined) and 092 (repeat error).
- Review of #122: that PR cancelled (only `<>xf2` ever worked; adding
  `<>2xf` was a language extension), this branch rebuilt as `main`
  plus its own change by a revert-style commit, carrying the README
  § 7.3.3 correction.
- Review loop 1: five fixtures at the seams of two specs (`f` on one
  side, `x` on one side, a layout with a stream direction on S2, its
  strict twin, a removal), each failing under the mutation flipping
  its claim. Findings: `x` on either spec was whole-filter, `f` per
  direction, a segment read by both sides counted once. My first draft
  wrote the flags after the span and errored; the channel flows use a
  DOT port, which my first reading of the goldens missed.
- Review loop 2, the reversal: the user's question on `!>1 ]1` (stream
  and layout directions do not compose) led to decision 1. Parser:
  `spec_given`, one message. Docs back to the singular grammar with
  the two-filter example. Fixtures 091 (error) and 092 (two filters)
  replace the seven; unit cases replaced. TODO 30 for `[]`.
- This devlog.

## 3. Delivery

### 3.1 Test report

1. Four parametrized cases raise, the strictness cases still parse
   (criterion 1).
2. `091….stderr` ends with `One neighbor specification per filter;
repeat the filter for another one`; pre-fix parser: `FAIL: 091`
   (recorded below). 092 keeps E2, P2, P3, P5, S1, S2, C2, the union
   of one level upstream and two downstream (criterion 2).
3. 135 pytest, 99 NR fixtures; lint and format clean; RULES.md 093+
   (criterion 3).

### 3.2 Verdict

**Recommendation:** accept

- The rule is one line in the parser, one sentence in each doc, one
  error fixture; every valid diagram renders as before.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                              | Agent    | User |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track, three loops; the draft's leaning was executed before the design question (`>` vs `]`) was asked              | not well |      |
| 2   | The seam fixtures were the right instrument: they proved the combined form consistent, which made the decision to forbid it a choice, not a repair | well     |      |
| 3   | The reversal cost one hour and left no trace in the code; deciding it at the draft would have cost one question                                    | tension  |      |

Process: 1 round before the go; 2 loops at the review; rework after the go: the #122 revert, then the reversal.

Pascal's note: the stop and review was the right call, to allow a deep
questioning of the thing, better late than never. It may read as a
`not well` item at the task's level; at a higher order it served the
product.

Closed: pending

### 4.2 Rule trace

| Source                  | Rule                                                              | Verb (applied / created) |
| ----------------------- | ----------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`        | Mutation smoke-test after adding NR fixtures                      | applied                  |
| `doc/README.md` § 7.3.3 | One neighbors specification per filter; another is another filter | created                  |
