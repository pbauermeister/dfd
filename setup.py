"""Supply the dynamic project version to setuptools.

All static metadata lives in pyproject.toml. The version is the latest
one listed in CHANGES.md, which is the single source of truth for both
version numbers and changelog texts.
"""

import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
changes = (here / "CHANGES.md").read_text(encoding="utf-8")

# extract the version from the first "## Version X.Y.Z:" heading
headings = [line[2:] for line in changes.splitlines() if line.startswith('##')]
version = headings[0].strip().split(':', 1)[0].split()[-1].strip()

setup(version=version)
