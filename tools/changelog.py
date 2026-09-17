#!/usr/bin/env python3
"""Read the latest version, or its changelog section, from CHANGES.md.

Usage:
  changelog.py version   # e.g. 1.17.6
  changelog.py notes     # the bullet list under "## Version 1.17.6:"

Used by the release workflow and by publish-to-github.py.
"""

import argparse
import re
import sys
from pathlib import Path

CHANGES_PATH = Path(__file__).resolve().parent.parent / "CHANGES.md"


def extract_version() -> str:
    """Extract the latest version from CHANGES.md."""
    changes = CHANGES_PATH.read_text()
    m = re.search(r"^## Version\s+(\S+?):", changes, re.MULTILINE)
    if not m:
        sys.exit("ERROR: could not extract version from CHANGES.md")
    return m.group(1)


def extract_notes(version: str) -> str:
    """Extract the changelog section of a given version."""
    changes = CHANGES_PATH.read_text()
    pattern = rf"^## Version\s+{re.escape(version)}:\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, changes, re.MULTILINE | re.DOTALL)
    if not m:
        return f"Release {version}"
    return m.group(1).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "what",
        choices=["version", "notes"],
        help="print the latest version, or its changelog section",
    )
    args = parser.parse_args()

    version = extract_version()
    if args.what == "version":
        print(version)
    else:
        print(extract_notes(version))


if __name__ == "__main__":
    main()
