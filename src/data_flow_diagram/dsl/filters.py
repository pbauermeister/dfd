"""Filter engine: only/without, neighbour expansion."""

from .. import exception, model
from ..console import dprint


def find_neighbors(
    filter: model.Filter,
    statements: model.Statements,
    max_neighbors: int,
    debug: bool,
) -> tuple[set[str], set[str]]:
    """Collect neighbour names by following connections outward from filter anchors."""

    def _find_neighbors(
        names: set[str], find_down: bool, nreverse: bool
    ) -> set[str]:
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

    def _nb(nb: int) -> int:
        if nb < 0:
            return max_neighbors
        return nb

    # expand neighbours in one direction by successive waves of connections
    def _find_neighbors_in_dir(
        fn: model.FilterNeighbors, down: bool
    ) -> set[str]:
        names = set(filter.names)
        neighbor_names: set[str] = set()
        for i in range(_nb(fn.distance)):
            names = _find_neighbors(
                names, find_down=down, nreverse=fn.layout_dir
            )
            if not names:
                break
            dprint(f"  - {i} {down} {fn}")
            dprint(f"     :", neighbor_names)
            dprint(f"   + :", names)
            neighbor_names.update(names)
            dprint(f"   = :", neighbor_names)
        return neighbor_names

    return _find_neighbors_in_dir(
        filter.neighbors_down, down=True
    ), _find_neighbors_in_dir(filter.neighbors_up, down=False)


def handle_filters(
    statements: model.Statements, debug: bool = False
) -> model.Statements:
    # collect all item names and initialize filter state
    all_names = set([s.name for s in statements if isinstance(s, model.Item)])
    kept_names: set[str] | None = None
    only_names: set[str] = set()

    def _check_names(
        names: set[str], in_names: set[str], source: model.SourceLine
    ) -> None:
        if not names.issubset(all_names):
            diff = ", ".join(names - all_names)
            raise exception.DfdException(
                f' Name(s) unknown: {diff}', source=source
            )

        if not names.issubset(in_names):
            diff = ", ".join(names - in_names)
            raise exception.DfdException(
                f' Name(s) no longer available due to previous filters: {diff}',
                source=source,
            )

    # state for name replacement (Without→replace) and frame suppression
    replacement: dict[str, str] = {}
    skip_frames_for_names: set[str] = (
        set()
    )  # names whose frames should be suppressed (neighbor-only mode)

    # phase 1: collect filtered names
    for statement in statements:
        if isinstance(statement, model.Filter):
            dprint("*** Filter:", statement)
            dprint("    before:", kept_names)

        def _collect_frame_skips(
            f: model.Filter,
            names: set[str],
            downs: set[str],
            ups: set[str],
        ) -> None:
            if f.neighbors_up.no_frames:
                skip_frames_for_names.update(ups)
                if not f.neighbors_up.no_anchors:
                    skip_frames_for_names.update(names)
            if f.neighbors_down.no_frames:
                skip_frames_for_names.update(downs)
                if not f.neighbors_down.no_anchors:
                    skip_frames_for_names.update(names)

        match statement:
            case model.Only() as f:
                # Only is additive: first Only starts with an empty kept set
                if kept_names is None:
                    kept_names = set()

                # validate filter names
                names = set(f.names)
                _check_names(names, all_names, statement.source)

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

                _collect_frame_skips(f, names, downs, ups)

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
                _check_names(names_to_check, kept_names, statement.source)

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

                _collect_frame_skips(f, names, downs, ups)

        if isinstance(statement, model.Filter):
            dprint("    after:", kept_names)

    # An item in the only_names set may lose its connections and, if it is
    # hidable, vanish (or, if in a frame, reappear as a basic item).
    # To keep it, we make it non-hidable.
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name in only_names:
                    item.hidable = False  # make non-hidable

    # default to keeping all names if no filter was encountered
    kept_names = kept_names if kept_names is not None else all_names

    dprint("\nItems to keep", kept_names)

    # phase 2: apply filters to statements
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

    # phase 3: deduplicate connections created by replacements
    kept_new_statements = []
    skipped_statements = set()
    for statement in new_statements:
        match statement:
            case model.Connection() as conn:
                sig = conn.signature()
                if sig in skipped_statements:
                    continue
                if sig in replaced_connections:
                    skipped_statements.add(sig)
        kept_new_statements.append(statement)

    return kept_new_statements
