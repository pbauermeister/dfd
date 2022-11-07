"""Run the generation process"""

import sys
from typing import Optional

from . import dfd_dot_templates as TMPL
from . import dot, model, parser, scanner


def build(provenance: model.SourceLine, dfd_src: str, output_path: str,
          percent_zoom: int, bgcolor: str, format: str, debug: bool,
          snippet_by_name: model.SnippetByName = None) -> None:
    """Take a DFD source and build the final image or document"""
    lines = scanner.scan(provenance, dfd_src, snippet_by_name, debug)
    statements = parser.parse(lines, debug)
    items_by_name = parser.check(statements)
    statements = filter_statements(statements)

    gen = Generator()
    text = generate_dot(gen, statements, items_by_name)
    if debug:
        print(text)
    dot.generate_image(text, output_path, format)


class Generator:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.star_nr = 0

    def append(self, line:str, statement: model.Statement) -> None:
        self.lines.append('')
        text = model.pack(statement.source.text)
        self.lines.append(f'/* {statement.source.line_nr}: {text} */')
        self.lines.append(line)

    def generate_item(self, item: model.Item) -> None:
        match item.type:
            case model.PROCESS:
                line = f'"{item.name}" [shape=ellipse label="{item.text}"]'
            case model.ENTITY:
                line = f'"{item.name}" [shape=rectangle label="{item.text}"]'
            case model.STORE:
                line = TMPL.STORE.format(**item.__dict__)
            case model.CHANNEL:
                line = TMPL.CHANNEL.format(**item.__dict__)
            case _:
                prefix = model.mk_err_prefix_from(item.source)
                raise model.DfdException(f'{prefix}Unsupported item type '
                                         f'"{item.type}"')
        self.append(line, item)

    def generate_star(self, text: str) -> str:
        star_name = f'__star_{self.star_nr}__'
        line = f'"{star_name}" [shape=none label="{text}" {TMPL.DOT_FONT_EDGE}]'
        self.lines.append(line)
        self.star_nr += 1
        return star_name

    def generate_connection(self, conn: model.Connection, src_item: model.Item,
                            dst_item: model.Item) -> None:
        text = conn.text or ''
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
        match conn.type:
            case model.FLOW:
                pass
            case model.BFLOW:
                attrs += ' dir=both'
            case model.SIGNAL:
                attrs += ' style=dashed'
            case _:
                prefix = model.mk_err_prefix_from(conn.source)
                raise model.DfdException(f'{prefix}Unsupported connection type '
                                         f'"{conn.type}"')

        line = f'"{src_name}"{src_port} -> "{dst_name}"{dst_port} [{attrs}]'
        self.append(line, conn)

    def generate_style(self, style: model.Style) -> None:
        pass

    def generate_dot_text(self) -> str:
        block = '\n'.join(self.lines).replace('\n', '\n  ')
        text = TMPL.DOT.format(block=block).replace('\n  \n', '\n\n')
        return text


def generate_dot(gen: Generator, statements: model.Statements,
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

    return gen.generate_dot_text()


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
