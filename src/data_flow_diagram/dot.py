"""Graphviz dot-related generation process"""

import subprocess
import sys

from . import model
from .error import print_error


def generate_image(
    graph_options: model.GraphOptions, text: str, output_path: str, format: str
) -> None:
    if graph_options.is_context:
        engine = 'neato'  # circo is not as good
    else:
        engine = 'dot'

    cmd = [engine, f'-T{format}', f'-o{output_path}']
    try:
        subprocess.run(cmd, input=text, encoding='utf-8', check=True)
    except subprocess.CalledProcessError as e:
        for n, line in enumerate(text.splitlines()):
            print(f'{n+1:2}: {line}', file=sys.stderr)
        print_error(f'ERROR: {e}')
        sys.exit(1)
    # print('Generated:', output_path, file=sys.stderr)


def check_installed() -> None:
    cmd = ['dot', '-V']
    try:
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print(f'ERROR: "Graphviz" seems not installed:', e, file=sys.stderr)
        sys.exit(2)
