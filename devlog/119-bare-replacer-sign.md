# 119 — A bare replacer sign in a filter is an error, not a hang

Date: 2026-09-25
Status: DONE
Issue: #119 · PR: #120 · Branch: `fix/119-bare-replacer-sign`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 20 (removed in the first commit), found while mocking up
#104. First of a batch of four filter tasks decided in one
conversation on 2026-09-25 (20, 21, 22, 23), each branch stacked on
the previous one; fixtures numbered 089 onward.

### 1.2 Goal

`~= G B` (a space after `=`) raises "Replacer name expected right
after '='" instead of spinning in `_parse_filter()`; a parse-error
unit case and an `-err-` fixture lock it.

### 1.3 Design decisions

| #   | Decision                                                                                       | Basis                                                                                           | Alternatives considered                                                 |
| --- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1   | Test the `replacer` group for `None`, raise on an empty one                                    | TODO 20, confirmed in the code: the falsy empty group left the argument unconsumed              | Change the regex to require one character after `=` (loses the message) |
| 2   | The unit case joins the existing `PARSE_ERROR_CASES`, not `CHECK_ERROR_CASES` as the TODO said | rule: the error is raised by `parse()`, which `test_check_raises` calls outside `pytest.raises` | A dedicated test (done first by mistake, duplicated an existing one)    |

### 1.4 Acceptance criteria

1. Fixture 089 errors with the message; against the pre-fix parser it
   hangs (mutation smoke-test, `tests/RULES.md`).
2. `make format lint test` green; `tests/RULES.md` next number 090.

Approved: 2026-09-25

## 2. Execution

### 2.1 Account

- First commit: TODO 20 removed, filed as #119.
- `de41659` fix: the `None` test and the message; fixture 089 and its
  golden; the unit case. Pushed with a lint error: my parse-error test
  duplicated an existing `test_parse_raises` (F811).
- `f6005d6` test: the case folded into the existing list.
- This devlog.
- Review (2026-09-25): the replacer group bound once with a walrus,
  used three times (asked in the review).

## 3. Delivery

### 3.1 Test report

1. `make nr-regenerate` wrote `089-err-filter-bare-replacer-sign.stderr`
   with the message. With `parser.py` of the previous commit checked
   out, `timeout 10 ./data-flow-diagram 089….dfd -f dot` exits 124
   (criterion 1).
2. 131 pytest, 96 NR fixtures; lint and format clean; `tests/RULES.md`
   says 090+ (criterion 2).

### 3.2 Verdict

**Recommendation:** accept

- A one-condition fix, proven both ways.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                           | Agent    | User     |
| --- | ----------------------------------------------------------------------------------------------- | -------- | -------- |
| 1   | Process and template fit: fast track for a diagnosed one-liner                                  | well     | well     |
| 2   | Lint was run before the commit but its exit was not read; the duplicate test reached the remote | not well | not well |

Process: 1 round before the go; no loop; rework after the go: the test placement.

Closed: 2026-09-25

### 4.2 Rule trace

| Source                 | Rule                                         | Verb (applied / created) |
| ---------------------- | -------------------------------------------- | ------------------------ |
| `tests/RULES.md`       | Mutation smoke-test after adding NR fixtures | applied                  |
| `engineering/RULES.md` | format, lint, test before pushing            | applied (late)           |
