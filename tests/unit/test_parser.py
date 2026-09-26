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
        r"process  P  Dir C:\hello",
        id="stray-backslash",  # backslash not starting a recognized escape
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
        id="filter-spec-only",  # neighbor spec but no anchor names
    ),
    pytest.param(
        "!=replacement A",
        id="filter-replacer-on-only",  # replacer specification on Only (!) filter
    ),
    pytest.param(
        "!<>z1 A",
        id="filter-bad-flag",  # unrecognized neighbor flag 'z'
    ),
    pytest.param(
        """
        process  A  text
        process  B  text
        ~=  B  A
        """,
        id="bare-replacer-sign",  # "=" alone: the parser used to spin forever
    ),
    pytest.param(
        """
        process  B  text
        process  C  text
        process  G  text
        merge  B  C
        """,
        id="merge-no-colon",
    ),
    pytest.param(
        """
        process  B  text
        process  C  text
        process  G  text
        merge  :  G
        """,
        id="merge-no-items",
    ),
    pytest.param(
        """
        process  B  text
        process  C  text
        process  G  text
        merge  B  C  :
        """,
        id="merge-no-replacer",
    ),
    pytest.param(
        """
        process  B  text
        process  C  text
        process  G  text
        merge  B  C  :  G  B
        """,
        id="merge-two-replacers",
    ),
    pytest.param(
        """
        process  B  text
        process  C  text
        process  G  text
        merge  B  C  :  B
        """,
        id="merge-into-a-merged-item",
    ),
]


# ── Filter strictness fixtures ────────────────────────────────────────────────

# Each entry: (filter line, expected Only.strict).  "!!" is the strict only
# filter, whole-filter, with or without a neighbor spec; "!" is never strict.
FILTER_STRICTNESS_CASES = [
    pytest.param("!!<>2 A", True, id="strict-with-neighbors"),
    pytest.param("!! A", True, id="strict-anchors-only"),
    pytest.param("!!A", True, id="strict-no-space"),
    pytest.param("!<>2 A", False, id="plain-with-neighbors"),
    pytest.param("! A", False, id="plain-anchors-only"),
]


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_parse_valid_syntax() -> None:
    # Full valid DFD must pass both parse() and check() without error
    tokens = scanner.scan(
        provenance=None, source_text=ALL_ITEMS_AND_CONNECTIONS
    )
    try:
        statements, _, _ = parser.parse(tokens)
        checker.check(statements)
    except exception.DfdException as e:
        pytest.fail(f"Unexpected DfdException on valid syntax: {e}")


def test_parse_unknown_keyword_raises() -> None:
    # An unrecognised keyword must be caught by parse(), not silently ignored
    tokens = scanner.scan(provenance=None, source_text="xyz")
    with pytest.raises(exception.DfdException):
        parser.parse(tokens)


@pytest.mark.parametrize("dfd_text", CHECK_ERROR_CASES)
def test_check_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in check()
    tokens = scanner.scan(provenance=None, source_text=dfd_text)
    statements, _, _ = parser.parse(tokens)
    with pytest.raises(exception.DfdException):
        checker.check(statements)


@pytest.mark.parametrize(
    "specs",
    [
        pytest.param("<1 >2", id="upstream-and-downstream"),
        pytest.param("<1 <3", id="upstream-twice"),
        pytest.param(">1 ]1", id="stream-and-layout"),
        pytest.param("<>1 <3", id="both-then-upstream"),
    ],
)
def test_parse_filter_second_spec_raises(specs: str) -> None:
    # one neighbor specification per filter, "<>" being one
    tokens = scanner.scan(
        provenance=None, source_text=f"process A\n! {specs} A"
    )
    with pytest.raises(exception.DfdException, match="One neighbor"):
        parser.parse(tokens)


def test_parse_filter_second_replacer_raises() -> None:
    # the loop consumes every leading spec: a second replacer used to win
    tokens = scanner.scan(
        provenance=None, source_text="process A\nprocess B\n~=A =B A"
    )
    with pytest.raises(exception.DfdException, match="One replacer"):
        parser.parse(tokens)


@pytest.mark.parametrize(("filter_line", "strict"), FILTER_STRICTNESS_CASES)
def test_parse_filter_strictness(filter_line: str, *, strict: bool) -> None:
    # "!!" yields an Only statement flagged strict, "!" one that is not
    tokens = scanner.scan(
        provenance=None, source_text=f"process A\n{filter_line}"
    )
    statements, _, _ = parser.parse(tokens)
    only = statements[-1]
    assert isinstance(only, model.Only)
    assert only.strict is strict
    assert only.names == ["A"]


@pytest.mark.parametrize("dfd_text", PARSE_ERROR_CASES)
def test_parse_raises(dfd_text: str) -> None:
    # Each malformed snippet must trigger a DfdException in parse()
    tokens = scanner.scan(provenance=None, source_text=dfd_text)
    with pytest.raises(exception.DfdException):
        parser.parse(tokens)


def test_parse_merge() -> None:
    # "merge ITEMS : REPLACER" is a statement of its own
    tokens = scanner.scan(
        provenance=None,
        source_text="process B\nprocess C\nprocess G\nmerge B C : G",
    )
    statements, _, _ = parser.parse(tokens)
    merge = statements[-1]
    assert isinstance(merge, model.Merge)
    assert (merge.names, merge.replacer) == (["B", "C"], "G")


@pytest.mark.parametrize(
    ("line", "kinds", "hint"),
    [
        pytest.param(
            "~=G B C", [model.Merge], "write: merge B C : G\n", id="alone"
        ),
        pytest.param(
            "~<1 =G B C",
            [model.Merge, model.Without],
            "write: merge B C : G, then ~<x1 G\n",
            id="with-spec",
        ),
    ],
)
def test_parse_deprecated_replacer(
    *,
    line: str,
    kinds: list[type],
    hint: str,
    capsys: pytest.CaptureFixture[str],
) -> None:  # pytest passes parameters by keyword
    # the former "~[SPEC] =R ITEMS" yields a merge (and the neighbors'
    # removal, "x": not the group) with one warning naming the new form
    tokens = scanner.scan(
        provenance=None,
        source_text=f"process B\nprocess C\nprocess G\n{line}",
    )
    statements, _, _ = parser.parse(tokens)
    tail = statements[3:]
    assert [type(s) for s in tail] == kinds
    merge = tail[0]
    assert isinstance(merge, model.Merge)
    assert (merge.names, merge.replacer) == (["B", "C"], "G")
    if len(tail) == 2:
        without = tail[1]
        assert isinstance(without, model.Without)
        assert without.names == ["G"]
        assert without.neighbors_up.suppress_anchors
        assert without.neighbors_up.distance == 1
    err = capsys.readouterr().err
    assert err.count("deprecated") == 1
    assert err.endswith(hint)
