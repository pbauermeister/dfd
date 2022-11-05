import io
import os
import re
from collections import Counter
from dataclasses import dataclass
from typing import TextIO

from . import model

@dataclass
class SnippetParams:
    root: model.SourceLine
    input_fp: TextIO
    file_name: str
    snippet_by_name: dict[str, model.Snippet]


def extract_snippets(text: str) -> list[model.Snippet]:
    rx = re.compile(r'^```\s*data-flow-diagram\s+(?P<output>.*?)\s*'
                    r'^(?P<src>.*?)^\s*```', re.DOTALL | re.M)

    return [
        model.Snippet(
            text=match['src'],
            name=os.path.splitext(match['output'])[0],
            output=match['output'],
            line_nr=len(text[:match.start()].splitlines()))
        for match in rx.finditer(text)]  # FIXME: have text a TextIO and find in streaming


def make_snippets_params(provenance: str, snippets: list[model.Snippet]) -> list[SnippetParams]:
    res: list[SnippetParams] = []
    snippet_by_name = {s.name:s for s in snippets}
    snippet_names = [s.name for s in snippets]  # capture duplicates
    counts = Counter(snippet_names)
    multiples = {k:n for k, n in counts.items() if n>1}
    if multiples:
        root = model.SourceLine("", provenance, None, None)
        error_prefix = model.mk_err_prefix_from(root)
        raise model.DfdException(f'{error_prefix}Snippets defined multiple times: {multiples}')
    for snippet in snippets:
        if snippet.output.startswith('<'):
            # snippet w/o output, maybe just as includee
            continue
        # snippet with output
        input_fp = io.StringIO(snippet.text)
        snippet_provenance = f'{provenance}<snippet:{snippet.output}>'
        root = model.SourceLine("", snippet_provenance,
                                None, snippet.line_nr)
        file_name = input_fp.name = snippet.output
        res.append(SnippetParams(root, input_fp, file_name, snippet_by_name))

    return res
