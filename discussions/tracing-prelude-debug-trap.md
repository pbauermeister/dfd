# Tracing prelude without aliases: a DEBUG trap

Date: 2026-09-20
Status: PENDING
Origin: #90 (devlog `devlog/090-script-levels.md`), branch
`refactor/90-script-levels`; TODO item 16.

**Prompt:** After a CI failure caused by the `echo` alias of
`tools/init-tracing.sh` in a `||` fallback, find a prelude design whose
helpers behave like ordinary commands. This file is the brief for that
task: the problem, what exists, the candidate prelude with its trials,
and the migration.

## 1. The problem

The prelude runs the recipes under `set -x` and offers `echo`,
`banner`, `banner2`, `step` that print without the trace noise (no
`+ echo msg` line, no `+ set +x` / `+ set -x` lines). Bash prints the
trace line of a command before running it, so a function cannot hide
its own call line. The standard trick (https://superuser.com/a/1141026)
is an alias that turns tracing off before the helper runs:

```bash
alias echo='{ save_flags="$-"; set +x; } 2>/dev/null; _echo_';
_echo_() { \echo "$*"; case "$save_flags" in *x*)  set -x;; esac }
```

The alias carries a `;`, so it is two commands. In `a || echo msg` the
`||` binds to the brace group only and `_echo_` runs unconditionally;
under `set -u` it then fails on `save_flags` when `a` succeeded. Seen
in #88 inside `$(...)`, and in #90 in the `||` fallbacks of
`recipes/require-system.sh` (CI run 35513228401): the fallback message
printed after a successful `apt install`, then `save_flags: unbound
variable`. Workaround in place: `printf` in list context, and the rule
in the prelude header.

Replacing `;` by `&&` does not help: `&&` and `||` have equal
precedence and group left, so `true || { ...; } && _echo_ "X"` still
runs `_echo_` (trialed: X printed, then the unbound error).

## 2. What exists (2026-09-20)

Searches for hiding the trace of one command return three mechanisms:
toggling `set +x` around a section, the `PS4` prefix, and
`BASH_XTRACEFD` to send the trace to another descriptor. None removes
the call line of a helper. The alias trick is the accepted answer, with
its limitation. A fourth mechanism is not documented for this purpose:
the DEBUG trap.

## 3. Candidate: a DEBUG trap

Bash runs the DEBUG trap before every simple command, with the command
text in `BASH_COMMAND`. When the next command is a helper, the trap
turns tracing off; the helper turns it back on as its last action. The
helpers are plain functions, so they behave like any command after
`||`, after `&&`, inside `$(...)` and inside `if` blocks.

`tools/init-tracing.sh` candidate, 29 lines against 49 today:

```bash
# Shell prelude for the recipes and tools: exit on error, trace commands,
# and echo/banner/banner2/step helpers that print without the trace
# noise. A DEBUG trap turns tracing off just before a helper runs and
# the helper turns it back on when it returns, so the helpers are plain
# functions, usable anywhere a command is (after `||`, inside `$(...)`).
# Source it from the repository root: `. ./tools/init-tracing.sh`.
# bash only (DEBUG trap, BASH_COMMAND).
set +x -e -u -o pipefail

_quiet_() {  # DEBUG trap: before a helper, turn tracing off (once)
    case "$BASH_COMMAND" in
        echo|echo\ *|banner\ *|banner2\ *|step\ *)
            case "$-" in *x*) save_flags="$-"; set +x ;; esac ;;
    esac
}
_restore_() {  # last command of every helper: tracing back as it was
    local flags="${save_flags-}"
    save_flags=""
    case "$flags" in *x*) set -x ;; esac
}
echo()    { builtin echo "$@"; _restore_; }
banner()  { _box_ '######################################################################' "$*"; _restore_; }
banner2() { _box_ '----------------------------------------------------------------------' "$*"; _restore_; }
step()    { builtin echo; builtin echo "==== $* ===="; builtin echo; _restore_; }
_box_()   { builtin echo; builtin echo "$1"; builtin echo "$2"; builtin echo "$1"; builtin echo; }

trap '{ _quiet_; } 2>/dev/null' DEBUG
set -o functrace  # the trap also fires inside functions and $(...)
set -x
```

Two subtleties, both hit during the trial:

- Under `functrace` the trap fires twice for a function call (the
  command, then the function entry). The second firing saw tracing
  already off and overwrote `save_flags` without `x`, so nothing was
  restored. Hence "save only while tracing is on".
- Clearing `save_flags` after `set -x` leaked `+ save_flags=` into the
  trace. Hence the local copy and `set -x` as the last command.

## 4. Trials

Test script (run with `bash`, prelude sourced from the same folder):

```bash
banner "Banner"
step "a step"
uv --version
true || echo "X should NOT print"
false || echo "Y should print"
true && echo "Z should print"
V=$(echo "inside command substitution")
banner2 "banner2: V=$V"
if [ ! -f .no-such-token ]; then
    echo "ERROR: guard message, then exit 3"
    exit 3
fi
```

Output, verbatim (stdout and stderr):

```

######################################################################
Banner
######################################################################


==== a step ====

+ uv --version
uv 0.11.7 (x86_64-unknown-linux-gnu)
+ true
+ false
Y should print
+ true
Z should print
+ V='inside command substitution'

----------------------------------------------------------------------
banner2: V=inside command substitution
----------------------------------------------------------------------

+ '[' '!' -f .no-such-token ']'
ERROR: guard message, then exit 3
+ exit 3
exit 3
```

Every case behaves: no `+ echo` line, no `+ set` line, the `||`
fallback fires only on failure, `&&` fires only on success, the
substitution works, the guard prints and its exit code propagates,
`+ true` / `+ false` / `+ uv --version` are traced as before.

## 5. Balance and migration

- 29 lines against 49; no alias, no `shopt`; the rule "never as an
  operand of `&&` or `||`, nor inside `$(...)`" and the `printf`
  workaround disappear.
- bash only (`DEBUG` trap, `BASH_COMMAND`, `functrace`). Today
  `recipes/publish-to-pypi.sh` and `recipes/publish-to-testpypi.sh`
  carry `#!/bin/sh`: switch to `#!/bin/bash`. The Makefile already sets
  `SHELL := /bin/bash`.
- No call site changes: no recipe uses a helper in list context today
  (grep in #90).
- Cost per command: one trap invocation and a `case`; irrelevant at
  the recipes' scale (dozens of commands).

Steps:

1. Replace `tools/init-tracing.sh` by the candidate; the two shebangs.
2. `recipes/require-system.sh`: `printf` back to `echo` in the
   fallbacks (the workaround is no longer needed), or keep `printf`
   (it works too); decide for uniformity.
3. Trials: the test script above copied under `tests/` or the job
   scratch folder; `make build`; `make smoke-test-wheel`;
   `recipes/require-system.sh` with fake `apt`/`sudo` on the PATH as
   in #90; `bash -n` on the publishing recipes.
4. Check the remaining interactions: `set -e` with the trap (a failing
   command inside `_quiet_` would exit the script; none can fail);
   `trap ... DEBUG` inherited by subshells only with `functrace`
   (needed for `$(...)`, kept).
