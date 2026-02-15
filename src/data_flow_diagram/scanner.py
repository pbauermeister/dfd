import os
import re

from . import model
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

    # stitch continuated lines
    input = RX_LINE_CONT.sub("", input)

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
    pair = line.split(maxsplit=1)
    name = pair[1]
    prefix = model.mk_err_prefix_from(parent)

    if name in includes:
        raise model.DfdException(f'{prefix}Recursive include of "{name}"')
    includes.add(name)

    caller = model.SourceLine("", f"<snippet {name}>", parent, 0)
    if name.startswith(model.SNIPPET_PREFIX):
        # include from MD snippet
        if not snippet_by_name:
            raise model.DfdException(
                f"{prefix}source is not markdown, "
                f'cannot include snippet "{name}".'
            )
        name0 = name
        name = name[len(model.SNIPPET_PREFIX) :]
        snippet = snippet_by_name.get(name) or snippet_by_name.get(name0)
        if not snippet:
            raise model.DfdException(
                f'{prefix}included snippet "{name}" not found.'
            )

        _scan(snippet.text, caller, output, snippet_by_name, includes)

    else:
        # include from file
        if not os.path.exists(name):
            raise model.DfdException(
                f'{prefix}included file "{name}" not found.'
            )
        with open(name, encoding="utf-8") as f:
            text = f.read()
        _scan(text, caller, output, snippet_by_name, includes)
