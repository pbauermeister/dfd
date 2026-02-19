# 047 — Break up large functions

**Date:** 2026-02-19

**Status:** PENDING

**Issue:** https://github.com/pbauermeister/dfd/issues/47

## Requirement

Part of the refactoring strategy (#34, task H). Depends on F (module
boundaries, done in #45).

Split oversized functions into smaller, well-named units within their
(now properly located) modules. Function names must follow the
action-first convention defined in `doc/CONVENTIONS.md`.

### Target functions

| Function                          | File             | Lines | Phases |
| --------------------------------- | ---------------- | ----- | ------ |
| `handle_filters()`                | dsl/filters.py   | 205   | 5      |
| `_parse_filter()`                 | dsl/filters.py   | 97    | 3      |
| `parser.check()`                  | dsl/parser.py    | 87    | 3      |
| `Generator.generate_connection()` | rendering/dot.py | 76    | 3      |
| `Generator.generate_item()`       | rendering/dot.py | 53    | 3      |

### Safety net

Non-regression tests (task A, #34) and `make test` validate that
splitting doesn't change behaviour.

## Design

### Principle: move inner functions out

All inner functions in the three target files are moved to module-level
private functions with explicit parameters (no closure captures).

**Exceptions** (kept nested):

- Factory closures (`_make_item_parser`, `_make_connection_parser`) —
  the inner `parse()` is the return value; that's the point.
- Regex callback (`replacer` in `_expand_attribs`) — idiomatic one-off
  callback for `re.sub`.

### Function splits

**`parser.check()`** → orchestrator + 3 helpers:

```
check(statements)                                       ~10 lines
├── _check_items(statements)                            ~22 lines
├── _check_connections(statements, items_by_name)       ~34 lines
└── _check_frames(statements, items_by_name)            ~24 lines
```

**`handle_filters()`** → orchestrator + 4 helpers:

```
handle_filters(statements, debug)                       ~15 lines
├── _collect_kept_names(statements, all_names, debug)   ~85 lines
├── _mark_non_hidable(statements, only_names)           ~8 lines
├── _apply_filters(statements, kept_names, replacement, ~60 lines
│                   skip_frames_for_names, debug)
└── _deduplicate_connections(statements,                ~14 lines
                             replaced_connections)
```

**`_parse_filter()`** → extract `_parse_neighbor_spec()`:

Extract `_parse_neighbor_spec(match, arg)` →
`(FilterNeighbors, is_up, is_down)` (~35 lines out).

**`Generator.generate_connection()`** → extract attr builder:

Extract `_build_connection_attrs(self, conn, text)` → `str` as a
private method (~40 lines of match statements).

**`Generator.generate_item()`** — left as-is (53 lines, mostly a
single match statement where each case is 2–7 lines).

### No new NR fixtures

Purely structural refactoring — existing 73 fixtures are the safety
net.

### Implementation steps

1. `parser.py` — move out `_fmt`, `_resolve`; split `check()` into
   3 helpers.
2. `filters.py` — move out inner functions from `find_neighbors()`.
3. `filters.py` — split `handle_filters()` into orchestrator +
   4 helpers (moves out `_check_names`, `_collect_frame_skips`).
4. `filters.py` — extract `_parse_neighbor_spec()` from
   `_parse_filter()`.
5. `dot.py` — move out `strip_quotes`, `split_attr`, `get_item`;
   extract `_build_connection_attrs()`.

Each step: modify → `make black` → `make lint` → `make test` →
commit.
