"""Integration tests: exercise the full pipeline end-to-end.

These tests call main() directly, which drives the complete DFD → DOT → SVG
pipeline including Graphviz.  They require the `dot` binary to be installed.
"""

import io
import subprocess
import sys

import pytest

from data_flow_diagram import main


def test_stdin_to_stdout_produces_svg(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Feed a minimal DFD on stdin; stdout must contain a well-formed SVG
    monkeypatch.setattr(sys, 'stdin', io.StringIO("process P Process"))
    monkeypatch.setattr(sys, 'argv', ['prog'])
    main()
    output = capsys.readouterr().out.strip()
    assert output.startswith(
        '<?xml'
    ), "Output does not begin with XML declaration"
    assert output.endswith('</svg>'), "Output does not end with </svg>"


def test_subprocess_cli_produces_svg() -> None:
    # Invoke the dev wrapper as a subprocess — tests the OS-level entry point
    result = subprocess.run(
        ['./data-flow-diagram'],
        input='process P Process',
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (
        result.returncode == 0
    ), f"CLI exited with {result.returncode}: {result.stderr}"
    output = result.stdout.strip()
    assert output.startswith(
        '<?xml'
    ), "Output does not begin with XML declaration"
    assert output.endswith('</svg>'), "Output does not end with </svg>"
