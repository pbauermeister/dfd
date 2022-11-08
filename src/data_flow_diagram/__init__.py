"""Command-line DFD diagram generator. Converts a textual description
into a graphic file.

-----

See https://github.com/pbauermeister/dfd for information, syntax and
examples.

-----

This module parses the commandline args, prepares the I/Os and calls the stuff.
"""

import argparse
import io
import os
import pkg_resources
import re
import sys
import tempfile
from typing import TextIO

from . import dfd
from . import model
from . import markdown
from . import dot

VERSION = pkg_resources.require("data-flow-diagram")[0].version

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
                        help='emit debug messages')

    parser.add_argument('--version', '-V',
                        action='store_true',
                        help='print the version and exit')

    return parser.parse_args()


def handle_markdown_source(args: argparse.Namespace, provenance: str,
                           input_fp: TextIO) -> None:
    text = input_fp.read()
    snippets = markdown.extract_snippets(text)
    markdown.check_snippets_unicity(provenance, snippets)
    snippets_params = markdown.make_snippets_params(provenance, snippets)
    for params in snippets_params:
        dfd.build(params.root, params.input_fp.read(), params.file_name,
                  args.percent_zoom, args.background_color, args.format,
                  args.debug, snippet_by_name=params.snippet_by_name)
        print(f'{sys.argv[0]}: generated {params.file_name}', file=sys.stderr)


def handle_dfd_source(args: argparse.Namespace, provenance: str,
                      input_fp: TextIO, output_path: str) -> None:
    root = model.SourceLine("", provenance, None, None)
    if output_path == '-':
        # output to stdout
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'file.svg')
            dfd.build(root, input_fp.read(), path, args.percent_zoom,
                      args.background_color, args.format, args.debug)
            with open(path) as f:
                print(f.read())
    else:
        # output to file
        dfd.build(root, input_fp.read(), output_path, args.percent_zoom,
                  args.background_color, args.format, args.debug, )


def run(args: argparse.Namespace) -> None:
    # adjust input
    if args.INPUT_FILE is None:
        input_fp = sys.stdin
        provenance = '<stdin>'
    else:
        input_fp = open(args.INPUT_FILE)
        provenance = f'<file:{args.INPUT_FILE}>'

    # markdown source
    if args.markdown:
        handle_markdown_source(args, provenance, input_fp)
        return

    # adjust output
    if args.output_file is None:
        if args.INPUT_FILE is not None:
            basename = os.path.splitext(args.INPUT_FILE)[0]
            output_path = basename + '.' + args.format
        else:
            output_path = '-'
    else:
        output_path = args.output_file

    # DFD source
    handle_dfd_source(args, provenance, input_fp, output_path)


def main() -> None:
    """Entry point for the application script"""

    dot.check_installed()

    args = parse_args()
    if args.version:
        print('data-flow-diagram', VERSION)
        sys.exit(0)

    try:
        run(args)
    except model.DfdException as e:
        print('ERROR:', e, file=sys.stdout)
        sys.exit(1)
