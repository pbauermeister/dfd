# 123 — Two neighbor specs in one filter

Date: 2026-09-25
Status: ONGOING
Issue: #123 · PR: #124 · Branch: `fix/123-filter-two-specs`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 22 (removed in the first commit), found at the stop 1
discussion of #104. Third of the filter batch of 2026-09-25, first stacked
on #121 (PR #122, cancelled at its review; see the Account). `_parse_filter()` already consumed every leading
neighbor spec, so `!<1 >2 C` worked, undocumented, and `!<1 <3 C`
silently kept the last spec.

### 1.2 Goal

The combined form is documented, one spec per direction; a direction
given twice is an error; the reach of the flags and of strictness is
stated from the code.

### 1.3 Design decisions

| #   | Decision                                                                                                           | Basis                                                                                      | Alternatives considered                           |
| --- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| 1   | Document the combined form and refuse a repeated direction                                                         | user (the go), the TODO's leaning: it exists and is harmless                               | Reject any second spec                            |
| 2   | `<>` counts for both directions: `<>1 <3` is a repeat                                                              | user (the go)                                                                              | The later spec overrides                          |
| 3   | Doc statements from the code: `x` on either spec is whole-filter; `f` per direction and anchors; `!!` whole-filter | rule: read off `_collect_kept_names()` and `_collect_frame_skips()`                        | The TODO's note (which said `f` was whole-filter) |
| 4   | Fixture 091 is proven equivalent to the two single-spec filters, titles aside                                      | rule: the doc says "as `!<1 P` followed by `!>2 P` would"; a claim is checked, not written | Trust the reading of the code                     |

### 1.4 Acceptance criteria

1. `! <1 >2 A` parses to up 1, down 2; `<1 <3`, `>1 >3`, `<>1 <3`,
   `[1 <3` raise.
2. Fixture 091 renders as the two filters would; 092 errors "Upstream
   neighbors specified twice", and passes silently on the pre-fix
   parser (mutation smoke-test).
3. `make format lint test` green; `tests/RULES.md` next number 093.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 22 removed, filed as #123.
- `8de1ca9` fix: `up_given`/`down_given` in the loop, two messages;
  README § 7.3.1, § 7.3.2 grammar and a § 7.3.3 paragraph; SYNTAX.md
  § 7.1, § 7.2 grammar and a § 7.3 sentence; fixtures 091, 092; five
  unit cases.
- This devlog.
- Review of #122 (2026-09-25): that PR was cancelled (only `<>xf2`
  ever worked; adding `<>2xf` was a language extension for a gain of
  taste), so this branch drops its commits by a revert commit, the
  squash keeping the net diff; it carries the one-line correction of
  README § 7.3.3 instead: `DIRECTION[FLAGS]SPAN`, the grammar the
  parser and SYNTAX.md always had. Fixture 090 is gone; 091 and 092
  keep their numbers.

## 3. Delivery

### 3.1 Test report

1. Five unit cases green (criterion 1).
2. `091….dot` against a scratch diagram with `!<1 P2` then `!>2 P2`:
   identical but for the title lines. Pre-fix parser: `FAIL: 092`, its
   stderr empty, exit 2 (criterion 2).
3. 139 pytest, 99 NR fixtures; lint and format clean; RULES.md 093+
   (criterion 3).

### 3.2 Verdict

**Recommendation:** accept

- Behavior unchanged for every valid diagram; the silent overwrite is
  now an error; the doc says what the code does.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                  | Agent | User |
| --- | ------------------------------------------------------------------------------------------------------ | ----- | ---- |
| 1   | Process and template fit: fast track; the decision was taken from the draft in one line                | well  |      |
| 2   | The TODO's note on `f` was wrong; reading the two functions before writing the doc paragraph caught it | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                  | Rule                                               | Verb (applied / created) |
| ----------------------- | -------------------------------------------------- | ------------------------ |
| `tests/RULES.md`        | Mutation smoke-test after adding NR fixtures       | applied                  |
| `doc/README.md` § 7.3.3 | Two specs, one per direction; a repeat is an error | created                  |
