# 043 — Streamline error handling

**Date:** 2026-02-19

**Status:** PENDING

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

*(To be filled after approach is chosen and confirmed.)*
