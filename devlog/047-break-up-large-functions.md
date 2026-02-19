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

_To be filled during spec refinement._
