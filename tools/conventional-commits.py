#!/usr/bin/env python3
"""Conventional commits helper, driven by the bump map of pyproject.toml.

Usage:
  conventional-commits.py table   # print the commit type to version bump map

The map is `[tool.semantic_release.commit_parser_options]`, the same
section python-semantic-release applies at release time, so the table
cannot drift from the actual behavior.
"""

import argparse
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import assert_never

PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


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


class Command(StrEnum):
    TABLE = "table"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "command",
        type=Command,
        choices=list(Command),
        help="table: print the type to bump map",
    )
    args = parser.parse_args()
    command: Command = args.command  # argparse boundary

    bump_map = load_bump_map()
    match command:
        case Command.TABLE:
            print_table(bump_map)
        case _:
            assert_never(command)


if __name__ == "__main__":
    main()
