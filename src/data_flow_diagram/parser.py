"""Parse DFD source text in our DSL"""

import os.path
import re
from typing import Callable, Tuple

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
            if point == model.NODE_STAR:
                nb_stars += 1
            if point != model.NODE_STAR:
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
        line = _apply_syntactic_sugars(src_line)
        source.text = line  # fixup text

        word = source.text.split()[0]

        f = _PARSERS.get(word)

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
                _parse_item_external(item, dependencies)
                item.text = item.text or item.name
                # Items are also Drawables, so parse drawable attributes here
                parse_drawable_attrs(item)

            case model.Drawable() as drawable:
                parse_drawable_attrs(drawable)

            case model.Attrib() as attrib:
                attribs[attrib.alias] = attrib

        statements.append(statement)

    if debug:
        for s in statements:
            dprint(model.repr(s))
    return statements, dependencies, attribs


def _split_args(
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


def _parse_item_name(name: str) -> Tuple[str, bool]:
    """If name ends with ?, make it hidable"""
    if name.endswith("?"):
        return name[:-1], True
    else:
        return name, False


def _parse_style(source: model.SourceLine) -> model.Statement:
    """Parse style statement"""
    style, value = _split_args(source.text, 2, True)
    return model.Style(source, style, value)


def _parse_attrib(source: model.SourceLine) -> model.Statement:
    """Parse attrib name text"""
    alias, text = _split_args(source.text, 2, True)
    return model.Attrib(source, alias, text)


RX_FILTER_ARG = re.compile(
    r"""(
      # either a neighbor specification
      (?P<neighbors><>|<|>|\[|])    # direction
      (?P<flags>[a-zA-Z]*)              # flags
      (?: (?P<all>[%s]) | (?P<num>[0-9]+) )  # "all" distance, or decimal number
      |
      # or a replacer specification
      =                             # indicates replacer
      (?P<replacer>.*)              # name if item replacing the others
    )"""
    % re.escape(model.ALL_NEIGHBORS),
    re.X,
)


def _parse_filter(source: model.SourceLine) -> model.Statement:
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


def _make_item_parser(
    keyword: Keyword,
) -> Callable[[model.SourceLine], model.Statement]:
    """Create a parser for an item statement of the given type."""

    def parse(source: model.SourceLine) -> model.Statement:
        name, text = _split_args(source.text, 2, True)
        name, hidable = _parse_item_name(name)
        return model.Item(source, keyword, text, "", name, hidable)

    return parse


def _make_connection_parser(
    keyword: Keyword,
    reversed: bool = False,
    relaxed: bool = False,
    swap: bool = False,
) -> Callable[[model.SourceLine], model.Statement]:
    """Create a parser for a connection statement."""

    def parse(source: model.SourceLine) -> model.Statement:
        src, dst, text = _split_args(source.text, 3, True)
        if swap:
            src, dst = dst, src
        return model.Connection(
            source, keyword, text, "", src, dst, reversed, relaxed
        )

    return parse


def _apply_syntactic_sugars(src_line: str) -> str:

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


def _parse_item_external(
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


def _parse_frame(source: model.SourceLine) -> model.Statement:
    """Parse frame statement"""
    parts = source.text.split("=", maxsplit=1)
    if len(parts) == 1:
        text = ""
    else:
        text = parts[1].strip()

    items = parts[0].split()[1:]
    attrs = "style=dashed"
    return model.Frame(source, Keyword.FRAME, text, attrs, items)


##############################################################################
# Keyword-to-parser dispatch table (module-level, built once)

_PARSERS: dict[str, Callable[[model.SourceLine], model.Statement]] = {
    # Options
    Keyword.STYLE: _parse_style,
    Keyword.ATTRIB: _parse_attrib,
    # Items
    Keyword.PROCESS: _make_item_parser(Keyword.PROCESS),
    Keyword.CONTROL: _make_item_parser(Keyword.CONTROL),
    Keyword.ENTITY: _make_item_parser(Keyword.ENTITY),
    Keyword.STORE: _make_item_parser(Keyword.STORE),
    Keyword.NONE: _make_item_parser(Keyword.NONE),
    Keyword.CHANNEL: _make_item_parser(Keyword.CHANNEL),
    # Connections
    Keyword.FLOW: _make_connection_parser(Keyword.FLOW),
    Keyword.CFLOW: _make_connection_parser(Keyword.CFLOW),
    Keyword.BFLOW: _make_connection_parser(Keyword.BFLOW),
    Keyword.UFLOW: _make_connection_parser(Keyword.UFLOW),
    Keyword.SIGNAL: _make_connection_parser(Keyword.SIGNAL),
    Keyword.CONSTRAINT: _make_connection_parser(Keyword.CONSTRAINT),
    # Connections: reversed
    Keyword.FLOW_REVERSED: _make_connection_parser(Keyword.FLOW, reversed=True),
    Keyword.CFLOW_REVERSED: _make_connection_parser(
        Keyword.CFLOW, reversed=True
    ),
    Keyword.SIGNAL_REVERSED: _make_connection_parser(
        Keyword.SIGNAL, reversed=True
    ),
    Keyword.CONSTRAINT_REVERSED: _make_connection_parser(
        Keyword.CONSTRAINT, swap=True
    ),
    # Connections: relaxed
    Keyword.FLOW_RELAXED: _make_connection_parser(Keyword.FLOW, relaxed=True),
    Keyword.CFLOW_RELAXED: _make_connection_parser(Keyword.CFLOW, relaxed=True),
    Keyword.BFLOW_RELAXED: _make_connection_parser(Keyword.BFLOW, relaxed=True),
    Keyword.UFLOW_RELAXED: _make_connection_parser(Keyword.UFLOW, relaxed=True),
    Keyword.SIGNAL_RELAXED: _make_connection_parser(
        Keyword.SIGNAL, relaxed=True
    ),
    # Connections: reversed + relaxed
    Keyword.FLOW_REVERSED_RELAXED: _make_connection_parser(
        Keyword.FLOW, reversed=True, relaxed=True
    ),
    Keyword.CFLOW_REVERSED_RELAXED: _make_connection_parser(
        Keyword.CFLOW, reversed=True, relaxed=True
    ),
    Keyword.SIGNAL_REVERSED_RELAXED: _make_connection_parser(
        Keyword.SIGNAL, reversed=True, relaxed=True
    ),
    # Frame
    Keyword.FRAME: _parse_frame,
    # Filters
    Keyword.ONLY: _parse_filter,
    Keyword.WITHOUT: _parse_filter,
}
