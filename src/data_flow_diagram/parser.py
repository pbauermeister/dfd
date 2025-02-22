"""Parse DFD source text in our DSL"""

import os.path
import re
from typing import Callable, Tuple

from . import dfd_dot_templates as TMPL
from . import model


def check(statements: model.Statements) -> dict[str, model.Item]:
    """Check that all statement make sense"""

    # collect items
    items_by_name: dict[str, model.Item] = {}
    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Item() as item:
                pass
            case _:
                continue
        name = item.name

        # make sure there are no duplicates
        if name not in items_by_name:
            items_by_name[name] = item
            continue

        other = items_by_name[name]
        other_text = model.pack(other.source.text)
        raise model.DfdException(
            f'{error_prefix}Name "{name}" already exists '
            f'at line {other.source.line_nr+1}: {other_text}'
        )

    # check references and values of connections
    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Connection() as conn:
                pass
            case _:
                continue
        nb_stars = 0
        for point in conn.src, conn.dst:
            if point == "*":
                nb_stars += 1
            if point != "*":
                if point not in items_by_name:
                    raise model.DfdException(
                        f'{error_prefix}Connection "{conn.type}" links to "{point}", '
                        f'which is not defined'
                    )
                if (
                    items_by_name[point].type == model.CONTROL
                    and conn.type != model.SIGNAL
                ):
                    raise model.DfdException(
                        f'{error_prefix}Connection to {model.CONTROL} "{point}" is '
                        f'of type "{conn.type}", however only connections of type '
                        f'"{model.SIGNAL}" are allowed'
                    )

        if nb_stars == 2:
            raise model.DfdException(
                f'{error_prefix}Connection "{conn.type}" may not link to two '
                f'stars'
            )

    # check references of frames
    framed_items: set[str] = set()
    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Frame() as frame:
                pass
            case _:
                continue
        if not frame.items:
            raise model.DfdException(f'{error_prefix}Frame is empty')
        for name in frame.items:
            if name not in items_by_name:
                raise model.DfdException(
                    f'{error_prefix}Frame includes "{name}", '
                    f'which is not defined'
                )
            if name in framed_items:
                raise model.DfdException(
                    f'{error_prefix}Item "{name}", ' f'is in multiple frames'
                )
            framed_items.add(name)

    return items_by_name


def parse(
    source_lines: model.SourceLines,
    debug: bool = False,
) -> tuple[model.Statements, model.GraphDependencies, model.Attribs]:
    """Parse the DFD source text as list of statements"""

    statements: model.Statements = []
    dependencies: model.GraphDependencies = []
    attribs: model.Attribs = {}

    for n, source in enumerate(source_lines):
        src_line = source.text

        src_line = src_line.strip()
        if not src_line or src_line.startswith('#'):
            continue
        error_prefix = model.mk_err_prefix_from(source)

        # syntactic sugars may rewrite the line
        line = apply_syntactic_sugars(src_line)
        source.text = line  # fixup text

        word = source.text.split()[0]

        f = {
            model.STYLE: parse_style,
            model.PROCESS: parse_process,
            model.CONTROL: parse_control,
            model.ENTITY: parse_entity,
            model.STORE: parse_store,
            model.NONE: parse_none,
            model.CHANNEL: parse_channel,
            model.FLOW: parse_flow,
            model.CFLOW: parse_cflow,
            model.BFLOW: parse_bflow,
            model.UFLOW: parse_uflow,
            model.SIGNAL: parse_signal,
            model.FLOW + '?': parse_flow_q,
            model.CFLOW + '?': parse_cflow_q,
            model.BFLOW + '?': parse_bflow_q,
            model.UFLOW + '?': parse_uflow_q,
            model.SIGNAL + '?': parse_signal_q,
            'flow.r': parse_flow_r,
            'cflow.r': parse_cflow_r,
            'signal.r': parse_signal_r,
            'flow.r?': parse_flow_r_q,
            'cflow.r?': parse_cflow_r_q,
            'signal.r?': parse_signal_r_q,
            model.FRAME: parse_frame,
            model.ATTRIB: parse_attrib,
        }.get(word)

        if f is None:
            raise model.DfdException(
                f'{error_prefix}Unrecognized keyword ' f'"{word}"'
            )

        try:
            statement = f(source)
        except model.DfdException as e:
            raise model.DfdException(f'{error_prefix}{e}"')

        match statement:
            case model.Item() as item:
                parse_item_external(item, dependencies)
                item.text = item.text or item.name

        match statement:
            case model.Drawable() as drawable:
                parse_drawable_attrs(drawable)

        match statement:
            case model.Attrib() as attrib:
                attribs[attrib.alias] = attrib

        statements.append(statement)

    if debug:
        for s in statements:
            print(model.repr(s))
    return statements, dependencies, attribs


def split_args(
    dfd_line: str, n: int, last_is_optional: bool = False
) -> list[str]:
    """Split DFD line into n (possibly n-1) tokens"""

    terms: list[str] = dfd_line.split(maxsplit=n)
    if len(terms) - 1 == n - 1 and last_is_optional:
        terms.append('')

    if len(terms) - 1 != n:
        if not last_is_optional:
            raise model.DfdException(f'Expected {n} argument(s)')
        else:
            raise model.DfdException(f'Expected {n-1} or {n} argument')

    return terms[1:]


def parse_item_name(name: str) -> Tuple[str, bool]:
    """If name ends with ?, make it hidable"""
    if name.endswith('?'):
        return name[:-1], True
    else:
        return name, False


def parse_style(source: model.SourceLine) -> model.Statement:
    """Parse style statement"""
    style, value = split_args(source.text, 2, True)
    return model.Style(source, style, value)


def parse_attrib(source: model.SourceLine) -> model.Statement:
    """Parse attrib name text"""
    alias, text = split_args(source.text, 2, True)
    return model.Attrib(source, alias, text)


def parse_process(source: model.SourceLine) -> model.Statement:
    """Parse process statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.PROCESS, text, "", name, hidable)


def parse_control(source: model.SourceLine) -> model.Statement:
    """Parse control statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.CONTROL, text, "", name, hidable)


def parse_entity(source: model.SourceLine) -> model.Statement:
    """Parse entity statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.ENTITY, text, "", name, hidable)


def parse_store(source: model.SourceLine) -> model.Statement:
    """Parse store statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.STORE, text, "", name, hidable)


def parse_none(source: model.SourceLine) -> model.Statement:
    """Parse none statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.NONE, text, "", name, hidable)


def parse_channel(source: model.SourceLine) -> model.Statement:
    """Parse channel statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.CHANNEL, text, "", name, hidable)


def parse_flow(source: model.SourceLine) -> model.Statement:
    """Parse directional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.FLOW, text, "", src, dst)


def parse_flow_r(source: model.SourceLine) -> model.Statement:
    """Parse directional reversed flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.FLOW, text, "", src, dst, True)


def parse_cflow(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.CFLOW, text, "", src, dst)


def parse_cflow_r(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.CFLOW, text, "", src, dst, True)


def parse_bflow(source: model.SourceLine) -> model.Statement:
    """Parse bidirectional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.BFLOW, text, "", src, dst)


def parse_uflow(source: model.SourceLine) -> model.Statement:
    """Parse undirected flow flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.UFLOW, text, "", src, dst)


def parse_signal(source: model.SourceLine) -> model.Statement:
    """Parse signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.SIGNAL, text, "", src, dst)


def parse_signal_r(source: model.SourceLine) -> model.Statement:
    """Parse reversed signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.SIGNAL, text, "", src, dst, True)


def parse_flow_q(source: model.SourceLine) -> model.Statement:
    """Parse directional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.FLOW, text, "", src, dst, relaxed=True
    )


def parse_flow_r_q(source: model.SourceLine) -> model.Statement:
    """Parse directional reversed flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.FLOW, text, "", src, dst, True, relaxed=True
    )


def parse_cflow_q(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.CFLOW, text, "", src, dst, relaxed=True
    )


def parse_cflow_r_q(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.CFLOW, text, "", src, dst, True, relaxed=True
    )


def parse_bflow_q(source: model.SourceLine) -> model.Statement:
    """Parse bidirectional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.BFLOW, text, "", src, dst, relaxed=True
    )


def parse_uflow_q(source: model.SourceLine) -> model.Statement:
    """Parse undirected flow flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.UFLOW, text, "", src, dst, relaxed=True
    )


def parse_signal_q(source: model.SourceLine) -> model.Statement:
    """Parse signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.SIGNAL, text, "", src, dst, relaxed=True
    )


def parse_signal_r_q(source: model.SourceLine) -> model.Statement:
    """Parse reversed signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, model.SIGNAL, text, "", src, dst, True, relaxed=True
    )


def apply_syntactic_sugars(src_line: str) -> str:
    terms = src_line.split()
    if len(terms) < 3:
        return src_line

    op = terms[1]

    def fmt(verb: str, args: list[str], swap: bool = False) -> str:
        array = [verb] + args
        del array[2]  # remove arrow
        if swap:
            array[1], array[2] = array[2], array[1]
        return '\t'.join(array)

    new_line = ''
    if re.fullmatch(r'-+>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('flow' + q, parts)
    elif re.fullmatch(r'<-+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('flow.r' + q, parts)  # , swap=True)

    if re.fullmatch(r'-+>>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('cflow' + q, parts)
    elif re.fullmatch(r'<<-+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('cflow.r' + q, parts)  # , swap=True)

    elif re.fullmatch(r'<-+>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('bflow' + q, parts)

    elif re.fullmatch(r'--+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('uflow' + q, parts)

    elif re.fullmatch(r':+>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('signal' + q, parts)
    elif re.fullmatch(r'<:+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('signal.r' + q, parts)  # , swap=True)

    if new_line:
        return new_line
    else:
        return src_line


def parse_drawable_attrs(drawable: model.Drawable) -> None:
    if drawable.text and drawable.text.startswith('['):
        parts = drawable.text[1:].split(']', 1)
        drawable.attrs = parts[0]
        drawable.text = parts[1].strip()

        match drawable:
            case model.Item() as item:
                item.text = item.text or item.name


def parse_item_external(
    item: model.Item, dependencies: model.GraphDependencies
) -> None:
    parts = item.name.split(':', 1)
    if len(parts) > 1:
        item.attrs = TMPL.ITEM_EXTERNAL_ATTRS
        if parts[-1]:
            item.name = parts[-1]
        else:
            item.name = parts[-2]

        if item.name.startswith('#'):
            item.name = item.name[1:]
        else:
            item.name = os.path.splitext(item.name)[0]

        if not item.text:
            item.text = item.name

        dependency = model.GraphDependency(
            parts[0], parts[1] or None, item.type, item.source
        )
        dependencies.append(dependency)


def parse_frame(source: model.SourceLine) -> model.Statement:
    """Parse frame statement"""
    parts = source.text.split('=', maxsplit=1)
    if len(parts) == 1:
        text = ''
    else:
        text = parts[1].strip()

    items = parts[0].split()[1:]
    type = ''  # so far there is only one type of frame
    attrs = 'style=dashed'
    return model.Frame(source, type, text, attrs, items)
