# Shell prelude for the recipes: exit on error, trace commands, and
# echo/banner/banner2/step helpers that print without the trace noise.
# A DEBUG trap owns the tracing state: it turns tracing off before a
# helper and back on before the next command outside one, so the helpers
# are plain functions (echo stays the builtin), usable anywhere a
# command is: after `||`, inside `$(...)`, in a pipeline.
# Source it from the repository root: `. ./tools/init-tracing.sh`.
# bash only (DEBUG trap, BASH_COMMAND, FUNCNAME); recipes only, a tool
# never traces (engineering/CONVENTIONS.md, "Script levels").
set +x -e -u -o pipefail

banner()  { _tracing_box_ '######################################################################' "$*"; }
banner2() { _tracing_box_ '----------------------------------------------------------------------' "$*"; }
step()    { echo; echo "==== $* ===="; echo; }
_tracing_box_() { echo; echo "$1"; echo "$2"; echo "$1"; echo; }

_tracing_saved_flags_=""
export -n _tracing_saved_flags_
_tracing_quiet_() {  # DEBUG trap, before every command
    case "$BASH_COMMAND" in
        echo|echo\ *|banner\ *|banner2\ *|step\ *)  # a helper: tracing off, once
            case "$-" in *x*) _tracing_saved_flags_="$-"; set +x ;; esac ;;
        *)  case " ${FUNCNAME[*]} " in  # inside a helper: leave it off
                *" banner "*|*" banner2 "*|*" step "*) ;;
                *) case "$_tracing_saved_flags_" in *x*) _tracing_saved_flags_=""; set -x ;; esac ;;
            esac ;;
    esac
}
trap '{ _tracing_quiet_; } 2>/dev/null' DEBUG
set -o functrace  # the trap also fires inside functions, $(...) and pipelines
set -x
