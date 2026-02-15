"""Run the generation process"""

import os.path
import pprint
import re
import textwrap
from typing import Any

from . import dependency_checker
from . import dfd_dot_templates as TMPL
from . import dot, model, parser, scanner
from .console import dprint


def build(
    provenance: model.SourceLine,
    dfd_src: str,
    output_path: str,
    options: model.Options,
    snippet_by_name: model.SnippetByName | None = None,
) -> None:
    """Take a DFD source and build the final image or document"""
    lines = scanner.scan(provenance, dfd_src, snippet_by_name, options.debug)
    statements, dependencies, attribs = parser.parse(lines, options)
    if dependencies and not options.no_check_dependencies:
        dependency_checker.check(dependencies, snippet_by_name, options)

    items_by_name = parser.check(statements)

    statements = handle_filters(statements, options.debug)
    statements = remove_unused_hidables(statements)
    statements, graph_options = handle_options(statements)

    if options.no_graph_title:
        title = ""
    else:
        title = os.path.splitext(output_path)[0]

    gen = Generator(graph_options, attribs)
    text = generate_dot(gen, title, statements, items_by_name)
    dprint(text)
    dot.generate_image(graph_options, text, output_path, options.format)


def wrap(text: str, cols: int) -> str:
    res: list[str] = []
    for each in text.strip().split("\\n"):
        res += textwrap.wrap(each, width=cols, break_long_words=False) or [""]
    return "\\n".join(res)


class Generator:
    RX_NUMBERED_NAME = re.compile(r"(\d+[.])(.*)")

    def __init__(
        self, graph_options: model.GraphOptions, attribs: model.Attribs
    ) -> None:
        self.lines: list[str] = []
        self.star_nr = 0
        self.frame_nr = 0
        self.graph_options = graph_options
        self.attribs = attribs
        self.attribs_rx = self._compile_attribs_names(attribs)

    def append(self, line: str, statement: model.Statement) -> None:
        self.lines.append("")
        text = model.pack(statement.source.text)
        self.lines.append(f"/* {statement.source.line_nr}: {text} */")
        self.lines.append(line)

    def generate_item(self, item: model.Item) -> None:
        copy = model.Item(**item.__dict__)
        hits = self.RX_NUMBERED_NAME.findall(copy.text)
        if hits:
            copy.text = "\\n".join(hits[0])

        copy.text = wrap(copy.text, self.graph_options.item_text_width)
        attrs = copy.attrs or ""
        attrs = self._expand_attribs(attrs)

        match copy.type:
            case model.Keyword.PROCESS:
                if self.graph_options.is_context:
                    shape = "circle"
                    fc = "white"
                else:
                    shape = "ellipse"
                    fc = '"#eeeeee"'
                line = (
                    f'"{copy.name}" [shape={shape} label="{copy.text}" '
                    f"fillcolor={fc} style=filled {attrs}]"
                )
            case model.Keyword.CONTROL:
                fc = '"#eeeeee"'
                line = (
                    f'"{copy.name}" [shape=ellipse label="{copy.text}" '
                    f'fillcolor={fc} style="filled,dashed" {attrs}]'
                )
            case model.Keyword.ENTITY:
                line = (
                    f'"{copy.name}" [shape=rectangle label="{copy.text}" '
                    f"{attrs}]"
                )
            case model.Keyword.STORE:
                d = self._attrib_to_dict(copy, attrs)
                line = TMPL.STORE.format(**d)
            case model.Keyword.NONE:
                line = f'"{copy.name}" [shape=none label="{copy.text}" {attrs}]'
            case model.Keyword.CHANNEL:
                d = self._attrib_to_dict(copy, attrs)
                if self.graph_options.is_vertical:
                    line = TMPL.CHANNEL_HORIZONTAL.format(**d)
                else:
                    line = TMPL.CHANNEL.format(**d)
            case _:
                prefix = model.mk_err_prefix_from(copy.source)
                raise model.DfdException(
                    f"{prefix}Unsupported item type " f'"{copy.type}"'
                )
        self.append(line, item)

    def _attrib_to_dict(self, item: model.Item, attrs: str) -> dict[str, str]:
        d = self._item_to_html_dict(item)
        d.update({"fontcolor": "black", "color": "black"})

        def strip_quotes(s: str) -> str:
            if s.startswith('"'):
                return s.strip('"')
            elif s.startswith("'"):
                return s.strip("'")
            return s

        def split_attr(s: str) -> tuple[str, str]:
            pair = s.split("=", 1)
            if len(pair) != 2:
                prefix = model.mk_err_prefix_from(item.source)
                raise model.DfdException(
                    f'{prefix}Invalid attribute "{s}" in item "{item.name}"'
                    "; maybe referring to an inexistent attrib alias?"
                )
            return pair[0], pair[1]

        attrs_d = {
            k: strip_quotes(v)
            for k, v in [split_attr(each) for each in attrs.split()]
        }
        d.update(attrs_d)
        return d

    def _item_to_html_dict(self, item: model.Item) -> dict[str, Any]:
        d = item.__dict__
        d["text"] = d["text"].replace("\\n", "<br/>")
        return d

    def _compile_attribs_names(
        self, attribs: model.Attribs
    ) -> re.Pattern[str] | None:
        if not attribs:
            return None
        names = ["\\b" + re.escape(k) + "\\b" for k in attribs.keys()]
        pattern = "|".join(names)
        return re.compile(pattern)

    def _expand_attribs(self, attrs: str) -> str:
        def replacer(m: re.Match[str]) -> str:
            alias = m[0]
            if alias not in self.attribs:
                raise model.DfdException(
                    f"Alias "
                    f'"{alias}" '
                    f"not found in "
                    f"{pprint.pformat(self.attribs)}"
                )

            return self.attribs[alias].text

        return (
            self.attribs_rx.sub(replacer, attrs) if self.attribs_rx else attrs
        )

    def generate_star(self, text: str) -> str:
        text = wrap(text, self.graph_options.item_text_width)
        star_name = f"__star_{self.star_nr}__"
        line = f'"{star_name}" [shape=none label="{text}" {TMPL.DOT_FONT_EDGE}]'
        self.lines.append(line)
        self.star_nr += 1
        return star_name

    def generate_connection(
        self,
        conn: model.Connection,
        src_item: model.Item | None,
        dst_item: model.Item | None,
    ) -> None:
        text = conn.text or ""
        text = wrap(text, self.graph_options.connection_text_width)

        src_port = dst_port = ""

        if not src_item:
            src_name = self.generate_star(text)
            text = ""
        else:
            src_name = src_item.name
            if src_item.type == model.Keyword.CHANNEL:
                src_port = ":x:c"

        if not dst_item:
            dst_name = self.generate_star(text)
            text = ""
        else:
            dst_name = dst_item.name
            if dst_item.type == model.Keyword.CHANNEL:
                dst_port = ":x:c"

        attrs = f'label="{text}"'

        match conn.type:
            # make the edge invisible before other attributes
            case model.Keyword.CONSTRAINT:
                if text and not conn.attrs:
                    # transparent edge, to reveal the label
                    attrs += " style=solid color=invis"
                else:
                    # invisible edge and label
                    attrs += " style=invis dir=none"

        if conn.attrs:
            attrs += " " + self._expand_attribs(conn.attrs)

        match conn.type:
            case model.Keyword.FLOW:
                if conn.reversed:
                    attrs += " dir=back"
            case model.Keyword.BFLOW:
                attrs += " dir=both"
            case model.Keyword.CFLOW:
                if conn.reversed:
                    attrs += " dir=back"
                    attrs += " arrowtail=normalnormal"
                else:
                    attrs += " arrowhead=normalnormal"
            case model.Keyword.UFLOW:
                attrs += " dir=none"
            case model.Keyword.SIGNAL:
                if conn.reversed:
                    attrs += " dir=back"
                attrs += " style=dashed"
            case model.Keyword.CONSTRAINT:
                pass
            case _:
                prefix = model.mk_err_prefix_from(conn.source)
                raise model.DfdException(
                    f"{prefix}Unsupported connection type " f'"{conn.type}"'
                )
        if conn.relaxed:
            attrs += " constraint=false"

        line = f'"{src_name}"{src_port} -> "{dst_name}"{dst_port} [{attrs}]'
        self.append(line, conn)

    def generate_style(self, style: model.Style) -> None:
        pass

    def generate_frame(self, frame: model.Frame) -> None:
        self.append(f"subgraph cluster_{self.frame_nr} {{", frame)
        self.frame_nr += 1

        self.lines.append(f'  label="{frame.text}"')
        if frame.attrs:
            attrs = self._expand_attribs(frame.attrs)
            self.lines.append(f"  {attrs}")

        for item in frame.items:
            self.lines.append(f'  "{item}"')
        self.lines.append("}")

    def generate_dot_text(self, title: str) -> str:
        graph_params = []

        if self.graph_options.is_context:
            graph_params.append(TMPL.GRAPH_PARAMS_CONTEXT_DIAGRAM)

        if title:
            graph_params.append(TMPL.DOT_GRAPH_TITLE.format(title=title))
        else:
            graph_params.append(TMPL.DOT_GRAPH_NOTITLE)

        if self.graph_options.is_vertical:
            graph_params.append("rankdir=TB")
        else:
            graph_params.append("rankdir=LR")

        if self.graph_options.is_rotated:
            graph_params.append(f"rotate=90")

        block = "\n".join(self.lines).replace("\n", "\n  ")
        text = TMPL.DOT.format(
            title=title,
            block=block,
            graph_params="\n  ".join(graph_params),
        ).replace("\n  \n", "\n\n")
        # dprint(text)
        return text


def generate_dot(
    gen: Generator,
    title: str,
    statements: model.Statements,
    items_by_name: dict[str, model.Item],
) -> str:
    """Iterate over statements and generate a dot source file"""

    def get_item(name: str) -> model.Item | None:
        return None if name == model.NODE_STAR else items_by_name[name]

    for statement in statements:
        match statement:
            case model.Item() as item:
                gen.generate_item(item)

            case model.Connection() as connection:
                src_item = get_item(connection.src)
                dst_item = get_item(connection.dst)
                gen.generate_connection(connection, src_item, dst_item)

            case model.Style() as style:
                gen.generate_style(style)

            case model.Frame() as frame:
                gen.generate_frame(frame)

    return gen.generate_dot_text(title)


def remove_unused_hidables(statements: model.Statements) -> model.Statements:
    # collect used items
    connected_items = set()
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                pass
            case _:
                continue
        for point in conn.src, conn.dst:
            connected_items.add(point)

    # filter out unconnected items
    new_statements = []
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.hidable and item.name not in connected_items:
                    continue
        new_statements.append(statement)

    return new_statements


def handle_options(
    statements: model.Statements,
) -> tuple[model.Statements, model.GraphOptions]:
    new_statements = []
    options = model.GraphOptions()
    for statement in statements:
        prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Style() as style:
                match style.style:
                    case model.StyleOption.VERTICAL:
                        options.is_vertical = True
                    case model.StyleOption.CONTEXT:
                        options.is_context = True
                    case model.StyleOption.HORIZONTAL:
                        options.is_vertical = False
                    case model.StyleOption.ROTATED:
                        options.is_rotated = True
                    case model.StyleOption.UNROTATED:
                        options.is_rotated = False
                    case model.StyleOption.ITEM_TEXT_WIDTH:
                        try:
                            options.item_text_width = int(style.value)
                        except ValueError as e:
                            raise model.DfdException(f'{prefix}{e}"')
                    case model.StyleOption.CONNECTION_TEXT_WIDTH:
                        try:
                            options.connection_text_width = int(style.value)
                        except ValueError as e:
                            raise model.DfdException(f'{prefix}{e}"')

                    case _:
                        raise model.DfdException(
                            f"{prefix}Unsupported style " f'"{style.style}"'
                        )

                continue
        new_statements.append(statement)

    return new_statements, options


def find_neighbors(
    filter: model.Filter,
    statements: model.Statements,
    max_neighbors: int,
    debug: bool,
) -> tuple[set[str], set[str]]:
    """Collect names from filter statements of the given type."""

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

    # find down and up neighbors by successive waves of connections
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
    all_names = set([s.name for s in statements if isinstance(s, model.Item)])
    kept_names: set[str] | None = None
    only_names: set[str] = set()

    def _check_names(names: set[str], in_names: set[str], prefix: str) -> None:
        if not names.issubset(all_names):
            diff = ", ".join(names - all_names)
            raise model.DfdException(f'{prefix} Name(s) unknown: {diff}')

        if not names.issubset(in_names):
            diff = ", ".join(names - in_names)
            raise model.DfdException(
                f'{prefix} Name(s) no longer available due to previous filters: {diff}'
            )

    replacement: dict[str, str] = {}
    skip_frames_for_names: set[str] = (
        set()
    )  # names for which frames should be skipped due to neighbors_only

    # collect filtered names
    for statement in statements:
        prefix = model.mk_err_prefix_from(statement.source)

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
                if kept_names is None:
                    kept_names = set()

                # all Only names must be valid
                names = set(f.names)
                _check_names(names, all_names, prefix)

                # add names from this Only statement
                if (
                    not f.neighbors_up.no_anchors
                    and not f.neighbors_down.no_anchors
                ):
                    dprint("ONLY: adding nodes:", names)
                    kept_names.update(f.names)
                    only_names.update(f.names)

                # add neighbors
                downs, ups = find_neighbors(
                    f, statements, len(all_names), debug
                )
                dprint("ONLY: adding neighbors:", downs, ups)
                kept_names.update(downs)
                kept_names.update(ups)

                _collect_frame_skips(f, names, downs, ups)

            case model.Without() as f:
                if kept_names is None:
                    kept_names = all_names.copy()

                # all Without names must be valid
                names = set(f.names)
                names_to_check = names.copy()
                if f.replaced_by:
                    names_to_check.add(f.replaced_by)
                    for name in names:
                        replacement[name] = f.replaced_by
                _check_names(names_to_check, kept_names, prefix)

                # remove names from this Without statement
                if (
                    not f.neighbors_up.no_anchors
                    and not f.neighbors_down.no_anchors
                ):
                    dprint("WITHOUT: removing nodes:", names)
                    kept_names.difference_update(names)

                # remove neighbors
                downs, ups = find_neighbors(
                    f, statements, len(all_names), debug
                )
                dprint("WITHOUT: removing neighbors:", downs, ups)
                kept_names.difference_update(downs)
                kept_names.difference_update(ups)

                _collect_frame_skips(f, names, downs, ups)

        if isinstance(statement, model.Filter):
            dprint("    after:", kept_names)

    # A node in the only_names set may lose its connections and, if it is
    # hidable, vanish (or, if in a frame, reappear as a basic node).
    # To keep it, we make it non-hidable.
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name in only_names:
                    item.hidable = False  # make non-hidable

    kept_names = kept_names if kept_names is not None else all_names

    dprint("\nItems to keep", kept_names)

    # apply filters
    new_statements: list[model.Statement] = []
    replaced_connections: dict[str, model.Connection] = {}
    for statement in statements:
        dprint(f"\nHandling statement: {statement}")
        match statement:
            case model.Item() as item:
                # skip nodes that are not in the only list
                if item.name not in kept_names:
                    dprint("=> Skipping item: its name is not in the kept list")
                    continue

            case model.Connection() as conn:
                if conn.src in replacement or conn.dst in replacement:
                    if conn.src in replacement and conn.dst in replacement:
                        continue  # skip connections if both ends are replaced by the same name
                    # replace any end
                    if conn.src in replacement:
                        conn.src = replacement[conn.src]
                    if conn.dst in replacement:
                        conn.dst = replacement[conn.dst]
                    replaced_connections[conn.signature()] = conn
                else:
                    # skip connections if either src or dst is not in the kept list
                    if conn.src not in kept_names or conn.dst not in kept_names:
                        dprint(
                            "=> Skipping connection: some end is not in the kept list"
                        )
                        continue

            case model.Frame() as frame:
                # apply replacements
                for name in frame.items:
                    if name in replacement:
                        frame.items.remove(name)
                        frame.items.append(replacement[name])

                # skip frames if none of the items are in the kept list
                names = set(frame.items)
                if not names.intersection(kept_names):
                    dprint("=> Skipping frame: no items are in the kept list")
                    continue
                else:
                    # adjust frame items by removing those not in the kept list
                    new_items = [n for n in frame.items if n in kept_names]
                    dprint(
                        f"=> Adjusting frame items: {frame.items} -> {new_items}"
                    )
                    frame.items = new_items

                    # skip frames if they contain items for which frames should be skipped
                    if set(new_items).intersection(skip_frames_for_names):
                        dprint(
                            "=> Skipping frame: some items are in the skip-frames list"
                        )
                        continue

        # keep statement
        dprint("=> Keeping statement")
        new_statements.append(statement)

    # remove duplicate connections due to replacements
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
