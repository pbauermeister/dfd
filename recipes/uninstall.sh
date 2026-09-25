#!/bin/bash
#
# Remove the user-wide install of data-flow-diagram, whatever installed
# it and whatever version it is: a uv tool (make install, or uv tool
# install from PyPI), a pipx install, a pip install in the current
# Python. Each installer is asked in turn; nothing found is not an
# error. The development wrappers (./data-flow-diagram, .venv/bin) are
# not installs and stay.

. ./tools/init-tracing.sh

NAME=data-flow-diagram
FOUND=no

step "uv tool"
if uv tool list 2>/dev/null | grep -q "^$NAME "; then
    uv tool uninstall "$NAME"
    FOUND=yes
fi

step "pipx"
if command -v pipx >/dev/null && pipx list --short 2>/dev/null | grep -q "^$NAME "; then
    pipx uninstall "$NAME"
    FOUND=yes
fi

step "pip, current python3"
if python3 -m pip show "$NAME" >/dev/null 2>&1; then
    python3 -m pip uninstall --yes "$NAME"
    FOUND=yes
fi

step "result"
[ "$FOUND" = yes ] || echo "nothing installed as $NAME"
REMAINING=$(command -v "$NAME" || true)
case "$REMAINING" in
    "" | "$PWD"/*) echo "$NAME is gone from PATH" ;;
    *) echo "WARNING: still on PATH: $REMAINING (not installed by uv tool, pipx or pip)" ;;
esac
