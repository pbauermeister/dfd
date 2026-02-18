# 025 — Improve Unit Tests Framework

**Date:** 2026-02-18
**Status:** DONE

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

### 2.1. Current situation (step 2 analysis)

| Item | Current state | Problem |
|------|---------------|---------|
| Framework | `unittest.TestCase`, run via `python3 tests/unit_tests.py -v` | Not idiomatic; no parametrize, no fixtures, no monkeypatch |
| Path setup | `sys.path.insert(0, "src")` in `unit_tests.py` and `inputs.py` | Fragile hack, non-Pythonic |
| Fixture data | `tests/inputs.py` — plain module with string constants | Imported with a bare `import inputs` that only works when CWD is project root |
| File layout | Single `tests/unit_tests.py` (8 tests across 4 subsystems) | No separation of concerns |
| Parametrize | 3 near-identical `parser.check()` error tests written out separately | Adding a new error case requires copy-pasting a whole test method |
| `sys.argv`/`sys.stdin` | Manually saved and restored in try/finally blocks | pytest's `monkeypatch` handles this more safely |
| Makefile | `test:` calls `./test.sh` (which calls `python3 tests/unit_tests.py -v`) | `pytest` not used; `require:` doesn't install it |
| GitHub Actions | No CI workflow | Tests never run automatically |

**Subsystem-to-test mapping:**

| Subsystem | File | Tests |
|-----------|------|-------|
| CLI entry point | `__init__.py` | `test_parse_args` |
| Parser + Scanner | `parser.py`, `scanner.py` | 5 tests (1 success, 1 parse error, 3 check errors) |
| Markdown | `markdown.py` | `test_input_md` |
| Integration | full pipeline | `test_output_stdout` (stdin → stdout SVG) |

### 2.2. Target layout

```
tests/
  conftest.py              # shared pytest fixtures (markdown data)
  test_integration.py      # end-to-end pipeline test
  unit/
    __init__.py
    test_cli.py            # parse_args() tests
    test_parser.py         # scanner + parser + check tests
    test_markdown.py       # snippet extraction tests
  non-regression/          # unchanged
```

### 2.3. Key design choices

- **conftest.py**: only proper `@pytest.fixture` functions, for data too complex or
  verbose to inline (currently: markdown fixtures). Small DFD strings stay inline as
  `pytest.param` entries in the test file that uses them.
- **Parametrize**: the 3 `parser.check()` error cases become one `@pytest.mark.parametrize`
  test; each case is a `pytest.param(dfd_text, id="...")`.
- **monkeypatch**: replaces manual `sys.argv`/`sys.stdin` save/restore in CLI and integration tests.
- **capsys**: replaces `contextlib.redirect_stdout` in the integration test.
- **No golden data** for unit tests.
- **pyproject.toml**: gains `[tool.pytest.ini_options]` with `pythonpath = ["src"]`
  and `testpaths = ["tests"]`.
- **Makefile**: `require:` gains `pytest`; `test:` calls `pytest` directly, dropping `test.sh`.
- **GitHub Actions**: installs Python 3.12 + Graphviz, installs `pytest` + project,
  runs `pytest tests/` then `./tests/nr-test.sh`.

### 2.4. Files deleted

- `tests/unit_tests.py` — replaced by `tests/unit/test_*.py`
- `tests/inputs.py` — replaced by `tests/conftest.py` and inline params
- `test.sh` — superseded by direct `pytest` call in Makefile

## 3. Implementation decisions

- `conftest.py` uses both module-level constants (for potential reuse in parametrize)
  and `@pytest.fixture` functions that wrap them (for auto-injection by pytest).
- Small DFD error strings stay inline in `test_parser.py` as `pytest.param` entries,
  avoiding any need to import from conftest.
- `tests/__init__.py` was deleted (empty, unneeded with pytest discovery).
- `test.sh` was deleted; Makefile calls `pytest` directly.
- The original 8 tests become 9 (the single `test_parse_args` was split into two
  focused assertions: keys check and positional-arg check).

## 4. Implementation summary

Files created:
- `tests/conftest.py` — shared markdown fixtures
- `tests/unit/__init__.py` — marks directory as package
- `tests/unit/test_cli.py` — 2 tests for `parse_args()`
- `tests/unit/test_parser.py` — 3 tests (1 success, 1 parse error, 1 parametrized check error × 3 cases)
- `tests/unit/test_markdown.py` — 1 test for `extract_snippets()`
- `tests/test_integration.py` — 1 end-to-end test
- `.github/workflows/ci.yml` — CI workflow

Files modified:
- `pyproject.toml` — added `[tool.pytest.ini_options]`
- `Makefile` — `require:` gains `pytest`; `test:` calls `pytest` directly

Files deleted:
- `tests/unit_tests.py`, `tests/inputs.py`, `test.sh`, `tests/__init__.py`

Result: 9 tests, all passing in 0.11 s.
