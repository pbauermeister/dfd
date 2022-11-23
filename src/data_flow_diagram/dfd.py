"""Run the generation process"""

import os.path
import sys
import textwrap
from typing import Any, Optional

from . import config
from . import dfd_dot_templates as TMPL
from . import dot, model, parser, scanner, dependency_checker


def build(provenance: model.SourceLine, dfd_src: str, output_path: str,
          options: model.Options,
          snippet_by_name: model.SnippetByName = None) -> None:
    """Take a DFD source and build the final image or document"""
    lines = scanner.scan(provenance, dfd_src, snippet_by_name, options.debug)
    statements, dependencies = parser.parse(lines, options.debug)
    if dependencies and not options.no_check_dependencies:
        dependency_checker.check(dependencies, snippet_by_name, options)
    items_by_name = parser.check(statements)
    statements = filter_statements(statements)
    statements, graph_options = handle_options(statements)

    if options.no_graph_title:
        title = None
    else:
        title = os.path.splitext(output_path)[0]

    gen = Generator(graph_options)
    text = generate_dot(gen, title, statements, items_by_name)
    if options.debug:
        print(text)
    dot.generate_image(graph_options, text, output_path, options.format)


def wrap(text: str, cols: int) -> str:
    res: list[str] = []
    for each in text.strip().split('\\n'):
        res += textwrap.wrap(each, width=cols, break_long_words=False) or ['']
    return '\\n'.join(res)

class Generator:
    def __init__(self, graph_options: model.GraphOptions) -> None:
        self.lines: list[str] = []
        self.star_nr = 0
        self.frame_nr = 0
        self.graph_options = graph_options

    def append(self, line:str, statement: model.Statement) -> None:
        self.lines.append('')
        text = model.pack(statement.source.text)
        self.lines.append(f'/* {statement.source.line_nr}: {text} */')
        self.lines.append(line)

    def generate_item(self, item: model.Item) -> None:
        text = wrap(item.text, self.graph_options.item_text_width)
        attrs = item.attrs or ''
        match item.type:
            case model.PROCESS:
                if self.graph_options.is_context:
                    shape = 'circle'
                    fc = 'white'
                else:
                    shape = 'ellipse'
                    fc = '"#eeeeee"'
                line = (f'"{item.name}" [shape={shape} label="{text}" '
                        f'fillcolor={fc} style=filled {attrs}]')
            case model.CONTROL:
                fc = '"#eeeeee"'
                line = (f'"{item.name}" [shape=ellipse label="{text}" '
                        f'fillcolor={fc} style="filled,dashed" {attrs}]')
            case model.ENTITY:
                line = (f'"{item.name}" [shape=rectangle label="{text}" '
                        f'{attrs}]')
            case model.STORE:
                d = self._item_to_html_dict(item)
                line = TMPL.STORE.format(**d)
            case model.NONE:
                line = f'"{item.name}" [shape=none label="{text}" {attrs}]'
            case model.CHANNEL:
                d = self._item_to_html_dict(item)
                if self.graph_options.is_vertical:
                    line = TMPL.CHANNEL_HORIZONTAL.format(**d)
                else:
                    line = TMPL.CHANNEL.format(**d)
            case _:
                prefix = model.mk_err_prefix_from(item.source)
                raise model.DfdException(f'{prefix}Unsupported item type '
                                         f'"{item.type}"')
        self.append(line, item)

    def _item_to_html_dict(self, item: model.Item) -> dict[str, Any]:
        d = item.__dict__
        d['text'] = d['text'].replace('\\n', '<br/>')
        return d

    def generate_star(self, text: str) -> str:
        text = wrap(text, self.graph_options.item_text_width)
        star_name = f'__star_{self.star_nr}__'
        line = f'"{star_name}" [shape=none label="{text}" {TMPL.DOT_FONT_EDGE}]'
        self.lines.append(line)
        self.star_nr += 1
        return star_name

    def generate_connection(self, conn: model.Connection, src_item: model.Item,
                            dst_item: model.Item) -> None:
        text = conn.text or ''
        text = wrap(text, self.graph_options.connection_text_width)

        src_port = dst_port = ""

        if not src_item:
            src_name = self.generate_star(text)
            text = ''
        else:
            src_name = src_item.name
            if src_item.type == model.CHANNEL:
                src_port = ':x:c'

        if not dst_item:
            dst_name = self.generate_star(text)
            text = ''
        else:
            dst_name = dst_item.name
            if dst_item.type == model.CHANNEL:
                dst_port = ':x:c'

        attrs = f'label="{text}"'
        if conn.attrs: attrs += ' ' + conn.attrs

        match conn.type:
            case model.FLOW:
                if conn.reversed:
                    attrs += ' dir=back'
            case model.BFLOW:
                attrs += ' dir=both'
            case model.CFLOW:
                if conn.reversed:
                    attrs += ' dir=back'
                    attrs += ' arrowtail=normalnormal'
                else:
                    attrs += ' arrowhead=normalnormal'
            case model.UFLOW:
                attrs += ' dir=none'
            case model.SIGNAL:
                if conn.reversed:
                    attrs += ' dir=back'
                attrs += ' style=dashed'
            case _:
                prefix = model.mk_err_prefix_from(conn.source)
                raise model.DfdException(f'{prefix}Unsupported connection type '
                                         f'"{conn.type}"')
        if conn.relaxed:
            attrs += ' constraint=false'

        line = f'"{src_name}"{src_port} -> "{dst_name}"{dst_port} [{attrs}]'
        self.append(line, conn)

    def generate_style(self, style: model.Style) -> None:
        pass

    def generate_frame(self, frame: model.Frame) -> None:
        self.append(f'subgraph cluster_{self.frame_nr} {{', frame)
        self.frame_nr += 1

        self.lines.append(f'  label="{frame.text}"')
        if frame.attrs:
            self.lines.append(f'  {frame.attrs}')

        for item in frame.items:
            self.lines.append(f'  "{item}"')
        self.lines.append('}')

    def generate_dot_text(self, title: str) -> str:
        graph_params = []
        if self.graph_options.is_context:
            graph_params.append(TMPL.GRAPH_PARAMS_CONTEXT_DIAGRAM)

        if title:
            graph_params.append(TMPL.DOT_GRAPH_TITLE.format(title=title))

        if self.graph_options.is_vertical:
            graph_params.append('rankdir=TB')
        else:
            graph_params.append('rankdir=LR')

        block = '\n'.join(self.lines).replace('\n', '\n  ')
        text = TMPL.DOT.format(
            title=title,
            block=block,
            graph_params='\n  '.join(graph_params),
        ).replace('\n  \n', '\n\n')
        #print(text)
        return text


def generate_dot(gen: Generator, title: str, statements: model.Statements,
                 items_by_name: dict[str, model.Item]) -> str:
    """Iterate over statements and generate a dot source file"""
    def get_item(name: str) -> Optional[model.Item]:
        return None if name == '*' else items_by_name[name]

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


def filter_statements(statements: model.Statements) -> model.Statements:
    # collect used items
    connected_items = set()
    for statement in statements:
        match statement:
            case model.Connection() as conn: pass
            case _: continue
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


def handle_options(statements: model.Statements) -> tuple[
        model.Statements, model.GraphOptions]:
    new_statements = []
    options = model.GraphOptions()
    for statement in statements:
        prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Style() as style:
                match style.style:
                    case 'vertical':
                        options.is_vertical = True
                    case 'context':
                        options.is_context = True
                    case 'horizontal':
                        options.is_vertical = False
                    case 'item-text-width':
                        try:
                            options.item_text_width = int(style.value)
                        except ValueError as e:
                            raise model.DfdException(f'{prefix}{e}"')
                    case 'connection-text-width':
                        try:
                            options.connection_text_width = int(style.value)
                        except ValueError as e:
                            raise model.DfdException(f'{prefix}{e}"')

                    case _:
                        raise model.DfdException(f'{prefix}Unsupported style '
                                                 f'"{style.style}"')

                continue
        new_statements.append(statement)

    return new_statements, options
