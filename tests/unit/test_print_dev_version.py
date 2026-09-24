"""Unit tests for tools/print-dev-version.py: the local label."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

TOOL_PATH = (
    Path(__file__).resolve().parents[2] / "tools" / "print-dev-version.py"
)


def load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "print_dev_version", TOOL_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load_tool()


@pytest.mark.parametrize(
    "branch, revision, dirty, expected",
    [
        pytest.param("main", "c0afbb3", False, "main.gc0afbb3", id="clean"),
        pytest.param(
            "main", "c0afbb3", True, "main.gc0afbb3.dirty", id="dirty"
        ),
        pytest.param(
            "feature/104-keep_flows",
            "294a988",
            False,
            "feature.104.keep.flows.g294a988",
            id="separators-to-dots",
        ),
        pytest.param("", "294a988", False, "detached.g294a988", id="detached"),
        pytest.param("a--b/", "1", False, "a.b.g1", id="runs-collapse"),
    ],
)
def test_local_label(
    *, branch: str, revision: str, dirty: bool, expected: str
) -> None:  # pytest passes parameters by keyword
    assert (
        tool.local_label(branch=branch, revision=revision, dirty=dirty)
        == expected
    )


def test_dev_version() -> None:
    assert tool.dev_version("1.18.0", label="main.gc0afbb3") == (
        "1.18.0+main.gc0afbb3"
    )
