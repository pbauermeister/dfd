# 049 — Improve testability: decouple pipeline stages from I/O

**Date:** 2026-02-19

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/49

## Requirement

Task I of the refactoring strategy (#34).

Make pipeline stages independently testable by reducing I/O coupling and
making data flow explicit.

Currently `build()` in `dfd.py` mixes core pipeline logic (scan → parse →
check → filter → render) with I/O concerns (deriving the title from
`output_path`, writing DOT text to disk, calling Graphviz). This makes it
impossible to unit-test the full pipeline without touching the filesystem.

The filter engine (`dsl/filters.py`) and DOT generator (`rendering/dot.py`)
already expose pure functions. The remaining coupling is in `build()` itself
and in `dependency_checker.check()` (which reads files and re-parses).

### Anticipated actions

1. **Refactor `build()` to return DOT text** — move file-writing and Graphviz
   invocation to the caller (`cli.py`). Title derivation (currently done from
   `output_path`) also moves to the caller.
2. **Ensure each stage has a pure interface** — verify filters (statements →
   statements) and rendering (statements → DOT text) remain clean after the
   refactor.
3. **Add unit tests for pipeline stages** — exercise scan, parse, check,
   filter, handle_options, remove_unused_hidables, and generate_dot in
   isolation with programmatically constructed `model.Statements`.
4. **Consider `dependency_checker` testability** — evaluate whether it can
   accept pre-parsed data or use dependency injection to avoid file I/O in
   tests.

## Design

### Step 1 — Refactor `build()` to return DOT text

Change `build()` signature:

- **Remove** `output_path: str` parameter.
- **Add** `title: str` parameter (caller derives it from the output path).
- **Return** `str` (DOT text) instead of `None`.
- Remove the file-writing / Graphviz invocation block at the end.
- Keep `dprint(text)` for debug output.

### Step 2 — Move I/O to `cli.py`

Add a helper in `cli.py`:

```python
def write_output(
    dot_text: str, output_path: str, format: str,
    graph_options: model.GraphOptions,
) -> None:
```

This handles the choice between writing DOT text to disk and calling
`graphviz.generate_image()`. Update `handle_dfd_source()` and
`handle_markdown_source()` to:

1. Derive `title` from the output path (moved from `build()`).
2. Call `build()` to get DOT text.
3. Call `write_output()` to produce the file.

Note: `build()` currently returns `graph_options` implicitly (it's computed
inside). Since `write_output()` needs it for `graphviz.generate_image()`,
`build()` must return it alongside the DOT text. New return type:
`tuple[str, model.GraphOptions]`.

### Step 3 — Add `file_texts` to `dependency_checker.check()`

Add an optional parameter for testing without filesystem access:

```python
def check(
    dependencies: model.GraphDependencies,
    snippet_by_name: model.SnippetByName | None,
    options: model.Options,
    file_texts: dict[str, str] | None = None,
) -> None:
```

Extract a `_read_file(name, file_texts)` helper that returns the file
content. When `file_texts` is provided it looks up the dict; when the key
is missing it raises `FileNotFoundError(2, "No such file or directory", name)`
so the existing `except FileNotFoundError` handler produces identical error
messages. Production callers pass nothing; tests pass a dict.

### Step 4 — Run `make test` to verify no regressions

All existing NR, unit, and integration tests must pass after steps 1–3.

### Step 5 — Add unit tests

New file: `tests/unit/test_pipeline.py`.

Tests to add:

- **`build()` end-to-end** — pass DFD source text, get DOT text back.
  Assert `digraph` preamble and expected item/connection fragments.
- **`handle_options()`** — happy-path: extract style options from
  constructed statements, verify returned `GraphOptions` fields.
- **`remove_unused_hidables()`** — constructed statements with a hidable
  item that has no connections; verify it's removed.
- **`generate_dot()`** — pass a `Generator` and model objects, verify
  DOT output contains expected fragments.
- **`handle_filters()`** — happy-path: only/without on constructed
  statements (complementing the existing error tests in `test_dfd.py`).
- **`dependency_checker.check()`** — use `file_texts` dict to test both
  success (item found) and error (missing file, wrong type) without
  filesystem access.

### Step 6 — Update devlog and PR

Mark devlog DONE, update PR body, mark PR ready.

### NR fixtures

No new NR fixtures needed — this task changes internal structure, not
observable output. Existing NR tests serve as the safety net.

### Implementation order

| Step | Description                                          | Depends on |
| ---- | ---------------------------------------------------- | ---------- |
| 1    | Refactor `build()` to accept title, return DOT text  | —          |
| 2    | Move I/O to `cli.py`                                 | 1          |
| 3    | Add `file_texts` to `dependency_checker.check()`     | —          |
| 4    | Run `make test` — verify no regressions              | 1, 2, 3    |
| 5    | Add unit tests in `tests/unit/test_pipeline.py`      | 4          |
| 6    | Update devlog and PR                                 | 5          |

Steps 1+2 are tightly coupled (changing `build()` requires updating its
callers). Step 3 is independent and can be done before or after 1+2.
