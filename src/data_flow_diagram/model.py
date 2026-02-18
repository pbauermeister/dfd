"""Internal data model"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from . import config


def repr(o: Any) -> str:
    name: str = o.__class__.__name__
    val: str = json.dumps(dataclasses.asdict(o), indent="  ")
    return f"{name} {val}"


##############################################################################
# Classes representing elementsstatements and internal data structures


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


@dataclass
class GraphOptions:
    is_vertical: bool = False
    is_context: bool = False
    is_rotated: bool = False
    item_text_width: int = config.DEFAULT_ITEM_TEXT_WIDTH
    connection_text_width: int = config.DEFAULT_CONNECTION_TEXT_WIDTH
    background_color: str | None = None
    no_graph_title: bool = False


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
    distance: int  # neighborhood distance to keep, or -1 for all
    no_anchors: bool  # consider only neighbors, not listed nodes themselves
    layout_dir: bool  # consider layout direction, not flow direction
    no_frames: bool  # suppress impacted frames


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
# Style options


class StyleOption(StrEnum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    CONTEXT = "context"
    ROTATED = "rotated"
    UNROTATED = "unrotated"
    ITEM_TEXT_WIDTH = "item-text-width"
    CONNECTION_TEXT_WIDTH = "connection-text-width"
    BACKGROUND_COLOR = "background-color"
    NO_GRAPH_TITLE = "no-graph-title"


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

NODE_STAR = "*"  # star as src/dst in connections will declare and generate a distinct "none" node
ALL_NEIGHBORS = "*"  # "all" distance in filter neighbor spec
SNIPPET_PREFIX = "#"  # prefix distinguishing snippet references from file paths
INCLUDE_DIRECTIVE = "#include"  # DSL directive for including external sources


##############################################################################
# Helpers


def pack(src_line: str | None) -> str:
    if src_line is None:
        return "<none>"
    return " ".join(src_line.split())


def mk_err_prefix_from(src: SourceLine) -> str:

    def _add_to_stack(stack: list[str], src: SourceLine) -> None:
        if src.line_nr is None:
            stack += [f"  {pack(src.raw_text)}"]
        else:
            if src.parent and src.parent.is_container:
                nr = src.parent.line_nr + 1
                delta = src.line_nr + 1
                final = nr + delta
                stack += [f"  line {final}: {pack(src.raw_text)}"]
            else:
                nr = src.line_nr + 1
                stack += [f"  line {nr}: {pack(src.raw_text)}"]
        if src.parent:
            _add_to_stack(stack, src.parent)

    stack: list[str] = ["(most recent first)"]
    _add_to_stack(stack, src)
    stack += [""]
    return "\n".join(stack) + "Error: "


class DfdException(Exception):
    pass


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
