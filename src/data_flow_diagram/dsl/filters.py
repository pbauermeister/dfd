"""Filter engine: only/without, neighbour expansion."""

from .. import exception, model
from ..console import dprint


def _collect_connected_names(
    statements: model.Statements,
    names: set[str],
    find_down: bool,
    nreverse: bool,
) -> set[str]:
    """Find items connected to a set of names in one direction."""
    found_names: set[str] = set()
    for statement in statements:
        match statement:
            case model.Connection() as conn:

                # constraints do not define neighborhood
                if conn.type == model.Keyword.CONSTRAINT:
                    continue

                src, dst = conn.src, conn.dst
                if conn.reversed and not nreverse:
                    src, dst = dst, src

                if conn.type in (model.Keyword.BFLOW, model.Keyword.UFLOW):
                    if dst in names:
                        found_names.add(src)
                    if src in names:
                        found_names.add(dst)
                else:
                    if find_down:
                        if src in names:
                            found_names.add(dst)
                    else:
                        if dst in names:
                            found_names.add(src)
            case _:
                continue
    return found_names


def _resolve_distance(distance: int, max_neighbors: int) -> int:
    """Resolve a neighbor distance, treating negative as unlimited."""
    if distance < 0:
        return max_neighbors
    return distance


def _expand_neighbors_in_dir(
    statements: model.Statements,
    anchor_names: list[str],
    max_neighbors: int,
    fn: model.FilterNeighbors,
    down: bool,
) -> set[str]:
    """Expand neighbours in one direction by successive waves of connections."""
    names = set(anchor_names)
    neighbor_names: set[str] = set()
    for i in range(_resolve_distance(fn.distance, max_neighbors)):
        names = _collect_connected_names(
            statements, names, find_down=down, nreverse=fn.layout_dir
        )
        if not names:
            break
        dprint(f"  - {i} {down} {fn}")
        dprint(f"     :", neighbor_names)
        dprint(f"   + :", names)
        neighbor_names.update(names)
        dprint(f"   = :", neighbor_names)
    return neighbor_names


def find_neighbors(
    filter: model.Filter,
    statements: model.Statements,
    max_neighbors: int,
    debug: bool,
) -> tuple[set[str], set[str]]:
    """Collect neighbour names by following connections outward from filter anchors."""
    return _expand_neighbors_in_dir(
        statements,
        filter.names,
        max_neighbors,
        filter.neighbors_down,
        down=True,
    ), _expand_neighbors_in_dir(
        statements, filter.names, max_neighbors, filter.neighbors_up, down=False
    )


def _check_filter_names(
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


def _collect_frame_skips(
    f: model.Filter,
    names: set[str],
    downs: set[str],
    ups: set[str],
    skip_frames_for_names: set[str],
) -> None:
    """Record names whose frames should be suppressed (neighbor-only mode)."""
    if f.neighbors_up.no_frames:
        skip_frames_for_names.update(ups)
        if not f.neighbors_up.no_anchors:
            skip_frames_for_names.update(names)
    if f.neighbors_down.no_frames:
        skip_frames_for_names.update(downs)
        if not f.neighbors_down.no_anchors:
            skip_frames_for_names.update(names)


def _collect_kept_names(
    statements: model.Statements,
    all_names: set[str],
    debug: bool,
) -> tuple[set[str] | None, set[str], dict[str, str], set[str]]:
    """Process filter statements to determine which names to keep.

    Returns (kept_names, only_names, replacement, skip_frames_for_names).
    """
    kept_names: set[str] | None = None
    only_names: set[str] = set()
    replacement: dict[str, str] = {}
    skip_frames_for_names: set[str] = set()

    for statement in statements:
        if isinstance(statement, model.Filter):
            dprint("*** Filter:", statement)
            dprint("    before:", kept_names)

        match statement:
            case model.Only() as f:
                # Only is additive: first Only starts with an empty kept set
                if kept_names is None:
                    kept_names = set()

                # validate filter names
                names = set(f.names)
                _check_filter_names(
                    names, all_names, all_names, statement.source
                )

                # add anchor names (suppressed by "x" flag: neighbours only)
                if (
                    not f.neighbors_up.no_anchors
                    and not f.neighbors_down.no_anchors
                ):
                    dprint("ONLY: adding nodes:", names)
                    kept_names.update(f.names)
                    only_names.update(f.names)

                # add upstream/downstream neighbour names
                downs, ups = find_neighbors(
                    f, statements, len(all_names), debug
                )
                dprint("ONLY: adding neighbors:", downs, ups)
                kept_names.update(downs)
                kept_names.update(ups)

                _collect_frame_skips(
                    f, names, downs, ups, skip_frames_for_names
                )

            case model.Without() as f:
                # Without is subtractive: first Without starts with all names
                if kept_names is None:
                    kept_names = all_names.copy()

                # validate filter names and register replacements
                names = set(f.names)
                names_to_check = names.copy()
                if f.replaced_by:
                    names_to_check.add(f.replaced_by)
                    for name in names:
                        replacement[name] = f.replaced_by
                _check_filter_names(
                    names_to_check, kept_names, all_names, statement.source
                )

                # remove anchor names (suppressed by "x" flag: neighbours only)
                if (
                    not f.neighbors_up.no_anchors
                    and not f.neighbors_down.no_anchors
                ):
                    dprint("WITHOUT: removing nodes:", names)
                    kept_names.difference_update(names)

                # remove upstream/downstream neighbour names
                downs, ups = find_neighbors(
                    f, statements, len(all_names), debug
                )
                dprint("WITHOUT: removing neighbors:", downs, ups)
                kept_names.difference_update(downs)
                kept_names.difference_update(ups)

                _collect_frame_skips(
                    f, names, downs, ups, skip_frames_for_names
                )

        if isinstance(statement, model.Filter):
            dprint("    after:", kept_names)

    return kept_names, only_names, replacement, skip_frames_for_names


def _mark_non_hidable(
    statements: model.Statements, only_names: set[str]
) -> None:
    """Make items in the only_names set non-hidable so they don't vanish."""
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name in only_names:
                    item.hidable = False


def _apply_filters(
    statements: model.Statements,
    kept_names: set[str],
    replacement: dict[str, str],
    skip_frames_for_names: set[str],
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
                if conn.src in replacement or conn.dst in replacement:
                    # skip if both ends are replaced (would collapse to self-loop)
                    if conn.src in replacement and conn.dst in replacement:
                        continue
                    # rewrite replaced endpoint(s)
                    if conn.src in replacement:
                        conn.src = replacement[conn.src]
                    if conn.dst in replacement:
                        conn.dst = replacement[conn.dst]
                    replaced_connections[conn.signature()] = conn
                else:
                    # skip if either endpoint was filtered out
                    if conn.src not in kept_names or conn.dst not in kept_names:
                        dprint(
                            "=> Skipping connection: some end is not in the kept list"
                        )
                        continue

            case model.Frame() as frame:
                # rewrite replaced names in frame membership
                for name in frame.items:
                    if name in replacement:
                        frame.items.remove(name)
                        frame.items.append(replacement[name])

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
    statements: model.Statements, debug: bool = False
) -> model.Statements:
    """Apply only/without filters to a statement list."""
    all_names = set([s.name for s in statements if isinstance(s, model.Item)])

    # phase 1: collect filtered names
    kept_names, only_names, replacement, skip_frames_for_names = (
        _collect_kept_names(statements, all_names, debug)
    )

    _mark_non_hidable(statements, only_names)

    # default to keeping all names if no filter was encountered
    kept_names = kept_names if kept_names is not None else all_names
    dprint("\nItems to keep", kept_names)

    # phase 2: apply filters to statements
    new_statements, replaced_connections = _apply_filters(
        statements, kept_names, replacement, skip_frames_for_names
    )

    # phase 3: deduplicate connections created by replacements
    return _deduplicate_connections(new_statements, replaced_connections)
