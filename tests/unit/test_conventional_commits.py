"""Unit tests for tools/conventional-commits.py: bump levels and the gate.

The tool is a script with a hyphenated name: loaded with importlib.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

TOOL_PATH = (
    Path(__file__).resolve().parents[2] / "tools" / "conventional-commits.py"
)


def load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "conventional_commits", TOOL_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = load_tool()

# the bump map of pyproject.toml, as data: the tests are independent of it
BUMP_MAP = cc.BumpMap(
    allowed_tags=["feat", "fix", "docs", "chore"],
    minor_tags=["feat"],
    patch_tags=["fix", "docs"],
    default=cc.Bump.NONE,
)


@pytest.mark.parametrize(
    "message, expected",
    [
        pytest.param("feat: add x", "minor", id="feat"),
        pytest.param("fix(scope): handle y", "patch", id="fix-scope"),
        pytest.param("docs: readme", "patch", id="docs"),
        pytest.param("chore: bump actions", "none", id="chore"),
        pytest.param("feat!: drop z", "major", id="bang"),
        pytest.param("fix(a)!: drop z", "major", id="bang-scope"),
        pytest.param(
            "fix: x\n\nBREAKING CHANGE: the y option is gone",
            "major",
            id="footer",
        ),
        pytest.param(
            "chore: x\n\nBREAKING-CHANGE: y", "major", id="footer-dash"
        ),
        pytest.param(
            "feat: x\n\nsee BREAKING CHANGE: not a footer",
            "minor",
            id="footer-inline",
        ),
    ],
)
def test_parse_level(message: str, expected: str) -> None:
    assert cc.parse_level(message, BUMP_MAP) == expected


@pytest.mark.parametrize(
    "message",
    [
        pytest.param("Fix #84: old style", id="old-style"),
        pytest.param("revert: not in the map", id="unknown-type"),
        pytest.param("feat:no space", id="no-space"),
        pytest.param("", id="empty"),
    ],
)
def test_parse_level_rejects(message: str) -> None:
    with pytest.raises(ValueError):
        cc.parse_level(message, BUMP_MAP)


@pytest.mark.parametrize(
    "current, next_, expected",
    [
        pytest.param("1.17.7", "1.17.7", "none", id="equal"),
        pytest.param("1.17.7", "1.17.8", "patch", id="patch"),
        pytest.param("1.17.7", "1.18.0", "minor", id="minor"),
        pytest.param("1.17.7", "2.0.0", "major", id="major"),
    ],
)
def test_level_between(current: str, next_: str, expected: str) -> None:
    assert cc.level_between(current, next_) == expected


def test_level_between_rejects_dev_version() -> None:
    with pytest.raises(ValueError):
        cc.level_between("1.17.7", "1.17.8.dev1")


@pytest.mark.parametrize(
    "pending, incoming, allowed",
    [
        pytest.param("none", "major", True, id="empty-main"),
        pytest.param("patch", "patch", True, id="patch-on-patch"),
        pytest.param("patch", "minor", False, id="minor-on-patch"),
        pytest.param("patch", "major", False, id="major-on-patch"),
        pytest.param("minor", "patch", True, id="patch-on-minor"),
        pytest.param("minor", "minor", True, id="minor-on-minor"),
        pytest.param("minor", "major", False, id="major-on-minor"),
        pytest.param("major", "major", True, id="major-on-major"),
        pytest.param("patch", "none", True, id="none-on-patch"),
    ],
)
def test_gate_verdict(
    pending: str,
    incoming: str,
    allowed: bool,  # noqa: FBT001  pytest passes parameters by keyword
) -> None:
    verdict = cc.gate_verdict(
        pending=cc.Bump(pending), incoming=cc.Bump(incoming), next_="1.17.8"
    )
    assert verdict.allowed is allowed
    if not allowed:
        assert "release 1.17.8 first" in verdict.reason
