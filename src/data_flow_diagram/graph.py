"""The graph: the items, connections and frames of a diagram, indexed by
item name, with the questions the view stage asks it: the names it
holds, the frame of an item, the names adjacent to a set of names in
one direction, the flows touching a set of names.

A graph is immutable. `with_element` returns the graph grown by one
declaration. The view stage holds the current view as a graph and
derives the next one from it (see `dsl/filters.py`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import assert_never

from . import model

# the declarations a graph is made of
Element = model.Item | model.Connection | model.Frame


@dataclass(frozen=True, kw_only=True)
class Graph:
    """A diagram's elements, the items indexed by name."""

    items: dict[str, model.Item]  # name -> item, in declaration order
    connections: tuple[model.Connection, ...]
    frames: tuple[model.Frame, ...]

    @classmethod
    def empty(cls) -> Graph:
        return cls(items={}, connections=(), frames=())

    @classmethod
    def build(cls, elements: Iterable[Element]) -> Graph:
        """The graph of some elements, in their order."""
        graph = cls.empty()
        for element in elements:
            graph = graph.with_element(element)
        return graph

    def with_element(self, element: Element) -> Graph:
        """The graph grown by one declaration."""
        match element:
            case model.Item() as item:
                return replace(self, items={**self.items, item.name: item})
            case model.Connection() as conn:
                return replace(self, connections=(*self.connections, conn))
            case model.Frame() as frame:
                return replace(self, frames=(*self.frames, frame))
            case _:
                assert_never(element)

    @property
    def names(self) -> set[str]:
        """The names of the items."""
        return set(self.items)

    def frame_of(self, name: str) -> model.Frame | None:
        """The frame holding an item, if any (the last one wins, as the
        checker admits one frame per item)."""
        found: model.Frame | None = None
        for frame in self.frames:
            if name in frame.items:
                found = frame
        return found

    def adjacent(
        self, names: set[str], *, downstream: bool, layout: bool
    ) -> tuple[set[str], set[model.Connection]]:
        """The names one connection away from a set of names, in one
        direction: the stream direction, or the layout direction (a flow
        drawn reversed counts against the stream, with the layout).
        Bidirectional and undirected flows go both ways; constraints
        define no neighborhood. Returns (names found, flows followed)."""
        found: set[str] = set()
        followed: set[model.Connection] = set()
        for conn in self.connections:
            if conn.type == model.Keyword.CONSTRAINT:
                continue
            src, dst = conn.src, conn.dst
            if conn.reversed and not layout:
                src, dst = dst, src
            if conn.type in (model.Keyword.BFLOW, model.Keyword.UFLOW):
                if dst in names:
                    found.add(src)
                    followed.add(conn)
                if src in names:
                    found.add(dst)
                    followed.add(conn)
            elif downstream:
                if src in names:
                    found.add(dst)
                    followed.add(conn)
            elif dst in names:
                found.add(src)
                followed.add(conn)
        return found, followed

    def flows_touching(
        self, names: set[str], *, both_ends: bool
    ) -> set[model.Connection]:
        """The flows joining (both ends) or touching (one end at least)
        a set of names."""
        flows: set[model.Connection] = set()
        for conn in self.connections:
            ends_in = (conn.src in names) + (conn.dst in names)
            if ends_in == 2 or (not both_ends and ends_in == 1):
                flows.add(conn)
        return flows
