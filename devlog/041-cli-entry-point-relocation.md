# 041 — CLI entry point relocation

**Date:** 2026-02-19

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/41

## Requirement

Task C of the refactoring strategy (#34): move CLI logic out of
`__init__.py` into a dedicated `cli.py` module, so that `__init__.py`
serves only as the package interface.

Specific actions from the strategy:

- Create `cli.py` with `parse_args()`, `run()`,
  `handle_markdown_source()`, `handle_dfd_source()`, and `main()`.
- Reduce `__init__.py` to re-exports and the `VERSION` constant.
- Keep `main()` re-exported from `__init__.py` so both entry points
  work unchanged (`setup.py` console script and `./data-flow-diagram`
  dev wrapper).
- Fix the stale `"UML sequence input file"` help string.

## Design

### New file: `src/data_flow_diagram/cli.py`

Move all CLI functions from `__init__.py`:
- `parse_args()` — argument parser definition
- `handle_markdown_source()` — markdown dispatch
- `handle_dfd_source()` — single-file dispatch
- `run()` — option resolution and dispatch
- `main()` — top-level entry point

The module docstring (used by argparse for `--help`) moves to `cli.py`.

### Reduced `__init__.py`

Keeps:
- `VERSION` constant (package metadata)
- Re-exports: `main` and `parse_args` (for backward compatibility
  with existing test imports and the `setup.py` console script entry
  point `data_flow_diagram:main`)

### Help string fix

Replace `"UML sequence input file"` with `"DFD input file"` in the
`INPUT_FILE` argument help text.

### No new tests needed

This is a pure mechanical move. Existing coverage is sufficient:
- `tests/unit/test_cli.py` — imports `parse_args` from
  `data_flow_diagram`
- `tests/test_integration.py` — imports `main` from
  `data_flow_diagram`
- `make nr-test` — full pipeline via CLI
