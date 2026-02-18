"""Tests for the scanner include resolution (scanner.scan, scanner.include).

These tests exercise error paths in the #include directive handling:
recursive includes, missing files, and missing/invalid snippets.
"""

from pathlib import Path

import pytest

from data_flow_diagram import model, scanner


def test_include_nonexistent_file() -> None:
    # Including a file that does not exist must raise
    dfd_text = "#include __nonexistent_file_that_does_not_exist__.dfd"
    with pytest.raises(model.DfdException, match="not found"):
        scanner.scan(None, dfd_text)


def test_include_snippet_not_markdown() -> None:
    # Including a snippet (#name) outside a markdown context must raise
    dfd_text = "#include #my_snippet"
    with pytest.raises(model.DfdException, match="not markdown"):
        scanner.scan(None, dfd_text, snippet_by_name=None)


def test_include_snippet_not_found() -> None:
    # Including a snippet that doesn't exist in the snippet map must raise
    dfd_text = "#include #nosuchsnippet"
    # snippet_by_name must be non-empty (truthy) to reach the "not found" path
    dummy_snippet = model.Snippet(text="x", name="other", output="o", line_nr=0)
    with pytest.raises(model.DfdException, match="not found"):
        scanner.scan(None, dfd_text, snippet_by_name={"other": dummy_snippet})


def test_include_recursive(tmp_path: Path) -> None:
    # A file that includes itself must be detected as recursive
    self_including = tmp_path / "self.dfd"
    self_including.write_text(f"#include {self_including}\nprocess\tP\tProc")
    with pytest.raises(model.DfdException, match="Recursive"):
        scanner.scan(None, self_including.read_text())
