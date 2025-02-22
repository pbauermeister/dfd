import sys

from . import model, scanner, parser


def check(
    dependencies: model.GraphDependencies,
    snippet_by_name: model.SnippetByName | None,
    options: model.Options,
) -> None:

    snippet_by_name = snippet_by_name or {}
    errors: list[str] = []
    for dep in dependencies:
        prefix = model.mk_err_prefix_from(dep.source)

        # load source text
        if dep.to_graph.startswith('#'):
            # from snippet
            name = dep.to_graph[1:]
            if name not in snippet_by_name:
                errors.append(f'{prefix}Referring to unknown snippet "{name}"')
                continue
            text = snippet_by_name[name].text
            what = 'snippet'
        else:
            # from file
            name = dep.to_graph
            try:
                with open(name, encoding='utf-8') as f:
                    text = f.read()
            except FileNotFoundError as e:
                if name in snippet_by_name:
                    errors.append(f'{prefix}{e}. Did you mean "#{name}" ?')
                else:
                    errors.append(f'{prefix}{e}')
                continue
            what = 'file'

        # if only graph is targetted, we're done
        if dep.to_item is None:
            if dep.to_type != model.NONE:
                errors.append(
                    f'{prefix}A whole graph may only be referred to '
                    f'by an item of type "{model.NONE}", and not '
                    f'"{dep.to_type}"'
                )
            continue

        # scan and parse
        lines = scanner.scan(dep.source, text, snippet_by_name, options.debug)
        statements, _, _ = parser.parse(lines, options.debug)

        # find name
        item = find_item(dep.to_item, statements)
        if item:
            if dep.to_type != item.type:
                errors.append(
                    f'{prefix}Referred item "{dep.to_item}" is of '
                    f'type "{item.type}", but is referred to as '
                    f'type "{dep.to_type}"'
                )

            continue  # Found!

        errors.append(
            f'{prefix}Referring to unknown item name "{dep.to_item}"'
            f' of {what} "{name}"'
        )

    if errors:
        errors.insert(0, 'Dependency error(s) found:')
        raise model.DfdException('\n\n'.join(errors))


def find_item(name: str, statements: model.Statements) -> model.Item | None:
    for statement in statements:
        match statement:
            case model.Item() as item:
                if item.name == name:
                    return statement
    return None
