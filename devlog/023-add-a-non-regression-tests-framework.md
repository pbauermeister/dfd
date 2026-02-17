# 023 — Add a Non-Regression Tests Framework

**Date:** 2026-02-17
**Status:** DONE

## 1. Requirement

Add a non-regression (NR) test framework that verifies the Graphviz DOT
text generated from DFD sources against committed golden references.

### Workflow

1. The developer creates a DFD source file in `tests/non-regression/`,
   named with a numeric prefix (e.g. `001-items.dfd`).
2. A **preview step** generates the corresponding `.svg` file for visual
   inspection.
3. The developer inspects the SVG. If satisfied, a **confirmation step**
   generates the `.dot` golden file (the Graphviz DOT source text that
   the tool produces internally).
4. Both `.dfd` and `.dot` are committed. The `.svg` is gitignored.
5. When running NR tests, each `.dfd` is loaded, the DOT text is
   regenerated, and compared against the committed `.dot`. Any mismatch
   is a failure.

Each step is triggered by a Makefile target.

## 2. Design

### `--format dot`

A new value `dot` is added to the existing `--format` CLI option. When
specified:

- The tool runs the full pipeline (scan, parse, check, filters, hidable
  removal, options handling, DOT generation) but skips the Graphviz
  rendering step.
- The DOT text is written directly to the output file (or stdout when
  outputting to `-`).
- The default output extension becomes `.dot` (via the existing
  `basename + "." + format` logic).

This requires a small conditional in `dfd.py:build()` or
`__init__.py:handle_dfd_source()`.

No `--no-graph-title` is needed: since the `.dfd` files live at fixed
relative paths in the repository, the derived title is stable and
comparisons remain valid.

### File structure

```
tests/non-regression/
    001-items.dfd             # DFD source (committed)
    001-items.dot             # Golden DOT output (committed after approval)
    001-items.svg             # Preview render (gitignored)
```

Flat naming convention: `NNN-description.{dfd,dot,svg}`.

### Makefile targets

| Target            | Action                                                                             |
| ----------------- | ---------------------------------------------------------------------------------- |
| `make nr-preview` | For each `*.dfd`, run `data-flow-diagram -f svg -o *.svg`                          |
| `make nr-approve` | For each `*.dfd`, run `data-flow-diagram -f dot -o *.dot`, then print a warning    |
| `make nr-test`    | For each `*.dfd` with a `.dot`, regenerate DOT to a temp file, diff against golden |

`make nr-approve` finishes by printing a reminder that any git change to
`tests/non-regression/*.dot` files must be carefully examined by the
developer, as it is either deliberate changes, or an early sign of regression.

`make nr-test` exits non-zero on any mismatch. The existing `make test`
target is extended to also run `make nr-test`.

### First test case

`001-items.dfd` — the first example from `doc/README.md`, covering all
item types (process, control, entity, store, channel, none).
