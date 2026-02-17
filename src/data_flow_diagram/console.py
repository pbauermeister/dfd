import sys
from typing_extensions import Literal


def print_error(text: str) -> None:
    if sys.stderr.isatty():
        text = f"\033[31m{text}\033[0m"
    print(text, file=sys.stderr)


debug = False


def set_debug(value: bool) -> None:
    global debug
    debug = value


def dprint(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    flush: Literal[False] = False,
) -> None:
    if not debug:
        return
    print(*values, sep=sep, end=end, flush=flush, file=sys.stderr)
