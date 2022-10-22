"""Graphviz dot-related generation process"""

import subprocess
import sys


def generate_image(text: str, output_path: str, format: str) -> None:
    cmd = ['dot', f'-T{format}',  f'-o{output_path}']
    subprocess.run(cmd, input=text, encoding='utf-8')
    #print('Generated:', output_path, file=sys.stderr)
