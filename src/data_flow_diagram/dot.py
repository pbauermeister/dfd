"""Graphviz dot-related generation process"""

import subprocess
from . import model

TMPL_STORE = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="black" WIDTH="6"></TD></TR>
    <TR><TD>{text}</TD></TR>
    <TR><TD BGCOLOR="black" WIDTH="6"></TD></TR>
  </TABLE>>]
""".strip()

TMPL_CHANNEL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR>
      <TD WIDTH="48"></TD>
      <TD BGCOLOR="black" WIDTH="0" PORT="x"><BR/><BR/></TD>
      <TD WIDTH="48"></TD>
    </TR>
    <TR>
      <TD COLSPAN="3">{text}</TD>
    </TR>
  </TABLE>>]
""".strip()

TMPL_CHANNEL_HORIZONTAL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="black" PORT="x"></TD></TR>
    <TR><TD>{text}</TD></TR>
  </TABLE>>]
""".strip()

TMPL_DOT = """
digraph D {{
  rankdir=LR
  edge[color=gray fontname="times-italic"]
  node[fontname=helvetica]
  {block}
}}
""".strip()


class Generator:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.star_nr = 0

    def append(self, line:str, statement: model.Statement) -> None:
        self.lines.append('')
        source = model.pack(statement.line)
        self.lines.append(f'/* {statement.line_nr}: {source} */')
        self.lines.append(line)

    def generate_item(self, item: model.Item) -> None:
        match item.type:
            case model.PROCESS:
                line = f'"{item.name}" [shape=ellipse label="{item.text}"]'
            case model.ENTITY:
                line = f'"{item.name}" [shape=rectangle label="{item.text}"]'
            case model.STORE:
                line = TMPL_STORE.format(**item.__dict__)
            case model.CHANNEL:
                line = TMPL_CHANNEL.format(**item.__dict__)
            case _:
                prefix = model.mk_err_prefix_from(item)
                raise RuntimeError(f'{prefix}Unsupported item type '
                                   f'"{item.type}"')
        self.append(line, item)

    def generate_star(self, text: str) -> str:
        star_name = f'__star_{self.star_nr}__'
        line = f'"{star_name}" [shape=none label="{text}"]'
        self.lines.append(line)
        return star_name

    def generate_connection(self, conn: model.Connection,
                            src_item: model.Item, dst_item: model.Item) -> None:
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
                prefix = model.mk_err_prefix_from(conn)
                raise RuntimeError(f'{prefix}Unsupported connection type '
                                   f'"{conn.type}"')

        line = f'"{src_name}"{src_port} -> "{dst_name}"{dst_port} [{attrs}]'
        self.append(line, conn)

    def generate_style(self, style: model.Style) -> None:
        pass

    def generate_dot_text(self) -> str:
        block = '\n'.join(self.lines).replace('\n', '\n  ')
        text = TMPL_DOT.format(block=block).replace('\n  \n', '\n\n')
        return text

    def generate_image(self, output_path: str, format: str) -> None:
        text = self.generate_dot_text()
        cmd = ['dot', f'-T{format}',  f'-o{output_path}']
        subprocess.run(cmd, input=text, encoding='utf-8')
        print('Generated:', output_path)
