"""Internal data model"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any

def repr(o: Any) -> str:
    name: str = o.__class__.__name__
    val: str = json.dumps(dataclasses.asdict(o), indent='  ')
    return f'{name} {val}'


@dataclass
class Base:
    def __repr__(self) -> str:
        return (self.__class__.__name__ + ' '
                + json.dumps(dataclasses.asdict(self), indent='  '))


@dataclass
class Snippet(Base):
    text: str
    name: str
    output: str
    line_nr: int


@dataclass
class SourceLine(Base):
    text: str  # after pre-processor
    raw_text: str
    parent: SourceLine  # https://stackoverflow.com/a/62521947
    line_nr: int


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
class Style(Statement):
    style: str


STYLE   = 'style'

PROCESS = 'process'
ENTITY  = 'entity'
STORE   = 'store'
CHANNEL = 'channel'
NONE    = 'none'

FLOW    = 'flow'
BFLOW   = 'bflow'
UFLOW   = 'uflow'
SIGNAL  = 'signal'


@dataclass
class GraphOptions():
    is_vertical: bool = False
    is_context: bool = False


def pack(src_line: str) -> str:
    if src_line is None:
        return '<none>'
    return ' '.join(src_line.split())


def mk_err_prefix_from(src: SourceLine) -> str:

    def _add_to_stack(stack: list[str], src: SourceLine) -> None:
        if src.line_nr is None:
            stack += [f'  {pack(src.raw_text)}']
        else:
            stack += [f'  line {src.line_nr+1}: {pack(src.raw_text)}']
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
