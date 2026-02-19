# 045 — Define module boundaries and move code

**Date:** 2026-02-19

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/45

## Requirement

Restructure the `data_flow_diagram` package into `dsl/` and `rendering/`
sub-packages following the target layout defined in `doc/CONVENTIONS.md`,
reducing `dfd.py` from ~714 lines to a thin pipeline orchestrator.

This is task F in the sequenced refactoring strategy (#34). It depends on
tasks A (NR tests), B (constants), C (CLI entry point), and D (error
handling) being complete.

## Design

### Current state (post-B/C/D)

```
src/data_flow_diagram/          lines
    __init__.py                    12   re-exports main()
    cli.py                        212   CLI (task C)
    config.py                       4   defaults (task B)
    console.py                     31   debug/error output
    dfd.py                        714   ← the big one
    dfd_dot_templates.py          107   DOT templates
    dependency_checker.py          89   dependency validation
    dot.py                         37   Graphviz invocation
    exception.py                   67   DfdException (task D)
    markdown.py                    78   markdown extraction
    model.py                      251   data types, enums
    parser.py                     523   DSL parsing
    scanner.py                    110   DSL preprocessing
                                -----
                                 2235
```

### Target state

```
src/data_flow_diagram/          lines (approx.)
    __init__.py                    12   unchanged
    cli.py                        212   unchanged
    config.py                       4   unchanged
    console.py                     31   unchanged
    exception.py                   67   unchanged
    markdown.py                    78   unchanged
    model.py                      251   unchanged
    dfd.py                       ~125   orchestrator only
    dsl/
        __init__.py                 1   empty (package marker)
        scanner.py                110   ← from scanner.py
        parser.py                 523   ← from parser.py
        filters.py               ~272   ← extracted from dfd.py
        checker.py                 89   ← from dependency_checker.py
    rendering/
        __init__.py                 1   empty (package marker)
        dot.py                   ~302   ← extracted from dfd.py
        templates.py              107   ← from dfd_dot_templates.py
        graphviz.py                37   ← from dot.py
```

### What stays in dfd.py

The orchestrator retains three functions (~125 lines total):

- **`build()`** (~43 lines) — the pipeline: scan → parse → check →
  filter → options → generate → output.
- **`handle_options()`** (~48 lines) — extracts `Style` statements into
  `GraphOptions`. This is a simple statement→options transformation that
  sits between parsing and rendering, natural for the orchestrator.
- **`remove_unused_hidables()`** (~23 lines) — drops conditional items
  with no connections. Same rationale: a lightweight pipeline step.

### What moves to rendering/dot.py

- **`Generator` class** (~268 lines) — all DOT code generation methods:
  `generate_item()`, `generate_connection()`, `generate_frame()`,
  `generate_star()`, `generate_style()`, `generate_dot_text()`, plus
  private helpers (`_attrib_to_dict`, `_item_to_html_dict`,
  `_compile_attribs_names`, `_expand_attribs`).
- **`generate_dot()`** (~29 lines) — iterates statements, dispatches to
  Generator methods, calls `generate_dot_text()`.
- **`wrap()`** (~5 lines) — text wrapping utility used by Generator.

### What moves to dsl/filters.py

- **`handle_filters()`** (~205 lines, 3 phases) — the full filter engine
  with its nested helpers (`_check_names`, `_collect_frame_skips`).
- **`find_neighbors()`** (~67 lines) — neighbour traversal with its
  nested helpers (`_find_neighbors`, `_nb`, `_find_neighbors_in_dir`).

### Cross-package import: parser → rendering.templates

`dsl/parser.py` needs two constants from `rendering/templates.py`:
- `ITEM_EXTERNAL_ATTRS` (used in `_parse_item_external()`)
- `FRAME_DEFAULT_ATTRS` (used in `_parse_frame()`)

This creates a one-way dependency: `dsl → rendering` (constants only,
no behaviour). This is acceptable because:
1. It's unidirectional (rendering never imports from dsl).
2. The dependency is on string constants, not on classes or functions.
3. Moving these constants elsewhere (e.g. config.py) would scatter
   rendering concerns into infrastructure modules.

### Import style

All modules use **relative imports**, consistent with the existing
codebase:
- Within `dsl/`: `from . import scanner` for siblings,
  `from .. import model` for parent package modules.
- Within `rendering/`: same pattern.
- Top-level modules: `from .dsl import filters` or
  `from .rendering import dot as rendering_dot`.

Sub-package `__init__.py` files are empty (package markers only). The
orchestrator imports directly from sub-modules. No re-exports — callers
use the full path. This is YAGNI; re-exports can be added later if a
public API emerges.

### Minor doc update: CONVENTIONS.md

The target layout in `doc/CONVENTIONS.md` lists `model.py` as holding
"data types, exceptions, enums", but task D created a separate
`exception.py`. We update the target layout to include `exception.py`
as a separate top-level module, reflecting the actual post-D state.

### Test import updates

Tests currently import from the flat package:
```python
from data_flow_diagram import parser, scanner
```
After the move, these become:
```python
from data_flow_diagram.dsl import parser, scanner
```

Affected test files:
- `tests/unit/test_parser.py` — `parser`, `scanner`
- `tests/unit/test_scanner.py` — `scanner`
- `tests/unit/test_dfd.py` — `parser`, `scanner`
- `tests/conftest.py` — unchanged (only imports `model`)
- `tests/unit/test_cli.py` — unchanged (only imports `main`, `parse_args`)
- `tests/unit/test_markdown.py` — unchanged (only imports `model`, `markdown`)
- `tests/test_integration.py` — unchanged (only imports `main`)

Non-regression tests are unaffected (they test through the CLI or
`build()`, not individual module imports).

### New NR tests needed?

**No.** This is a purely structural refactoring with no behavioural
changes. The existing 67 NR fixtures (including comprehensive filter
coverage from task A: fixtures 028–048, and error coverage: 049–067)
already anchor all code paths. Running `make test` after each commit
is sufficient validation.

## Implementation plan

Four logical commits, each leaving the codebase in a working state
(`make test` passes).

### Commit 1: Create dsl/ sub-package

Move the three existing DSL modules into `dsl/`:
- `git mv scanner.py dsl/scanner.py`
- `git mv parser.py dsl/parser.py`
- `git mv dependency_checker.py dsl/checker.py`
- Create `dsl/__init__.py` (empty)
- Update relative imports in moved files (`from .` → `from ..`)
- Update imports in `dfd.py`, test files
- `make black && make lint && make test`

### Commit 2: Create rendering/ sub-package

Move the two existing rendering modules:
- `git mv dfd_dot_templates.py rendering/templates.py`
- `git mv dot.py rendering/graphviz.py`
- Create `rendering/__init__.py` (empty)
- Update relative imports in moved files
- Update imports in `dfd.py`, `dsl/parser.py`, `cli.py`
- `make black && make lint && make test`

### Commit 3: Extract Generator + generate_dot + wrap → rendering/dot.py

- Create `rendering/dot.py` with `Generator`, `generate_dot()`, `wrap()`
- Remove extracted code from `dfd.py`
- Update `dfd.py` to import from `.rendering.dot`
- `make black && make lint && make test`

### Commit 4: Extract filter engine → dsl/filters.py

- Create `dsl/filters.py` with `handle_filters()`, `find_neighbors()`
- Remove extracted code from `dfd.py`
- Update `dfd.py` to import from `.dsl.filters`
- Update `tests/unit/test_dfd.py` (filter error tests import path)
- `make black && make lint && make test`

### Post-implementation

- Update `doc/CONVENTIONS.md` target layout to include `exception.py`
- Verify both entry points: `./data-flow-diagram` and `pip install`
- Final `make test` on clean state
