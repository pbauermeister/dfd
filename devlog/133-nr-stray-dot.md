# 133 — The NR runner reports a stray `.dot` of an error fixture

Date: 2026-09-26
Status: ONGOING
Issue: #133 · PR: #134 · Branch: `test/133-nr-stray-dot`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 34 (removed in the first commit), met twice during the
mutation smoke-tests of #127. Third of the batch 31, 29, 34, 35 of
2026-09-26, stacked on #131 (PR #132), base of #135; reviewed second.
Reproduced before the change: a stray `.dot` next to
`053-err-empty-frame.dfd` made `nr-test.sh` exit 1 with no `FAIL:`
line, the tool's error as the last output.

### 1.2 Goal

Neither NR script writes a `.dot` next to an error fixture, and
`nr-test.sh` reports every anomaly as a `FAIL:` line: a stray
`.dot`, an error fixture that succeeds, a plain fixture whose render
fails.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                      | Basis                                                                 | Alternatives considered                                   |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| 1   | Both scripts render error fixtures with `-o` to a scratch path they delete: the root cause is the write beside the input, and `nr-test.sh` had it too         | TODO 34, lesson (a) of #127 (rule)                                    | `rm` the `.dot` after the fact in `nr-regenerate.sh` only |
| 2   | The plain loop of `nr-test.sh` skips `-err-` fixtures; the error loop reports a stray `.dot` as a FAIL with the remedy in the line                            | TODO 34 (rule)                                                        | Delete the stray silently                                 |
| 3   | A render that fails in the plain loop is a FAIL line with the tool's stderr, the run goes on; `set -e` stays for the rest                                     | the silent abort (rule)                                               | Drop `set -e`                                             |
| 4   | Verified first by hand on disposable fixtures, then by a pytest that drives both scripts on a temporary fixture set through an `NR_DIR` override (five cases) | user (review): effective tests; the tracing-prelude test is the model | By-hand scenarios only (the first version)                |
| 5   | One bullet in `tests/RULES.md`: an error fixture has no `.dot`                                                                                                | rule                                                                  |                                                           |

### 1.4 Acceptance criteria

1. Stray `.dot` next to an error fixture: one FAIL naming it, the
   other fixtures still run.
2. An error fixture that succeeds: FAIL in `nr-test.sh`, ERROR and
   exit 1 in `nr-regenerate.sh`, no `.dot` left by either.
3. A plain fixture whose render fails: FAIL with the error, no abort.
4. Clean tree: `make nr-test` green, no scratch file left.

Approved: 2026-09-26 (the go for the batch)

## 2. Execution

### 2.1 Account

- First commit: TODO 34 removed, filed as #133.
- `f4ad604` test: the two scripts and the rule bullet. Scenarios: stray
  `.dot` (1 FAIL, 116 PASS, criterion 1); `998-err-trial.dfd` with a
  valid body, FAIL "expected to fail but succeeded" from `nr-test.sh`,
  ERROR and exit 1 from `nr-regenerate.sh`, no `.dot` after either
  (criterion 2); `000-trial.dfd` with an undeclared flow and an empty
  golden, FAIL "render failed" with the tool's error, 116 PASS after
  it (criterion 3); clean tree, 116 PASS, no `.tmp` (criterion 4).
- This devlog.
- Review loop (2026-09-26): `NR_DIR` overridable in both scripts,
  `tests/test_nr_scripts.py` with the five cases (row 4), an entry in
  `tests/README.md`. The merge of `main` forward re-added TODO item 29
  (the conflict was resolved from `main`'s file); fixed in the same
  commit.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- The two silent paths of the mutation loop (#127, lesson b) now end
  in a FAIL line that names the file.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                                                            | Agent    | User |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track; reproduce first, then five disposable-fixture scenarios in one command                                                                     | well     |      |
| 2   | The TODO named one script; reading both found the same write in the other                                                                                                        | well     |      |
| 3   | The decision "no shell test harness" rested on a false premise: `tests/test_tracing_prelude.py` drives a script already; check the tests folder before ruling a kind of test out | not well |      |

Process: 1 round before the go (the batch assessment); 1 loop at the review (effective tests).

Closed:

### 4.2 Rule trace

| Source           | Rule                                                     | Verb (applied / created) |
| ---------------- | -------------------------------------------------------- | ------------------------ |
| `tests/RULES.md` | Mutation smoke-test after changing fixtures              | applied (the scenarios)  |
| `tests/RULES.md` | An error fixture has no `.dot`; a stray one is a failure | created                  |
