"""Tests for the scanner and parser (scanner.scan, parser.parse, parser.check).

The scanner is exercised here as a prerequisite to parsing; dedicated scanner
tests (e.g. for include resolution) belong in test_scanner.py.
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
control\tCtrl\tController

flow\tP\tC\tdata
bflow\tP\tS\tconfig
signal\tP\tP2\tevent
signal\tCtrl\tP\tcontrol event
flow\tP2\tC2\tmore data
flow\t*\tP2\text data
flow\tP\tT

frame P P2 = Processes
"""

# ── Error case fixtures ───────────────────────────────────────────────────────

# Each entry: (dfd_text, pytest id).  All should make parser.check() raise.
CHECK_ERROR_CASES = [
    pytest.param(
        "process\tP\ttext\nentity\tP\ttext",
        id="duplicate-item",  # two items share the same name
    ),
    pytest.param(
        "process\tP\ttext\nflow\tP\tQ\ttext",
        id="missing-ref",  # connection references undefined item Q
    ),
    pytest.param(
        "flow\t*\t*\ttext",
        id="double-star",  # both endpoints of a connection are wildcards
    ),
    pytest.param(
        "control\tC\tCtrl\nflow\tC\t*\tdata",
        id="connection-to-control",  # non-signal connection to a control item
    ),
    pytest.param(
        "frame = Title",
        id="empty-frame",  # frame with no item names
    ),
    pytest.param(
        "process\tP\tProc\nframe UNKNOWN = Title",
        id="frame-undefined-item",  # frame references an item that doesn't exist
    ),
    pytest.param(
        "process\tA\ta\nprocess\tB\tb\nframe A = F1\nframe A B = F2",
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
        "flow\tA",
        id="missing-connection-args",  # connection with too few arguments
    ),
    pytest.param(
        "!",
        id="filter-no-args",  # filter keyword alone
    ),
    pytest.param(
        "! <>2",
        id="filter-spec-only",  # neighbour spec but no anchor names
    ),
    pytest.param(
        "! =replacement A",
        id="filter-replacer-on-only",  # replacer specification on Only (!) filter
    ),
    pytest.param(
        "! <>z1 A",
        id="filter-bad-flag",  # unrecognized neighbour flag 'z'
    ),
]


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_parse_valid_syntax() -> None:
    # Full valid DFD must pass both parse() and check() without error
    tokens = scanner.scan(None, ALL_ITEMS_AND_CONNECTIONS)
    try:
        statements, _, _ = parser.parse(tokens)
        parser.check(statements)
    except model.DfdException as e:
        pytest.fail(f"Unexpected DfdException on valid syntax: {e}")


def test_parse_unknown_keyword_raises() -> None:
    # An unrecognised keyword must be caught by parse(), not silently ignored
    tokens = scanner.scan(None, "xyz")
    with pytest.raises(model.DfdException):
        parser.parse(tokens)


@pytest.mark.parametrize("dfd_text", CHECK_ERROR_CASES)  # type: ignore[misc]
def test_check_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in check()
    tokens = scanner.scan(None, dfd_text)
    statements, _, _ = parser.parse(tokens)
    with pytest.raises(model.DfdException):
        parser.check(statements)


@pytest.mark.parametrize("dfd_text", PARSE_ERROR_CASES)  # type: ignore[misc]
def test_parse_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in parse()
    tokens = scanner.scan(None, dfd_text)
    with pytest.raises(model.DfdException):
        parser.parse(tokens)
