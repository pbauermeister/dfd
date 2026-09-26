# 131 — Git hooks run `make lint` at commit and `make test` at push

Date: 2026-09-26
Status: DONE
Issue: #131 · PR: #132 · Branch: `build/131-lint-test-hooks`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 29 (removed in the first commit), raised at the review of
#120: a commit with a `ruff` F811 reached the remote because the agent
ran `make lint` and did not read its exit. Second of the batch 31, 29,
34, 35 of 2026-09-26, off `main`, base of #133 and #135; reviewed
first. Measured before the go: `make lint` 0.46 s with a warm mypy
cache, 3.3 s cold; `make test` 9.9 s.

### 1.2 Goal

The rule "format, lint, test before pushing" of `engineering/RULES.md`
is mechanical: a commit that fails `make lint` and a push that fails
`make test` are refused by git hooks that `make require` installs.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                    | Basis                                                                                | Alternatives considered                       |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------- |
| 1   | Two local hooks in `.pre-commit-config.yaml`, `make lint` at the `pre-commit` stage and `make test` at `pre-push`; `make require` installs the three stages | user (the go); the framework was installed for `commit-msg` already                  | A `ruff`-only hook; CI as a required check    |
| 2   | The whole `make lint`, on every commit: format check, mypy and the list checks come with it at 0.5 s                                                        | measured (rule)                                                                      | Filter on staged `.py` files                  |
| 3   | `make test` at push, 10 s: the rule names it, and the unread-exit slip applies to tests as to lint                                                          | user (the go)                                                                        | Lint only, tests left to CI                   |
| 4   | CI stays a non-required check                                                                                                                               | `engineering/RELEASING.md` "Bookkeeping commits": a bookkeeping push starts no run   | Required CI, with a `paths-ignore` workaround |
| 5   | `UV_NO_SYNC=1` in the hook entries: a hook never rewrites the environment or `uv.lock`                                                                      | the `--no-sync` of the bookkeeping hook (#107): a release commit changes the version | Plain `make lint`                             |
| 6   | The rule stays in `RULES.md` for the agent and names the hooks: a hook can be skipped with `--no-verify`, and the agent reads exits                         | rule                                                                                 | Drop the manual rule                          |
| 7   | Type `build:`, patch: dev tooling ships no code                                                                                                             | #115 precedent                                                                       | `chore:`                                      |

### 1.4 Acceptance criteria

1. A staged file with a `ruff` F811 is refused at commit; the same
   commit passes without it.
2. A push runs `make test` and passes on a green tree.
3. `make require` installs the three stages.

Approved: 2026-09-26 (the go for the batch)

## 2. Execution

### 2.1 Account

- First commit: TODO 29 removed, filed as #131.
- `b96f955` build: the two hooks, the install line, the rule text.
  The first trial commit was refused for the wrong reason (the hook
  config itself was unstaged), the second, after the config was
  committed, by `make lint` with F811 and F401 on the trial file
  (criterion 1). Its push ran `make test` in 13 s (criterion 2). The
  three stages installed by the `make require` line (criterion 3).
- This devlog, through both hooks.
- Review loop (2026-09-26): the test report above, the failing-test
  trial at push added to the failing-lint one at commit.

## 3. Delivery

### 3.1 Test report

Trials on this branch, 2026-09-26, at the review's request; the trial
commits were undone, the branch holds none of them.

1. A staged `src/data_flow_diagram/_trial.py` with `import os` twice,
   `git commit`: refused, exit 1, `HEAD` unchanged (criterion 1).

   ```
   make lint................................................................Failed
   F811 [*] Redefinition of unused `os` from line 1
   F401 [*] `os` imported but unused
   ```

2. A committed `tests/unit/test_trial.py` asserting `False` (lint
   passes, the commit goes through), `git push`: refused, exit 1, the
   remote branch unchanged (criterion 2, the refusal side).

   ```
   make test................................................................Failed
   FAILED tests/unit/test_trial.py::test_trial - AssertionError: a trial failure
   error: failed to push some refs to 'github.com:pbauermeister/dfd.git'
   ```

3. The commit of this report and its push: both hooks `Passed`
   (criteria 1 and 2, the passing side).
4. Observed on the other branches of the batch: pre-commit reads the
   hook config of the checkout, so a branch without this PR's config
   runs the `commit-msg` hooks only and nothing at push. The hooks
   cover every branch once this PR is merged forward.

### 3.2 Verdict

**Recommendation:** accept

- The case of TODO 29 is refused at commit; the cost is half a second
  per commit, ten seconds per push.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                               | Agent | User |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track, decisions from the batch assessment, one measurement settled the whole-lint question          | well  | well |
| 2   | A negative trial that exits non-zero is not yet a proof: read why it failed (the first refusal was the framework's, not the lint's) | well  | well |

Process: 1 round before the go (the batch assessment); 1 loop at the review (the trials made visible).

Closed: 2026-09-26

### 4.2 Rule trace

| Source                 | Rule                                         | Verb (applied / created)  |
| ---------------------- | -------------------------------------------- | ------------------------- |
| `engineering/RULES.md` | Format, lint before commit, test before push | created (made mechanical) |
