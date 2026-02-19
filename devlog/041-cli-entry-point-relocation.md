# 041 — CLI entry point relocation

**Date:** 2026-02-19

**Status:** DONE

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

### Entry-point analysis and test coverage

There are four distinct invocation paths. Each resolves `main()` via a
different mechanism, and a break in any one would be invisible to the
others.

| #   | Invocation path                   | Mechanism                                                               | Current test coverage                     | Gap?                  |
| --- | --------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------- | --------------------- |
| 1   | `./data-flow-diagram` (local dev) | Script imports `src.data_flow_diagram` → `__init__.main` → `cli.main`  | `make nr-test` (56 cases)                 | None                  |
| 2   | `make install` → global command   | `setup.py` console_scripts `data_flow_diagram:main` → `__init__.main`  | None                                      | **Entry-point resolve** |
| 3   | PyPI install → global command     | Same `data_flow_diagram:main` entry point as #2                         | None (release verification)               | Out of scope          |
| 4   | Tests (direct Python calls)       | `from data_flow_diagram import main` / `parse_args`                     | `test_cli.py`, `test_integration.py`      | None                  |

**Diagnosis:** Paths 1 and 4 are well covered. Paths 2 and 3 share
the same mechanism (`console_scripts` entry point string
`data_flow_diagram:main`) and have zero automated coverage today. A
broken re-export in `__init__.py` would pass all existing tests but
fail on install.

### Tests to add

1. **Entry-point resolution test** (unit, `test_cli.py`): verify that
   the string `data_flow_diagram:main` resolves to a callable. This
   uses `importlib.metadata` to read the console_scripts entry point
   from the installed package metadata — the same mechanism pip uses
   to generate the wrapper script. Covers path 2 without needing an
   actual install.

2. **Subprocess CLI test** (integration, `test_integration.py`):
   invoke `./data-flow-diagram` as a subprocess with a minimal DFD on
   stdin and assert exit code 0 + SVG output. This tests the full
   OS-level invocation (path 1) end-to-end, complementing the
   existing in-process `main()` test.

3. **`--version` flag test** (unit, `test_cli.py`): verify that
   `main()` prints the version string and exits when called with
   `--version`. This exercises the `VERSION` re-export path.

4. **`--help` text test** (unit, `test_cli.py`): verify that the help
   output contains `"DFD input file"` and does NOT contain the stale
   `"UML sequence"` string. Locks in the help string fix.

Path 3 (PyPI install) is out of scope — it uses the same mechanism as
path 2 and is verified at release time.

No new NR tests (golden DOT files) are needed — the refactoring does
not change any diagram output.
