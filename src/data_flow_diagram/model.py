"""Internal data model"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any

from . import config


def repr(o: Any) -> str:
    name: str = o.__class__.__name__
    val: str = json.dumps(dataclasses.asdict(o), indent='  ')
    return f'{name} {val}'


@dataclass
class Base:
    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + ' '
            + json.dumps(dataclasses.asdict(self), indent='  ')
        )


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


@dataclass
class Statement(Base):
    source: SourceLine


@dataclass
class Drawable(Statement):
    type: str
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


@dataclass
class Frame(Drawable):
    items: list[str]


@dataclass
class Style(Statement):
    style: str
    value: Any = None


@dataclass
class Attrib(Statement):
    alias: str
    text: str


Attribs = dict[str, Attrib]


STYLE = 'style'

PROCESS = 'process'
CONTROL = 'control'
ENTITY = 'entity'
STORE = 'store'
CHANNEL = 'channel'
NONE = 'none'

FLOW = 'flow'
BFLOW = 'bflow'
CFLOW = 'cflow'
UFLOW = 'uflow'
SIGNAL = 'signal'

FRAME = 'frame'

ATTRIB = 'attrib'


@dataclass
class GraphOptions:
    is_vertical: bool = False
    is_context: bool = False
    item_text_width = config.DEFAULT_ITEM_TEXT_WIDTH
    connection_text_width = config.DEFAULT_CONNECTION_TEXT_WIDTH


def pack(src_line: str | None) -> str:
    if src_line is None:
        return '<none>'
    return ' '.join(src_line.split())


def mk_err_prefix_from(src: SourceLine) -> str:

    def _add_to_stack(stack: list[str], src: SourceLine) -> None:
        if src.line_nr is None:
            stack += [f'  {pack(src.raw_text)}']
        else:
            if src.parent and src.parent.is_container:
                nr = src.parent.line_nr + 1
                delta = src.line_nr + 1
                final = nr + delta
                stack += [f'  line {final}: {pack(src.raw_text)}']
            else:
                nr = src.line_nr + 1
                stack += [f'  line {nr}: {pack(src.raw_text)}']
        if src.parent:
            _add_to_stack(stack, src.parent)

    stack: list[str] = ['(most recent first)']
    _add_to_stack(stack, src)
    stack += ['']
    return '\n'.join(stack) + 'Error: '


class DfdException(Exception):
    pass


# Handy type aliases
Snippets = list[Snippet]
SourceLines = list[SourceLine]
Statements = list[Statement]
SnippetByName = dict[str, Snippet]


@dataclass
class Options:
    format: str
    percent_zoom: int
    background_color: str
    no_graph_title: bool
    no_check_dependencies: bool
    debug: bool


@dataclass
class GraphDependency:
    to_graph: str
    to_item: str | None
    to_type: str
    source: SourceLine


GraphDependencies = list[GraphDependency]
