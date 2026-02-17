# 023 — Add a Non-Regression Tests Framework

**Date:** 2026-02-17
**Status:** DONE

## 1. Requirement

Add a non-regression (NR) test framework that verifies the Graphviz DOT
text generated from DFD sources against committed golden references.

### Workflow

1. The developer creates a DFD source file in `tests/non-regression/`,
   named with a numeric prefix (e.g. `001-items.dfd`).
2. A **preview step** generates the corresponding `.svg` file for visual
   inspection.
3. The developer inspects the SVG. If satisfied, a **confirmation step**
   generates the `.dot` golden file (the Graphviz DOT source text that
   the tool produces internally).
4. Both `.dfd` and `.dot` are committed. The `.svg` is gitignored.
5. When running NR tests, each `.dfd` is loaded, the DOT text is
   regenerated, and compared against the committed `.dot`. Any mismatch
   is a failure.

Each step is triggered by a Makefile target.

## 2. Design

### `--format dot`

A new value `dot` is added to the existing `--format` CLI option. When
specified:

- The tool runs the full pipeline (scan, parse, check, filters, hidable
  removal, options handling, DOT generation) but skips the Graphviz
  rendering step.
- The DOT text is written directly to the output file (or stdout when
  outputting to `-`).
- The default output extension becomes `.dot` (via the existing
  `basename + "." + format` logic).

This requires a small conditional in `dfd.py:build()` or
`__init__.py:handle_dfd_source()`.

No `--no-graph-title` is needed: since the `.dfd` files live at fixed
relative paths in the repository, the derived title is stable and
comparisons remain valid.

### File structure

```
tests/non-regression/
    001-items.dfd                   # Fixture: standalone DFD (committed)
    001-items.dot                   # Golden file (committed after approval)
    001-items.svg                   # Preview render (gitignored)
    022-include-snippet.md          # Fixture: markdown with snippets (committed)
    022-include-snippet/            # Golden files subdirectory
        included-snippet-1.dot
        includer-1.dot
```

Naming: `NNN-description.{dfd,dot,svg}` for standalone tests;
`NNN-description.md` + `NNN-description/*.dot` for markdown tests.
Numbering follows `doc/README.md` section order.

### Makefile targets

| Target            | Action                                                             |
| ----------------- | ------------------------------------------------------------------ |
| `make nr-preview` | Generate SVGs from `*.dfd` and `*.md` fixtures for inspection      |
| `make nr-approve` | Generate golden `.dot` files from all fixtures, print a warning    |
| `make nr-test`    | Regenerate DOT to temp files, diff against golden, fail on mismatch |
| `make nr-clean`   | Remove generated SVGs                                              |

`make nr-approve` finishes by printing a reminder that any git change to
`tests/non-regression/*.dot` files must be carefully examined by the
developer, as it is either deliberate changes, or an early sign of regression.

`make nr-test` exits non-zero on any mismatch. The existing `make test`
target is extended to also run `make nr-test`.

### First test case

`001-items.dfd` — the first example from `doc/README.md`, covering all
item types (process, control, entity, store, channel, none).

## 3. Implementation decisions

### Standalone `.dfd` fixtures (001–018, 020–021, 026)

Each `doc/README.md` example was extracted into a standalone `.dfd` file.
Where the original example used `--markdown` mode (rendering inline within
the doc), the DFD source was lifted out into a plain `.dfd` file with no
dependency on markdown processing.  This gives us coverage of items,
connections, connection sugar, unlabelled items, frames, frame variants,
the complete example, show-all-items, hide-if-unused, context, horizontal
and vertical layouts, constraints (strict and relaxed), attributes,
attribute aliases, wrapping, real-time aspects, and file-based dependencies.

Test 021 covers file-based `#include` (a `.dfd` that includes a `.part`
file).  This works with the existing `.dfd` loop in the NR scripts since
include paths resolve relative to CWD (the project root).

### Markdown-based fixtures (019, 022–025)

The remaining `doc/README.md` examples exercise include and dependency
mechanics that require `--markdown` mode: wrapping with includes, snippet
includes, include-only snippets, nested includes, and snippet-based
dependencies.  These cannot be converted to standalone `.dfd` files
because the `#include #snippet-name` syntax is only available within
markdown processing.

**Key constraint:** `--markdown` mode has no `-o` flag — output paths are
dictated by fence lines inside the `.md` file.  A single `.md` can produce
multiple outputs.

**Sed temp-copy approach for testing:** To avoid overwriting golden files
during test runs, `nr-test.sh` creates a temporary copy of each `.md` with
fence output paths rewritten (`.dot` → `.tmp`) via `sed 's/\.dot$/.tmp/g'`.
The tool then writes `.tmp` files instead, which are diffed against the
golden `.dot` files and cleaned up.  This is safe because:
- Only fence lines end with `.dot` in these test files.
- `#include` references use snippet names (no extension), so they are
  unaffected by the substitution.
- The snippet name is derived from `os.path.splitext(output)[0]`, so
  changing `.dot` to `.tmp` does not alter the name used for include
  resolution.

**Subdirectory structure for `.md` tests:** Each `.md` test's golden
files live in a subdirectory named after the `.md` file (e.g.,
`021-include-snippet/`).  This keeps the flat `NNN-name.{dfd,dot}` layout
for standalone tests while giving markdown tests (which can produce
multiple outputs) a clean namespace.

**Include-only snippets:** Fence names starting with `#` produce no output
file — they exist only as includees for other snippets within the same
`.md`.  Test 024 uses two such snippets to exercise nested include chains.

**Preview for `.md` tests:** `nr-preview.sh` uses a sed approach similar
to `nr-test.sh`, but rewriting fence `.dot` → `.svg` and flattening
`subdir/file` → `subdir--file`.  This generates SVG files flat in the
NR directory for easy inspection.  The `.svg` files are gitignored.

## 4. Implementation summary

### Code changes

- **`src/data_flow_diagram/dfd.py`** — `build()` now checks
  `options.format == "dot"` and writes the DOT text directly, skipping
  Graphviz rendering.
- **`src/data_flow_diagram/__init__.py`** — `"dot"` added to the
  `--format` choices.

### Test infrastructure

- **`tests/nr-preview.sh`** — generates SVGs for `.dfd` fixtures (direct
  `-o`) and `.md` fixtures (sed rewrite `.dot` → `.svg` with path
  flattening `subdir/file` → `subdir--file` for easy browsing).
- **`tests/nr-approve.sh`** — generates golden `.dot` files from both
  `.dfd` and `.md` fixtures.  Creates subdirectories as needed.
- **`tests/nr-test.sh`** — compares regenerated DOT output against golden
  files for both `.dfd` (direct `-o` redirection) and `.md` (sed
  temp-copy approach with `.dot` → `.tmp` rewrite).
- **`tests/non-regression/.gitignore`** — ignores `*.svg` and `*.tmp`.
- **Makefile targets:** `nr-preview`, `nr-approve`, `nr-test`, `nr-clean`;
  `test` extended to include `nr-test`.

### Test cases

| #   | File(s)                          | What it covers                       | Golden files |
| --- | -------------------------------- | ------------------------------------ | ------------ |
| 001 | `001-items.dfd`                  | All item types                       | 1            |
| 002 | `002-connections.dfd`            | All connection types                 | 1            |
| 003 | `003-connections-sugar.dfd`      | Arrow/keyword sugar variants         | 1            |
| 004 | `004-items-unlabelled.dfd`       | Unlabelled items                     | 1            |
| 005 | `005-frame.dfd`                  | Frame with label                     | 1            |
| 006 | `006-frame-without-label.dfd`    | Frame without label                  | 1            |
| 007 | `007-frame-blue.dfd`             | Frame with attributes                | 1            |
| 008 | `008-complete-example.dfd`       | Complete SA/SD example               | 1            |
| 009 | `009-show-all-items.dfd`         | `style show-all-items`               | 1            |
| 010 | `010-hide-if-unused.dfd`         | `style hide-if-unused`               | 1            |
| 011 | `011-context.dfd`                | Context diagram style                | 1            |
| 012 | `012-horizontal.dfd`             | Horizontal layout                    | 1            |
| 013 | `013-vertical.dfd`               | Vertical layout                      | 1            |
| 014 | `014-constraint.dfd`             | Strict constraint                    | 1            |
| 015 | `015-constraint-relaxed.dfd`     | Relaxed constraint                   | 1            |
| 016 | `016-attributes.dfd`             | Item/connection attributes           | 1            |
| 017 | `017-attributes-alias.dfd`       | Attribute aliases                    | 1            |
| 018 | `018-wrapping.dfd`               | Text wrapping and `\n`               | 1            |
| 019 | `019-wrapping-with-include.md`   | Include + style overrides            | 3            |
| 020 | `020-realtime.dfd`               | SA/RT signal and control             | 1            |
| 021 | `021-include-file.{dfd,part}`    | File-based `#include`                | 1            |
| 022 | `022-include-snippet.md`         | Snippet include (`#include #name`)   | 2            |
| 023 | `023-include-only-snippet.md`    | Include-only `#` snippet (no output) | 1            |
| 024 | `024-nested-include.md`          | Chained nested includes              | 1            |
| 025 | `025-dependencies-snippet.md`    | Dependencies via snippet references  | 4            |
| 026 | `026-dependencies-file{,-dep}.dfd` | Dependencies via file reference    | 2            |

**Total: 26 test cases, 33 golden `.dot` files.**
