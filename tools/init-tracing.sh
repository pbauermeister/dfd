# Shell prelude for the runbooks and tools: exit on error, trace
# commands, and echo/banner/banner2/step helpers that print without the
# trace noise (https://superuser.com/a/1141026). Source it from the
# repository root: `. ./tools/init-tracing.sh`.
set +x -e -o pipefail

shopt -s expand_aliases 2>/dev/null || true  # for bash

_here_=$(pwd)

alias echo='{ save_flags="$-"; set +x; } 2>/dev/null; _echo_';
_echo_() { \echo "$*"; case "$save_flags" in *x*)  set -x;; esac }

alias banner='{ save_flags="$-"; set +x; } 2>/dev/null; _banner_';
_banner_() { __banner__ "$*"; case "$save_flags" in *x*)  set -x;; esac }

alias banner2='{ save_flags="$-"; set +x; } 2>/dev/null; _banner2_';
_banner2_() { __banner2__ "$*"; case "$save_flags" in *x*)  set -x;; esac }

alias step='{ save_flags="$-"; set +x; } 2>/dev/null; _step_';
_step_() { __step__ "$*"; case "$save_flags" in *x*)  set -x;; esac }

__banner__() {
    \echo
    \echo "######################################################################"
    \echo "$*"
    \echo "######################################################################"
    \echo
}

__banner2__() {
    \echo
    \echo "----------------------------------------------------------------------"
    \echo "$*"
    \echo "----------------------------------------------------------------------"
    \echo
}

__step__() {
    \echo
    \echo "==== $* ===="
    \echo
}

set -ex

