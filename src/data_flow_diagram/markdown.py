import io
import os
import re
from collections import Counter
from dataclasses import dataclass
from typing import TextIO

from . import model

@dataclass
class SnippetContext:
    root: model.SourceLine
    input_fp: TextIO
    file_name: str
    snippet_by_name: model.SnippetByName

SnippetContexts = list[SnippetContext]


def extract_snippets(text: str) -> model.Snippets:
    rx = re.compile(r'^```\s*data-flow-diagram\s+(?P<output>.*?)\s*'
                    r'^(?P<src>.*?)^\s*```', re.DOTALL | re.M)

    return [
        model.Snippet(
            text=match['src'],
            name=os.path.splitext(match['output'])[0],
            output=match['output'],
            line_nr=len(text[:match.start()].splitlines()))
        for match in rx.finditer(text)]
        # FIXME: have text a TextIO and find in streaming


def make_snippets_params(provenance: str, snippets: model.Snippets,
                        ) -> SnippetContexts:
    res: SnippetContexts = []
    snippet_by_name = {s.name:s for s in snippets}

    for snippet in snippets:
        # snippet w/o output, maybe just as includee
        if snippet.output.startswith('#'):
            continue

        # snippet with output
        input_fp = io.StringIO(snippet.text)
        snippet_provenance = f'{provenance}<snippet:{snippet.output}>'
        root = model.SourceLine("", snippet_provenance,
                                None, snippet.line_nr)
        file_name = input_fp.name = snippet.output
        res.append(SnippetContext(root, input_fp, file_name, snippet_by_name))

    return res


def check_snippets_unicity(provenance: str, snippets: model.Snippets) -> None:
    snippet_names = [s.name for s in snippets]  # capture duplicates
    counts = Counter(snippet_names)
    multiples = {k:n for k, n in counts.items() if n>1}
    if multiples:
        root = model.SourceLine("", provenance, None, None)
        error_prefix = model.mk_err_prefix_from(root)
        raise model.DfdException(f'{error_prefix}Snippets defined multiple '
                                 f'times: {multiples}')
