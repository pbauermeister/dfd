# 038 — Consolidate scattered constants

**Date:** 2026-02-19
**Status:** DONE

## Requirement

Task B from the refactoring strategy (#34): magic values (colours, shapes, DOT
attributes, engine names) are scattered across `dfd.py`, `dot.py`, and
`parser.py`. Consolidate them into named constants.

## Design

Graphviz-specific constants go to `dfd_dot_templates.py` (already the home for
DOT templates); general configuration stays in `config.py`.

### Constants added to `dfd_dot_templates.py`

- **Item shapes/fills:** `SHAPE_PROCESS_CONTEXT`, `SHAPE_PROCESS`,
  `SHAPE_ENTITY`, `SHAPE_NONE`, `FILL_PROCESS_CONTEXT`, `FILL_PROCESS`,
  `STYLE_PROCESS`, `STYLE_CONTROL`
- **Connection attributes:** `ATTR_CONSTRAINT_LABELED`, `ATTR_CONSTRAINT_HIDDEN`,
  `ATTR_DIR_BACK`, `ATTR_DIR_BOTH`, `ATTR_DIR_NONE`, `ATTR_CFLOW_TAIL`,
  `ATTR_CFLOW_HEAD`, `ATTR_STYLE_DASHED`, `ATTR_RELAXED`
- **Layout parameters:** `LAYOUT_VERTICAL`, `LAYOUT_HORIZONTAL`,
  `ROTATION_DEGREES`
- **Miscellaneous:** `CHANNEL_PORT`, `STAR_NODE_FMT`, `HTML_ITEM_DEFAULTS`,
  `FRAME_DEFAULT_ATTRS`, `ENGINE_CONTEXT`, `ENGINE_DEFAULT`

### Files modified

| File                   | Changes                                       |
| ---------------------- | --------------------------------------------- |
| `dfd_dot_templates.py` | Added ~20 named constants                     |
| `dfd.py`               | Replaced ~25 magic literals with TMPL.*       |
| `dot.py`               | Replaced engine names, added TMPL import      |
| `parser.py`            | Replaced frame style literal                  |
| `config.py`            | Removed stale TODO comment                    |

### What stays in place

- ANSI codes in `console.py` (standard, used once, self-explanatory)
- Values inside DOT template strings (tightly coupled to template layout)
- `"dot"` in `check_installed()` (binary name, not a rendering constant)

## Verification

- `make black` / `make lint` / `make test` — all passing after each commit
- Pure refactoring: identical DOT output confirmed by non-regression tests
