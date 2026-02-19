# 049 — Improve testability: decouple pipeline stages from I/O

**Date:** 2026-02-19

**Status:** PENDING

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

*(To be filled during Phase 3 — specification refinement.)*
