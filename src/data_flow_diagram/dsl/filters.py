"""Filter engine: only/without, neighbor expansion, strict flows.

Items: a kept set built statement by statement ("!" adds, "~" removes).
Flows: kept when both ends are kept, unless a strict only filter ("!!")
vetoes them. A strict filter vetoes every flow touching an item it
selects; a flow shows anyway when it is a path flow (followed by some
strict filter to reach its neighbors) or joins two items a plain "!"
selects together. Flows vetoed and allowed by none are the stray flows.
"""

from dataclasses import dataclass

from .. import exception, model
from ..console import dprint


def _ends(conn: model.Connection, merged: dict[str, str]) -> tuple[str, str]:
    """A flow's ends as merged so far: what a rewrite would have written.

    The map is flat (see _register_merge), so one lookup per end.
    """
    return merged.get(conn.src, conn.src), merged.get(conn.dst, conn.dst)


def _register_merge(
    merged: dict[str, str], *, names: set[str], replacer: str
) -> None:
    """Add a merge to the map and keep it flat: a chain resolves in one hop."""
    target = merged.get(replacer, replacer)
    for name in names:
        merged[name] = target
    for name, value in merged.items():
        if value in names:
            merged[name] = target


def _collect_connected_names(
    *,
    statements: model.Statements,
    names: set[str],
    search_downstream: bool,
    use_layout_direction: bool,
    merged: dict[str, str],
) -> tuple[set[str], list[model.Connection]]:
    """Find items connected to a set of names in one direction.

    Returns (found_names, connections followed).
    """
    found_names: set[str] = set()
    followed: list[model.Connection] = []
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                # constraints do not define neighborhood
                if conn.type == model.Keyword.CONSTRAINT:
                    continue

                src, dst = _ends(conn, merged)
                if src == dst:
                    continue  # collapsed by a merge
                if conn.reversed and not use_layout_direction:
                    src, dst = dst, src

                if conn.type in (model.Keyword.BFLOW, model.Keyword.UFLOW):
                    if dst in names:
                        found_names.add(src)
                        followed.append(conn)
                    if src in names:
                        found_names.add(dst)
                        followed.append(conn)
                else:
                    if search_downstream:
                        if src in names:
                            found_names.add(dst)
                            followed.append(conn)
                    else:
                        if dst in names:
                            found_names.add(src)
                            followed.append(conn)
            case _:
                continue
    return found_names, followed


def _resolve_distance(distance: int, max_neighbors: int) -> int:
    """Resolve a neighbor distance, treating negative as unlimited."""
    if distance < 0:
        return max_neighbors
    return distance


def _expand_neighbors_in_dir(
    *,
    statements: model.Statements,
    anchor_names: list[str],
    max_neighbors: int,
    fn: model.FilterNeighbors,
    down: bool,
    merged: dict[str, str],
) -> tuple[set[str], set[int]]:
    """Expand neighbors in one direction by successive waves of connections.

    Returns (neighbor_names, ids of the connections followed: the path flows).
    """
    names = set(anchor_names)
    neighbor_names: set[str] = set()
    path_ids: set[int] = set()
    for i in range(_resolve_distance(fn.distance, max_neighbors)):
        names, followed = _collect_connected_names(
            statements=statements,
            names=names,
            search_downstream=down,
            use_layout_direction=fn.layout_direction,
            merged=merged,
        )
        if not names:
            break
        dprint(f"  - {i} {down} {fn}")
        dprint("     :", neighbor_names)
        dprint("   + :", names)
        neighbor_names.update(names)
        path_ids.update(id(c) for c in followed)
        dprint("   = :", neighbor_names)
    return neighbor_names, path_ids


def find_neighbors(
    *,
    filter: model.Filter,
    statements: model.Statements,
    max_neighbors: int,
    merged: dict[str, str],
    debug: bool,
) -> tuple[set[str], set[str], set[int]]:
    """Collect neighbor names by following connections outward from filter anchors.

    Returns (downstream names, upstream names, ids of the path flows).
    """
    downs, down_ids = _expand_neighbors_in_dir(
        statements=statements,
        anchor_names=filter.names,
        max_neighbors=max_neighbors,
        fn=filter.neighbors_down,
        down=True,
        merged=merged,
    )
    ups, up_ids = _expand_neighbors_in_dir(
        statements=statements,
        anchor_names=filter.names,
        max_neighbors=max_neighbors,
        fn=filter.neighbors_up,
        down=False,
        merged=merged,
    )
    return downs, ups, down_ids | up_ids


def _collect_flow_ids(
    statements: model.Statements,
    names: set[str],
    *,
    touching: bool,
    merged: dict[str, str],
) -> set[int]:
    """Ids of the flows joining (or touching) a set of names, ends read
    through the merges."""
    ids: set[int] = set()
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                src, dst = _ends(conn, merged)
                if src == dst:
                    continue
                ends_in = (src in names) + (dst in names)
                if ends_in == 2 or (touching and ends_in == 1):
                    ids.add(id(conn))
            case _:
                continue
    return ids


def _check_filter_names(
    *,
    names: set[str],
    in_names: set[str],
    all_names: set[str],
    source: model.SourceLine,
) -> None:
    """Validate that filter names exist and are still available."""
    if not names.issubset(all_names):
        diff = ", ".join(names - all_names)
        raise exception.DfdException(f' Name(s) unknown: {diff}', source=source)

    if not names.issubset(in_names):
        diff = ", ".join(names - in_names)
        raise exception.DfdException(
            f' Name(s) no longer available due to previous filters: {diff}',
            source=source,
        )


def _cause(what: str, source: model.SourceLine) -> str:
    """How a name became unavailable: the statement that did it."""
    text = (source.raw_text or source.text).strip()
    return f"{what} at line {source.line_nr}: {text}"


def _check_available(
    *, names: set[str], unavailable: dict[str, str], source: model.SourceLine
) -> None:
    """Refuse a name that a previous statement removed or merged away."""
    gone = sorted(names & unavailable.keys())
    if gone:
        diff = "; ".join(f"{name} ({unavailable[name]})" for name in gone)
        raise exception.DfdException(
            f" Name(s) no longer available: {diff}", source=source
        )


def _check_kept(
    *, names: set[str], kept_names: set[str], source: model.SourceLine
) -> None:
    """A merge names kept items only, once a kept set exists."""
    missing = sorted(names - kept_names)
    if missing:
        raise exception.DfdException(
            f" Name(s) not kept, cannot be merged: {', '.join(missing)}",
            source=source,
        )


def _frame_of_items(statements: model.Statements) -> dict[str, model.Frame]:
    """Item name -> the frame declaring it."""
    frame_of: dict[str, model.Frame] = {}
    for statement in statements:
        if isinstance(statement, model.Frame):
            for name in statement.items:
                frame_of[name] = statement
    return frame_of


def _check_one_frame(
    *,
    names: set[str],
    frame_of: dict[str, model.Frame],
    source: model.SourceLine,
) -> model.Frame | None:
    """Items merged together are in one frame, or all unframed.

    Returns the frame the replacer inherits, if any.
    """
    frames = {
        id(frame_of[name]) if name in frame_of else None for name in names
    }
    if len(frames) > 1:
        diff = ", ".join(
            f"{name} ({frame_of[name].text if name in frame_of else 'no frame'})"
            for name in sorted(names)
        )
        raise exception.DfdException(
            f" Cannot merge items from different frames: {diff}",
            source=source,
        )
    (frame_id,) = frames
    if frame_id is None:
        return None
    return frame_of[next(iter(names & frame_of.keys()))]


def _collect_frame_skips(
    *,
    f: model.Filter,
    names: set[str],
    downs: set[str],
    ups: set[str],
    skip_frames_for_names: set[str],
) -> None:
    """Record names whose frames should be suppressed (neighbors-only mode)."""
    if f.neighbors_up.suppress_frames:
        skip_frames_for_names.update(ups)
        if not f.neighbors_up.suppress_anchors:
            skip_frames_for_names.update(names)
    if f.neighbors_down.suppress_frames:
        skip_frames_for_names.update(downs)
        if not f.neighbors_down.suppress_anchors:
            skip_frames_for_names.update(names)


@dataclass(frozen=True, kw_only=True)
class _FilterDecisions:
    """Outcome of the filter statements, consumed by _apply_filters()."""

    kept_names: set[str] | None  # None: no filter statement encountered
    only_names: set[str]  # anchors of "only" filters, made non-hidable
    replacement: dict[str, str]  # merged name -> replacer (flat)
    merged_names: set[str]  # names merged away: never kept
    inherited_frames: dict[str, int]  # replacer -> id of the frame it joins
    skip_frames_for_names: set[str]
    vetoed_ids: set[int]  # flows touching a strict selection
    allowed_ids: set[int]  # path flows, and flows joining a plain selection


def _collect_kept_names(
    statements: model.Statements,
    all_names: set[str],
    *,
    debug: bool,
) -> _FilterDecisions:
    """Process filter statements to determine which names to keep."""
    kept_names: set[str] | None = None
    only_names: set[str] = set()
    replacement: dict[str, str] = {}
    unavailable: dict[str, str] = {}  # removed or merged away -> cause
    frame_of = _frame_of_items(statements)
    inherited_frames: dict[str, int] = {}
    skip_frames_for_names: set[str] = set()
    vetoed_ids: set[int] = set()
    allowed_ids: set[int] = set()

    for statement in statements:
        if isinstance(statement, model.Filter):
            dprint("*** Filter:", statement)
            dprint("    before:", kept_names)

        match statement:
            case model.Only() as f:
                # Only is additive: first Only starts with an empty kept set
                if kept_names is None:
                    kept_names = set()

                # validate filter names: known, and not removed or merged
                names = set(f.names)
                _check_filter_names(
                    names=names,
                    in_names=all_names,
                    all_names=all_names,
                    source=statement.source,
                )
                _check_available(
                    names=names,
                    unavailable=unavailable,
                    source=statement.source,
                )

                # add anchor names (suppressed by "x" flag: neighbors only)
                if (
                    not f.neighbors_up.suppress_anchors
                    and not f.neighbors_down.suppress_anchors
                ):
                    dprint("ONLY: adding items:", names)
                    kept_names.update(f.names)
                    only_names.update(f.names)

                # add upstream/downstream neighbor names
                downs, ups, path_ids = find_neighbors(
                    filter=f,
                    statements=statements,
                    max_neighbors=len(all_names),
                    merged=replacement,
                    debug=debug,
                )
                dprint("ONLY: adding neighbors:", downs, ups)
                kept_names.update(downs)
                kept_names.update(ups)

                # flows: a strict filter vetoes the flows touching its
                # selection and allows its path flows; a plain filter
                # allows the flows joining its selection
                selection = downs | ups
                if not (
                    f.neighbors_up.suppress_anchors
                    or f.neighbors_down.suppress_anchors
                ):
                    selection |= names
                if f.strict:
                    vetoed_ids |= _collect_flow_ids(
                        statements, selection, touching=True, merged=replacement
                    )
                    allowed_ids |= path_ids
                else:
                    allowed_ids |= _collect_flow_ids(
                        statements,
                        selection,
                        touching=False,
                        merged=replacement,
                    )

                _collect_frame_skips(
                    f=f,
                    names=names,
                    downs=downs,
                    ups=ups,
                    skip_frames_for_names=skip_frames_for_names,
                )

            case model.Merge() as m:
                # a substitution: the items merged away into the replacer
                names = set(m.names)
                _check_filter_names(
                    names=names | {m.replacer},
                    in_names=all_names,
                    all_names=all_names,
                    source=statement.source,
                )
                _check_available(
                    names=names | {m.replacer},
                    unavailable=unavailable,
                    source=statement.source,
                )
                if kept_names is not None:
                    _check_kept(
                        names=names,
                        kept_names=kept_names,
                        source=statement.source,
                    )
                frame = _check_one_frame(
                    names=names, frame_of=frame_of, source=statement.source
                )
                dprint("MERGE:", names, "->", m.replacer)
                _register_merge(replacement, names=names, replacer=m.replacer)
                cause = _cause(f"merged into {m.replacer}", statement.source)
                unavailable.update({name: cause for name in names})
                # the replacer takes the merged items' place: in the kept set
                # and in their frame (when it is declared in none)
                if kept_names is not None:
                    kept_names -= names
                    kept_names.add(m.replacer)
                if frame is not None:
                    # a replacer declared in another frame is then in two:
                    # the frame check re-run after the filters reports it
                    inherited_frames[m.replacer] = id(frame)
                    frame_of.setdefault(m.replacer, frame)

            case model.Without() as f:
                # Without is subtractive: first Without starts with all names
                if kept_names is None:
                    kept_names = all_names - unavailable.keys()

                # validate filter names: known, not removed or merged, kept
                names = set(f.names)
                _check_filter_names(
                    names=names,
                    in_names=all_names,
                    all_names=all_names,
                    source=statement.source,
                )
                _check_available(
                    names=names,
                    unavailable=unavailable,
                    source=statement.source,
                )
                _check_filter_names(
                    names=names,
                    in_names=kept_names,
                    all_names=all_names,
                    source=statement.source,
                )
                cause = _cause("removed", statement.source)

                # remove anchor names (suppressed by "x" flag: neighbors only)
                if (
                    not f.neighbors_up.suppress_anchors
                    and not f.neighbors_down.suppress_anchors
                ):
                    dprint("WITHOUT: removing items:", names)
                    kept_names.difference_update(names)
                    unavailable.update({name: cause for name in names})

                # remove upstream/downstream neighbor names
                downs, ups, _ = find_neighbors(
                    filter=f,
                    statements=statements,
                    max_neighbors=len(all_names),
                    merged=replacement,
                    debug=debug,
                )
                dprint("WITHOUT: removing neighbors:", downs, ups)
                kept_names.difference_update(downs)
                kept_names.difference_update(ups)
                unavailable.update({name: cause for name in downs | ups})

                _collect_frame_skips(
                    f=f,
                    names=names,
                    downs=downs,
                    ups=ups,
                    skip_frames_for_names=skip_frames_for_names,
                )

        if isinstance(statement, model.Filter):
            dprint("    after:", kept_names)

    return _FilterDecisions(
        kept_names=kept_names,
        only_names=only_names,
        replacement=replacement,
        merged_names=set(replacement),
        inherited_frames=inherited_frames,
        skip_frames_for_names=skip_frames_for_names,
        vetoed_ids=vetoed_ids,
        allowed_ids=allowed_ids,
    )


def _mark_non_hidable(
    statements: model.Statements, only_names: set[str]
) -> None:
    """Make items in the only_names set non-hidable so they don't vanish."""
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name in only_names:
                    item.hidable = False


def _merge_frame_items(
    frame: model.Frame,
    *,
    replacement: dict[str, str],
    inherited: dict[str, int],
) -> list[str]:
    """A frame's items once merged: merged names out, an inheriting
    replacer in, at the place of its first merged item."""
    items: list[str] = []
    for name in frame.items:
        replacer = replacement.get(name)
        if replacer is None:
            if name not in items:
                items.append(name)
        elif inherited.get(replacer) == id(frame) and replacer not in items:
            items.append(replacer)
    return items


def _apply_filters(
    *,
    statements: model.Statements,
    kept_names: set[str],
    replacement: dict[str, str],
    inherited_frames: dict[str, int],
    skip_frames_for_names: set[str],
    hidden_ids: set[int],
) -> tuple[list[model.Statement], dict[str, model.Connection]]:
    """Apply kept/replacement/skip decisions to produce filtered statements.

    Returns (new_statements, replaced_connections).
    """
    new_statements: list[model.Statement] = []
    replaced_connections: dict[str, model.Connection] = {}
    for statement in statements:
        dprint(f"\nHandling statement: {statement}")
        match statement:
            case model.Item() as item:
                # skip items not in the kept set
                if item.name not in kept_names:
                    dprint("=> Skipping item: its name is not in the kept list")
                    continue

            case model.Connection() as conn:
                replaced = conn.src in replacement or conn.dst in replacement
                if replaced:
                    # rewrite replaced endpoint(s)
                    conn.src = replacement.get(conn.src, conn.src)
                    conn.dst = replacement.get(conn.dst, conn.dst)
                    # skip if both ends collapsed to one item (self-loop):
                    # both in one group, or one end being the replacer
                    if conn.src == conn.dst:
                        dprint(
                            "=> Skipping connection: collapsed by replacement"
                        )
                        continue

                # skip if either endpoint was filtered out, replaced or not
                if conn.src not in kept_names or conn.dst not in kept_names:
                    dprint(
                        "=> Skipping connection: some end is not in the kept list"
                    )
                    continue

                # skip stray flows: vetoed by a strict filter, allowed by none
                if id(conn) in hidden_ids:
                    dprint("=> Skipping connection: stray flow")
                    continue

                if replaced:
                    replaced_connections[conn.signature()] = conn

            case model.Frame() as frame:
                # merged names leave the frame; a replacer takes their place
                # only in the one frame holding all the items merged into it
                frame.items = _merge_frame_items(
                    frame, replacement=replacement, inherited=inherited_frames
                )

                # skip frames with no remaining kept items
                names = set(frame.items)
                if not names.intersection(kept_names):
                    dprint("=> Skipping frame: no items are in the kept list")
                    continue
                else:
                    # trim frame to kept items only
                    new_items = [n for n in frame.items if n in kept_names]
                    dprint(
                        f"=> Adjusting frame items: {frame.items} -> {new_items}"
                    )
                    frame.items = new_items

                    # skip frames containing items selected via "f" flag
                    if set(new_items).intersection(skip_frames_for_names):
                        dprint(
                            "=> Skipping frame: some items are in the skip-frames list"
                        )
                        continue

        # keep statement
        dprint("=> Keeping statement")
        new_statements.append(statement)

    return new_statements, replaced_connections


def _deduplicate_connections(
    statements: list[model.Statement],
    replaced_connections: dict[str, model.Connection],
) -> list[model.Statement]:
    """Remove duplicate connections created by replacements."""
    kept_statements: list[model.Statement] = []
    skipped_signatures: set[str] = set()
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                sig = conn.signature()
                if sig in skipped_signatures:
                    continue
                if sig in replaced_connections:
                    skipped_signatures.add(sig)
        kept_statements.append(statement)
    return kept_statements


def handle_filters(
    statements: model.Statements, *, debug: bool = False
) -> model.Statements:
    """Apply only/without filters to a statement list."""
    all_names = {s.name for s in statements if isinstance(s, model.Item)}

    # phase 1: collect filtered names
    decisions = _collect_kept_names(statements, all_names, debug=debug)

    _mark_non_hidable(statements, decisions.only_names)

    # default to keeping all names if no filter was encountered; a merged
    # name is never kept, whichever filter initialised the set
    kept_names = (
        decisions.kept_names if decisions.kept_names is not None else all_names
    ) - decisions.merged_names
    dprint("\nItems to keep", kept_names)

    # phase 2: apply filters to statements
    new_statements, replaced_connections = _apply_filters(
        statements=statements,
        kept_names=kept_names,
        replacement=decisions.replacement,
        inherited_frames=decisions.inherited_frames,
        skip_frames_for_names=decisions.skip_frames_for_names,
        hidden_ids=decisions.vetoed_ids - decisions.allowed_ids,
    )

    # phase 3: deduplicate connections created by replacements
    return _deduplicate_connections(new_statements, replaced_connections)
