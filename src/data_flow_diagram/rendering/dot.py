"""DOT code generation: Generator class and statement-to-DOT dispatch."""

import html
import pprint
import re
import textwrap

from .. import exception, model
from . import templates as TMPL

# label escapes needing translation in HTML-like label context
RX_HTML_LABEL_ESCAPE = re.compile(r"\\(\\|n)")


def _escape_dot_string(s: str) -> str:
    """Escape a value for embedding in a double-quoted DOT string.

    Only double quotes need escaping: the checker rejects stray
    backslashes, and recognized label escapes (\\n, \\l, \\r, \\\\) are
    deliberately forwarded to Graphviz.
    """
    return s.replace('"', '\\"')


def _strip_quotes(s: str) -> str:
    """Remove matching quotes from a string."""
    if s.startswith('"'):
        return s.strip('"')
    elif s.startswith("'"):
        return s.strip("'")
    return s


def _split_attr(s: str, item: model.Item) -> tuple[str, str]:
    """Split a key=value attribute string, raising on invalid format."""
    pair = s.split("=", 1)
    if len(pair) != 2:
        raise exception.DfdException(
            f'Invalid attribute "{s}" in item "{item.name}"'
            "; maybe referring to an inexistent attrib alias?",
            source=item.source,
        )
    return pair[0], pair[1]


def _get_item(name: str, items_by_name: dict[str, model.Item]) -> model.Item:
    """Look up an item by name."""
    return items_by_name[name]


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
        self.frame_nr = 0
        self.graph_options = graph_options
        self.attribs = attribs
        self.attribs_rx = self._compile_attribs_names(attribs)

    def append(self, line: str, statement: model.Statement) -> None:
        self.lines.append("")
        # break any */ in the source echo so the DOT comment stays valid
        text = model.pack(statement.source.text).replace("*/", "* /")
        self.lines.append(f"/* {statement.source.line_nr}: {text} */")
        self.lines.append(line)

    def generate_item(self, item: model.Item) -> None:
        """Emit the DOT declaration for a single item."""

        # prepare a working copy with text wrapping and attrib expansion
        copy = model.Item(**item.__dict__)
        hits = self.RX_NUMBERED_NAME.findall(copy.text)
        if hits:
            copy.text = "\\n".join(hits[0])

        copy.text = wrap(copy.text, self.graph_options.item_text_width)
        attrs = copy.attrs or ""
        attrs = self._expand_attribs(attrs)

        # escape for the double-quoted emission sites below
        name = _escape_dot_string(copy.name)
        text = _escape_dot_string(copy.text)

        # emit shape-specific DOT declaration
        match copy.type:
            case model.Keyword.PROCESS:
                if self.graph_options.is_context:
                    shape = TMPL.SHAPE_PROCESS_CONTEXT
                    fc = TMPL.FILL_PROCESS_CONTEXT
                else:
                    shape = TMPL.SHAPE_PROCESS
                    fc = TMPL.FILL_PROCESS
                line = (
                    f'"{name}" [shape={shape} label="{text}" '
                    f"fillcolor={fc} style={TMPL.STYLE_PROCESS} {attrs}]"
                )
            case model.Keyword.CONTROL:
                line = (
                    f'"{name}" [shape={TMPL.SHAPE_PROCESS} label="{text}" '
                    f'fillcolor={TMPL.FILL_PROCESS} style={TMPL.STYLE_CONTROL} {attrs}]'
                )
            case model.Keyword.ENTITY:
                line = (
                    f'"{name}" [shape={TMPL.SHAPE_ENTITY} label="{text}" '
                    f"{attrs}]"
                )
            case model.Keyword.STORE:
                d = self._attrib_to_dict(copy, attrs)
                line = TMPL.STORE.format(**d)
            case model.Keyword.NONE | model.Keyword.STAR:
                line = (
                    f'"{name}" [shape={TMPL.SHAPE_NONE} label="{text}" {attrs}]'
                )
            case model.Keyword.CHANNEL:
                d = self._attrib_to_dict(copy, attrs)
                if self.graph_options.is_vertical:
                    line = TMPL.CHANNEL_HORIZONTAL.format(**d)
                else:
                    line = TMPL.CHANNEL.format(**d)
            case _:
                raise exception.DfdException(
                    f'Unsupported item type "{copy.type}"',
                    source=copy.source,
                )
        self.append(line, item)

    def _attrib_to_dict(self, item: model.Item, attrs: str) -> dict[str, str]:
        d = self._item_to_html_dict(item)
        d.update(TMPL.HTML_ITEM_DEFAULTS.copy())

        attrs_d = {
            k: _strip_quotes(v)
            for k, v in [_split_attr(each, item) for each in attrs.split()]
        }
        d.update(attrs_d)
        return d

    def _item_to_html_dict(self, item: model.Item) -> dict[str, str]:
        """Build the placeholder fields of the HTML-like item templates."""
        # HTML-like label context: entity-escape, then translate label
        # escapes left-to-right (\\ -> literal backslash, \n -> <br/>)
        text = RX_HTML_LABEL_ESCAPE.sub(
            lambda m: "<br/>" if m[1] == "n" else "\\",
            html.escape(item.text),
        )
        return {"name": _escape_dot_string(item.name), "text": text}

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
                raise exception.DfdException(
                    f"Alias "
                    f'"{alias}" '
                    f"not found in "
                    f"{pprint.pformat(self.attribs)}"
                )

            return self.attribs[alias].text

        return (
            self.attribs_rx.sub(replacer, attrs) if self.attribs_rx else attrs
        )

    def _build_connection_attrs(self, conn: model.Connection, text: str) -> str:
        """Build the DOT attribute string for a connection edge."""
        attrs = f'label="{_escape_dot_string(text)}"'

        # constraints are invisible layout-only edges
        match conn.type:
            case model.Keyword.CONSTRAINT:
                if text and not conn.attrs:
                    attrs += TMPL.ATTR_CONSTRAINT_LABELED
                else:
                    attrs += TMPL.ATTR_CONSTRAINT_HIDDEN

        if conn.attrs:
            attrs += " " + self._expand_attribs(conn.attrs)

        # apply connection-type-specific DOT attributes
        match conn.type:
            case model.Keyword.FLOW:
                if conn.reversed:
                    attrs += TMPL.ATTR_DIR_BACK
            case model.Keyword.BFLOW:
                attrs += TMPL.ATTR_DIR_BOTH
            case model.Keyword.CFLOW:
                if conn.reversed:
                    attrs += TMPL.ATTR_DIR_BACK
                    attrs += TMPL.ATTR_CFLOW_TAIL
                else:
                    attrs += TMPL.ATTR_CFLOW_HEAD
            case model.Keyword.UFLOW:
                attrs += TMPL.ATTR_DIR_NONE
            case model.Keyword.SIGNAL:
                if conn.reversed:
                    attrs += TMPL.ATTR_DIR_BACK
                attrs += TMPL.ATTR_STYLE_DASHED
            case model.Keyword.CONSTRAINT:
                pass
            case _:
                raise exception.DfdException(
                    f'Unsupported connection type "{conn.type}"',
                    source=conn.source,
                )
        if conn.relaxed:
            attrs += TMPL.ATTR_RELAXED

        return attrs

    def generate_connection(
        self,
        conn: model.Connection,
        src_item: model.Item,
        dst_item: model.Item,
    ) -> None:
        """Emit the DOT edge declaration for a connection."""
        text = conn.text or ""
        text = wrap(text, self.graph_options.connection_text_width)

        # resolve channel ports
        src_port = (
            TMPL.CHANNEL_PORT if src_item.type == model.Keyword.CHANNEL else ""
        )
        dst_port = (
            TMPL.CHANNEL_PORT if dst_item.type == model.Keyword.CHANNEL else ""
        )

        attrs = self._build_connection_attrs(conn, text)
        src_name = _escape_dot_string(src_item.name)
        dst_name = _escape_dot_string(dst_item.name)
        line = f'"{src_name}"{src_port} -> "{dst_name}"{dst_port} [{attrs}]'
        self.append(line, conn)

    def generate_style(self, style: model.Style) -> None:
        pass

    def generate_frame(self, frame: model.Frame) -> None:
        self.append(f"subgraph cluster_{self.frame_nr} {{", frame)
        self.frame_nr += 1

        self.lines.append(f'  label="{_escape_dot_string(frame.text)}"')
        if frame.attrs:
            attrs = self._expand_attribs(frame.attrs)
            self.lines.append(f"  {attrs}")

        for item in frame.items:
            self.lines.append(f'  "{_escape_dot_string(item)}"')
        self.lines.append("}")

    def generate_dot_text(self, title: str, bg_color: str | None) -> str:
        """Assemble all generated lines into the final DOT source text."""

        # collect graph-level parameters from options
        graph_params = []

        if self.graph_options.is_context:
            graph_params.append(TMPL.GRAPH_PARAMS_CONTEXT_DIAGRAM)

        if title:
            escaped_title = _escape_dot_string(title)
            graph_params.append(
                TMPL.DOT_GRAPH_TITLE.format(
                    title=escaped_title,
                    graph_title_size=self.graph_options.graph_title_size,
                )
            )
        else:
            graph_params.append(
                TMPL.DOT_GRAPH_NOTITLE.format(
                    graph_title_size=self.graph_options.graph_title_size
                )
            )

        if self.graph_options.is_vertical:
            graph_params.append(TMPL.LAYOUT_VERTICAL)
        else:
            graph_params.append(TMPL.LAYOUT_HORIZONTAL)

        if self.graph_options.is_rotated:
            graph_params.append(f"rotate={TMPL.ROTATION_DEGREES}")

        if bg_color:
            graph_params.append(f"bgcolor={bg_color}")

        # wrap generated lines into the DOT digraph template
        block = "\n".join(self.lines).replace("\n", "\n  ")
        text = TMPL.DOT.format(
            title=title,
            block=block,
            graph_params="\n  ".join(graph_params),
            connection_text_size=self.graph_options.connection_text_size,
            item_text_size=self.graph_options.item_text_size,
        ).replace("\n  \n", "\n\n")
        return text


def generate_dot(
    gen: Generator,
    title: str,
    bg_color: str | None,
    statements: model.Statements,
    items_by_name: dict[str, model.Item],
) -> str:
    """Iterate over statements and generate a dot source file"""

    for statement in statements:
        match statement:
            case model.Item() as item:
                gen.generate_item(item)

            case model.Connection() as connection:
                src_item = _get_item(connection.src, items_by_name)
                dst_item = _get_item(connection.dst, items_by_name)
                gen.generate_connection(connection, src_item, dst_item)

            case model.Style() as style:
                gen.generate_style(style)

            case model.Frame() as frame:
                gen.generate_frame(frame)

    return gen.generate_dot_text(title, bg_color)
