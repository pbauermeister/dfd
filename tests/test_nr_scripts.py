"""NR runner scripts test.

tests/nr-test.sh and tests/nr-regenerate.sh take the fixture directory
from NR_DIR (default tests/non-regression). Each case builds a small
fixture set in a temporary directory and checks the verdict: a stray
.dot next to an error fixture, an error fixture that succeeds and a
plain fixture whose render fails are FAIL lines with the run going on;
a clean set passes; the regenerate script refuses a succeeding error
fixture, and neither script leaves a .dot beside an error fixture.
"""

import os
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "data-flow-diagram"
NR_TEST = ROOT / "tests" / "nr-test.sh"
NR_REGENERATE = ROOT / "tests" / "nr-regenerate.sh"

VALID = "process P\nprocess Q\nP -> Q flow\n"
INVALID = "process P\nX -> Y\n"  # undeclared items: a DfdException


def _run(
    script: pathlib.Path, nr_dir: pathlib.Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(script)],
        cwd=ROOT,
        env={**os.environ, "NR_DIR": str(nr_dir)},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )


def _plain(nr_dir: pathlib.Path, name: str, text: str) -> pathlib.Path:
    """A plain fixture with its golden .dot, as nr-regenerate.sh writes it."""
    dfd = nr_dir / f"{name}.dfd"
    dfd.write_text(text)
    subprocess.run(
        [str(TOOL), str(dfd), "-f", "dot", "-o", str(nr_dir / f"{name}.dot")],
        cwd=ROOT,
        check=True,
    )
    return dfd


def _error(nr_dir: pathlib.Path, name: str, text: str) -> pathlib.Path:
    """An error fixture with its golden .stderr (empty when the text is valid)."""
    dfd = nr_dir / f"{name}.dfd"
    dfd.write_text(text)
    result = subprocess.run(
        [str(TOOL), str(dfd), "-f", "dot", "-o", os.devnull],
        cwd=ROOT,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    (nr_dir / f"{name}.stderr").write_text(result.stderr)
    return dfd


@pytest.fixture
def nr_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """A clean fixture set: one plain fixture, one error fixture."""
    _plain(tmp_path, "002-ok", VALID)
    _error(tmp_path, "001-err-bad", INVALID)
    return tmp_path


def test_clean_set_passes(nr_dir: pathlib.Path) -> None:
    result = _run(NR_TEST, nr_dir)
    assert result.returncode == 0
    assert "FAIL:" not in result.stdout
    assert result.stdout.count("PASS:") == 2


def test_stray_dot_beside_error_fixture_is_a_failure(
    nr_dir: pathlib.Path,
) -> None:
    stray = nr_dir / "001-err-bad.dot"
    stray.touch()
    result = _run(NR_TEST, nr_dir)
    assert result.returncode == 1
    assert f"FAIL: {nr_dir}/001-err-bad.dfd (stray {stray}" in result.stdout
    assert f"PASS: {nr_dir}/002-ok.dfd" in result.stdout  # the run went on


def test_error_fixture_that_succeeds_is_a_failure(nr_dir: pathlib.Path) -> None:
    _error(nr_dir, "001-err-bad", VALID)
    result = _run(NR_TEST, nr_dir)
    assert result.returncode == 1
    assert (
        f"FAIL: {nr_dir}/001-err-bad.dfd (expected to fail but succeeded)"
        in result.stdout
    )
    assert not (nr_dir / "001-err-bad.dot").exists()


def test_regenerate_refuses_error_fixture_that_succeeds(
    nr_dir: pathlib.Path,
) -> None:
    _error(nr_dir, "001-err-bad", VALID)
    result = _run(NR_REGENERATE, nr_dir)
    assert result.returncode == 1
    assert (
        f"ERROR: {nr_dir}/001-err-bad.dfd was expected to fail but succeeded"
        in result.stdout
    )
    assert not (nr_dir / "001-err-bad.dot").exists()


def test_plain_fixture_render_failure_is_a_failure_not_an_abort(
    nr_dir: pathlib.Path,
) -> None:
    bad = nr_dir / "000-bad.dfd"
    bad.write_text(INVALID)
    (nr_dir / "000-bad.dot").touch()
    result = _run(NR_TEST, nr_dir)
    assert result.returncode == 1
    fail = result.stdout.index(f"FAIL: {bad} (render failed)")
    assert (
        result.stdout.index(f"PASS: {nr_dir}/002-ok.dfd") > fail
    )  # the run went on
    assert not list(nr_dir.glob("*.tmp*"))
