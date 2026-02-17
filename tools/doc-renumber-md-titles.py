#!/usr/bin/env python3
"""This program reads a markdown file and (re)numbers its titles.
---

If there is only one top-level title, it is considered as the document
title, and numbering affects only the titles of lower level.

"""
import argparse
from dataclasses import dataclass
from typing import Generator
import re


RX_TITLE = re.compile(
    '^(?P<hashes>#+) +(?P<number>[0-9]+(?:[.][0-9]+)*[.] +)?(?P<title>.*)'
)


@dataclass
class Line:
    text: str


@dataclass
class Title(Line):
    depth: int


assert __doc__
parts = __doc__.split('---')
parser = argparse.ArgumentParser(description=parts[0], epilog=parts[1])
parser.add_argument(
    'input',
    metavar='INPUT',
    help='input file path; shall be in markdown format',
)
parser.add_argument(
    '-o',
    '--output',
    metavar='OUTPUT',
    help='output file path; if omitted, INPUT file will be '
    'overwritten; use \'-\' for standard output.',
)
args = parser.parse_args()


def walk_file(path: str) -> Generator[Line, None, None]:
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    in_block = False
    for line in lines:
        if line.startswith('```'):
            in_block = not in_block
        if in_block:
            yield Line(text=line)
            continue

        match = RX_TITLE.match(line)
        # print(match if match else line)
        if match:
            yield Title(
                depth=len(match.group('hashes')),
                text=match.group('title'),
            )
        else:
            yield Line(text=line)


def find_out_min_level(path: str) -> int:
    # collect lines
    titles_by_level: dict[int, int] = {}
    for line in walk_file(path):
        match line:
            case Title() as t:
                titles_by_level.setdefault(t.depth, 0)
                titles_by_level[t.depth] += 1

    # determine level from which we emit numbering
    levels = sorted(titles_by_level.keys())
    min_level = 0
    if len(levels) > 0:
        if titles_by_level[levels[0]] == 1:
            # there is only one top-level, so find out next level if any
            min_level = levels[1] if len(levels) > 1 else levels[0] + 1
    return min_level


def compute_numbering(index_by_level: dict[int, int], depth: int) -> str:
    parts = [
        index_by_level[l] for l in sorted(index_by_level.keys()) if l <= depth
    ]
    return '.'.join([str(p) for p in parts]) + '. '


def strip_numbering(text: str) -> str:
    return re.sub(r'^([0-9A-Za-z]+[.])+ ', '', text)


def renumber_title(
    t: Title,
    index_by_level: dict[int, int],
    min_level: int,
    last_depth: int | None,
) -> str:
    hashes = '#' * t.depth
    if t.depth < min_level:
        return f'{hashes} {t.text}'

    # find out index and increment it
    index_by_level.setdefault(t.depth, 0)
    if last_depth is None or t.depth > last_depth:
        index_by_level[t.depth] = 0  # reset index for this level
    index_by_level[t.depth] += 1  # increment index

    numbering = compute_numbering(index_by_level, t.depth)
    text = strip_numbering(t.text)

    return f'{hashes} {numbering}{text}'


def renumber_file(path: str, min_level: int) -> str:
    out: list[str] = []
    index_by_level: dict[int, int] = {}
    last_depth = None
    for line in walk_file(path):
        match line:
            case Title() as t:
                out.append(
                    renumber_title(
                        t,
                        index_by_level=index_by_level,
                        min_level=min_level,
                        last_depth=last_depth,
                    )
                )
                last_depth = t.depth

            case Line() as l:
                ll: Line = l
                out.append(ll.text)
    return '\n'.join(out)


# go for it
path = args.input
min_level = find_out_min_level(path)
text = renumber_file(path, min_level).strip() + '\n'

out_path = args.output or args.input
if out_path == '-':
    print(text)
else:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
