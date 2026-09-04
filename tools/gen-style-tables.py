#!/usr/bin/env python3
"""Print the `style` options table of doc/README.md or doc/SYNTAX.md.

Usage: gen-style-tables.py readme|syntax

The tables are derived from data_flow_diagram.model.STYLE_SPECS, so the
GraphOptions declarations stay the single source of truth. Output is padded
like prettier / VSCode format tables, so re-formatting produces no diff.
"""

import pathlib
import sys
from collections.abc import Iterator
from typing import assert_never

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from data_flow_diagram import model  # noqa: E402


def format_table(header: list[str], rows: list[list[str]]) -> str:
    """Render a Markdown table with every column padded to its widest cell."""
    widths = [max(len(cell) for cell in col) for col in zip(header, *rows)]

    def line(cells: list[str]) -> str:
        padded = [cell.ljust(w) for cell, w in zip(cells, widths)]
        return "| " + " | ".join(padded) + " |"

    separator = ["-" * w for w in widths]
    return "\n".join([line(header), line(separator), *map(line, rows)])


def readme_rows() -> Iterator[list[str]]:
    """Rows for doc/README.md: full statement form and effect."""
    for keyword, spec in model.STYLE_SPECS.items():
        if spec.kind is model.StyleKind.FLAG:
            statement = f"`style {keyword}`"
        else:
            statement = f"`style {keyword} {spec.placeholder}`"
        yield [statement, spec.doc]


def syntax_rows() -> Iterator[list[str]]:
    """Rows for doc/SYNTAX.md: option, value kind, default, and effect."""
    for keyword, spec in model.STYLE_SPECS.items():
        match spec.kind:
            case model.StyleKind.FLAG:
                value, default = "-", "-"
            case model.StyleKind.INT:
                value, default = "integer", str(spec.value)
            case model.StyleKind.STR:
                value = spec.placeholder.lower()
                default = "-" if spec.value is None else str(spec.value)
            case _:
                assert_never(spec.kind)
        yield [f"`{keyword}`", value, default, spec.doc]


def main() -> None:
    match sys.argv[1:]:
        case ["readme"]:
            print(
                format_table(["Style statement", "Effect"], list(readme_rows()))
            )
        case ["syntax"]:
            header = ["Option", "Value", "Default", "Effect"]
            print(format_table(header, list(syntax_rows())))
        case _:
            sys.exit(f"usage: {sys.argv[0]} readme|syntax")


if __name__ == "__main__":
    main()
