"""Tests for the scanner and parser (scanner.scan, parser.parse, parser.check).

The scanner is exercised here as a prerequisite to parsing; dedicated scanner
tests (e.g. for include resolution) belong in a future test_scanner.py.
"""

import pytest

from data_flow_diagram import model, parser, scanner

# ── Valid syntax fixture ──────────────────────────────────────────────────────

# A DFD snippet that exercises every item type and several connection types;
# parse() and check() must both accept it without raising.
ALL_ITEMS_AND_CONNECTIONS = """
style\tvertical
style\thorizontal

process\tP\tProcess
process\tP2\tProcess 2
entity\tT\tTerminal
store\tS\tStore
channel\tC\tChannel
channel\tC2\tChannel 2b

flow\tP\tC\tdata
bflow\tP\tS\tconfig
signal\tP\tP2\tevent
flow\tP2\tC2\tmore data
flow\t*\tP2\text data
flow\tP\tT
"""

# ── Error case fixtures ───────────────────────────────────────────────────────

# Each entry: (dfd_text, pytest id).  All should make parser.check() raise.
CHECK_ERROR_CASES = [
    pytest.param(
        "process\tP text\nentity P text",
        id="duplicate-item",  # two items share the same name
    ),
    pytest.param(
        "process\tP text\nflow P Q text",
        id="missing-ref",  # connection references undefined item Q
    ),
    pytest.param(
        "flow * * text",
        id="double-star",  # both endpoints of a connection are wildcards
    ),
]


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_parse_valid_syntax():
    # Full valid DFD must pass both parse() and check() without error
    tokens = scanner.scan(None, ALL_ITEMS_AND_CONNECTIONS)
    try:
        parser.parse(tokens)
    except model.DfdException as e:
        pytest.fail(f"Unexpected DfdException on valid syntax: {e}")


def test_parse_unknown_keyword_raises():
    # An unrecognised keyword must be caught by parse(), not silently ignored
    tokens = scanner.scan(None, "xyz")
    with pytest.raises(model.DfdException):
        parser.parse(tokens)


@pytest.mark.parametrize("dfd_text", CHECK_ERROR_CASES)
def test_check_raises(dfd_text):
    # Each malformed snippet must trigger a DfdException in check()
    tokens = scanner.scan(None, dfd_text)
    statements, _, _ = parser.parse(tokens)
    with pytest.raises(model.DfdException):
        parser.check(statements)
