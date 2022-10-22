"""Run the generation process"""

from typing import Optional

from . import model
from . import dot
from . import parse


def build(dfd_src: str, output_path: str, percent_zoom: int, bgcolor: str,
          format: str, debug: bool) -> None:
    """Take a DFD source and build the final image or document"""
    statements = parse.parse(dfd_src)
    items_by_name = parse.check(statements)
    gen = dot.Generator()
    text = generate_dot(gen, statements, items_by_name)
    if debug:
        print(text)
    gen.generate_image(output_path, format)


def generate_dot(gen: dot.Generator,
                 statements: list[model.Statement],
                 items_by_name: dict[str, model.Item]) -> str:
    """Iterate over statements and generate a dot source file"""
    def get_item(name: str) -> Optional[model.Item]:
        return None if name == '*' else items_by_name[name]

    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement)
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
