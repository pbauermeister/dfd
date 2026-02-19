"""Pipeline orchestrator: scan → parse → check → resolve → filter → render."""

from . import config, exception, model
from .console import dprint
from .dsl import checker, dependency_checker, filters, parser, scanner
from .rendering.dot import Generator, generate_dot
from .rendering import templates as TMPL


def build(
    provenance: model.SourceLine,
    dfd_src: str,
    title: str,
    options: model.Options,
    snippet_by_name: model.SnippetByName | None = None,
) -> tuple[str, model.GraphOptions]:
    """Run the pure pipeline and return (DOT text, graph options).

    No file I/O is performed here; the caller is responsible for writing
    the DOT text to disk or invoking Graphviz.
    """

    # scan (includes, line continuations) and parse the DSL into statements
    lines = scanner.scan(provenance, dfd_src, snippet_by_name, options.debug)
    statements, dependencies, attribs = parser.parse(lines, options)
    if dependencies and not options.no_check_dependencies:
        dependency_checker.check(dependencies, snippet_by_name, options)

    # validate statements, resolve star endpoints, and apply filters
    items_by_name = checker.check(statements)
    statements = resolve_star_endpoints(statements, items_by_name)
    statements = filters.handle_filters(statements, options.debug)
    statements = remove_unused_hidables(statements)
    statements, graph_options = handle_options(statements)

    # resolve title and background color (CLI args override DFD style)
    if options.no_graph_title or graph_options.no_graph_title:
        title = ""

    bg_color = (
        options.background_color
        if options.background_color is not None
        else graph_options.background_color
    )

    # generate DOT text
    gen = Generator(graph_options, attribs)
    text = generate_dot(gen, title, bg_color, statements, items_by_name)
    dprint(text)
    return text, graph_options


def resolve_star_endpoints(
    statements: model.Statements,
    items_by_name: dict[str, model.Item],
) -> model.Statements:
    """Replace anonymous star endpoints with unique named items.

    Each ENDPOINT_STAR ("*") in a connection becomes a distinct none item
    with the connection's label. This must run before filtering so that
    stars participate as regular items in the kept set.
    """
    star_nr = 0
    new_statements: model.Statements = []
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                for attr in ("src", "dst"):
                    if getattr(conn, attr) == model.ENDPOINT_STAR:
                        star_name = TMPL.STAR_ITEM_FMT.format(nr=star_nr)
                        star_nr += 1
                        # create a none item with the connection's label
                        star_item = model.Item(
                            source=conn.source,
                            type=model.Keyword.NONE,
                            text=conn.text or "",
                            attrs=config.ITEM_STAR_ATTRS,
                            name=star_name,
                            hidable=False,
                        )
                        new_statements.append(star_item)
                        items_by_name[star_name] = star_item
                        setattr(conn, attr, star_name)
                        conn.text = ""
        new_statements.append(statement)
    return new_statements


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
        for endpoint in conn.src, conn.dst:
            connected_items.add(endpoint)

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
