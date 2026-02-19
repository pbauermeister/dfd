"""Tests for the DFD generation pipeline (filters.handle_filters, dfd.handle_options).

These tests exercise error paths that occur after parsing: invalid filter
names, already-removed names, unknown style options, and bad style values.
"""

import pytest

from data_flow_diagram import dfd, exception, model
from data_flow_diagram.dsl import filters, parser, scanner


def _parse(dfd_text: str) -> model.Statements:
    """Scan, parse, and check a DFD snippet, returning its statements."""
    tokens = scanner.scan(None, dfd_text)
    statements, _, _ = parser.parse(tokens)
    parser.check(statements)
    return statements


# ── handle_filters error cases ────────────────────────────────────────────────


def test_filter_unknown_name() -> None:
    # Filtering on a name that doesn't exist in the diagram must raise
    statements = _parse(
        """
        process  A  aaa
        ! unknown_item
    """
    )
    with pytest.raises(exception.DfdException, match="unknown"):
        filters.handle_filters(statements)


def test_filter_already_removed() -> None:
    # Removing a name that was already removed by a previous filter must raise
    statements = _parse(
        """
        process  A  aaa
        process  B  bbb
        ~ A
        ~ A
    """
    )
    with pytest.raises(exception.DfdException, match="no longer available"):
        filters.handle_filters(statements)


def test_filter_replacer_unknown() -> None:
    # Replacing with a name that doesn't exist in the diagram must raise
    statements = _parse(
        """
        process  A  aaa
        process  B  bbb
        ~ =NONEXISTENT A
    """
    )
    with pytest.raises(exception.DfdException, match="unknown"):
        filters.handle_filters(statements)


# ── handle_options error cases ────────────────────────────────────────────────


def test_style_unknown() -> None:
    # An unrecognized style name must raise
    statements = _parse(
        """
        style  unknown_style_name
    """
    )
    with pytest.raises(exception.DfdException, match="Unsupported style"):
        dfd.handle_options(statements)


def test_style_bad_int() -> None:
    # A style that expects an integer but receives text must raise
    statements = _parse(
        """
        style  item-text-width  abc
    """
    )
    with pytest.raises(exception.DfdException):
        dfd.handle_options(statements)
