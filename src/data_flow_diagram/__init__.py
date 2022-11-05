"""Command-line DFD diagram generator. Converts a textual description
into a graphic file.

-----

See https://github.com/pbauermeister/dfd for information, syntax and
examples.

-----

This module does pretty much all the work for now.

"""

import argparse
import io
import os
import re
import sys
import tempfile
from typing import TextIO
from collections import Counter

from .dfd import build
from. import model


def parse_args() -> argparse.Namespace:
    description, epilog = [each.strip() for each in __doc__.split('-----')[:2]]

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('INPUT_FILE',
                        action='store',
                        default=None, nargs='?',
                        help='UML sequence input file; '
                        'if omitted, stdin is used')

    parser.add_argument('--output-file', '-o',
                        required=False,
                        help='output file name; pass \'-\' to use stdout; '
                        'if omitted, use INPUT_FILE base name with \'.svg\' '
                        'extension, or stdout')

    parser.add_argument('--markdown', '-m',
                        action='store_true',
                        help='consider snippets between opening marker: '
                        '```data-flow-diagram OUTFILE, and closing marker: ``` '
                        'allowing to generate all diagrams contained in an '
                        'INPUT_FILE that is a markdown file');

    parser.add_argument('--format', '-f',
                        required=False,
                        default='svg',
                        help='output format: gif, jpg, tiff, bmp, pnm, eps, '
                        'pdf, svg (any supported by reportlab); default is svg')

    parser.add_argument('--percent-zoom', '-p',
                        required=False,
                        default=100, type=int,
                        help='magnification percentage; default is 100')

    parser.add_argument('--background-color', '-b',
                        required=False,
                        default='white',
                        help='background color name (including \'none\' for'
                        ' transparent) in web color notation; see'
                        ' https://developer.mozilla.org/en-US/docs/Web/CSS/color_value'
                        ' for a list of valid names; default is white')

    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='emits debug messages')
    return parser.parse_args()


def call_build(provenance: model.SourceLine,
               input_fp: TextIO, output_path: str, percent_zoom: int,
               debug: bool, bgcolor: str, format: str,
               snippet_by_name: dict[str, model.Snippet] = None) -> None:
    if debug:
        print(dict(input=input_fp.name,
                   output=output_path,
                   percent_zoom=percent_zoom,
                   debug=debug,
                   bgcolor=bgcolor,
                   format=format,
        ), file=sys.stderr)

    src = input_fp.read()

    if debug:
        print(src, file=sys.stderr)
        print("----------", file=sys.stderr)
        #for cmd in cmds:
        #    print(cmd[0], ', '.join([repr(a) for a in cmd[1:]]))

    try:
        build(provenance, src, output_path, percent_zoom, bgcolor, format, debug,
              snippet_by_name)
    except model.DfdException as e:
        print('ERROR:', e, file=sys.stdout)
        sys.exit(1)


def extract_snippets(text: str) -> list[model.Snippet]:
    rx = re.compile(r'^```\s*data-flow-diagram\s+(?P<output>.*?)\s*'
                    r'^(?P<src>.*?)^\s*```', re.DOTALL | re.M)

    return [
        model.Snippet(
            text=match['src'],
            name=os.path.splitext(match['output'])[0],
            output=match['output'],
            line_nr=len(text[:match.start()].splitlines()))
        for match in rx.finditer(text)]


def main() -> None:
    """Entry point for the application script"""
    args = parse_args()

    # treat input
    if args.INPUT_FILE is None:
        inp = sys.stdin
        provenance = '<stdin>'
    else:
        inp = open(args.INPUT_FILE)
        provenance = f'<file:{args.INPUT_FILE}>'

    # markdown
    if args.markdown:
        md = inp.read()
        snippets = extract_snippets(md)
        snippet_by_name = {s.name:s for s in snippets}
        names = snippet_by_name.keys()
        counts = Counter(names)
        multiples = {k:n for k, n in counts.items() if n>1}
        if multiples:
            raise RuntimeError(f'snippets defined multiple times: {multiples}')
        for snippet in snippets:
            if snippet.output.startswith('<'):
                # snippet w/o output, maybe just as includee
                continue
            # snippet with output
            inp = io.StringIO(snippet.text)
            snippet_provenance = f'{provenance}<snippet:{snippet.output}>'
            snippet_root = model.SourceLine("", snippet_provenance,
                                            None, snippet.line_nr)
            file_name = inp.name =snippet.output
            call_build(snippet_root,
                       inp, file_name, args.percent_zoom, args.debug,
                       args.background_color, args.format,
                       snippet_by_name=snippet_by_name)
            print(f'{sys.argv[0]}: generated {file_name}', file=sys.stderr)
        return

    # treat output
    if args.output_file is None:
        if args.INPUT_FILE is not None:
            name = os.path.splitext(args.INPUT_FILE)[0] + '.' + args.format
        else:
            name = '-'
    else:
        name = args.output_file

    root = model.SourceLine("", provenance, None, None)
    if name == '-':
        # output to stdout
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'file.svg')
            call_build(root, inp, path, args.percent_zoom, args.debug,
                       args.background_color, args.format)
            with open(path) as f:
                print(f.read())
    else:
        # output to file
        call_build(root, inp, name, args.percent_zoom, args.debug,
                   args.background_color, args.format)
    return
