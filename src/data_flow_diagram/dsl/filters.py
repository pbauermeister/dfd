"""The view stage: the view statements (filters and merges) derive the
view, the diagram drawn, from the declarations.

There is one view, the current one, and the derivation (_Derivation)
folds the statements in source order into it. A declaration (item,
connection, frame) joins the current view. A keep filter ("!", "!!")
walks its neighborhood in the current view and adds what it finds to
a keep list: items, flows per its strictness, frames; adjacent keep
filters share one keep list, a compound. At a statement of another
kind, a "~", a merge or a declaration, the keep list is realized: the
next view is the current one induced on the kept items, then the keep
list is flushed. A "~" derives the next view less its anchors and
their neighbors, walked in the current view; a merge derives it with
the merged items' flows rewired to the replacer, which takes their
place, in their frame too.

Flows at a realization: kept when both ends are kept, unless a strict
keep filter ("!!") vetoes them. A strict filter vetoes every flow
touching an item it selects; a flow shows anyway when it is a path
flow (followed by some strict filter to reach its neighbors) or joins
two items a plain "!" selects together. Flows vetoed and allowed by
none are the stray flows, dropped for good.

A name leaving the view is recorded with its cause (removed, merged
into), for the error a later statement naming it gets; a statement
names items of the current view, or it is an error (#145). The items
declared stay on record for one more purpose: a merge's replacer
declared outside the view rejoins it.
"""

from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field, replace

from .. import exception, model
from ..console import dprint
from ..graph import Element, Graph


def _cause(what: str, source: model.SourceLine) -> str:
    """How a name became unavailable: the statement that did it."""
    text = (source.raw_text or source.text).strip()
    return f"{what} at line {source.line_nr}: {text}"


@dataclass(kw_only=True)
class _KeepList:
    """What a compound of keep filters selects in the current view,
    realized at the next statement of another kind: the names kept,
    the anchors (made non-hidable), the strict filters' gate on the
    flows, the names whose frames the "f" flag suppresses."""

    names: set[str] = field(default_factory=set)
    anchors: set[str] = field(default_factory=set)
    vetoed: set[model.Connection] = field(default_factory=set)
    allowed: set[model.Connection] = field(default_factory=set)
    skip_frames: set[str] = field(default_factory=set)

    @property
    def hidden(self) -> set[model.Connection]:
        """The stray flows: vetoed, allowed by none."""
        return self.vetoed - self.allowed


# a connection as compared after a merge: every field but its source
_FlowKey = tuple[model.Keyword, str, str, str, str, bool, bool]


def _flow_key(conn: model.Connection) -> _FlowKey:
    return (
        conn.type,
        conn.text,
        conn.attrs,
        conn.src,
        conn.dst,
        conn.reversed,
        conn.relaxed,
    )


# the view's elements by the declaration each derives from
_View = dict[Element, Element]


class _Derivation:
    """The statements folded in source order into the current view (see
    the module docstring)."""

    def __init__(self) -> None:
        self.declared: dict[str, model.Item] = {}  # every item, by name
        self.unavailable: dict[str, str] = {}  # removed or merged -> cause
        self.view: _View = {}
        self.current = Graph.empty()
        self.keep: _KeepList | None = None

    # the fold

    def run(self, statements: model.Statements) -> _View:
        """Read the statements; return the view's elements by origin."""
        for statement in statements:
            match statement:
                case model.Item() | model.Connection() | model.Frame():
                    self._declare(statement)
                case model.Only() as f:
                    self._keep(f)
                case model.Merge() as m:
                    self._merge(m)
                case model.Without() as f:
                    self._remove(f)
                case _:
                    pass  # a style, an attrib: not a view matter
        self._realize()
        return self.view

    def _declare(self, element: Element) -> None:
        """A declaration joins the current view, naming items of it."""
        self._realize()
        match element:
            case model.Item() as item:
                self.declared[item.name] = item
            case model.Connection() as conn:
                self._check_in_view({conn.src, conn.dst}, conn.source)
            case model.Frame() as frame:
                self._check_in_view(set(frame.items), frame.source)
        self.view[element] = element
        self.current = self.current.with_element(element)

    def _keep(self, f: model.Only) -> None:
        """A keep filter: its selection joins the keep list."""
        dprint("*** Filter:", f)
        names = set(f.names)
        self._check_known(names, f.source)
        self._check_available(names, f.source)
        self._check_kept(names, f.source)
        if self.keep is None:
            self.keep = _KeepList()
        keep = self.keep

        # add anchor names (suppressed by "x" flag: neighbors only)
        anchors_kept = not (
            f.neighbors_up.suppress_anchors or f.neighbors_down.suppress_anchors
        )
        if anchors_kept:
            dprint("ONLY: adding items:", names)
            keep.names |= names
            keep.anchors |= names

        # add upstream/downstream neighbor names
        downs, ups, path_flows = self._neighbors(f)
        dprint("ONLY: adding neighbors:", downs, ups)
        keep.names |= downs | ups

        # flows: a strict filter vetoes the flows touching its selection
        # and allows its path flows; a plain filter allows the flows
        # joining its selection
        selected = downs | ups
        if anchors_kept:
            selected |= names
        if f.strict:
            keep.vetoed |= self.current.flows_touching(
                selected, both_ends=False
            )
            keep.allowed |= path_flows
        else:
            keep.allowed |= self.current.flows_touching(
                selected, both_ends=True
            )

        # the "f" flag: the frames of the selected items are suppressed
        if f.neighbors_up.suppress_frames:
            keep.skip_frames |= ups
            if not f.neighbors_up.suppress_anchors:
                keep.skip_frames |= names
        if f.neighbors_down.suppress_frames:
            keep.skip_frames |= downs
            if not f.neighbors_down.suppress_anchors:
                keep.skip_frames |= names

    def _remove(self, f: model.Without) -> None:
        """A without filter: the next view is the current one less the
        anchors and their neighbors."""
        self._realize()
        dprint("*** Filter:", f)
        names = set(f.names)
        self._check_known(names, f.source)
        self._check_available(names, f.source)
        self._check_kept(names, f.source)
        cause = _cause("removed", f.source)

        # remove anchor names (suppressed by "x" flag: neighbors only)
        removed: set[str] = set()
        if not (
            f.neighbors_up.suppress_anchors or f.neighbors_down.suppress_anchors
        ):
            dprint("WITHOUT: removing items:", names)
            removed |= names

        # remove upstream/downstream neighbor names
        downs, ups, _ = self._neighbors(f)
        dprint("WITHOUT: removing neighbors:", downs, ups)
        removed |= downs | ups
        self.unavailable.update({name: cause for name in removed})
        self._induce(self.current.names - removed)

    def _merge(self, m: model.Merge) -> None:
        """A merge: the next view has the merged items' flows rewired to
        the replacer, which takes their place, in their frame too."""
        self._realize()
        names = set(m.names)
        self._check_known(names | {m.replacer}, m.source)
        self._check_available(names | {m.replacer}, m.source)
        missing = sorted(names - self.current.names)
        if missing:
            raise exception.DfdException(
                f" Name(s) not kept, cannot be merged: {', '.join(missing)}",
                source=m.source,
            )
        frame = self._check_one_frame(names, m.source)
        dprint("MERGE:", names, "->", m.replacer)
        cause = _cause(f"merged into {m.replacer}", m.source)
        self.unavailable.update({name: cause for name in names})

        view: _View = {}
        rewired: set[_FlowKey] = set()  # keys of the flows rewired
        for origin, element in self.view.items():
            dprint(f"\nHandling statement: {element}")
            match element:
                case model.Item() as item:
                    if item.name in names:
                        dprint("=> Skipping item: merged away")
                        continue

                case model.Connection() as conn:
                    if conn.src in names or conn.dst in names:
                        src = m.replacer if conn.src in names else conn.src
                        dst = m.replacer if conn.dst in names else conn.dst
                        if src == dst:
                            dprint(
                                "=> Skipping connection: collapsed by the merge"
                            )
                            continue
                        element = replace(conn, src=src, dst=dst)
                        rewired.add(_flow_key(element))

                case model.Frame() as fr:
                    # merged names leave the frame; the replacer takes
                    # their place in the frame holding them all
                    items: list[str] = []
                    for name in fr.items:
                        if name not in names:
                            if name not in items:
                                items.append(name)
                        elif fr is frame and m.replacer not in items:
                            items.append(m.replacer)
                    if not items:
                        dprint("=> Skipping frame: no item left")
                        continue
                    dprint(f"=> Adjusting frame items: {fr.items} -> {items}")
                    element = replace(fr, items=items)

            dprint("=> Keeping statement")
            view[origin] = element

        if m.replacer not in self.current.names:
            # declared outside the view: rejoins it
            replacer = self.declared[m.replacer]
            view[replacer] = replacer
        self._set_view(_deduplicate_flows(view, rewired))

    # the realization

    def _realize(self) -> None:
        """Derive the next view from the keep list, if any."""
        if self.keep is None:
            return
        keep, self.keep = self.keep, None
        self._induce(
            keep.names,
            anchors=keep.anchors,
            hidden=keep.hidden,
            skip_frames=keep.skip_frames,
        )

    def _induce(
        self,
        names: set[str],
        *,
        anchors: AbstractSet[str] = frozenset(),
        hidden: AbstractSet[model.Connection] = frozenset(),
        skip_frames: AbstractSet[str] = frozenset(),
    ) -> None:
        """The current view induced on a set of names: the items (an
        anchor made non-hidable), the flows joining them (the hidden
        ones out), the frames trimmed to them (a suppressed one out)."""
        dprint("\nItems to keep", names)
        view: _View = {}
        for origin, element in self.view.items():
            dprint(f"\nHandling statement: {element}")
            match element:
                case model.Item() as item:
                    if item.name not in names:
                        dprint("=> Skipping item: not kept")
                        continue
                    # An anchor may lose its connections and, if it is
                    # hidable, vanish: made non-hidable to keep it.
                    if item.name in anchors and item.hidable:
                        element = replace(item, hidable=False)

                case model.Connection() as conn:
                    if conn.src not in names or conn.dst not in names:
                        dprint("=> Skipping connection: an end is not kept")
                        continue
                    if conn in hidden:
                        dprint("=> Skipping connection: stray flow")
                        continue

                case model.Frame() as frame:
                    items = [n for n in frame.items if n in names]
                    if not items:
                        dprint("=> Skipping frame: no kept item")
                        continue
                    dprint(
                        f"=> Adjusting frame items: {frame.items} -> {items}"
                    )
                    if set(items) & skip_frames:
                        dprint(
                            "=> Skipping frame: an item's frame is suppressed"
                        )
                        continue
                    element = replace(frame, items=items)

            dprint("=> Keeping statement")
            view[origin] = element
        self._set_view(view)

    def _set_view(self, view: _View) -> None:
        self.view = view
        self.current = Graph.build(view.values())

    # the checks a statement's names go through

    def _check_known(self, names: set[str], source: model.SourceLine) -> None:
        """Every name is an item declared so far."""
        unknown = names - self.declared.keys()
        if unknown:
            raise exception.DfdException(
                f' Name(s) unknown: {", ".join(unknown)}', source=source
            )

    def _check_available(
        self, names: set[str], source: model.SourceLine
    ) -> None:
        """Refuse a name that a previous statement removed or merged away."""
        gone = sorted(names & self.unavailable.keys())
        if gone:
            diff = "; ".join(
                f"{name} ({self.unavailable[name]})" for name in gone
            )
            raise exception.DfdException(
                f" Name(s) no longer available: {diff}", source=source
            )

    def _check_kept(self, names: set[str], source: model.SourceLine) -> None:
        """Every name is an item of the current view."""
        unkept = names - self.current.names
        if unkept:
            raise exception.DfdException(
                " Name(s) no longer available due to previous filters:"
                f' {", ".join(unkept)}',
                source=source,
            )

    def _check_in_view(self, names: set[str], source: model.SourceLine) -> None:
        """A connection or a frame names items of the current view: of
        its names declared so far, none removed or merged away, all kept
        (a name declared below joins the view at its declaration)."""
        names = names & self.declared.keys()
        self._check_available(names, source)
        self._check_kept(names, source)

    def _check_one_frame(
        self, names: set[str], source: model.SourceLine
    ) -> model.Frame | None:
        """Items merged together are in one frame, or all unframed.

        Returns the frame the replacer takes their place in, if any.
        """
        frame_of = {name: self.current.frame_of(name) for name in names}
        frames = set(frame_of.values())
        if len(frames) > 1:
            diff = ", ".join(
                f"{name} ({frame_of[name].text if frame_of[name] else 'no frame'})"
                for name in sorted(names)
            )
            raise exception.DfdException(
                f" Cannot merge items from different frames: {diff}",
                source=source,
            )
        (frame,) = frames
        return frame

    # the walk

    def _neighbors(
        self, f: model.Filter
    ) -> tuple[set[str], set[str], set[model.Connection]]:
        """The neighbors of the filter's anchors in the current view.
        Returns (downstream, upstream, the path flows)."""
        downs, down_flows = self._expand(f, f.neighbors_down, down=True)
        ups, up_flows = self._expand(f, f.neighbors_up, down=False)
        return downs, ups, down_flows | up_flows

    def _expand(
        self, f: model.Filter, fn: model.FilterNeighbors, *, down: bool
    ) -> tuple[set[str], set[model.Connection]]:
        """Expand neighbors in one direction by successive waves of
        connections. Returns (neighbor names, the flows followed)."""
        # a negative distance is the unlimited span: every item at most
        span = len(self.current.items) if fn.distance < 0 else fn.distance
        names = set(f.names)
        neighbor_names: set[str] = set()
        path_flows: set[model.Connection] = set()
        for i in range(span):
            names, followed = self.current.adjacent(
                names, downstream=down, layout=fn.layout_direction
            )
            if not names:
                break
            dprint(f"  - {i} {down} {fn}")
            dprint("   + :", names)
            neighbor_names |= names
            path_flows |= followed
        return neighbor_names, path_flows


def _deduplicate_flows(view: _View, rewired: set[_FlowKey]) -> _View:
    """Remove the duplicates a merge created: of the flows equal to a
    rewired one, the first stays."""
    kept: _View = {}
    seen: set[_FlowKey] = set()
    for origin, element in view.items():
        match element:
            case model.Connection() as conn:
                key = _flow_key(conn)
                if key in seen:
                    continue
                if key in rewired:
                    seen.add(key)
        kept[origin] = element
    return kept


def handle_filters(
    statements: model.Statements, *, debug: bool = False
) -> model.Statements:
    """Derive the view the view statements describe: its elements in
    the source order, the other statements (styles, attribs, the view
    statements themselves) passed through in their place."""
    view = _Derivation().run(statements)
    result: model.Statements = []
    for statement in statements:
        match statement:
            case model.Item() | model.Connection() | model.Frame():
                if statement in view:
                    result.append(view[statement])
            case _:
                result.append(statement)
    return result
