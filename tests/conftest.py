"""Shared pytest fixtures for unit and integration tests.

Only fixtures that are non-trivial or potentially shared across test modules
live here. Small, single-use DFD strings are kept inline in their test files.
"""

import pytest

from data_flow_diagram import model


# ── Markdown fixtures ─────────────────────────────────────────────────────────

# A markdown document containing two data-flow-diagram code blocks (and one
# unrelated ruby block that must be ignored).
MD_WITH_TWO_SNIPPETS = """
Some text
```data-flow-diagram diagram1.svg
body 1
```

Some more text
```
data-flow-diagram diagram2.svg
body 2
```

Yet more text

```ruby
Baby
```
"""

# The two Snippet objects that extract_snippets() should produce from the above.
MD_EXPECTED_SNIPPETS = [
    model.Snippet(
        text='body 1\n', name='diagram1', output='diagram1.svg', line_nr=2
    ),
    model.Snippet(
        text='\nbody 2\n', name='diagram2', output='diagram2.svg', line_nr=7
    ),
]


@pytest.fixture  # type: ignore[misc]
def md_with_two_snippets() -> str:
    """Markdown text containing two DFD snippets and one unrelated code block."""
    return MD_WITH_TWO_SNIPPETS


@pytest.fixture  # type: ignore[misc]
def md_expected_snippets() -> list[model.Snippet]:
    """Expected Snippet objects for md_with_two_snippets."""
    return MD_EXPECTED_SNIPPETS
