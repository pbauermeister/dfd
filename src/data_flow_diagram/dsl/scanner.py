"""This module does the first steps of DFD scanning, principally handling the #include directives."""

import os
import re

from .. import exception, model
from ..console import dprint

# Regex to transform lines like:
#   abc\
#   def
# into:
#   abcdef
RX_LINE_CONT = re.compile("[\\\\]\\s*\n\\s*", re.MULTILINE)


def scan(
    *,
    provenance: model.SourceLine | None,
    source_text: str,
    snippet_by_name: model.SnippetByName | None = None,
    debug: bool = False,
) -> model.SourceLines:
    output: model.SourceLines = []
    includes: set[str] = set()

    # stitch continuation lines (trailing backslash)
    source_text = RX_LINE_CONT.sub("", source_text)

    # default provenance for top-level sources
    if provenance is None:
        provenance = model.SourceLine(
            text="", raw_text=provenance, parent=None, line_nr=0
        )
    _scan(
        source_text=source_text,
        parent=provenance,
        output=output,
        snippet_by_name=snippet_by_name,
        includes=includes,
    )

    if debug:
        dprint("=" * 40)
        dprint(provenance)
        dprint("----------")
        dprint(source_text)
        dprint("----------")
        for l in output:
            dprint(model.repr(l))
        dprint("=" * 40)

    return output


def _scan(
    *,
    source_text: str,
    parent: model.SourceLine,
    output: model.SourceLines,
    snippet_by_name: model.SnippetByName | None,
    includes: set[str],
) -> None:
    """Process each non-blank line: dispatch includes, collect the rest."""
    for nr, line in enumerate(source_text.splitlines()):
        if not line.strip():
            continue
        source_line = model.SourceLine(
            text=line, raw_text=line, parent=parent, line_nr=nr
        )
        pair = line.split(maxsplit=1)
        if len(pair) == 2 and pair[0] == model.INCLUDE_DIRECTIVE:
            include(
                line=line,
                parent=source_line,
                output=output,
                snippet_by_name=snippet_by_name,
                includes=includes,
            )
        else:
            output.append(source_line)


def include(
    *,
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
    caller = model.SourceLine(
        text="", raw_text=f"<snippet {name}>", parent=parent, line_nr=0
    )
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

        _scan(
            source_text=snippet.text,
            parent=caller,
            output=output,
            snippet_by_name=snippet_by_name,
            includes=includes,
        )

    else:
        # include from file
        if not os.path.exists(name):
            raise exception.DfdException(
                f'included file "{name}" not found.', source=parent
            )
        with open(name, encoding="utf-8") as f:
            text = f.read()
        _scan(
            source_text=text,
            parent=caller,
            output=output,
            snippet_by_name=snippet_by_name,
            includes=includes,
        )
