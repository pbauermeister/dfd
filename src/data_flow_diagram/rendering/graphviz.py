"""Graphviz dot-related generation process"""

import subprocess
import sys

from .. import model
from ..console import print_error
from . import templates as TMPL


def generate_image(
    graph_options: model.GraphOptions, text: str, output_path: str, fmt: str
) -> None:
    # choose Graphviz engine based on diagram mode
    if graph_options.is_context:
        engine = TMPL.ENGINE_CONTEXT
    else:
        engine = TMPL.ENGINE_DEFAULT

    # invoke Graphviz and handle errors
    cmd = [engine, f"-T{fmt}", f"-o{output_path}"]
    try:
        subprocess.run(cmd, input=text, encoding="utf-8", check=True)
    except subprocess.CalledProcessError as e:
        for n, line in enumerate(text.splitlines()):
            print(f"{n+1:2}: {line}", file=sys.stderr)
        print_error(f"ERROR: {e}")
        sys.exit(1)


def check_installed() -> None:
    cmd = ["dot", "-V"]
    try:
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print(f'ERROR: "Graphviz" seems not installed:', e, file=sys.stderr)
        sys.exit(2)
