"""Validate parsed statements: items, connections, frames."""

from .. import exception, model
from ..model import Keyword


def _check_items(statements: model.Statements) -> dict[str, model.Item]:
    """Collect items and reject duplicates."""
    items_by_name: dict[str, model.Item] = {}
    for statement in statements:
        match statement:
            case model.Item() as item:
                pass
            case _:
                continue
        name = item.name

        if name not in items_by_name:
            items_by_name[name] = item
            continue

        other = items_by_name[name]
        other_text = model.pack(other.source.text)
        raise exception.DfdException(
            f'Name "{name}" already exists '
            f"at line {other.source.line_nr+1}: {other_text}",
            source=statement.source,
        )
    return items_by_name


def _check_connections(
    statements: model.Statements, items_by_name: dict[str, model.Item]
) -> None:
    """Validate connection endpoints and type constraints."""
    for statement in statements:
        match statement:
            case model.Connection() as conn:
                pass
            case _:
                continue
        nb_stars = 0
        for endpoint in conn.src, conn.dst:
            if endpoint == model.ENDPOINT_STAR:
                nb_stars += 1
            if endpoint != model.ENDPOINT_STAR:
                if endpoint not in items_by_name:
                    raise exception.DfdException(
                        f'Connection "{conn.type}" connects to "{endpoint}", '
                        f"which is not defined",
                        source=statement.source,
                    )
                if (
                    items_by_name[endpoint].type == Keyword.CONTROL
                    and conn.type != Keyword.SIGNAL
                ):
                    raise exception.DfdException(
                        f'Connection to {Keyword.CONTROL} "{endpoint}" is '
                        f'of type "{conn.type}", however only connections of type '
                        f'"{Keyword.SIGNAL}" are allowed',
                        source=statement.source,
                    )

        if nb_stars == 2:
            raise exception.DfdException(
                f'Connection "{conn.type}" may not connect two '
                f"anonymous endpoints",
                source=statement.source,
            )


def _check_frames(
    statements: model.Statements, items_by_name: dict[str, model.Item]
) -> None:
    """Validate frame membership: items must exist and not belong to multiple frames."""
    framed_items: set[str] = set()
    for statement in statements:
        match statement:
            case model.Frame() as frame:
                pass
            case _:
                continue
        if not frame.items:
            raise exception.DfdException(
                "Frame is empty", source=statement.source
            )
        for name in frame.items:
            if name not in items_by_name:
                raise exception.DfdException(
                    f'Frame includes "{name}", ' f"which is not defined",
                    source=statement.source,
                )
            if name in framed_items:
                raise exception.DfdException(
                    f'Item "{name}", ' f"is in multiple frames",
                    source=statement.source,
                )
            framed_items.add(name)


def check(statements: model.Statements) -> dict[str, model.Item]:
    """Validate all statements: no duplicate items, valid connection endpoints, valid frames."""
    items_by_name = _check_items(statements)
    _check_connections(statements, items_by_name)
    _check_frames(statements, items_by_name)
    return items_by_name
