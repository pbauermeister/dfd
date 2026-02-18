# 025 — Improve Unit Tests Framework

**Date:** 2026-02-18
**Status:** IN-SPECS

## 1. Requirement

Consider the existing unit tests framework embryo.

Analyze how it could be improved to achieve the same results, but be more Pythonic and use conventions (naming, packages) that are commonly used.

1. Refine this specification
2. Analyze current situation
3. Propose and plan changes
4. Implement and test changes

### 1.1. Scope

Call internal features by direct Python access — no CLI subprocess calls in unit tests.

Instrumentation of application code is allowed.

Modifications of application code is encouraged to avoid mocking.

Running all tests must be fast enough not to hamper the install/publish process, and suitable for future CI on pull requests.

The existing tests check successes and failures. They shall be easy to extended to cover edge cases. They must not duplicate basic nominal cases, which are covered by the non-regression tests.

The framework must not anticipate future tests (no hooks, markers, or base classes for hypothetical needs), but must not create obstacles to adding them later.

### 1.2. Developer workflow

Unit tests are called via a Makefile target (`make test`) that can be run standalone or combined with other targets (`make all`). The underlying command switches from `python3 tests/unit_tests.py -v` to `pytest`.

### 1.3. Terminology

- **Fixtures**: DFD text snippets and other input data used as test inputs, defined in `tests/conftest.py`.
- **Golden data**: Not used for unit tests (only relevant for non-regression tests).
- **Unit tests**: Tests that call internal Python APIs directly and assert structural or exception properties.
- **Integration tests**: Tests that exercise the full pipeline end-to-end (e.g. stdin → stdout SVG), kept in a flat `tests/test_integration.py`.

### 1.4. Decisions (from spec chat, 2026-02-18)

| #   | Topic             | Decision                                                                                                                                                                                 |
| --- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Test framework    | Switch to `pytest`; include sparse comments to guide pytest non-experts                                                                                                                  |
| 2   | Path hack         | Remove `sys.path.insert(0, "src")` everywhere; configure `pythonpath = ["src"]` in `pyproject.toml [tool.pytest.ini_options]`                                                            |
| 3   | Fixtures          | Move to `tests/conftest.py`; use module-level constants for DFD snippets (maximum readability); `pytest.fixture` only where setup/teardown genuinely adds value                          |
| 4   | File organisation | Split by subsystem: `tests/unit/test_cli.py`, `tests/unit/test_parser.py`, `tests/unit/test_scanner.py`, `tests/unit/test_markdown.py`; one file per subsystem                           |
| 5   | Golden data       | Not used for unit tests                                                                                                                                                                  |
| 6   | Integration tests | Flat `tests/test_integration.py`; extend to a subdirectory later only if it outgrows a single file                                                                                       |
| 7   | No anticipation   | Framework is minimal; no infrastructure invented for hypothetical future tests                                                                                                           |
| 8   | Readability       | Descriptive names; inline comments on non-obvious assertions; `@pytest.mark.parametrize` with explicit string IDs                                                                        |
| 9   | Type-bounded      | Test code imports and uses application types directly (`model.DfdException`, `model.Snippet`, `model.Keyword`, …); no string literals where the application defines enums or dataclasses |
| 10  | Engaging          | Error-case tests use `parametrize`; adding a new case means adding one tuple to a list                                                                                                   |
| 11  | GitHub Actions    | Add `.github/workflows/ci.yml` running `make test` (covers both unit and non-regression tests)                                                                                           |

### 1.5. Naming conventions

- Test files: `test_<subsystem>.py` (e.g. `test_parser.py`)
- Test functions: `test_<what>_<condition>` (e.g. `test_parse_duplicate_item_raises`)
- Parametrize IDs: short, human-readable strings (e.g. `"duplicate-item"`, `"missing-ref"`)
- Fixture constants in `conftest.py`: `UPPER_CASE` for raw DFD/MD strings; `pytest.fixture` functions in `lower_case`

## 2. Design

_(to be filled in step 3)_

## 3. Implementation decisions

_(to be filled during implementation)_

## 4. Implementation summary

_(to be filled after implementation)_
