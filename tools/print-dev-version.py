#!/usr/bin/env python3
"""Print the version of the working tree, stamped with where it comes from.

Usage:
  print-dev-version.py   # e.g. 1.18.0+feature.104.keep.flows.g294a988.dirty

The bare version of pyproject.toml gets a PEP 440 local label: the
branch, the short revision prefixed by `g` and, when the tree has
uncommitted changes to tracked files, `dirty`. A local version sorts
after the release it builds on, so a development install (make
install) is told apart from the release it extends. The label allows
letters, digits and dots only: any other character becomes a dot.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"


def extract_version() -> str:
    """The bare version of pyproject.toml."""
    with PYPROJECT_PATH.open("rb") as f:
        version: str = tomllib.load(f)["project"]["version"]
    return version


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()


def local_label(*, branch: str, revision: str, dirty: bool) -> str:
    """The PEP 440 local label of a tree: `branch.grevision[.dirty]`."""
    parts = [branch or "detached", f"g{revision}"]
    if dirty:
        parts.append("dirty")
    label = re.sub(r"[^A-Za-z0-9]+", ".", ".".join(parts))
    return label.strip(".")


def dev_version(version: str, *, label: str) -> str:
    return f"{version}+{label}"


def main() -> None:
    label = local_label(
        branch=git("branch", "--show-current"),
        revision=git("rev-parse", "--short", "HEAD"),
        dirty=bool(git("status", "--porcelain", "--untracked-files=no")),
    )
    print(dev_version(extract_version(), label=label))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: {' '.join(e.cmd)}: {e.stderr.strip()}")
