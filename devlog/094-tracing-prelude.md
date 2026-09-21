# 094 — Tracing prelude without aliases (DEBUG trap)

Date: 2026-09-21
Status: DONE
Issue: #94 · PR: #95 · Branch: `refactor/94-tracing-prelude`
Task nature: refactor
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 16, issue #94; brief with the candidate prelude, its trials
and the migration in `discussions/tracing-prelude-debug-trap.md`
(from #90). The helpers of `tools/init-tracing.sh` (`echo`, `banner`,
`banner2`, `step`) are aliases carrying a `;`: as an operand of `||`
or `&&`, or inside `$(...)`, the second command runs unconditionally
and `set -u` fails on `save_flags`. Bit #88 in `$(...)` and #90 in
the fallbacks of `recipes/require-system.sh` (CI run 35513228401);
workaround in place: `printf` in list context and a rule in the
prelude header. Six scripts source the prelude (`recipes/doc.sh`,
`release.sh`, `require-system.sh`, `publish-to-pypi.sh`,
`publish-to-testpypi.sh`, `tools/test-installation.sh`); the two
publishing recipes carry `#!/bin/sh`.

### 1.2 Goal

`echo`, `banner`, `banner2` and `step` are plain shell functions,
usable anywhere a command is: after `||` and `&&`, inside `$(...)`,
in an `if` condition, with a redirection. A `DEBUG` trap turns
tracing off just before a helper runs and the helper turns it back on
when it returns, so their trace lines are hidden as today. The "never
in list context" rule is gone from the prelude header and the `printf`
workaround from `recipes/require-system.sh`. The trace of every other
command is unchanged. The prelude is sourced by recipes only: tracing
is the orchestrator's view, a tool prints what it decides to print;
`tools/test-installation.sh` stops sourcing it. TODO item 16 is done
and the discussion's status is DONE.

### 1.3 Non-goals

- POSIX `sh` compatibility: the prelude uses `DEBUG`, `BASH_COMMAND`
  and `functrace`, so it is bash only; the two `#!/bin/sh` recipes
  switch to `#!/bin/bash`. The Makefile already runs bash.
- Changing call sites beyond the two `printf` fallbacks: no sourcing
  script uses a helper in list context today (grep in #90).
- The script-level and naming rules of #90: the prelude stays
  `tools/init-tracing.sh`, sourced mechanics only.
- Tracing or helpers for tools, bash or Python: a tool is not an
  orchestrator; a flood of trace lines makes its output unusable.
- Moving the prelude out of `tools/`: #90 placed sourced mechanics
  there, and only its readers change.

### 1.4 Invariants

- Script levels and calling directory (`doc/CONVENTIONS.md`, "Script
  levels", "Calling directory"): the prelude holds sourced mechanics
  only and is sourced as `. ./tools/init-tracing.sh`.
- `set -e -u -o pipefail` and `set -x` stay in force in every sourcing
  script; the output of every non-helper command, trace line included,
  is byte-identical before and after.
- A helper prints what it printed before (same text, same blank
  lines) and never leaves tracing in a state other than the one it
  found. `echo` behaves as the builtin everywhere, in a pipeline
  included: a strange bug when someone pipes it all the same is worse
  than a rule.
- Every recipe parses (`bash -n`) and runs as before;
  `tools/test-installation.sh` runs standalone with the same options
  and message texts; CI (`ci.yml`, `merge-gate.yml`) stays green.

Framed: 2026-09-21

### 1.5 Taste

- Recalled (#90): established mechanism over bespoke trick when
  measured equal; the prelude stays a single sourced file.
- Recalled (#88, #90): a defect that bit twice deserves a guard that
  fails on its return, not a rule in a comment.
- Stated (2026-09-21, after the mock-up): tracing belongs to `recipes/`,
  the orchestrators; `tools/` may do detailed things where tracing
  floods the output, so they neither source the prelude nor trace.
- Stated (2026-09-21): tools do print their titles and phases, in a
  lighter markup than recipes, so that the level of a line is readable
  in the output.

### 1.6 Set-based design

Triggers: an intent inherited from a prior task (the brief's candidate
from #90); one conceptual row (the trap) among mechanical churn (two
shebangs, two `printf`).
Mock-up: yes, the brief's candidate in a throwaway worktree, run on
the brief's trial script extended with a redirection, a pipeline, an
`if` condition, a brace group after `||` and a user function.
Design question: in `echo "piped" | cat` the trap fires in the parent
shell for each element before the fork (probed: `BASH_SUBSHELL=0` for
both), so `echo` turns tracing off in the parent and only the subshell
restores it; the parent stays untraced until the next helper. The
brief's trials did not cover pipelines.
Options: three preludes, same trial script, outputs diffed.

| Option | What differs                                                                                                                                         | For                                                                                                                                 | Against                                                                               |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 1      | The brief's candidate: the trap turns tracing off, each helper restores it as its last command                                                       | 29 lines, trialed in the brief                                                                                                      | Loses the trace after a pipeline (`+ cat`, `+ true` missing); needs a documented rule |
| 2      | Option 1 plus a self-heal: the trap also restores tracing before the next command outside a helper                                                   | Passes every case                                                                                                                   | 33 lines, two restore paths for one state                                             |
| 3      | The trap owns the state: off before a helper, on before the next command outside one; helpers only print; `echo` stays the builtin (**recommended**) | Passes every case, output identical to option 2; 28 lines; no `_restore_`, no `echo` function, the brief's two subtleties disappear | `FUNCNAME` scan on every command (measured, § 1.7)                                    |

Decisive slice, the diff of option 1 against option 3 on the trial
(options 2 and 3 are identical):

```
23a24
> + cat
24a26
> + true
```

Option 3, the trap:

```bash
_quiet_() {  # DEBUG trap, before every command
    case "$BASH_COMMAND" in
        echo|echo\ *|banner\ *|banner2\ *|step\ *)  # a helper: tracing off, once
            case "$-" in *x*) _saved_flags_="$-"; set +x ;; esac ;;
        *)  case " ${FUNCNAME[*]} " in  # inside a helper: leave it off
                *" banner "*|*" banner2 "*|*" step "*) ;;
                *) case "${_saved_flags_-}" in *x*) _saved_flags_=""; set -x ;; esac ;;
            esac ;;
    esac
}
trap '{ _quiet_; } 2>/dev/null' DEBUG
set -o functrace  # the trap also fires inside functions, $(...) and pipelines
set -x
```

### 1.7 Spikes

All run in the throwaway worktree with option 3, bash 5.2.21:

- `recipes/require-system.sh` with fake `sudo`, `apt`, `curl` on the
  PATH: apt present and succeeding, no fallback line; apt hidden by a
  fake `which`, the fallback line printed once; `sudo apt` failing, the
  fallback line printed once. Exit 0 in all three.
- `bash -n` on the six sourcing scripts and the prelude: all parse.
- A reduced trial (helpers in plain context only) under the old and
  the new prelude: outputs byte-identical.
- Overhead: 2000 `true` in a loop, 0.17 s with the trap against 0.014 s
  without, about 80 µs per command. A recipe runs dozens of commands
  and its `uv` steps take seconds: irrelevant.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                          | Basis                                                                          | Alternatives considered                                                                     |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 1   | DEBUG trap owning the tracing state; helpers are plain printing functions; `echo` stays the builtin                                                               | option 3                                                                       | Options 1 and 2 (§ 1.6)                                                                     |
| 2   | Prelude bash only; `#!/bin/bash` on the two `sh` recipes                                                                                                          | rule: Makefile `SHELL := /bin/bash`                                            | Keep `sh` shebangs (they would fail on `trap DEBUG`)                                        |
| 6   | Prelude sourced by recipes only; `tools/test-installation.sh` sets its own options, prints with `echo`; the rule is one sentence in the Script levels convention  | taste: tracing is the orchestrator's view                                      | Keep the tool sourcing it (a tool that traces); a helper-only prelude for tools (YAGNI)     |
| 7   | Tool markup: `--- title ---` for the title, `-- phase` for a phase, a blank line before each, plain `echo`; recipes keep the boxes and `====`                     | taste: level readable in the output                                            | Same helpers in tools (levels indistinguishable); a helper file for tools (YAGNI, one tool) |
| 8   | Internals namespaced `_tracing_quiet_`, `_tracing_box_`, `_tracing_saved_flags_`; the variable initialized to empty and `export -n` at load; public API unchanged | taste: no shadowing of a caller's or a child's variable, provable not probable | Bare `_saved_flags_` (private by convention only; an exported homonym would leak)           |
| 3   | `printf` back to `echo` in the two fallbacks                                                                                                                      | taste: uniformity                                                              | Keep `printf` (works; leaves a trace of the workaround)                                     |
| 4   | A pytest integration test runs the trial script and compares the full output to an expected text                                                                  | taste: guard for a defect that bit twice                                       | Trial in the job scratch folder only (nothing fails when the next prelude regresses)        |
| 5   | The trial's expected output avoids machine-dependent commands (`true`, `false`, `ls` only)                                                                        | rule: tests deterministic                                                      | Keep `uv --version` (version drift)                                                         |

### 1.9 Acceptance criteria

1. The trial script under `tests/` prints the expected output: no
   `+ echo`/`+ banner`/`+ step`/`+ set` lines; `||` fires only on
   failure, `&&` only on success; `$(...)`, redirection, pipeline,
   `if` condition, brace group, user function all traced as before
   the helper and after it; exit code propagates.
2. `bash -n` passes on the five sourcing recipes, the prelude and
   `tools/test-installation.sh`; `grep -l init-tracing tools/*.sh` lists
   the prelude only.
3. `recipes/require-system.sh` with fake `apt`/`sudo`: fallback line
   only when `which apt` or `sudo apt` fails, once.
4. `make smoke-test-wheel` passes (it runs `tools/test-installation.sh`,
   which sources the prelude).
5. No `alias`, `shopt`, `printf` workaround or list-context rule
   remains: `grep -n 'alias\|shopt\|printf' tools/init-tracing.sh recipes/*.sh` is empty.
6. `make format lint test` pass; CI green on the PR.
7. TODO item 16 struck through with `DONE (#94)`; the discussion's
   status is DONE.

## 2. Plan

### 2.1 Steps

Steps 1 and 2 share one step gate.

**Step 1 — Prelude, call sites, docs** (`refactor:`)

Files: `tools/init-tracing.sh`, `recipes/publish-to-pypi.sh`,
`recipes/publish-to-testpypi.sh`, `recipes/require-system.sh`,
`tools/test-installation.sh`, `doc/CONVENTIONS.md`, `TODO.md`,
`discussions/tracing-prelude-debug-trap.md`.

Actions:

1. Replace `tools/init-tracing.sh` by option 3 (header comment:
   purpose, the trap in two sentences, bash only, sourcing line).
2. `#!/bin/sh` → `#!/bin/bash` in the two publishing recipes.
3. `printf "%s\n"` → `echo` in the two fallbacks of `require-system.sh`.
4. `tools/test-installation.sh`: the sourcing line becomes
   `set -e -u -o pipefail`; its two `banner2` lines become
   `echo; echo "--- ... ---"`, its three `step` lines `echo; echo "-- ..."`,
   same texts.
5. `doc/CONVENTIONS.md`, Script levels: after the prelude sentence,
   "Recipes source it, and they are bash: tracing is the orchestrator's
   view. A tool never traces; it prints its title as `--- title ---`
   and its phases as `-- phase`, lighter than the recipes' banners, so
   that the level of a line is readable in the output."
6. `TODO.md` item 16 → `~~...~~ — DONE (#94)`; discussion status → DONE,
   with a one-line pointer to this devlog under its section 5
   (pipeline finding, option 3 chosen, recipes-only sourcing).
7. Sweep: the grep of criterion 5, plus `grep -rn 'init-tracing' --exclude-dir=devlog --exclude-dir=.venv .` for stale mentions.

Verify: criteria 2, 3, 4, 5; the mock-up trial from the scratch
folder gives the option 3 output; `make format lint test`.

Commit: `refactor: tracing prelude as a DEBUG trap, sourced by recipes only`

**Step 2 — Prelude test** (`test:`)

Files: `tests/test_tracing_prelude.py`, `tests/tracing-prelude/trial.sh`,
`tests/tracing-prelude/expected.txt`, `tests/README.md`.

Actions:

1. Read `tests/README.md`; classify: integration, nominal plus
   robustness (list contexts); add the file to its section 2 listing
   if the README enumerates files.
2. `trial.sh`: the § 1.6 trial with `uv --version` replaced by `true`;
   sourced prelude, run from the repository root.
3. `expected.txt`: the output of the mock-up, stdout and stderr merged.
4. The test runs `bash tests/tracing-prelude/trial.sh` with `cwd` the
   repository root, `stderr=STDOUT`, asserts output and exit code 3.
5. Mutation smoke-test: drop the `FUNCNAME` branch (option 1 behavior),
   confirm the test fails on the missing `+ cat`; revert.

Verify: criterion 1; `make format lint test` (test count 97 + 83).

Commit: `test: tracing prelude trial as an integration test`

### 2.2 Inventory

Grep: `grep -rn 'init-tracing\|printf\|#!/bin/sh' --include=*.sh --include=*.md --include=Makefile --exclude-dir=devlog --exclude-dir=.venv .`

| File                                        | Change                                                   |
| ------------------------------------------- | -------------------------------------------------------- |
| `tools/init-tracing.sh`                     | rewritten: option 3, 28 lines                            |
| `recipes/publish-to-pypi.sh`                | shebang `#!/bin/bash`                                    |
| `recipes/publish-to-testpypi.sh`            | shebang `#!/bin/bash`                                    |
| `recipes/require-system.sh`                 | two `printf` → `echo`                                    |
| `tools/test-installation.sh`                | no longer sources the prelude; own options; plain `echo` |
| `doc/CONVENTIONS.md`                        | two sentences, Script levels                             |
| `TODO.md`                                   | item 16 done                                             |
| `discussions/tracing-prelude-debug-trap.md` | status DONE, pointer to this devlog                      |
| `tests/test_tracing_prelude.py`             | new, integration test                                    |
| `tests/tracing-prelude/trial.sh`            | new, the trial script                                    |
| `tests/tracing-prelude/expected.txt`        | new, its expected output                                 |
| `tests/README.md`                           | the new test listed, if files are enumerated             |
| `devlog/094-tracing-prelude.md`             | this file                                                |

### 2.3 Scope boundary

- macOS `/bin/bash` is 3.2: `DEBUG` trap, `BASH_COMMAND`, `FUNCNAME`
  and `functrace` date from bash 3.0, but no macOS run is available;
  noted as a reservation in § 4.3, not trialed.
- The `SHELL` of the Makefile and the folder of the prelude: untouched.
- The template's Stop 0 (this task's experiment): after closure, per
  the user's decision at Stop 0; a TODO item is filed on this branch
  at § 5.2 if the retrospective confirms it.

Approved: 2026-09-21

## 3. Execution

### 3.1 Account

- Step 1 (16db69a): as planned. The trial output from the scratch
  worktree is identical to option 3; the sweep found no stale mention
  beyond the discussion's own history. `make smoke-test-wheel` shows
  the new tool markup.
- Step 2 (3f9cdcf): as planned. Mutation smoke-test: the restore
  branch of the trap dropped, the test fails on the missing `+ cat`;
  reverted with a file copy, not `git checkout`.
- Between stop 0 and stop 1: the mock-up's pipeline case led the user
  to state the rule "recipes trace, tools do not" and the tool markup
  (decisions 6 and 7); the namespacing question came after stop 1,
  before any step ran (decision 8).

## 4. Delivery

### 4.1 Try it

- Read `tools/init-tracing.sh` (30 lines) and the diff of
  `tools/test-installation.sh`.
- Run the trial and read its output, the helpers silent and every
  other command traced:
  `bash tests/tracing-prelude/trial.sh; echo "exit $?"`
- See the tool markup under the recipe's trace:
  `make smoke-test-wheel`
- See the fallback fire only on failure, with fake commands ahead on
  the PATH (`sudo` exiting 1, `apt` present):
  `make require-system` from a shell where `PATH=/path/to/fakes:$PATH`,
  or `bash tests/tracing-prelude/trial.sh` with a `false ||` line of
  your own.

Tried: 2026-09-21

### 4.2 Test report

1. [x] Trial output: `tests/test_tracing_prelude.py` passes; the
       expected file shows no `+ echo`/`+ banner`/`+ step`/`+ set` line,
       `Y should print` after `false ||`, `Z should print` after `true &&`,
       `+ cat` and `+ true` after the pipeline, `+ true` inside the user
       function, `+ exit 3` last; exit code 3 asserted.
2. [x] `bash -n` on the five recipes, the prelude and
       `tools/test-installation.sh`: all parse; `grep -l init-tracing
tools/*.sh` lists the prelude only.
3. [x] Fake `apt`/`sudo`/`which`: apt present and succeeding, no
       fallback; apt hidden, one fallback line; `sudo apt` failing, one
       fallback line.
4. [x] `make smoke-test-wheel`: `Installation OK: 1.17.8 from-wheel`
       under the new markup.
5. [x] `grep -n 'alias\|shopt\|printf' tools/init-tracing.sh recipes/*.sh`:
       empty.
6. [x] `make format lint test`: all checks passed, 97 pytest + 77 NR.
       CI on PR #95: conventional: pass;gate: pass;smoke-test-wheel: pass;test (3.11): pass;test (3.12): pass;test (3.13): pass;
7. [x] TODO item 16 struck through with `DONE (#94)`; discussion status
       DONE, outcome in its § 6.

Caught during the task: the mutation smoke-test (restore branch
dropped) fails criterion 1 on the missing `+ cat`.

### 4.3 Verdict

**Recommendation:** accept with reservations

Rationale:

- Every acceptance criterion is proven by a command above; the
  defect class that bit #88 and #90 is covered by a test that fails
  when the trap regresses.
- The prelude is 31 lines against 49, with no alias, no `shopt`, no
  rule in a comment.

Reservations:

1. macOS `/bin/bash` 3.2 not trialed: the four features used date
   from bash 3.0 per the manual, but no run backs it. Surfaces only
   for a macOS contributor running a recipe.
2. `tests/README.md` is not covered by the doc sync test; its new
   section is prose only.

### 4.4 Discussion

| #   | Point                                                                                    | Decision                                                            |
| --- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 1   | macOS bash 3.2 untrialed (reservation 1)                                                 | accept as is; a macOS CI job is a separate decision                 |
| 2   | Mandate and Plan at ~250 lines against the template's 120                                | accept as is; budget finding for the retrospective and the template |
| 3   | Stop 0 experiment: frame confirmed before the mock-up, then amended twice by the mock-up | to the retrospective; template change after closure per the user    |

Shipped: 2026-09-21

## 5. Closure

### 5.1 Retrospective

| #   | Point                                                                                                                                                       | Agent    | User       |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------- |
| 1   | Process and template fit: Stop 0 (`Framed:` after § 1.4) added as an experiment; the frame took one round, then the mock-up amended it twice (rule, markup) | well     | surprise   |
| 2   | Mandate and Plan at ~250 lines against the 120 budget: the option table, the trap listing and the inventory                                                 | tension  | don't care |
| 3   | The brief's trial missed the pipeline case; the mock-up's extra cases found it in one run (zero diff on the happy path is not evidence, again)              | surprise | well       |
| 4   | A brief from a prior task as the mandate's seed: Context to Invariants written in one pass                                                                  | well     | well       |
| 5   | Namespacing raised by the user after approval and before any step ran: a table row, no rework                                                               | well     | well       |
| 6   | Mutation smoke-test reverted by file copy, never `git checkout`                                                                                             | well     | don't care |

Process: 1 round at stop 0, 2 amendments from the mock-up before stop 1,
1 round at stop 1; 0 loops at stop 2; rework after stop 1: none.

Closed: 2026-09-21

### 5.2 Forward-looking

- TODO item 17, on this branch: Stop 0 in the devlog template and
  CLAUDE.md Phase 3, plus the budget revisit (row 2).
- The next recipes can use the helpers anywhere a command is; the
  next tool prints `--- title ---` / `-- phase` and never traces.
- `tests/tracing-prelude/trial.sh` is where a new helper context goes
  when one bites.

### 5.3 Rule trace

| Source                                  | Rule                                                                                        | Verb (applied / created) |
| --------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------ |
| `doc/CONVENTIONS.md`, Script levels     | prelude holds sourced mechanics only; calls go down only                                    | applied                  |
| `doc/CONVENTIONS.md`, Calling directory | sourced as `. ./tools/init-tracing.sh` from the repository root                             | applied                  |
| `CLAUDE.md`, Non-regression tests       | mutation smoke-test after adding a test                                                     | applied                  |
| `tests/README.md`, § 1                  | classification integration, nominal plus robustness                                         | applied                  |
| `doc/CONVENTIONS.md`, Script levels     | recipes source the prelude and are bash; a tool never traces, lighter markup for its phases | created                  |
