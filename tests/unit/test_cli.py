"""Tests for the CLI argument parser and entry points."""

import importlib
import io
import sys

import pytest

from data_flow_diagram import main, parse_args

# The full set of argument names the CLI must expose; a mismatch here means
# an arg was added or removed without updating this test.
EXPECTED_ARG_KEYS = {
    'INPUT_FILE',
    'output_file',
    'markdown',
    'format',
    'background_color',
    'no_graph_title',
    'no_check_dependencies',
    'debug',
    'version',
}


def test_parse_args_exposes_expected_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simulate calling the CLI with a single positional argument
    monkeypatch.setattr(sys, 'argv', ['prog', 'my-file'])
    args = parse_args()
    assert set(args.__dict__.keys()) == EXPECTED_ARG_KEYS


def test_parse_args_positional_input_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The positional INPUT_FILE argument must be captured verbatim
    monkeypatch.setattr(sys, 'argv', ['prog', 'my-file'])
    args = parse_args()
    assert args.INPUT_FILE == 'my-file'


def test_console_scripts_entry_point_resolves() -> None:
    # Verify that the entry point string "data_flow_diagram:main" from
    # setup.py resolves to the expected callable.  Uses importlib directly
    # so the test works without the package being pip-installed.
    ENTRY_POINT = 'data_flow_diagram:main'
    module_name, attr_name = ENTRY_POINT.split(':')
    module = importlib.import_module(module_name)
    resolved = getattr(module, attr_name)
    assert callable(resolved)
    assert resolved is main


def test_version_flag_prints_version_and_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, 'argv', ['prog', '--version'])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert output.startswith('data-flow-diagram ')


def test_help_text_contains_dfd_not_uml(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, 'argv', ['prog', '--help'])
    with pytest.raises(SystemExit) as exc_info:
        parse_args()
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert 'DFD input file' in output
    assert 'UML sequence' not in output


# ── Graphviz is needed only to render a non-DOT format (#84) ─────────────────


def test_version_works_without_graphviz(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv('PATH', '')
    monkeypatch.setattr(sys, 'argv', ['prog', '--version'])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.startswith('data-flow-diagram ')


def test_dot_format_works_without_graphviz(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv('PATH', '')
    monkeypatch.setattr(sys, 'stdin', io.StringIO("process P Process"))
    monkeypatch.setattr(sys, 'argv', ['prog', '-f', 'dot'])
    main()
    output = capsys.readouterr().out.strip()
    assert output.startswith('digraph')
    assert 'Process' in output


def test_rendering_without_graphviz_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv('PATH', '')
    monkeypatch.setattr(sys, 'stdin', io.StringIO("process P Process"))
    monkeypatch.setattr(sys, 'argv', ['prog', '-f', 'svg'])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2
    assert '"Graphviz" seems not installed' in capsys.readouterr().err
