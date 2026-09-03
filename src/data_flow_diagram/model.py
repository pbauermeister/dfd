"""Internal data model"""

from __future__ import annotations

import dataclasses
import json
import typing
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, TypeVar


def repr(o: Any) -> str:
    name: str = o.__class__.__name__
    val: str = json.dumps(dataclasses.asdict(o), indent="  ")
    return f"{name} {val}"


##############################################################################
# Classes representing elements, statements, and internal data structures


@dataclass
class Base:
    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + " "
            + json.dumps(dataclasses.asdict(self), indent="  ")
        )


# Source text


@dataclass
class Snippet(Base):
    text: str
    name: str
    output: str
    line_nr: int


@dataclass
class SourceLine(Base):
    text: str  # after pre-processor
    raw_text: str | None
    parent: SourceLine | None  # https://stackoverflow.com/a/62521947
    line_nr: int
    is_container: bool = False


# Statements
@dataclass
class Statement(Base):
    source: SourceLine


# Statements: options


T = TypeVar("T")

# Metadata attached to each GraphOptions field: which `style` keyword(s) set
# it and how it is documented. Everything else (registry, parsing, doc
# tables) is derived from these declarations.
StyleFlags = dict[str, tuple[bool, str]]  # keyword -> (value, doc)


def style(
    default: T,
    *,
    name: str = "",
    doc: str = "",
    placeholder: str = "N",
    flags: StyleFlags | None = None,
) -> T:
    """Declare a GraphOptions field settable by a `style` statement.

    Valued options (int or str fields) give `name` (the DSL keyword),
    `doc`, and the `placeholder` word shown for the value in the docs.
    Flag options (bool fields) give `flags`, mapping each DSL keyword to the
    value it sets and its doc. Type and default come from the field itself.
    """
    metadata = {
        "name": name,
        "doc": doc,
        "placeholder": placeholder,
        "flags": flags or {},
    }
    return dataclasses.field(default=default, metadata=metadata)


@dataclass
class GraphOptions:
    """Whole-diagram rendering options. Declaration order is the doc order."""

    # layout
    is_vertical: bool = style(
        False,
        flags={
            "horizontal": (
                False,
                "Layouts flows in the horizontal direction (the default).",
            ),
            "vertical": (True, "Layouts flows in the vertical direction."),
        },
    )
    is_rotated: bool = style(
        False,
        flags={
            "rotated": (True, "Rotates the diagram by 90°."),
            "unrotated": (False, "Reverts the diagram rotation, if any."),
        },
    )
    is_context: bool = style(
        False,
        flags={"context": (True, "Makes the diagram a context diagram.")},
    )

    # text
    item_text_width: int = style(
        20,
        name="item-text-width",
        doc="Sets the items labels wrapping to use N chars columns.",
    )
    item_text_size: int = style(
        10,
        name="item-text-size",
        doc="Sets the items label text size.",
    )
    connection_text_width: int = style(
        14,
        name="connection-text-width",
        doc="Sets the connections labels wrapping to use N chars columns.",
    )
    connection_text_size: int = style(
        10,
        name="connection-text-size",
        doc="Sets the connections label text size.",
    )

    # graph
    background_color: str | None = style(
        None,
        name="background-color",
        placeholder="COLOR",
        doc="Sets a graph background color as per "
        "https://graphviz.org/docs/attr-types/color/.",
    )
    no_graph_title: bool = style(
        False,
        flags={
            "no-graph-title": (
                True,
                "Suppress graph title containing the image file path "
                "(without extension).",
            ),
        },
    )
    graph_title_size: int = style(
        9,
        name="graph-title-size",
        doc="Sets the graph title text size.",
    )


StyleKind = Literal["flag", "int", "str"]


@dataclass(frozen=True)
class StyleSpec:
    """One `style` keyword: the GraphOptions field it sets, and how."""

    field: str
    kind: StyleKind
    value: Any  # fixed value for flags; default value otherwise
    doc: str
    placeholder: str  # value placeholder word in docs (valued options only)


def _build_style_specs() -> dict[str, StyleSpec]:
    """Derive the keyword registry from the GraphOptions declarations."""
    specs: dict[str, StyleSpec] = {}
    hints = typing.get_type_hints(GraphOptions)
    for f in dataclasses.fields(GraphOptions):
        md = f.metadata
        if md["flags"]:
            for keyword, (value, doc) in md["flags"].items():
                specs[keyword] = StyleSpec(f.name, "flag", value, doc, "")
        else:
            kind: StyleKind = "int" if hints[f.name] is int else "str"
            specs[md["name"]] = StyleSpec(
                f.name, kind, f.default, md["doc"], md["placeholder"]
            )
    return specs


STYLE_SPECS = _build_style_specs()  # keyword -> spec, in doc order


@dataclass
class Style(Statement):
    style: str
    value: str = ""


@dataclass
class Attrib(Statement):
    alias: str
    text: str


Attribs = dict[str, Attrib]


# Statements: elements
@dataclass
class Drawable(Statement):
    type: Keyword
    text: str
    attrs: str


@dataclass
class Item(Drawable):
    name: str
    hidable: bool


@dataclass
class Connection(Drawable):
    src: str
    dst: str
    reversed: bool = False
    relaxed: bool = False

    def signature(self) -> str:
        d = dataclasses.asdict(self).copy()
        del d["source"]
        return json.dumps(d, sort_keys=True)


@dataclass
class Frame(Drawable):
    items: list[str]


@dataclass
class FilterNeighbors:
    distance: int  # span: how many levels of neighbors (-1 = unlimited)
    suppress_anchors: bool  # "x" flag: select only neighbors, not anchors
    layout_direction: (
        bool  # use layout direction (left/right) instead of flow direction
    )
    suppress_frames: bool  # "f" flag: suppress frames involving selected items


@dataclass
class Filter(Statement):
    names: list[str]
    neighbors_up: FilterNeighbors
    neighbors_down: FilterNeighbors


@dataclass
class Only(Filter):
    pass


@dataclass
class Without(Filter):
    replaced_by: str


##############################################################################
# Statement keywords


class Keyword(StrEnum):
    STYLE = "style"
    ATTRIB = "attrib"

    PROCESS = "process"
    CONTROL = "control"
    ENTITY = "entity"
    STORE = "store"
    CHANNEL = "channel"
    NONE = "none"
    STAR = "star"

    FLOW = "flow"
    BFLOW = "bflow"
    CFLOW = "cflow"
    UFLOW = "uflow"
    SIGNAL = "signal"
    CONSTRAINT = "constraint"

    FRAME = "frame"

    ONLY = "!"
    WITHOUT = "~"

    # Connection variants
    FLOW_REVERSED = "flow.r"
    FLOW_RELAXED = "flow?"
    FLOW_REVERSED_RELAXED = "flow.r?"
    CFLOW_REVERSED = "cflow.r"
    CFLOW_RELAXED = "cflow?"
    CFLOW_REVERSED_RELAXED = "cflow.r?"
    BFLOW_RELAXED = "bflow?"
    UFLOW_RELAXED = "uflow?"
    SIGNAL_REVERSED = "signal.r"
    SIGNAL_RELAXED = "signal?"
    SIGNAL_REVERSED_RELAXED = "signal.r?"
    CONSTRAINT_REVERSED = "constraint.r"


##############################################################################
# DSL syntax literals

ENDPOINT_STAR = "*"  # anonymous endpoint: generates a distinct star item
ALL_NEIGHBORS = "*"  # unlimited span in filter neighbor spec
SNIPPET_PREFIX = "#"  # prefix distinguishing snippet references from file paths
INCLUDE_DIRECTIVE = "#include"  # DSL directive for including external sources


##############################################################################
# Helpers


def pack(src_line: str | None) -> str:
    if src_line is None:
        return "<none>"
    return " ".join(src_line.split())


# Handy type aliases
Snippets = list[Snippet]
SourceLines = list[SourceLine]
Statements = list[Statement]
SnippetByName = dict[str, Snippet]


@dataclass
class Options:
    """These options can be specified as commandline args."""

    background_color: str | None
    no_graph_title: bool
    format: str
    no_check_dependencies: bool
    debug: bool


@dataclass
class GraphDependency:
    to_graph: str
    to_item: str | None
    to_type: Keyword
    source: SourceLine


GraphDependencies = list[GraphDependency]
