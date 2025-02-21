import sys


def print_error(text: str) -> None:
    if sys.stderr.isatty():
        text = f'\033[31m{text}\033[0m'
    print(text, file=sys.stderr)
