#!/usr/bin/env python3
"""Read the project version, or its changelog section from CHANGES.md.

Usage:
  changelog.py version   # e.g. 1.17.6, from pyproject.toml
  changelog.py notes     # the section under "## v1.17.6 (date)"

Used by the release workflow and by publish-to-github.py.
"""

import argparse
import re
import tomllib
from enum import StrEnum
from pathlib import Path
from typing import assert_never

ROOT = Path(__file__).resolve().parent.parent
CHANGES_PATH = ROOT / "CHANGES.md"
PYPROJECT_PATH = ROOT / "pyproject.toml"


def extract_version() -> str:
    """Extract the project version from pyproject.toml."""
    with PYPROJECT_PATH.open("rb") as f:
        version: str = tomllib.load(f)["project"]["version"]
    return version


def extract_notes(version: str) -> str:
    """Extract the changelog section of a given version."""
    changes = CHANGES_PATH.read_text()
    # match the generated heading "## vX.Y.Z (date)" and the former
    # hand-written "## Version X.Y.Z:"
    v = re.escape(version)
    heading = rf"^## (?:v{v} \(\d{{4}}-\d{{2}}-\d{{2}}\)|Version\s+{v}:)"
    pattern = rf"{heading}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, changes, re.MULTILINE | re.DOTALL)
    if not m:
        return f"Release {version}"
    return m.group(1).strip()


class What(StrEnum):
    VERSION = "version"
    NOTES = "notes"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "what",
        type=What,
        choices=list(What),
        help="print the latest version, or its changelog section",
    )
    args = parser.parse_args()
    what: What = args.what  # argparse boundary

    version = extract_version()
    match what:
        case What.VERSION:
            print(version)
        case What.NOTES:
            print(extract_notes(version))
        case _:
            assert_never(what)


if __name__ == "__main__":
    main()
