"""Documentation sync tests.

The style option tables in doc/README.md and doc/SYNTAX.md are generated
from the GraphOptions declarations (see tools/gen-style-tables.py). These
tests fail when the docs drift from the code; run `make readme` to refresh.
"""

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "tools" / "gen-style-tables.py"


def extract_auto_section(text: str, name: str) -> str:
    """Return the content between <!-- AUTO:name --> markers, stripped."""
    open_marker = f"<!-- AUTO:{name} -->"
    close_marker = f"<!-- /AUTO:{name} -->"
    start = text.index(open_marker) + len(open_marker)
    end = text.index(close_marker)
    return text[start:end].strip()


@pytest.mark.parametrize(
    "doc, table",
    [
        pytest.param("doc/README.md", "readme", id="readme"),
        pytest.param("doc/SYNTAX.md", "syntax", id="syntax"),
    ],
)
def test_style_table_in_sync(doc: str, table: str) -> None:
    # regenerate the table and compare with the committed doc section
    result = subprocess.run(
        [sys.executable, str(GENERATOR), table],
        check=True,
        capture_output=True,
        text=True,
    )
    expected = result.stdout.strip()
    actual = extract_auto_section((ROOT / doc).read_text(), "style-table")
    assert actual == expected, f"{doc} style table is stale: run 'make readme'"
