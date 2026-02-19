"""Tests for the CLI argument parser and entry points."""

import sys
from importlib.metadata import entry_points

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
    # The setup.py console_scripts entry point must resolve to a callable
    eps = entry_points(group='console_scripts', name='data-flow-diagram')
    assert len(list(eps)) == 1, "Expected exactly one console_scripts entry"
    ep = list(eps)[0]
    resolved = ep.load()
    assert (
        resolved is main
    ), f"Entry point resolved to {resolved!r}, expected main()"


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
