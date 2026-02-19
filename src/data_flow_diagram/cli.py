"""Command-line DFD diagram generator. Converts a textual description
into a graphic file.

-----

See https://github.com/pbauermeister/dfd for information, syntax and
examples.

-----

This module parses the commandline args, prepares the I/Os and calls the stuff.
"""

import argparse
import os
import sys
import tempfile
from typing import TextIO

from . import dfd, exception, markdown, model
from .console import dprint, print_error, set_debug
from .rendering import graphviz

from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("data-flow-diagram")
except PackageNotFoundError:
    VERSION = "undefined"


def parse_args() -> argparse.Namespace:
    assert __doc__ is not None
    description, epilog = [each.strip() for each in __doc__.split("-----")[:2]]

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument(
        "INPUT_FILE",
        action="store",
        default=None,
        nargs="?",
        help="DFD input file; " "if omitted, stdin is used",
    )

    parser.add_argument(
        "--output-file",
        "-o",
        required=False,
        help="output file name; pass '-' to use stdout; "
        "if omitted, use INPUT_FILE base name with '.svg' "
        "extension, or stdout",
    )

    parser.add_argument(
        "--markdown",
        "-m",
        action="store_true",
        help="consider snippets between opening marker: "
        "```data-flow-diagram OUTFILE, and closing marker: ``` "
        "allowing to generate all diagrams contained in an "
        "INPUT_FILE that is a markdown file",
    )

    parser.add_argument(
        "--format",
        "-f",
        required=False,
        default="svg",
        help="output format: gif, jpg, tiff, bmp, pnm, eps, "
        "pdf, svg (any supported by Graphviz), or dot "
        "(raw Graphviz DOT text); default is svg",
    )

    parser.add_argument(
        "--background-color",
        "-b",
        required=False,
        default=None,
        help="background color name (including 'none' for"
        " transparent) in web color notation; see"
        " https://developer.mozilla.org/en-US/docs/Web/CSS/color_value"
        " for a list of valid names; default is white",
    )

    parser.add_argument(
        "--no-graph-title",
        action="store_true",
        default=False,
        help="suppress graph title",
    )

    parser.add_argument(
        "--no-check-dependencies",
        action="store_true",
        default=False,
        help="suppress dependencies checking",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="emit debug messages",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="store_true",
        help="print the version and exit",
    )

    return parser.parse_args()


def write_output(
    dot_text: str,
    output_path: str,
    fmt: str,
    graph_options: model.GraphOptions,
) -> None:
    """Write pipeline output (DOT text or rendered image) to file or stdout."""
    if fmt == "dot":
        if output_path == "-":
            print(dot_text)
        else:
            with open(output_path, "w") as f:
                f.write(dot_text)
    elif output_path == "-":
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "output." + fmt)
            graphviz.generate_image(graph_options, dot_text, path, fmt)
            with open(path) as f:
                print(f.read())
    else:
        graphviz.generate_image(graph_options, dot_text, output_path, fmt)


def handle_markdown_source(
    options: model.Options, provenance: str, input_fp: TextIO
) -> None:
    """Call build() for the markdown case: isolate snippets and call build() for each."""

    # read MD file and extract snippets with their context (line number, provenance, etc.)
    text = input_fp.read()
    snippets = markdown.extract_snippets(text)
    markdown.check_snippets_unicity(provenance, snippets)
    snippets_params = markdown.make_snippets_params(provenance, snippets)

    # build and write output for each snippet
    for params in snippets_params:
        title = os.path.splitext(params.file_name)[0]
        dot_text, graph_options = dfd.build(
            params.root,
            params.input_fp.read(),
            title,
            options,
            snippet_by_name=params.snippet_by_name,
        )
        write_output(dot_text, params.file_name, options.format, graph_options)
        dprint(f"{sys.argv[0]}: generated {params.file_name}")


def handle_dfd_source(
    options: model.Options, provenance: str, input_fp: TextIO, output_path: str
) -> None:
    """Call build() for when the DFD is given by a path, and output to another path or stdout."""

    root = model.SourceLine("", provenance, None, 0)
    title = "" if output_path == "-" else os.path.splitext(output_path)[0]
    dot_text, graph_options = dfd.build(root, input_fp.read(), title, options)
    write_output(dot_text, output_path, options.format, graph_options)


def run(args: argparse.Namespace) -> None:
    """Run the application with the given commandline args."""

    # resolve input source (file or stdin)
    if args.INPUT_FILE is None:
        input_fp = sys.stdin
        provenance = "<stdin>"
    else:
        input_fp = open(args.INPUT_FILE)
        provenance = f"<file:{args.INPUT_FILE}>"

    options = model.Options(
        format=args.format,
        background_color=args.background_color,
        no_graph_title=args.no_graph_title,
        no_check_dependencies=args.no_check_dependencies,
        debug=args.debug,
    )

    set_debug(args.debug)

    # dispatch to markdown or single-source mode
    if args.markdown:
        handle_markdown_source(options, provenance, input_fp)
        return

    # resolve output path (explicit, derived from input, or stdout)
    if args.output_file is None:
        if args.INPUT_FILE is not None:
            basename = os.path.splitext(args.INPUT_FILE)[0]
            output_path = basename + "." + args.format
        else:
            output_path = "-"
    else:
        output_path = args.output_file

    # DFD source
    handle_dfd_source(options, provenance, input_fp, output_path)


def main() -> None:
    """Entry point for the application script."""

    graphviz.check_installed()

    args = parse_args()
    if args.version:
        print("data-flow-diagram", VERSION)
        sys.exit(0)

    try:
        run(args)
    except exception.DfdException as e:
        text = f"ERROR: {e}"
        print_error(text)
        sys.exit(1)
