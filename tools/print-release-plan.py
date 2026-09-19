#!/usr/bin/env python3
"""Print the release plan: versions and the pending commits with levels.

Usage:
  print-release-plan.py   # exits 1 when nothing bumps since the last release

Current version from pyproject.toml, next one from
`semantic-release --noop version --print`, commits since the current
version's tag from git, their levels from conventional-commits.py.
Warns when a lower level precedes a higher one: the merge gate was
bypassed, and the next version closes both levels. Example:

  current version: 1.17.7
  next version:    1.18.0
  commits since v1.17.7:
    9cffd9e docs: CLAUDE.md, one pushed commit per design step  [patch]
    7d3ff3f ci: conventional commit hook, PR title check  [none]
    178cb0f feat: add the graph-title-color style option (#100)  [minor]
  WARNING: a lower level precedes a higher one (the merge gate was bypassed): v1.18.0 closes both
"""

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from changelog import extract_version

TOOLS_DIR = Path(__file__).resolve().parent
CC_PATH = TOOLS_DIR / "conventional-commits.py"


def load_conventional_commits() -> ModuleType:
    """Load conventional-commits.py (hyphenated name) as a module."""
    spec = importlib.util.spec_from_file_location(
        "conventional_commits", CC_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = load_conventional_commits()


@dataclass(frozen=True, kw_only=True)
class PendingCommit:
    sha: str
    subject: str
    level: str  # a cc.Bump value, or "?" when not conventional


def run(cmd: list[str]) -> str:
    return subprocess.run(
        cmd, check=True, text=True, capture_output=True
    ).stdout


def next_version() -> str:
    """Ask semantic-release for the next version (the current one if none)."""
    return run(["semantic-release", "--noop", "version", "--print"]).strip()


def pending_commits(current: str) -> list[PendingCommit]:
    """The commits since the current version's tag, oldest first, with levels."""
    bump_map = cc.load_bump_map()
    commits = []
    for sha in run(
        ["git", "rev-list", "--reverse", f"v{current}..HEAD"]
    ).split():
        message = run(["git", "log", "-1", "--format=%B", sha])
        try:
            level = str(cc.parse_level(message, bump_map))
        except ValueError:
            level = "?"
        subject = message.split("\n", 1)[0]
        commits.append(PendingCommit(sha=sha[:7], subject=subject, level=level))
    return commits


def level_order_broken(commits: list[PendingCommit]) -> bool:
    """True when a commit's level exceeds a non-none level seen before it."""
    rank = {str(bump): i for i, bump in enumerate(cc.BUMP_LEVELS)}
    highest = 0
    for commit in commits:
        r = rank.get(commit.level, 0)
        if r > highest:
            if highest > 0:
                return True
            highest = r
    return False


def main() -> None:
    current = extract_version()
    next_ = next_version()
    commits = pending_commits(current)

    print(f"current version: {current}")
    print(f"next version:    {next_}")
    print(f"commits since v{current}:")
    for commit in commits:
        print(f"  {commit.sha} {commit.subject}  [{commit.level}]")
    if level_order_broken(commits):
        print(
            "WARNING: a lower level precedes a higher one (the merge gate "
            f"was bypassed): v{next_} closes both"
        )
    if next_ == current:
        sys.exit(f"ERROR: nothing to release since v{current}")


if __name__ == "__main__":
    main()
