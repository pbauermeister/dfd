"""Tests for the pipeline stages in isolation.

These tests exercise each stage of the DFD pipeline with programmatically
constructed inputs, verifying that:

- build() returns well-formed DOT text without any file I/O
- handle_options() extracts style statements into GraphOptions
- remove_unused_hidables() drops unconnected conditional items
- generate_dot() produces correct DOT fragments from model objects
- handle_filters() keeps/removes items on the happy path
- dependency_checker.check() validates dependencies via file_texts dict
"""

import pytest

from data_flow_diagram import dfd, exception, model
from data_flow_diagram.dsl import (
    checker,
    dependency_checker,
    filters,
    parser,
    scanner,
)
from data_flow_diagram.rendering.dot import Generator, generate_dot


# ── helpers ──────────────────────────────────────────────────────────────────


def _src(text: str = "", line_nr: int = 0) -> model.SourceLine:
    """Create a minimal SourceLine for testing."""
    return model.SourceLine(
        text=text, raw_text=text, parent=None, line_nr=line_nr
    )


def _parse(dfd_text: str) -> model.Statements:
    """Scan, parse, and check a DFD snippet, returning its statements."""
    tokens = scanner.scan(None, dfd_text)
    statements, _, _ = parser.parse(tokens)
    checker.check(statements)
    return statements


def _default_options(**overrides: object) -> model.Options:
    """Create Options with sensible defaults for testing."""
    defaults = dict(
        format="dot",
        background_color=None,
        no_graph_title=False,
        no_check_dependencies=True,
        debug=False,
    )
    defaults.update(overrides)
    return model.Options(**defaults)  # type: ignore[arg-type]


# ── build() ──────────────────────────────────────────────────────────────────


class TestBuild:
    def test_returns_dot_text(self) -> None:
        # build() must return a string containing valid DOT preamble
        provenance = _src("<test>")
        options = _default_options()
        dot_text, graph_options = dfd.build(
            provenance, "process P Process", "TestTitle", options
        )
        assert "digraph" in dot_text
        assert '"P"' in dot_text

    def test_title_appears_in_output(self) -> None:
        provenance = _src("<test>")
        options = _default_options()
        dot_text, _ = dfd.build(
            provenance, "process P Process", "My Diagram", options
        )
        assert "My Diagram" in dot_text

    def test_no_graph_title_blanks_title(self) -> None:
        provenance = _src("<test>")
        options = _default_options(no_graph_title=True)
        dot_text, _ = dfd.build(
            provenance, "process P Process", "ShouldNotAppear", options
        )
        assert "ShouldNotAppear" not in dot_text

    def test_empty_title(self) -> None:
        # Empty title (e.g. stdout output) should not crash
        provenance = _src("<test>")
        options = _default_options()
        dot_text, _ = dfd.build(provenance, "process P Process", "", options)
        assert "digraph" in dot_text

    def test_background_color_from_options(self) -> None:
        provenance = _src("<test>")
        options = _default_options(background_color="red")
        dot_text, _ = dfd.build(provenance, "process P Process", "", options)
        assert "bgcolor=red" in dot_text

    def test_multiple_items_and_connections(self) -> None:
        dfd_src = "process P proc\n" "entity E ent\n" "P --> E data\n"
        provenance = _src("<test>")
        options = _default_options()
        dot_text, _ = dfd.build(provenance, dfd_src, "Test", options)
        assert '"P"' in dot_text
        assert '"E"' in dot_text
        assert '"P" -> "E"' in dot_text


# ── handle_options() ─────────────────────────────────────────────────────────


class TestHandleOptions:
    def test_vertical_style(self) -> None:
        statements = _parse("style vertical\nprocess P proc")
        remaining, opts = dfd.handle_options(statements)
        assert opts.is_vertical is True
        # style statement should be consumed (not in remaining)
        assert all(not isinstance(s, model.Style) for s in remaining)

    def test_horizontal_style(self) -> None:
        statements = _parse("style horizontal\nprocess P proc")
        _, opts = dfd.handle_options(statements)
        assert opts.is_vertical is False

    def test_context_style(self) -> None:
        statements = _parse("style context\nprocess P proc")
        _, opts = dfd.handle_options(statements)
        assert opts.is_context is True

    def test_background_color_style(self) -> None:
        statements = _parse("style background-color #ff0000\nprocess P proc")
        _, opts = dfd.handle_options(statements)
        assert opts.background_color == "#ff0000"

    def test_no_graph_title_style(self) -> None:
        statements = _parse("style no-graph-title\nprocess P proc")
        _, opts = dfd.handle_options(statements)
        assert opts.no_graph_title is True

    def test_item_text_width(self) -> None:
        statements = _parse("style item-text-width 20\nprocess P proc")
        _, opts = dfd.handle_options(statements)
        assert opts.item_text_width == 20

    def test_non_style_statements_preserved(self) -> None:
        statements = _parse("style vertical\nprocess P proc\nentity E ent")
        remaining, _ = dfd.handle_options(statements)
        names = [s.name for s in remaining if isinstance(s, model.Item)]
        assert names == ["P", "E"]


# ── remove_unused_hidables() ─────────────────────────────────────────────────


class TestRemoveUnusedHidables:
    def test_removes_unconnected_hidable(self) -> None:
        src = _src()
        statements: model.Statements = [
            model.Item(
                source=src,
                type=model.Keyword.PROCESS,
                text="proc",
                attrs="",
                name="P",
                hidable=True,
            ),
            model.Item(
                source=src,
                type=model.Keyword.ENTITY,
                text="ent",
                attrs="",
                name="E",
                hidable=False,
            ),
        ]
        result = dfd.remove_unused_hidables(statements)
        names = [s.name for s in result if isinstance(s, model.Item)]
        # P is hidable and has no connections, so it should be removed
        assert names == ["E"]

    def test_keeps_connected_hidable(self) -> None:
        src = _src()
        statements: model.Statements = [
            model.Item(
                source=src,
                type=model.Keyword.PROCESS,
                text="proc",
                attrs="",
                name="P",
                hidable=True,
            ),
            model.Item(
                source=src,
                type=model.Keyword.ENTITY,
                text="ent",
                attrs="",
                name="E",
                hidable=False,
            ),
            model.Connection(
                source=src,
                type=model.Keyword.FLOW,
                text="data",
                attrs="",
                src="P",
                dst="E",
            ),
        ]
        result = dfd.remove_unused_hidables(statements)
        names = [s.name for s in result if isinstance(s, model.Item)]
        assert names == ["P", "E"]

    def test_keeps_non_hidable_without_connections(self) -> None:
        src = _src()
        statements: model.Statements = [
            model.Item(
                source=src,
                type=model.Keyword.PROCESS,
                text="proc",
                attrs="",
                name="P",
                hidable=False,
            ),
        ]
        result = dfd.remove_unused_hidables(statements)
        assert len(result) == 1


# ── generate_dot() ───────────────────────────────────────────────────────────


class TestGenerateDot:
    def test_single_item(self) -> None:
        src = _src()
        graph_options = model.GraphOptions()
        gen = Generator(graph_options, {})
        statements: model.Statements = [
            model.Item(
                source=src,
                type=model.Keyword.PROCESS,
                text="My Process",
                attrs="",
                name="P",
                hidable=False,
            ),
        ]
        items_by_name = {"P": statements[0]}
        dot = generate_dot(
            gen, "Title", None, statements, items_by_name  # type: ignore[arg-type]
        )
        assert "digraph" in dot
        assert '"P"' in dot
        assert "My Process" in dot

    def test_connection_produces_edge(self) -> None:
        src = _src()
        graph_options = model.GraphOptions()
        gen = Generator(graph_options, {})
        item_p = model.Item(
            source=src,
            type=model.Keyword.PROCESS,
            text="proc",
            attrs="",
            name="P",
            hidable=False,
        )
        item_e = model.Item(
            source=src,
            type=model.Keyword.ENTITY,
            text="ent",
            attrs="",
            name="E",
            hidable=False,
        )
        conn = model.Connection(
            source=src,
            type=model.Keyword.FLOW,
            text="data",
            attrs="",
            src="P",
            dst="E",
        )
        statements: model.Statements = [item_p, item_e, conn]
        items_by_name = {"P": item_p, "E": item_e}
        dot = generate_dot(gen, "", None, statements, items_by_name)
        assert '"P" -> "E"' in dot

    def test_frame_produces_subgraph(self) -> None:
        src = _src()
        graph_options = model.GraphOptions()
        gen = Generator(graph_options, {})
        item_p = model.Item(
            source=src,
            type=model.Keyword.PROCESS,
            text="proc",
            attrs="",
            name="P",
            hidable=False,
        )
        frame = model.Frame(
            source=src,
            type=model.Keyword.FRAME,
            text="My Frame",
            attrs="",
            items=["P"],
        )
        statements: model.Statements = [item_p, frame]
        items_by_name = {"P": item_p}
        dot = generate_dot(gen, "", None, statements, items_by_name)
        assert "subgraph cluster_" in dot
        assert "My Frame" in dot


# ── handle_filters() happy path ──────────────────────────────────────────────


class TestHandleFilters:
    def test_only_keeps_named_items(self) -> None:
        statements = _parse(
            "process A aaa\nprocess B bbb\nprocess C ccc\n! A B"
        )
        result = filters.handle_filters(statements)
        names = [s.name for s in result if isinstance(s, model.Item)]
        assert "A" in names
        assert "B" in names
        assert "C" not in names

    def test_without_removes_named_items(self) -> None:
        statements = _parse("process A aaa\nprocess B bbb\nprocess C ccc\n~ B")
        result = filters.handle_filters(statements)
        names = [s.name for s in result if isinstance(s, model.Item)]
        assert "A" in names
        assert "C" in names
        assert "B" not in names

    def test_no_filters_keeps_all(self) -> None:
        statements = _parse("process A aaa\nprocess B bbb")
        result = filters.handle_filters(statements)
        names = [s.name for s in result if isinstance(s, model.Item)]
        assert names == ["A", "B"]


# ── dependency_checker.check() with file_texts ──────────────────────────────


class TestDependencyChecker:
    def test_valid_dependency(self) -> None:
        # Dependency to a file containing the expected item should pass
        source = _src("depends-on other.dfd P process")
        dep = model.GraphDependency(
            to_graph="other.dfd",
            to_item="P",
            to_type=model.Keyword.PROCESS,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts = {"other.dfd": "process P proc"}
        # should not raise
        dependency_checker.check([dep], None, options, file_texts=file_texts)

    def test_missing_file(self) -> None:
        # Dependency to a file not in file_texts should raise
        source = _src("depends-on missing.dfd P process")
        dep = model.GraphDependency(
            to_graph="missing.dfd",
            to_item="P",
            to_type=model.Keyword.PROCESS,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts: dict[str, str] = {}
        with pytest.raises(exception.DfdException, match="No such file"):
            dependency_checker.check(
                [dep], None, options, file_texts=file_texts
            )

    def test_wrong_item_type(self) -> None:
        # Referring to an item with the wrong type should raise
        source = _src("depends-on other.dfd P entity")
        dep = model.GraphDependency(
            to_graph="other.dfd",
            to_item="P",
            to_type=model.Keyword.ENTITY,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts = {"other.dfd": "process P proc"}
        with pytest.raises(exception.DfdException, match="type"):
            dependency_checker.check(
                [dep], None, options, file_texts=file_texts
            )

    def test_unknown_item_name(self) -> None:
        # Referring to an item that doesn't exist in the target should raise
        source = _src("depends-on other.dfd X process")
        dep = model.GraphDependency(
            to_graph="other.dfd",
            to_item="X",
            to_type=model.Keyword.PROCESS,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts = {"other.dfd": "process P proc"}
        with pytest.raises(exception.DfdException, match="unknown item"):
            dependency_checker.check(
                [dep], None, options, file_texts=file_texts
            )

    def test_whole_graph_with_none_type(self) -> None:
        # Whole-graph dependency (to_item=None) with type "none" should pass
        source = _src("depends-on other.dfd none")
        dep = model.GraphDependency(
            to_graph="other.dfd",
            to_item=None,
            to_type=model.Keyword.NONE,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts = {"other.dfd": "process P proc"}
        dependency_checker.check([dep], None, options, file_texts=file_texts)

    def test_whole_graph_wrong_type(self) -> None:
        # Whole-graph dependency with non-"none" type should raise
        source = _src("depends-on other.dfd process")
        dep = model.GraphDependency(
            to_graph="other.dfd",
            to_item=None,
            to_type=model.Keyword.PROCESS,
            source=source,
        )
        options = _default_options(no_check_dependencies=False)
        file_texts = {"other.dfd": "process P proc"}
        with pytest.raises(exception.DfdException, match="none"):
            dependency_checker.check(
                [dep], None, options, file_texts=file_texts
            )
