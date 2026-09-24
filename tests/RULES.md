# Tests

## Writing or modifying tests

Before adding or changing any test, read `tests/README.md`. It defines: how to classify a test (unit / integration / non-regression; nominal / edge / robustness / regression), where to place it, how to run it in isolation, and how it gets picked up by the full suite (`make test`).

## Non-regression tests

- **Fixtures** (test inputs) live in `tests/non-regression/`: `.dfd`, `.part`, `.md` files.
- **Golden files** (expected outputs): `.dot` files. Standalone tests use `NNN-name.dot`; markdown tests use `NNN-name/output.dot` subdirectories.
- **Workflow:** `make nr-review` → inspect SVGs / error output → `make nr-regenerate` → commit fixtures and golden files together.
- `make nr-test` runs as part of `make test`. It compares regenerated output against golden files.
- Test numbering follows `doc/README.md` section order. When adding a new test case, use the next available number (currently 089+).
- **Mutation smoke-test:** After adding or changing NR fixtures, verify they are effective by introducing a tiny, deliberate mutation in the code path under test, running `make nr-test` to confirm the relevant fixtures fail, then reverting the mutation. This guards against golden files that silently pass because they don't actually exercise the intended code.
