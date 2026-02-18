"""Tests for Markdown snippet extraction (markdown.extract_snippets)."""

from data_flow_diagram import model
from data_flow_diagram.markdown import extract_snippets


def test_extract_snippets_finds_dfd_blocks(
    md_with_two_snippets: str,
    md_expected_snippets: list[model.Snippet],
) -> None:
    # Only data-flow-diagram blocks must be extracted; unrelated blocks ignored
    result = extract_snippets(md_with_two_snippets)
    assert result == md_expected_snippets
