"""Graphviz dot-related generation process"""

import subprocess
import sys


def generate_image(text: str, output_path: str, format: str) -> None:
    cmd = ['dot', f'-T{format}',  f'-o{output_path}']
    subprocess.run(cmd, input=text, encoding='utf-8')
    #print('Generated:', output_path, file=sys.stderr)


def check_installed() -> None:
    cmd = ['dot', '-V']
    try:
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print(f'ERROR: "Graphviz" seems not installed:', e, file=sys.stderr)
        sys.exit(2)
