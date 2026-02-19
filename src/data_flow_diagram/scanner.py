"""This module does the first steps of DFD scanning, principally handling the #include directives."""

import os
import re

from . import exception, model
from .console import dprint

# Regex to transform lines like:
#   abc\
#   def
# into:
#   abcdef
RX_LINE_CONT = re.compile("[\\\\]\\s*\n\\s*", re.MULTILINE)


def scan(
    provenance: model.SourceLine | None,
    input: str,
    snippet_by_name: model.SnippetByName | None = None,
    debug: bool = False,
) -> model.SourceLines:
    output: model.SourceLines = []
    includes: set[str] = set()

    # stitch continuation lines (trailing backslash)
    input = RX_LINE_CONT.sub("", input)

    # default provenance for top-level sources
    if provenance is None:
        provenance = model.SourceLine("", provenance, None, 0)
    _scan(input, provenance, output, snippet_by_name, includes)

    if debug:
        dprint("=" * 40)
        dprint(provenance)
        dprint("----------")
        dprint(input)
        dprint("----------")
        for l in output:
            dprint(model.repr(l))
        dprint("=" * 40)

    return output


def _scan(
    input: str,
    parent: model.SourceLine,
    output: model.SourceLines,
    snippet_by_name: model.SnippetByName | None,
    includes: set[str],
) -> None:
    """Process each non-blank line: dispatch includes, collect the rest."""
    for nr, line in enumerate(input.splitlines()):
        if not line.strip():
            continue
        source_line = model.SourceLine(line, line, parent, nr)
        pair = line.split(maxsplit=1)
        if len(pair) == 2 and pair[0] == model.INCLUDE_DIRECTIVE:
            include(line, source_line, output, snippet_by_name, includes)
        else:
            output.append(source_line)


def include(
    line: str,
    parent: model.SourceLine,
    output: model.SourceLines,
    snippet_by_name: model.SnippetByName | None,
    includes: set[str],
) -> None:
    # extract the include target and guard against recursion
    pair = line.split(maxsplit=1)
    name = pair[1]

    if name in includes:
        raise exception.DfdException(
            f'Recursive include of "{name}"', source=parent
        )
    includes.add(name)

    # resolve the includee: snippet (#-prefixed) or file
    caller = model.SourceLine("", f"<snippet {name}>", parent, 0)
    if name.startswith(model.SNIPPET_PREFIX):
        # include from MD snippet
        if not snippet_by_name:
            raise exception.DfdException(
                f"source is not markdown, " f'cannot include snippet "{name}".',
                source=parent,
            )
        name0 = name
        name = name[len(model.SNIPPET_PREFIX) :]
        snippet = snippet_by_name.get(name) or snippet_by_name.get(name0)
        if not snippet:
            raise exception.DfdException(
                f'included snippet "{name}" not found.', source=parent
            )

        _scan(snippet.text, caller, output, snippet_by_name, includes)

    else:
        # include from file
        if not os.path.exists(name):
            raise exception.DfdException(
                f'included file "{name}" not found.', source=parent
            )
        with open(name, encoding="utf-8") as f:
            text = f.read()
        _scan(text, caller, output, snippet_by_name, includes)
