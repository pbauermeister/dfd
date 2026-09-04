"""Internal data model"""

from __future__ import annotations

import dataclasses
import json
import typing
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from typing import Any, TypeVar, assert_never

from . import config


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


@dataclass(kw_only=True)
class Snippet(Base):
    text: str
    name: str
    output: str
    line_nr: int


@dataclass(kw_only=True)
class SourceLine(Base):
    text: str  # after pre-processor
    raw_text: str | None
    parent: SourceLine | None  # https://stackoverflow.com/a/62521947
    line_nr: int
    is_container: bool = False


# Statements
@dataclass(kw_only=True)
class Statement(Base):
    source: SourceLine


# Statements: options


T = TypeVar("T")

# Declarations attached to GraphOptions fields as dataclass metadata: which
# `style` keyword(s) set the field and how it is documented. Everything else
# (registry, parsing, doc tables) is derived from these declarations.
StyleFlags = dict[str, tuple[bool, str]]  # keyword -> (value, doc)
STYLE_METADATA = "style"  # the single dataclass metadata key


@dataclass(frozen=True)
class StyleFlagsDecl:
    flags: StyleFlags


@dataclass(frozen=True)
class StyleValueDecl:
    name: str  # DSL keyword
    doc: str
    placeholder: str  # word shown for the value in the docs


def declare_style_as_flags(*, default: bool, flags: StyleFlags) -> bool:
    """Declare a bool GraphOptions field set by flag `style` keywords.

    `flags` maps each DSL keyword to the value it sets and its doc.
    """
    decl = StyleFlagsDecl(flags)
    return dataclasses.field(default=default, metadata={STYLE_METADATA: decl})


def declare_style_as_value(
    *, default: T, name: str, doc: str, placeholder: str = "N"
) -> T:
    """Declare an int or str GraphOptions field set by a valued `style` keyword.

    `name` is the DSL keyword; `placeholder` is the word shown for the value
    in the docs. Type and default come from the field itself.
    """
    decl = StyleValueDecl(name, doc, placeholder)
    return dataclasses.field(default=default, metadata={STYLE_METADATA: decl})


@dataclass
class GraphOptions:
    """Whole-diagram rendering options. Declaration order is the doc order."""

    # layout
    is_vertical: bool = declare_style_as_flags(
        default=False,
        flags={
            "horizontal": (
                False,
                "Layouts flows in the horizontal direction (the default).",
            ),
            "vertical": (True, "Layouts flows in the vertical direction."),
        },
    )
    is_rotated: bool = declare_style_as_flags(
        default=False,
        flags={
            "rotated": (True, "Rotates the diagram by 90°."),
            "unrotated": (False, "Reverts the diagram rotation, if any."),
        },
    )
    is_context: bool = declare_style_as_flags(
        default=False,
        flags={"context": (True, "Makes the diagram a context diagram.")},
    )

    # text
    item_text_width: int = declare_style_as_value(
        default=config.DEFAULT_ITEM_TEXT_WIDTH,
        name="item-text-width",
        doc="Sets the items labels wrapping to use N chars columns.",
    )
    item_text_size: int = declare_style_as_value(
        default=config.DEFAULT_ITEM_TEXT_SIZE,
        name="item-text-size",
        doc="Sets the items label text size.",
    )
    connection_text_width: int = declare_style_as_value(
        default=config.DEFAULT_CONNECTION_TEXT_WIDTH,
        name="connection-text-width",
        doc="Sets the connections labels wrapping to use N chars columns.",
    )
    connection_text_size: int = declare_style_as_value(
        default=config.DEFAULT_CONNECTION_TEXT_SIZE,
        name="connection-text-size",
        doc="Sets the connections label text size.",
    )

    # graph
    background_color: str | None = declare_style_as_value(
        default=None,
        name="background-color",
        placeholder="COLOR",
        doc="Sets a graph background color as per "
        "https://graphviz.org/docs/attr-types/color/.",
    )
    no_graph_title: bool = declare_style_as_flags(
        default=False,
        flags={
            "no-graph-title": (
                True,
                "Suppress graph title containing the image file path "
                "(without extension).",
            ),
        },
    )
    graph_title_size: int = declare_style_as_value(
        default=config.DEFAULT_GRAPH_TITLE_SIZE,
        name="graph-title-size",
        doc="Sets the graph title text size.",
    )


class StyleKind(Enum):
    FLAG = auto()  # keyword sets a fixed bool value
    INT = auto()  # keyword takes an integer value
    STR = auto()  # keyword takes a string value


@dataclass(frozen=True, kw_only=True)
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
        match f.metadata[STYLE_METADATA]:
            case StyleFlagsDecl(flags):
                for keyword, (value, doc) in flags.items():
                    specs[keyword] = StyleSpec(
                        field=f.name,
                        kind=StyleKind.FLAG,
                        value=value,
                        doc=doc,
                        placeholder="",
                    )
            case StyleValueDecl(name, doc, placeholder):
                kind = StyleKind.INT if hints[f.name] is int else StyleKind.STR
                specs[name] = StyleSpec(
                    field=f.name,
                    kind=kind,
                    value=f.default,
                    doc=doc,
                    placeholder=placeholder,
                )
            case decl:
                raise TypeError(f"unexpected style declaration {decl!r}")
    return specs


STYLE_SPECS = _build_style_specs()  # keyword -> spec, in doc order


@dataclass(kw_only=True)
class Style(Statement):
    style: str
    value: str = ""


@dataclass(kw_only=True)
class Attrib(Statement):
    alias: str
    text: str


Attribs = dict[str, Attrib]


# Statements: elements
@dataclass(kw_only=True)
class Drawable(Statement):
    type: Keyword
    text: str
    attrs: str


@dataclass(kw_only=True)
class Item(Drawable):
    name: str
    hidable: bool


@dataclass(kw_only=True)
class Connection(Drawable):
    src: str
    dst: str
    reversed: bool = False
    relaxed: bool = False

    def signature(self) -> str:
        d = dataclasses.asdict(self).copy()
        del d["source"]
        return json.dumps(d, sort_keys=True)


@dataclass(kw_only=True)
class Frame(Drawable):
    items: list[str]


@dataclass(kw_only=True)
class FilterNeighbors:
    distance: int  # span: how many levels of neighbors (-1 = unlimited)
    suppress_anchors: bool  # "x" flag: select only neighbors, not anchors
    layout_direction: (
        bool  # use layout direction (left/right) instead of flow direction
    )
    suppress_frames: bool  # "f" flag: suppress frames involving selected items


@dataclass(kw_only=True)
class Filter(Statement):
    names: list[str]
    neighbors_up: FilterNeighbors
    neighbors_down: FilterNeighbors


@dataclass(kw_only=True)
class Only(Filter):
    pass


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
class Options:
    """These options can be specified as commandline args."""

    background_color: str | None
    no_graph_title: bool
    format: str
    no_check_dependencies: bool
    debug: bool


@dataclass(kw_only=True)
class GraphDependency:
    to_graph: str
    to_item: str | None
    to_type: Keyword
    source: SourceLine


GraphDependencies = list[GraphDependency]
