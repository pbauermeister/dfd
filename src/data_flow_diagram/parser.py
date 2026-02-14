"""Parse DFD source text in our DSL"""

import os.path
import re
from typing import Tuple

from . import dfd_dot_templates as TMPL
from . import model
from .model import Keyword
from .console import dprint


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
            f"at line {other.source.line_nr+1}: {other_text}"
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
                        f"which is not defined"
                    )
                if (
                    items_by_name[point].type == Keyword.CONTROL
                    and conn.type != Keyword.SIGNAL
                ):
                    raise model.DfdException(
                        f'{error_prefix}Connection to {Keyword.CONTROL} "{point}" is '
                        f'of type "{conn.type}", however only connections of type '
                        f'"{Keyword.SIGNAL}" are allowed'
                    )

        if nb_stars == 2:
            raise model.DfdException(
                f'{error_prefix}Connection "{conn.type}" may not link to two '
                f"stars"
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
            raise model.DfdException(f"{error_prefix}Frame is empty")
        for name in frame.items:
            if name not in items_by_name:
                raise model.DfdException(
                    f'{error_prefix}Frame includes "{name}", '
                    f"which is not defined"
                )
            if name in framed_items:
                raise model.DfdException(
                    f'{error_prefix}Item "{name}", ' f"is in multiple frames"
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
        if not src_line or src_line.startswith("#"):
            continue
        error_prefix = model.mk_err_prefix_from(source)

        # syntactic sugars may rewrite the line
        line = apply_syntactic_sugars(src_line)
        source.text = line  # fixup text

        word = source.text.split()[0]

        f = {
            Keyword.STYLE: parse_style,
            Keyword.PROCESS: parse_process,
            Keyword.CONTROL: parse_control,
            Keyword.ENTITY: parse_entity,
            Keyword.STORE: parse_store,
            Keyword.NONE: parse_none,
            Keyword.CHANNEL: parse_channel,
            Keyword.FLOW: parse_flow,
            Keyword.CFLOW: parse_cflow,
            Keyword.BFLOW: parse_bflow,
            Keyword.UFLOW: parse_uflow,
            Keyword.SIGNAL: parse_signal,
            Keyword.FLOW_RELAXED: parse_flow_q,
            Keyword.CFLOW_RELAXED: parse_cflow_q,
            Keyword.BFLOW_RELAXED: parse_bflow_q,
            Keyword.UFLOW_RELAXED: parse_uflow_q,
            Keyword.SIGNAL_RELAXED: parse_signal_q,
            Keyword.FLOW_REVERSED: parse_flow_r,
            Keyword.CFLOW_REVERSED: parse_cflow_r,
            Keyword.SIGNAL_REVERSED: parse_signal_r,
            Keyword.FLOW_REVERSED_RELAXED: parse_flow_r_q,
            Keyword.CFLOW_REVERSED_RELAXED: parse_cflow_r_q,
            Keyword.SIGNAL_REVERSED_RELAXED: parse_signal_r_q,
            Keyword.CONSTRAINT: parse_constraint,
            Keyword.CONSTRAINT_REVERSED: parse_constraint_r,
            Keyword.FRAME: parse_frame,
            Keyword.ATTRIB: parse_attrib,
            Keyword.ONLY: parse_filter,
            Keyword.WITHOUT: parse_filter,
        }.get(Keyword(word))

        if f is None:
            raise model.DfdException(
                f"{error_prefix}Unrecognized keyword " f'"{word}"'
            )

        try:
            statement = f(source)
        except model.DfdException as e:
            raise model.DfdException(f'{error_prefix}{e}')

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
            dprint(model.repr(s))
    return statements, dependencies, attribs


def split_args(
    dfd_line: str, n: int, last_is_optional: bool = False
) -> list[str]:
    """Split DFD line into n (possibly n-1) tokens"""

    terms: list[str] = dfd_line.split(maxsplit=n)
    if len(terms) - 1 == n - 1 and last_is_optional:
        terms.append("")

    if len(terms) - 1 != n:
        if not last_is_optional:
            raise model.DfdException(f"Expected {n} argument(s)")
        else:
            raise model.DfdException(f"Expected {n-1} or {n} argument")

    return terms[1:]


def parse_item_name(name: str) -> Tuple[str, bool]:
    """If name ends with ?, make it hidable"""
    if name.endswith("?"):
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


RX_FILTER_ARG = re.compile(
    r"""(
      # either a neighbor specification
      (?P<neighbors><>|<|>|\[|])    # direction
      (?P<flags>[a-zA-Z]*)              # flags
      (?: (?P<all>[*]) | (?P<num>[0-9]+) )  # "*" for all, or decimal number
      |
      # or a replacer specification
      =                             # indicates replacer
      (?P<replacer>.*)              # name if item replacing the others
    )""",
    re.X,
)


def parse_filter(source: model.SourceLine) -> model.Statement:
    """Parse !/~[NEIGHBOURS] NAME[S]"""
    terms: list[str] = source.text.split()
    if len(terms) < 2:
        raise model.DfdException(f"One or more arguments are expected")

    f = model.Filter(
        source,
        names=[],
        neighbors_up=model.FilterNeighbors(0, False, False, False),
        neighbors_down=model.FilterNeighbors(0, False, False, False),
    )

    cmd = terms[0]
    args = terms[1:]
    replacer = ""

    # first arguments may be +N or -N, which specify the number of down/up neighbors to include in the filter
    while args:
        arg = args[0]

        match = RX_FILTER_ARG.fullmatch(arg)
        if not match:
            break  # no neighbor/replacer specification

        if match.group("replacer"):
            if cmd != Keyword.WITHOUT:
                raise model.DfdException(
                    f"Replacer specification is only allowed for {Keyword.WITHOUT} filter"
                )
            replacer = arg[1:]
            args = args[1:]
        elif match.group("neighbors"):
            fn = model.FilterNeighbors(0, False, False, False)
            is_up = is_down = False

            match match.group("neighbors"):
                case "<>":
                    is_up = is_down = True
                case "<":
                    is_up = True
                case ">":
                    is_down = True
                case "[":
                    is_up = True
                    fn.layout_dir = True
                case "]":
                    is_down = True
                    fn.layout_dir = True

            for flag in match.group("flags"):
                match flag:
                    case "x":
                        fn.no_anchors = True
                    case "f":
                        fn.no_frames = True
                    case _:
                        raise model.DfdException(
                            f"Unrecognized filter flag: {flag}"
                        )
            if match.group("all"):
                fn.distance = -1  # special value for "all neighbors"
            elif match.group("num"):
                fn.distance = int(match.group("num"))
            else:
                raise model.DfdException(
                    f"Neighborhood size must be an integer or '*', not: {arg}"
                )

            if is_up:
                f.neighbors_up = fn
            if is_down:
                f.neighbors_down = fn

            # ready for next argument
            args = args[1:]

    if len(args) == 0:
        raise model.DfdException(f"One or more names are expected")

    f.names = args

    res: model.Statement
    if cmd == Keyword.ONLY:
        res = model.Only(**f.__dict__)
    else:  # cmd == Keyword.WITHOUT:
        res = model.Without(
            **f.__dict__, replaced_by=replacer
        )  # replaced_by is set later by the caller
    return res


def parse_process(source: model.SourceLine) -> model.Statement:
    """Parse process statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.PROCESS, text, "", name, hidable)


def parse_control(source: model.SourceLine) -> model.Statement:
    """Parse control statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.CONTROL, text, "", name, hidable)


def parse_entity(source: model.SourceLine) -> model.Statement:
    """Parse entity statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.ENTITY, text, "", name, hidable)


def parse_store(source: model.SourceLine) -> model.Statement:
    """Parse store statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.STORE, text, "", name, hidable)


def parse_none(source: model.SourceLine) -> model.Statement:
    """Parse none statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.NONE, text, "", name, hidable)


def parse_channel(source: model.SourceLine) -> model.Statement:
    """Parse channel statement"""
    name, text = split_args(source.text, 2, True)
    name, hidable = parse_item_name(name)
    return model.Item(source, Keyword.CHANNEL, text, "", name, hidable)


def parse_flow(source: model.SourceLine) -> model.Statement:
    """Parse directional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.FLOW, text, "", src, dst)


def parse_flow_r(source: model.SourceLine) -> model.Statement:
    """Parse directional reversed flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.FLOW, text, "", src, dst, True)


def parse_cflow(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.CFLOW, text, "", src, dst)


def parse_cflow_r(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.CFLOW, text, "", src, dst, True)


def parse_bflow(source: model.SourceLine) -> model.Statement:
    """Parse bidirectional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.BFLOW, text, "", src, dst)


def parse_uflow(source: model.SourceLine) -> model.Statement:
    """Parse undirected flow flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.UFLOW, text, "", src, dst)


def parse_signal(source: model.SourceLine) -> model.Statement:
    """Parse signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.SIGNAL, text, "", src, dst)


def parse_signal_r(source: model.SourceLine) -> model.Statement:
    """Parse reversed signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.SIGNAL, text, "", src, dst, True)


def parse_flow_q(source: model.SourceLine) -> model.Statement:
    """Parse directional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.FLOW, text, "", src, dst, relaxed=True
    )


def parse_flow_r_q(source: model.SourceLine) -> model.Statement:
    """Parse directional reversed flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.FLOW, text, "", src, dst, True, relaxed=True
    )


def parse_cflow_q(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.CFLOW, text, "", src, dst, relaxed=True
    )


def parse_cflow_r_q(source: model.SourceLine) -> model.Statement:
    """Parse continuous flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.CFLOW, text, "", src, dst, True, relaxed=True
    )


def parse_bflow_q(source: model.SourceLine) -> model.Statement:
    """Parse bidirectional flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.BFLOW, text, "", src, dst, relaxed=True
    )


def parse_uflow_q(source: model.SourceLine) -> model.Statement:
    """Parse undirected flow flow statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.UFLOW, text, "", src, dst, relaxed=True
    )


def parse_signal_q(source: model.SourceLine) -> model.Statement:
    """Parse signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.SIGNAL, text, "", src, dst, relaxed=True
    )


def parse_signal_r_q(source: model.SourceLine) -> model.Statement:
    """Parse reversed signal statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(
        source, Keyword.SIGNAL, text, "", src, dst, True, relaxed=True
    )


def parse_constraint(source: model.SourceLine) -> model.Statement:
    """Parse constraint statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.CONSTRAINT, text, "", src, dst)


def parse_constraint_r(source: model.SourceLine) -> model.Statement:
    """Parse reversed constraint statement"""
    src, dst, text = split_args(source.text, 3, True)
    return model.Connection(source, Keyword.CONSTRAINT, text, "", dst, src)


def apply_syntactic_sugars(src_line: str) -> str:

    # allow arguments to be sticked to the filter mnemonics
    if src_line and src_line[0] in (Keyword.ONLY, Keyword.WITHOUT):
        if len(src_line) > 1 and src_line[1] != " ":
            # insert a space after the filter, so that it is recognized as a filter
            new_line = src_line[0] + " " + src_line[1:]
            return new_line

    # others syntactic sugars apply on 3 or more terms
    terms = src_line.split()
    if len(terms) < 3:
        return src_line

    op = terms[1]

    def _fmt(verb: str, args: list[str]) -> str:
        array = [verb] + args
        del array[2]  # remove arrow
        return "\t".join(array)

    new_line = ""

    def _resolve(keyword: str, relaxed_keyword: str | None = None) -> str:
        parts = src_line.split(maxsplit=3)
        if relaxed_keyword is not None and op.endswith("?"):
            return _fmt(relaxed_keyword, parts)
        return _fmt(keyword, parts)

    if re.fullmatch(r"-+>[?]?", op):
        new_line = _resolve(Keyword.FLOW, Keyword.FLOW_RELAXED)

    elif re.fullmatch(r"<-+[?]?", op):
        new_line = _resolve(
            Keyword.FLOW_REVERSED, Keyword.FLOW_REVERSED_RELAXED
        )

    if re.fullmatch(r"-+>>[?]?", op):
        new_line = _resolve(Keyword.CFLOW, Keyword.CFLOW_RELAXED)
    elif re.fullmatch(r"<<-+[?]?", op):
        new_line = _resolve(
            Keyword.CFLOW_REVERSED, Keyword.CFLOW_REVERSED_RELAXED
        )

    elif re.fullmatch(r"<-+>[?]?", op):
        new_line = _resolve(Keyword.BFLOW, Keyword.BFLOW_RELAXED)

    elif re.fullmatch(r"--+[?]?", op):
        new_line = _resolve(Keyword.UFLOW, Keyword.UFLOW_RELAXED)

    elif re.fullmatch(r":+>[?]?", op):
        new_line = _resolve(Keyword.SIGNAL, Keyword.SIGNAL_RELAXED)
    elif re.fullmatch(r"<:+[?]?", op):
        new_line = _resolve(
            Keyword.SIGNAL_REVERSED, Keyword.SIGNAL_REVERSED_RELAXED
        )

    elif re.fullmatch(r">+", op):
        new_line = _resolve(Keyword.CONSTRAINT)
    elif re.fullmatch(r"<+", op):
        new_line = _resolve(Keyword.CONSTRAINT_REVERSED)

    if new_line:
        return new_line
    else:
        return src_line


def parse_drawable_attrs(drawable: model.Drawable) -> None:
    if drawable.text and drawable.text.startswith("["):
        parts = drawable.text[1:].split("]", 1)
        drawable.attrs = parts[0]
        drawable.text = parts[1].strip()

        match drawable:
            case model.Item() as item:
                item.text = item.text or item.name


def parse_item_external(
    item: model.Item, dependencies: model.GraphDependencies
) -> None:
    parts = item.name.split(":", 1)
    if len(parts) > 1:
        item.attrs = TMPL.ITEM_EXTERNAL_ATTRS
        if parts[-1]:
            item.name = parts[-1]
        else:
            item.name = parts[-2]

        if item.name.startswith("#"):
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
    parts = source.text.split("=", maxsplit=1)
    if len(parts) == 1:
        text = ""
    else:
        text = parts[1].strip()

    items = parts[0].split()[1:]
    type = ""  # so far there is only one type of frame
    attrs = "style=dashed"
    return model.Frame(source, type, text, attrs, items)
