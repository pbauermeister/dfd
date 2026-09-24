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


@pytest.mark.parametrize(
    "path, expected",
    [
        pytest.param("TODO.md", True, id="todo"),
        pytest.param("devlog/107-x.md", True, id="devlog"),
        pytest.param(".claude/settings.json", True, id="dot-claude"),
        pytest.param("engineering/PROCESS.md", True, id="engineering"),
        pytest.param("doc/README.md", False, id="doc-ships"),
        pytest.param("README.md", False, id="readme-ships"),
        pytest.param("templates.py", False, id="prefix-not-dir"),
        pytest.param("src/TODO.md", False, id="nested-name"),
    ],
)
def test_is_bookkeeping(
    path: str,
    expected: bool,  # noqa: FBT001  pytest passes parameters by keyword
) -> None:
    assert cc.is_bookkeeping(path) is expected


@pytest.mark.parametrize(
    "level, paths, allowed",
    [
        pytest.param("patch", ["TODO.md"], False, id="docs-on-todo"),
        pytest.param("minor", ["devlog/1.md", "TODO.md"], False, id="all"),
        pytest.param("none", ["TODO.md"], True, id="chore-on-todo"),
        pytest.param("patch", ["TODO.md", "doc/x.md"], True, id="mixed"),
        pytest.param("patch", ["src/a.py"], True, id="ships"),
        pytest.param("patch", [], True, id="empty-commit"),
    ],
)
def test_bookkeeping_verdict(
    level: str,
    paths: list[str],
    allowed: bool,  # noqa: FBT001  pytest passes parameters by keyword
) -> None:
    verdict = cc.bookkeeping_verdict(level=cc.Bump(level), paths=paths)
    assert verdict.allowed is allowed


def test_read_commit_message_drops_comments(tmp_path: Path) -> None:
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text("docs: x\n# Please enter the commit message\n#\n")
    assert cc.read_commit_message(f) == "docs: x\n"


def test_bookkeeping_globs() -> None:
    globs = cc.bookkeeping_globs()
    assert "TODO.md" in globs
    assert "devlog/**" in globs
    assert not any(g.endswith("/") for g in globs)


def test_check_bookkeeping_lets_a_merge_commit_through(
    tmp_path: Path,
) -> None:
    f = tmp_path / "MERGE_MSG"
    f.write_text("Merge branch 'a' into b\n")
    cc.run_check_bookkeeping(BUMP_MAP, message_path=f)  # no SystemExit
