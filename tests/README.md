# Tests — Developer Guide

This guide answers the four questions a developer faces when adding or updating a test.

---

## 1. What kind of test should I write?

Start by classifying your intent along two axes.

### Axis A — Test category

| Category           | What it verifies                                                                  | Needs Graphviz? |
| ------------------ | --------------------------------------------------------------------------------- | --------------- |
| **Unit**           | A single internal Python function or a small cluster of tightly related functions | No              |
| **Integration**    | The full pipeline end-to-end (stdin/file → SVG/DOT on stdout/disk)                | Yes             |
| **Non-regression** | That a known-good DFD input still produces the expected DOT output                | Yes (nr-test)   |

Decision questions:

- Does your test **call a specific internal function** (`parser.parse`, `scanner.scan`, `markdown.extract_snippets`, …) and assert on its return value or exception? → **Unit**
- Does your test drive the **complete pipeline** (`main()`) and check that output is valid? → **Integration**
- Do you want to **lock in the exact DOT output** of a DFD file so that future changes cannot silently alter it? → **Non-regression**

### Axis B — Test nature

| Nature         | Description                                                                              |
| -------------- | ---------------------------------------------------------------------------------------- |
| **Nominal**    | Valid input, expected happy-path output. Covered mainly by non-regression tests.         |
| **Edge case**  | Valid but boundary input: empty labels, maximum widths, special characters, `*` nodes …  |
| **Robustness** | Invalid input that must be caught and produce a `DfdException` with a meaningful message |
| **Regression** | Reproduces a specific past bug to prevent it from reappearing                            |

> **Rule of thumb:** unit tests focus on edge cases and robustness; non-regression tests
> cover nominal cases; integration tests verify the pipeline glue.

---

## 2. Where do I write it?

### Unit test

**File:** `tests/unit/test_<subsystem>.py`

| Subsystem          | File                          |
| ------------------ | ----------------------------- |
| CLI / arg parsing  | `tests/unit/test_cli.py`      |
| Scanner + Parser   | `tests/unit/test_parser.py`   |
| Markdown extractor | `tests/unit/test_markdown.py` |

**Fixtures (inputs):**

- Short DFD strings: define them inline as `pytest.param(…, id="…")` inside a
  `@pytest.mark.parametrize` block in the test file itself.
- Longer or shared inputs: add a `@pytest.fixture` to `tests/conftest.py`.

**Example to follow:** `tests/unit/test_parser.py::test_check_raises` — a parametrized
robustness test where adding a new error case means adding one `pytest.param` tuple.

### Integration test

**File:** `tests/test_integration.py`

Use `monkeypatch` to set `sys.argv` and `sys.stdin`, and `capsys` to capture stdout.
No fixture file needed.

**Example to follow:** `tests/test_integration.py::test_stdin_to_stdout_produces_svg`.

### Non-regression test

**Fixtures (inputs):** `tests/non-regression/NNN-name.dfd` (standalone) or
`tests/non-regression/NNN-name.md` (markdown mode). Use the next available number
(see `doc/README.md` section order).

**Golden files (expected output):**

- Standalone `.dfd` → `tests/non-regression/NNN-name.dot`
- Markdown `.md` → `tests/non-regression/NNN-name/<output-name>.dot`

Generate them with `make nr-approve` after visually checking `make nr-preview`.

---

## 3. How do I run my test individually while developing it?

### Unit or integration test

```bash
# Run one test file
pytest tests/unit/test_parser.py -v

# Run one specific test function
pytest tests/unit/test_parser.py::test_parse_valid_syntax -v

# Run one parametrize case
pytest "tests/unit/test_parser.py::test_check_raises[duplicate-item]" -v
```

### Non-regression test — single .dfd file

```bash
# Generate DOT and diff against golden
dfd=tests/non-regression/001-items.dfd
dot="${dfd%.dfd}.dot"
tmp="${dfd%.dfd}.tmp"
./data-flow-diagram "$dfd" -f dot -o "$tmp"
diff "$dot" "$tmp"
rm "$tmp"
```

### Non-regression test — single .md file

```bash
md=tests/non-regression/022-include-snippet.md
subdir="${md%.md}"
tmp_md="${md%.md}.tmp.md"
sed 's/\.dot$/.tmp/g' "$md" > "$tmp_md"
./data-flow-diagram --markdown -f dot "$tmp_md"
diff "$subdir/includer-1.dot" "$subdir/includer-1.tmp"
rm -f "$tmp_md" "$subdir"/*.tmp
```

---

## 4. How does my test get picked up by the full suite?

### Unit and integration tests

**Nothing to do.** pytest discovers any file matching `test_*.py` under `tests/`
automatically, thanks to `testpaths = ["tests"]` in `pyproject.toml`. Your new
function just needs to be named `test_*`.

Run the full suite: `make test`

### Non-regression tests

`make nr-approve` generates the golden `.dot` file(s). From that point on,
`make nr-test` (called by `make test`) picks them up automatically — no registration
needed.

Workflow: `make nr-preview` → inspect SVGs → `make nr-approve` → commit fixtures
and golden files together.
