"""Tracing prelude test.

tools/init-tracing.sh hides the trace lines of its echo/banner/banner2/
step helpers with a DEBUG trap. The trial script uses the helpers in
every context that bit before (after `||` and `&&`, inside `$(...)`, in
a pipeline, in an `if` condition, in a brace group, in a function) and
its merged output must match expected.txt byte for byte.
"""

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRIAL = ROOT / "tests" / "tracing-prelude" / "trial.sh"
EXPECTED = ROOT / "tests" / "tracing-prelude" / "expected.txt"


def test_prelude_trial_output_matches() -> None:
    # run the trial from the repository root, stderr merged into stdout
    result = subprocess.run(
        ["bash", str(TRIAL)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert result.stdout == EXPECTED.read_text()
    assert result.returncode == 3  # the guard's exit code propagates
