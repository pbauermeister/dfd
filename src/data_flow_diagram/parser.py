"""Parse DFD source text in our DSL"""

import re
from typing import Callable, Tuple

from . import model


def check(statements: model.Statements) -> dict[str, model.Item]:
    """Check that all statement make sense"""

    # collect items
    items_by_name: dict[str, model.Item] = {}
    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Item() as item: pass
            case _: continue
        name = item.name

        # make sure there are no duplicates
        if name not in items_by_name:
            items_by_name[name] = item
            continue

        other = items_by_name[name]
        other_text = model.pack(other.source.text)
        raise model.DfdException(
            f'{error_prefix}Name "{name}" already exists '
            f'at line {other.source.line_nr+1}: {other_text}')

    # check references and values
    for statement in statements:
        error_prefix = model.mk_err_prefix_from(statement.source)
        match statement:
            case model.Connection() as conn: pass
            case _: continue
        nb_stars = 0
        for point in conn.src, conn.dst:
            if point == "*":
                nb_stars += 1
            if point == "*" or point in items_by_name:
                continue
            raise model.DfdException(
                f'{error_prefix}Connection "{conn.type}" links to "{point}", '
                f'which is not defined')
        if nb_stars == 2:
            raise model.DfdException(
                f'{error_prefix}Connection "{conn.type}" may not link to two '
                f'stars')

    return items_by_name


def parse(source_lines: model.SourceLines, debug: bool = False,
         ) -> model.Statements:
    """Parse the DFD source text as list of statements"""

    statements: model.Statements = []

    for n, source in enumerate(source_lines):
        src_line = source.text

        src_line = src_line.strip()
        if not src_line or src_line.startswith('#'): continue
        error_prefix = model.mk_err_prefix_from(source)

        # syntactic sugars may rewrite the line
        line = apply_syntactic_sugars(src_line)
        source.text = line  # fixup text

        word = source.text.split()[0]

        f: Callable[[model.SourceLine], model.Statement] = {
            model.STYLE: parse_style,
            model.PROCESS: parse_process,
            model.ENTITY: parse_entity,
            model.STORE: parse_store,
            model.NONE: parse_none,
            model.CHANNEL: parse_channel,

            model.FLOW: parse_flow,
            model.BFLOW: parse_bflow,
            model.UFLOW: parse_uflow,
            model.SIGNAL: parse_signal,

            model.FLOW+'?': parse_flow_q,
            model.BFLOW+'?': parse_bflow_q,
            model.UFLOW+'?': parse_uflow_q,
            model.SIGNAL+'?': parse_signal_q,

            'flow.r': parse_flow_r,
            'signal.r': parse_signal_r,

            'flow.r?': parse_flow_r_q,
            'signal.r?': parse_signal_r_q,

        }.get(word)

        if f is None:
            raise model.DfdException(f'{error_prefix}Unrecognized keyword '
                                     f'"{word}"')

        try:
            statement = f(source)
        except model.DfdException as e:
            raise model.DfdException(f'{error_prefix}{e}"')

        match statement:
            case model.Drawable() as drawable:
                parse_drawable_attrs(drawable)

        statements.append(statement)

    if debug:
        for s in statements: print(model.repr(s))
    return statements


def split_args(dfd_line: str, n: int, last_is_optional: bool=False,
               make_last_from_previous: bool=False) -> list[str]:
    """Split DFD line into n (possibly n-1) tokens"""

    terms = dfd_line.split(maxsplit=n)
    if len(terms)-1 == n-1 and last_is_optional:
        if make_last_from_previous:
            terms.append(terms[-1])
        else:
            terms.append(None)
    if len(terms)-1 != n:
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
    style = split_args(source.text, 1)[0]
    return model.Style(source, style)


def parse_process(source: model.SourceLine) -> model.Statement:
    """Parse process statement"""
    name, text = split_args(source.text, 2, True, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.PROCESS, text, "", name, hidable)


def parse_entity(source: model.SourceLine) -> model.Statement:
    """Parse entity statement"""
    name, text = split_args(source.text, 2, True, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.ENTITY, text, "", name, hidable)


def parse_store(source: model.SourceLine) -> model.Statement:
    """Parse store statement"""
    name, text = split_args(source.text, 2, True, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.STORE, text, "", name, hidable)


def parse_none(source: model.SourceLine) -> model.Statement:
    """Parse none statement"""
    name, text = split_args(source.text, 2, True, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, model.NONE, text, "", name, hidable)


def parse_channel(source: model.SourceLine) -> model.Statement:
    """Parse channel statement"""
    name, text = split_args(source.text, 2, True, True)
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
    return model.Connection(source, model.FLOW, text, "", src, dst,
                            relaxed=True)


def parse_flow_r_q(source: model.SourceLine) -> model.Statement:
    """Parse directional reversed flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.FLOW, text, "", src, dst, True,
                            relaxed=True)


def parse_bflow_q(source: model.SourceLine) -> model.Statement:
    """Parse bidirectional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.BFLOW, text, "", src, dst,
                            relaxed=True)


def parse_uflow_q(source: model.SourceLine) -> model.Statement:
    """Parse undirected flow flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.UFLOW, text, "", src, dst,
                            relaxed=True)


def parse_signal_q(source: model.SourceLine) -> model.Statement:
    """Parse signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.SIGNAL, text, "", src, dst,
                            relaxed=True)


def parse_signal_r_q(source: model.SourceLine) -> model.Statement:
    """Parse reversed signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, model.SIGNAL, text, "", src, dst, True,
                            relaxed=True)


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
        new_line = fmt('flow'+q, parts)
    elif re.fullmatch(r'<-+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('flow.r'+q, parts)#, swap=True)

    elif re.fullmatch(r'<-+>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('bflow'+q, parts)

    elif re.fullmatch(r'--+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('uflow'+q, parts)

    elif re.fullmatch(r':+>[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('signal'+q, parts)
    elif re.fullmatch(r'<:+[?]?', op):
        q = '?' if op.endswith('?') else ''
        parts = src_line.split(maxsplit=3)
        new_line = fmt('signal.r'+q, parts)#, swap=True)

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
