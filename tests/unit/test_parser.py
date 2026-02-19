"""Tests for the scanner, parser, and checker (scanner.scan, parser.parse, checker.check).

The scanner is exercised here as a prerequisite to parsing; dedicated scanner
tests (e.g. for include resolution) belong in test_scanner.py.
"""

import pytest

from data_flow_diagram import exception, model
from data_flow_diagram.dsl import checker, parser, scanner

# ── Valid syntax fixture ──────────────────────────────────────────────────────

# A DFD snippet that exercises every item type and several connection types;
# parse() and check() must both accept it without raising.
ALL_ITEMS_AND_CONNECTIONS = """
    style    vertical
    style    horizontal

    process  P     Process
    process  P2    Process 2
    entity   T     Terminal
    store    S     Store
    channel  C     Channel
    channel  C2    Channel 2b
    control  Ctrl  Controller

    P     -->  C     data
    P     <->  S     config
    P     ::>  P2    event
    Ctrl  ::>  P     control event
    P2    -->  C2    more data
    *     -->  P2    ext data
    P     -->  T

    frame P P2 = Processes
"""

# ── Error case fixtures ───────────────────────────────────────────────────────

# Each entry: (dfd_text, pytest id).  All should make checker.check() raise.
CHECK_ERROR_CASES = [
    pytest.param(
        """
        process  P  text
        entity   P  text
        """,
        id="duplicate-item",  # two items share the same name
    ),
    pytest.param(
        """
        process  P  text
        P  -->  Q  text
        """,
        id="missing-ref",  # connection references undefined item Q
    ),
    pytest.param(
        "*  -->  *  text",
        id="double-star",  # both endpoints of a connection are wildcards
    ),
    pytest.param(
        """
        control  C  Ctrl
        C  -->  *  data
        """,
        id="connection-to-control",  # non-signal connection to a control item
    ),
    pytest.param(
        "frame = Title",
        id="empty-frame",  # frame with no item names
    ),
    pytest.param(
        """
        process  P  Proc
        frame UNKNOWN = Title
        """,
        id="frame-undefined-item",  # frame references an item that doesn't exist
    ),
    pytest.param(
        """
        process  A  a
        process  B  b
        frame A = F1
        frame A B = F2
        """,
        id="frame-item-in-multiple",  # item A appears in two different frames
    ),
]

# Each entry: (dfd_text, pytest id).  All should make parser.parse() raise.
PARSE_ERROR_CASES = [
    pytest.param(
        "process",
        id="missing-item-args",  # item keyword with no name
    ),
    pytest.param(
        "A  -->",
        id="missing-connection-args",  # connection with too few arguments
    ),
    pytest.param(
        "!",
        id="filter-no-args",  # filter keyword alone
    ),
    pytest.param(
        "!<>2",
        id="filter-spec-only",  # neighbour spec but no anchor names
    ),
    pytest.param(
        "!=replacement A",
        id="filter-replacer-on-only",  # replacer specification on Only (!) filter
    ),
    pytest.param(
        "!<>z1 A",
        id="filter-bad-flag",  # unrecognized neighbour flag 'z'
    ),
]


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_parse_valid_syntax() -> None:
    # Full valid DFD must pass both parse() and check() without error
    tokens = scanner.scan(None, ALL_ITEMS_AND_CONNECTIONS)
    try:
        statements, _, _ = parser.parse(tokens)
        checker.check(statements)
    except exception.DfdException as e:
        pytest.fail(f"Unexpected DfdException on valid syntax: {e}")


def test_parse_unknown_keyword_raises() -> None:
    # An unrecognised keyword must be caught by parse(), not silently ignored
    tokens = scanner.scan(None, "xyz")
    with pytest.raises(exception.DfdException):
        parser.parse(tokens)


@pytest.mark.parametrize("dfd_text", CHECK_ERROR_CASES)  # type: ignore[misc]
def test_check_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in check()
    tokens = scanner.scan(None, dfd_text)
    statements, _, _ = parser.parse(tokens)
    with pytest.raises(exception.DfdException):
        checker.check(statements)


@pytest.mark.parametrize("dfd_text", PARSE_ERROR_CASES)  # type: ignore[misc]
def test_parse_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in parse()
    tokens = scanner.scan(None, dfd_text)
    with pytest.raises(exception.DfdException):
        parser.parse(tokens)
