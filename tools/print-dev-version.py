#!/usr/bin/env python3
"""Print the stamp of the working tree, for a development install.

Usage:
  print-dev-version.py   # e.g. 0+feature.104.keep.flows.git294a988.dirty

A stamp, not a version: the release segment is `0`, which claims no
base and sorts below every release, and the PEP 440 local label says
where the tree comes from: the branch, the short revision prefixed by
`git` and, when the tree has uncommitted changes to tracked files,
`dirty`. The revision names the base; a development install (make
install) is thus told apart from any release, and a release always
upgrades it. The label allows letters, digits and dots only: any
other character becomes a dot.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE_SEGMENT = "0"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()


def local_label(*, branch: str, revision: str, dirty: bool) -> str:
    """The PEP 440 local label of a tree: `branch.gitrevision[.dirty]`."""
    parts = [branch or "detached", f"git{revision}"]
    if dirty:
        parts.append("dirty")
    label = re.sub(r"[^A-Za-z0-9]+", ".", ".".join(parts))
    return label.strip(".")


def dev_version(label: str) -> str:
    return f"{RELEASE_SEGMENT}+{label}"


def main() -> None:
    label = local_label(
        branch=git("branch", "--show-current"),
        revision=git("rev-parse", "--short", "HEAD"),
        dirty=bool(git("status", "--porcelain", "--untracked-files=no")),
    )
    print(dev_version(label))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: {' '.join(e.cmd)}: {e.stderr.strip()}")
