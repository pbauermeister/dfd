from .. import exception, model
from ..model import Keyword
from . import parser, scanner


def _read_file(name: str, file_texts: dict[str, str] | None) -> str:
    """Read graph source text from *file_texts* dict or from the filesystem.

    When *file_texts* is provided (typically in tests), the file content is
    looked up by name in the dict.  A missing key raises ``FileNotFoundError``
    with the same format as a real missing file, so the caller's error
    handling works identically in both modes.
    """
    if file_texts is not None:
        if name not in file_texts:
            raise FileNotFoundError(2, "No such file or directory", name)
        return file_texts[name]
    with open(name, encoding="utf-8") as f:
        return f.read()


def check(
    dependencies: model.GraphDependencies,
    snippet_by_name: model.SnippetByName | None,
    options: model.Options,
    file_texts: dict[str, str] | None = None,
) -> None:
    """Verify that all dependencies refer to existing items of compatible type.

    *file_texts*, when provided, is a ``{filename: content}`` dict used
    instead of the real filesystem.  This is intended for unit tests that
    need to exercise dependency checking without creating temporary files.
    """

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
                text = _read_file(name, file_texts)
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
