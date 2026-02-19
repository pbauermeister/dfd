"""Pipeline orchestrator: scan → parse → check → filter → render."""

import os.path

from . import exception, model
from .console import dprint
from .dsl import checker, dependency_checker, filters, parser, scanner
from .rendering import graphviz
from .rendering.dot import Generator, generate_dot


def build(
    provenance: model.SourceLine,
    dfd_src: str,
    output_path: str,
    options: model.Options,
    snippet_by_name: model.SnippetByName | None = None,
) -> None:
    """Take a DFD source and build the final image or document."""

    # scan (includes, line continuations) and parse the DSL into statements
    lines = scanner.scan(provenance, dfd_src, snippet_by_name, options.debug)
    statements, dependencies, attribs = parser.parse(lines, options)
    if dependencies and not options.no_check_dependencies:
        dependency_checker.check(dependencies, snippet_by_name, options)

    # validate statements and apply filters
    items_by_name = checker.check(statements)
    statements = filters.handle_filters(statements, options.debug)
    statements = remove_unused_hidables(statements)
    statements, graph_options = handle_options(statements)

    # resolve title and background color (CLI args override DFD style)
    if options.no_graph_title or graph_options.no_graph_title:
        title = ""
    else:
        title = os.path.splitext(output_path)[0]

    bg_color = (
        options.background_color
        if options.background_color is not None
        else graph_options.background_color
    )

    # generate DOT and produce the output file
    gen = Generator(graph_options, attribs)
    text = generate_dot(gen, title, bg_color, statements, items_by_name)
    dprint(text)
    if options.format == "dot":
        with open(output_path, "w") as f:
            f.write(text)
    else:
        graphviz.generate_image(
            graph_options, text, output_path, options.format
        )


def remove_unused_hidables(statements: model.Statements) -> model.Statements:
    """Drop hidable items that have no connections (conditional items marked with '?')."""
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
    """Extract style statements into GraphOptions and return the remaining statements."""
    new_statements = []
    options = model.GraphOptions()
    for statement in statements:
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
                            raise exception.DfdException(
                                f'{e}"', source=statement.source
                            ) from e
                    case model.StyleOption.CONNECTION_TEXT_WIDTH:
                        try:
                            options.connection_text_width = int(style.value)
                        except ValueError as e:
                            raise exception.DfdException(
                                f'{e}"', source=statement.source
                            ) from e
                    case model.StyleOption.BACKGROUND_COLOR:
                        options.background_color = style.value
                    case model.StyleOption.NO_GRAPH_TITLE:
                        options.no_graph_title = True
                    case _:
                        raise exception.DfdException(
                            f'Unsupported style "{style.style}"',
                            source=statement.source,
                        )

                continue
        new_statements.append(statement)

    return new_statements, options
