# 043 — Streamline error handling

**Date:** 2026-02-19

**Status:** DONE

**Issue:** https://github.com/pbauermeister/dfd/issues/43

## Requirement

Replace the repetitive `prefix = mk_err_prefix_from(src)` +
`raise DfdException(f"{prefix}...")` two-step pattern with a single-call
mechanism. This is task D from the refactoring strategy (#34).

There are ~12 `mk_err_prefix_from` calls and ~30 `raise DfdException`
sites across the codebase. The verbose pattern is error-prone (easy to
forget the prefix) and adds visual noise.

### Error-message NR tests (prerequisite)

Before any error-handling changes, create a series of non-regression
tests that capture the stderr output of erroneous `.dfd` inputs:

- **Fixtures:** `tests/non-regression/NNN-err-*.dfd` — each contains
  an invalid DFD that triggers a `DfdException`.
- **Golden files:** `tests/non-regression/NNN-err-*.stderr` — the
  expected stderr output (the `ERROR: ...` text printed by `cli.py`).
- **NR scripts:** Extend `nr-test.sh`, `nr-approve.sh`, and
  `nr-preview.sh` (or add parallel logic) to handle error-case
  fixtures alongside the existing success-case fixtures.
- **Workflow:** Same as existing NR tests — `make nr-approve` generates
  goldens, `make nr-test` verifies them.

After the error-handling refactoring, these NR tests must pass unchanged,
proving that error messages are identical.

Error scenarios to cover (drawn from existing unit tests and raise sites):

| Category     | Scenario                     | Source module        |
| ------------ | ---------------------------- | -------------------- |
| Parser       | Duplicate item name          | `parser.py`          |
| Parser       | Connection to undefined item | `parser.py`          |
| Parser       | Double wildcard connection   | `parser.py`          |
| Parser       | Connection to control item   | `parser.py`          |
| Parser       | Empty frame                  | `parser.py`          |
| Parser       | Frame references unknown item| `parser.py`          |
| Parser       | Item in multiple frames      | `parser.py`          |
| Parser       | Unknown keyword              | `parser.py`          |
| Parser       | Missing item arguments       | `parser.py`          |
| Parser       | Missing connection arguments | `parser.py`          |
| Parser       | Filter with no arguments     | `parser.py`          |
| Parser       | Filter spec only (no names)  | `parser.py`          |
| Parser       | Replacer on Only filter      | `parser.py`          |
| Parser       | Bad filter flag              | `parser.py`          |
| DFD pipeline | Filter unknown name          | `dfd.py`             |
| DFD pipeline | Filter already-removed name  | `dfd.py`             |
| DFD pipeline | Unknown style name           | `dfd.py`             |
| DFD pipeline | Bad style integer value      | `dfd.py`             |
| Scanner      | Include nonexistent file     | `scanner.py`         |

## Design

**Chosen approach:** Richer `DfdException` — the exception class itself
accepts an optional `source` parameter and formats the prefix internally.

```python
class DfdException(Exception):
    def __init__(self, msg: str, source: SourceLine | None = None):
        self.source = source
        if source is not None:
            prefix = mk_err_prefix_from(source)
            super().__init__(f"{prefix}{msg}")
        else:
            super().__init__(msg)
```

Call sites change from:

```python
prefix = mk_err_prefix_from(statement.source)
raise DfdException(f"{prefix}some message")
```

to:

```python
raise DfdException("some message", source=statement.source)
```

`mk_err_prefix_from` remains public — `dependency_checker.py` still uses
it directly for its accumulation pattern (multiple sources, one exception).

## Progress

### Phase 1: Error-case NR test infrastructure — DONE

Commit `04bd15b` added:

- 19 error-case NR fixtures (`049-err-*` through `067-err-*`) with
  `.stderr` golden files.
- Extended `nr-test.sh`, `nr-review.sh`, `nr-regenerate.sh` to handle
  error-case fixtures alongside success-case fixtures.
- All 19 scenarios from the requirement table are covered.

### Phase 2: Richer DfdException refactoring — DONE

Commit `d91c39c` implemented the design:

- **`model.py`** — Enriched `DfdException.__init__` with `source` parameter.
- **`parser.py`** — Removed 4 `mk_err_prefix_from` calls, converted 10
  raise sites. The re-wrapping catch in `parse()` now uses `from e` for
  proper exception chaining.
- **`dfd.py`** — Removed 5 `mk_err_prefix_from` calls, converted 8 raise
  sites. Changed `_check_names` signature from `prefix: str` to
  `source: SourceLine`.
- **`scanner.py`** — Removed 1 `mk_err_prefix_from` call, converted 4
  raise sites.
- **`markdown.py`** — Removed 1 `mk_err_prefix_from` call, converted 1
  raise site.
- **`dependency_checker.py`** — Left unchanged (accumulation pattern).

**Totals:** 11 of 12 `mk_err_prefix_from` calls removed, ~23 raise sites
converted. All 19 error-case NR golden files match byte-for-byte.

### Phase 3: Move prefix logic into DfdException, add accumulation API — DONE

Commit `cd6f975`:

- Moved `_mk_prefix` (formerly `mk_err_prefix_from`) into `DfdException`
  as a static method, removing the last standalone helper.
- Added `add()` / `__bool__` accumulation API to `DfdException`, letting
  `dependency_checker.py` collect multiple errors into a single exception
  instead of using a separate list.
- Removed `mk_err_prefix_from` from `model.py` (no remaining callers).

### Phase 4: Extract DfdException into its own module — DONE

Commit `477e32e`:

- Created `src/data_flow_diagram/exception.py` containing `DfdException`
  (moved verbatim from `model.py`).
- Updated all 9 source files and 3 test files to import from `exception`
  instead of `model`. No re-export from `model.py`.
- No circular dependency: `exception` → `model` is one-way (`pack` at
  runtime, `SourceLine` under `TYPE_CHECKING` only).

**Mutation smoke-test:** Injected `[X]` into `_format()` output; all 19
error NR tests failed, all 54 nominal tests passed. Reverted. Confirmed
that error NR fixtures are fully effective. Added mutation smoke-test
practice to `CLAUDE.md`.
