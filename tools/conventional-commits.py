#!/usr/bin/env python3
"""Conventional commits helper, driven by the bump map of pyproject.toml.

Usage:
  conventional-commits.py print-bump-table
      # the commit type to version bump map
  conventional-commits.py check-type-lists
      # the hook and the PR-title workflow accept exactly the map's types
  conventional-commits.py print-level-of-message
      # bump level of the commit message on stdin (subject, optional body)
  conventional-commits.py gate-pr-against-main --current X.Y.Z --next X.Y.Z
      # fail when the PR message on stdin would raise the pending level

The map is `[tool.semantic_release.commit_parser_options]`, the same
section python-semantic-release applies at release time, so the table
cannot drift from the actual behavior.
"""

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import assert_never

import yaml

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"
HOOK_CONFIG_PATH = ROOT / ".pre-commit-config.yaml"
PR_TITLE_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "pr-title.yml"
HOOK_ID = "conventional-pre-commit"

# `<type>[(scope)][!]: description`
SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)(\([^)]*\))?(?P<breaking>!)?: \S")
BREAKING_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE: ", re.MULTILINE)


class Bump(StrEnum):
    NONE = "none"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


# default_bump_level of python-semantic-release, by index
BUMP_LEVELS = [Bump.NONE, Bump.PATCH, Bump.MINOR, Bump.MAJOR]


@dataclass(frozen=True, kw_only=True)
class BumpMap:
    allowed_tags: list[str]
    minor_tags: list[str]
    patch_tags: list[str]
    default: Bump

    def bump_of(self, tag: str) -> Bump:
        if tag in self.minor_tags:
            return Bump.MINOR
        if tag in self.patch_tags:
            return Bump.PATCH
        return self.default


def load_bump_map() -> BumpMap:
    """Read the bump map from pyproject.toml."""
    with PYPROJECT_PATH.open("rb") as f:
        options = tomllib.load(f)["tool"]["semantic_release"][
            "commit_parser_options"
        ]
    return BumpMap(
        allowed_tags=options["allowed_tags"],
        minor_tags=options["minor_tags"],
        patch_tags=options["patch_tags"],
        default=BUMP_LEVELS[options["default_bump_level"]],
    )


def print_table(bump_map: BumpMap) -> None:
    """Print the type to bump table, one row per allowed type."""
    width = max(len(tag) for tag in bump_map.allowed_tags)
    print("Conventional commit type to version bump")
    print(f"  source: {PYPROJECT_PATH.name} [tool.semantic_release]")
    print()
    for tag in bump_map.allowed_tags:
        print(f"  {tag:<{width}}  {bump_map.bump_of(tag)}")
    print()
    print("  `<type>!:` or a `BREAKING CHANGE:` footer: major")


def load_hook_types() -> list[str]:
    """Read the type list the commit-msg hook accepts."""
    with HOOK_CONFIG_PATH.open() as f:
        config = yaml.safe_load(f)  # yaml boundary
    for repo in config["repos"]:
        for hook in repo["hooks"]:
            if hook["id"] == HOOK_ID:
                types: list[str] = hook["args"]
                return types
    sys.exit(f"ERROR: no hook {HOOK_ID} in {HOOK_CONFIG_PATH.name}")


def load_pr_title_types() -> list[str]:
    """Read the type list the PR-title workflow accepts."""
    with PR_TITLE_WORKFLOW_PATH.open() as f:
        workflow = yaml.safe_load(f)  # yaml boundary
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "with" in step and "types" in step["with"]:
                types: str = step["with"]["types"]
                return types.split()
    sys.exit(f"ERROR: no types input in {PR_TITLE_WORKFLOW_PATH.name}")


def check_types(bump_map: BumpMap) -> None:
    """Fail unless the hook and the workflow accept exactly the map's types."""
    expected = bump_map.allowed_tags
    ok = True
    for name, types in (
        (HOOK_CONFIG_PATH.name, load_hook_types()),
        (PR_TITLE_WORKFLOW_PATH.name, load_pr_title_types()),
    ):
        if types != expected:
            ok = False
            print(f"ERROR: {name} accepts {types}, expected {expected}")
    if not ok:
        sys.exit(1)
    print(f"Conventional commit types consistent: {' '.join(expected)}")


def parse_level(message: str, bump_map: BumpMap) -> Bump:
    """Bump level of a conventional commit message (subject, optional body)."""
    subject = message.strip().split("\n", 1)[0]
    m = SUBJECT_RE.match(subject)
    if not m:
        raise ValueError(f"not a conventional commit subject: {subject!r}")
    tag = m.group("type")
    if tag not in bump_map.allowed_tags:
        raise ValueError(f"unknown type {tag!r} in {subject!r}")
    if m.group("breaking") or BREAKING_FOOTER_RE.search(message):
        return Bump.MAJOR
    return bump_map.bump_of(tag)


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version: str) -> "Version":
        parts = version.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise ValueError(f"not a MAJOR.MINOR.PATCH version: {version!r}")
        major, minor, patch = (int(part) for part in parts)
        return cls(major, minor, patch)


def level_between(current: str, next_: str) -> Bump:
    """Bump level from one version to the next (none when equal)."""
    c, n = Version.parse(current), Version.parse(next_)
    if n == c:
        return Bump.NONE
    if n.major != c.major:
        return Bump.MAJOR
    if n.minor != c.minor:
        return Bump.MINOR
    return Bump.PATCH


@dataclass(frozen=True, kw_only=True)
class Verdict:
    allowed: bool
    reason: str


def gate_verdict(*, pending: Bump, incoming: Bump, next_: str) -> Verdict:
    """Allow a PR unless its level would raise a non-empty pending level.

    Unreleased changes on main never span two levels: a lower level is
    released before a higher one lands, so every level is closed before
    the next one opens.
    """
    rank = BUMP_LEVELS.index
    if pending != Bump.NONE and rank(incoming) > rank(pending):
        return Verdict(
            allowed=False,
            reason=f"a {incoming} PR would raise the pending {pending} level "
            f"of main: release {next_} first",
        )
    return Verdict(allowed=True, reason=f"{incoming} on pending {pending}")


def run_level(bump_map: BumpMap) -> None:
    """Print the bump level of the commit message on stdin."""
    try:
        print(parse_level(sys.stdin.read(), bump_map))
    except ValueError as e:
        sys.exit(f"ERROR: {e}")


def run_gate(bump_map: BumpMap, *, current: str, next_: str) -> None:
    """Gate the PR message on stdin against the pending level of main."""
    try:
        pending = level_between(current, next_)
        incoming = parse_level(sys.stdin.read(), bump_map)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")
    print(f"pending on main: {pending} ({current} -> {next_})")
    print(f"incoming PR:     {incoming}")
    verdict = gate_verdict(pending=pending, incoming=incoming, next_=next_)
    if not verdict.allowed:
        sys.exit(f"BLOCKED: {verdict.reason}")
    print(f"allowed: {verdict.reason}")


class Command(StrEnum):
    PRINT_BUMP_TABLE = "print-bump-table"
    CHECK_TYPE_LISTS = "check-type-lists"
    PRINT_LEVEL_OF_MESSAGE = "print-level-of-message"
    GATE_PR_AGAINST_MAIN = "gate-pr-against-main"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        Command.PRINT_BUMP_TABLE, help="print the type to bump map"
    )
    subparsers.add_parser(
        Command.CHECK_TYPE_LISTS,
        help="hook and workflow accept exactly the map's types",
    )
    subparsers.add_parser(
        Command.PRINT_LEVEL_OF_MESSAGE,
        help="bump level of the commit message on stdin",
    )
    gate = subparsers.add_parser(
        Command.GATE_PR_AGAINST_MAIN,
        help="gate the PR message on stdin against main",
    )
    gate.add_argument("--current", required=True, help="version of main")
    gate.add_argument("--next", required=True, help="next version of main")
    args = parser.parse_args()
    command = Command(args.command)  # argparse boundary

    bump_map = load_bump_map()
    match command:
        case Command.PRINT_BUMP_TABLE:
            print_table(bump_map)
        case Command.CHECK_TYPE_LISTS:
            check_types(bump_map)
        case Command.PRINT_LEVEL_OF_MESSAGE:
            run_level(bump_map)
        case Command.GATE_PR_AGAINST_MAIN:
            run_gate(bump_map, current=args.current, next_=args.next)
        case _:
            assert_never(command)


if __name__ == "__main__":
    main()
