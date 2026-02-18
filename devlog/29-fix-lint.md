# 29 — Fix Broken Lint

Date: 2026-02-18
Status: ONGOING

## Requirement

`make lint` fails with 9 mypy errors across 5 test files introduced when the
unit test suite was added. All errors are missing or incomplete type annotations
in test functions and fixtures.

Additionally, update `CLAUDE.md` to require running `make lint` during
development and before submitting fixes, so the issue cannot recur silently.

## Design

Fix each mypy error with the minimal annotation needed:

- `conftest.py` — `@pytest.fixture` is untyped from mypy's perspective; suppress
  the `[misc]` error with `# type: ignore[misc]` on each decorator line. The
  functions already carry correct return types.
- `test_cli.py` — annotate `monkeypatch` as `pytest.MonkeyPatch` and add
  `-> None` to both test functions.
- `test_parser.py` — add `-> None` to the two no-arg tests; annotate
  `dfd_text: str` and add `-> None` to the parametrized test.
- `test_markdown.py` — annotate both fixture arguments with their concrete types
  and add `-> None`.
- `test_integration.py` — annotate `monkeypatch: pytest.MonkeyPatch`,
  `capsys: pytest.CaptureFixture[str]`, and add `-> None`.

`CLAUDE.md` gets a new bullet in the **Formatting** section requiring
`make lint` after any Python changes.
