from .. import exception, model
from ..model import Keyword
from . import parser, scanner


def check(
    dependencies: model.GraphDependencies,
    snippet_by_name: model.SnippetByName | None,
    options: model.Options,
) -> None:
    """Verify that all dependencies refer to existing items of compatible type."""

    snippet_by_name = snippet_by_name or {}
    errors = exception.DfdException("Dependency error(s) found:")
    for dep in dependencies:
        # load source text
        if dep.to_graph.startswith(model.SNIPPET_PREFIX):
            # from snippet
            name = dep.to_graph[len(model.SNIPPET_PREFIX) :]
            if name not in snippet_by_name:
                errors.add(
                    f'Referring to unknown snippet "{name}"',
                    source=dep.source,
                )
                continue
            text = snippet_by_name[name].text
            what = "snippet"
        else:
            # from file
            name = dep.to_graph
            try:
                with open(name, encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError as e:
                if name in snippet_by_name:
                    errors.add(
                        f'{e}. Did you mean "{model.SNIPPET_PREFIX}{name}" ?',
                        source=dep.source,
                    )
                else:
                    errors.add(f"{e}", source=dep.source)
                continue
            what = "file"

        # whole-graph reference: only check that the item type is "none"
        if dep.to_item is None:
            if dep.to_type != Keyword.NONE:
                errors.add(
                    f"A whole graph may only be referred to "
                    f'by an item of type "{Keyword.NONE}", and not '
                    f'"{dep.to_type}"',
                    source=dep.source,
                )
            continue

        # scan and parse the referred graph to look up the item
        lines = scanner.scan(dep.source, text, snippet_by_name, options.debug)
        statements, _, _ = parser.parse(lines, options)

        # verify the referred item exists and has the expected type
        item = find_item(dep.to_item, statements)
        if item:
            if dep.to_type != item.type:
                errors.add(
                    f'Referred item "{dep.to_item}" is of '
                    f'type "{item.type}", but is referred to as '
                    f'type "{dep.to_type}"',
                    source=dep.source,
                )

            continue  # Found!

        errors.add(
            f'Referring to unknown item name "{dep.to_item}"'
            f' of {what} "{name}"',
            source=dep.source,
        )

    # raise all accumulated errors at once
    if errors:
        raise errors


def find_item(name: str, statements: model.Statements) -> model.Item | None:
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name == name:
                    return statement
    return None
