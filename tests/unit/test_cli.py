"""Tests for the CLI argument parser (data_flow_diagram.__init__.parse_args)."""

import sys

import pytest

from data_flow_diagram import parse_args

# The full set of argument names the CLI must expose; a mismatch here means
# an arg was added or removed without updating this test.
EXPECTED_ARG_KEYS = {
    'INPUT_FILE',
    'output_file',
    'markdown',
    'format',
    'percent_zoom',
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
