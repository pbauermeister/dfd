"""Internal data model"""

from dataclasses import dataclass

@dataclass
class Statement:
    line_nr: int
    line: str


@dataclass
class Item(Statement):
    type: str
    name: str
    text: str


@dataclass
class Connection(Statement):
    type: str
    src: str
    dst: str
    text: str


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
SIGNAL  = 'signal'


def pack(src_line: str) -> str:
    return ' '.join(src_line.split())


def mk_err_prefix(n: int, src_line: str) -> str:
    return f'line {n+1}: {pack(src_line)}\n'


def mk_err_prefix_from(statement: Statement) -> str:
    n, src_line = statement.line_nr, statement.line
    return mk_err_prefix(n, src_line)
