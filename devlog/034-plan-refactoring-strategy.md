# 034 — Plan refactoring strategy: identifiers, structure, DSL pipeline

**Date:** 2026-02-18

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/34

## Requirement

Create a comprehensive refactoring strategy that plans several future
tasks. This issue covers planning only — no production code changes,
but non-regression tests may be added to anchor current behaviour.

## Scope exclusion

**DSL parsing theory is out of scope.** The current parsing approach
(mix of regex, match-case, string comparisons, code-based parsers) has
evolved organically with ease of use in mind. A redesign using formal
grammar / parser generator techniques may be warranted, but that is a
separate, larger series of tasks. The DSL syntax itself is frozen for
backward compatibility.

## Deliverables

- This strategy document with sequenced task descriptions.
- Naming and structure conventions: `doc/CONVENTIONS.md`.
- Any additional non-regression test cases needed to make refactoring
  safe (delivered as part of task A).

## Naming conventions analysis

Before codifying conventions, we analysed the existing codebase:

| Pattern                  | Count | Percentage |
| ------------------------ | ----- | ---------- |
| Action-first (verb\_obj) | 54    | 98%        |
| Topic-first (obj\_verb)  | 0     | 0%         |
| Other                    | 1     | 2%         |

Comparison with industry conventions:

| Convention set          | Function naming     | Module naming     |
| ----------------------- | ------------------- | ----------------- |
| PEP 8                   | No preference       | Short, lowercase  |
| Google Python Style     | Verb or verb_phrase | Lowercase         |
| Clean Code (Martin)     | Verbs/verb phrases  | Nouns (domain)    |
| Python standard library | Action-first        | Noun              |
| Django / Flask          | Action-first        | Noun/role         |
| **This project**        | **Action-first**    | **Noun/role**     |

**Decision:** Codify the existing action-first convention. It matches
both the codebase's organic evolution and industry consensus. Full
rules are published in `doc/CONVENTIONS.md`; CLAUDE.md references it.

## Strategy: sequenced refactoring tasks

### A — Non-regression tests

**Goal:** Anchor current behaviour so that all subsequent refactoring
tasks can be validated mechanically.

**Actions anticipated:**

- Add non-regression test fixtures for **filters** — the biggest gap.
  Cover `!` (only) and `~` (without) with neighbour expansion,
  direction specifiers (`<`, `>`, `<>`, `[`, `]`), flags (`x`, `f`),
  distance (`*`, numeric), and replacements (`=name`). This is the
  most complex feature and has zero dedicated tests today.
- Add non-regression fixtures for **error cases** — malformed input,
  duplicate items, invalid connection endpoints, recursive includes,
  unknown snippets. These anchor the error messages which could
  otherwise silently change during refactoring.
- Review existing 34 non-regression fixtures and verify they cover all
  item types, connection variants, and style options. Fill any gaps.
- Consider adding unit tests for `scanner.scan()` in isolation (line
  continuations, include resolution, snippet vs file).

**Inter-aspect dependencies:** This task has no prerequisites and
blocks all subsequent tasks. The filter tests in particular are
critical for tasks F and H, which will restructure `handle_filters`.
Error-message tests matter for task D, which will change how errors
are constructed.

---

### B — Consolidate scattered constants

**Goal:** Gather magic values into `config.py` (or a small number of
well-defined locations as described in `doc/CONVENTIONS.md`) so they
are easy to find and adjust.

**Actions anticipated:**

- Audit all modules for literal values that act as configuration:
  colours (`"#eeeeee"`, `"white"`, `"grey"`), Graphviz attribute
  strings (`ITEM_EXTERNAL_ATTRS`), font specifications in
  `dfd_dot_templates.py`, shape names, etc.
- Move them to `config.py` or to a dedicated section in
  `dfd_dot_templates.py` (for Graphviz-specific constants), with
  clear names.
- Remove the existing TODO in `config.py`.

**Inter-aspect dependencies:** None — this is self-contained. Doing it
before the structural moves (F, H) avoids having to relocate these
constants twice.

---

### C — CLI entry point relocation

**Goal:** Move CLI logic out of `__init__.py` into a dedicated module
(`cli.py`), so that `__init__.py` serves only as the package
interface.

**Actions anticipated:**

- Create `cli.py` with `parse_args()`, `run()`,
  `handle_markdown_source()`, `handle_dfd_source()`, and `main()`.
- Reduce `__init__.py` to re-exports and the `VERSION` constant.
- Keep `main()` re-exported from `__init__.py` so that both entry
  points work unchanged:
  - pip install: `data_flow_diagram:main` (console script in
    `setup.py`)
  - local dev: `./data-flow-diagram` imports
    `src.data_flow_diagram` and calls `main()`
- Fix the stale `"UML sequence input file"` help string (known issue).

**Inter-aspect dependencies:** None — this is a mechanical move. Doing
it before F avoids confusion about where orchestration code lives
when deciding module boundaries.

---

### D — Streamline error handling

**Goal:** Replace the repetitive `prefix = mk_err_prefix_from(src)` +
`raise DfdException(f"{prefix}...")` pattern with a more concise
mechanism.

**Actions anticipated:**

- Evaluate two approaches:
  - **(a)** A helper function `raise_dfd_error(source, message)` that
    builds the prefix and raises in one call.
  - **(b)** Make `DfdException` carry a `SourceLine` and format the
    prefix in `__str__`. This is cleaner but requires updating every
    `except DfdException` site that reads `str(e)`.
- Whichever approach is chosen, apply it across all modules:
  - `parser.py` (~8 sites), `dependency_checker.py` (~5 sites),
  - `dfd.py` (~4 sites), `scanner.py` (~3 sites).
  - adapt the tests if needed.

**Inter-aspect dependencies:** The non-regression tests (A) should
include error-message tests before this task changes how messages are
constructed. After D, the error-handling code will be shorter, which
makes the structural moves in F easier to read and review.

---

### E — *(excluded — DSL parsing theory, separate series)*

---

### F — Define module boundaries and move code ✔ (#45, PR #46)

**Goal:** Restructure the package into sub-packages following the
target layout defined in `doc/CONVENTIONS.md`, reducing `dfd.py` from
~710 lines to a thin orchestrator.

**Actions anticipated:**

- Create `dsl/` sub-package:
  - Move `scanner.py` → `dsl/scanner.py`
  - Move `parser.py` → `dsl/parser.py`
  - Extract `handle_filters()` + `find_neighbors()` from `dfd.py` →
    `dsl/filters.py` (~260 lines, self-contained filter engine)
  - Move `dependency_checker.py` → `dsl/checker.py`
- Create `rendering/` sub-package:
  - Extract `Generator` class + `generate_dot()` + `wrap()` from
    `dfd.py` → `rendering/dot.py` (~300 lines, DOT generation)
  - Move `dfd_dot_templates.py` → `rendering/templates.py`
  - Move `dot.py` → `rendering/graphviz.py` (Graphviz binary
    invocation)
- Decide where `handle_options()` and `remove_unused_hidables()` fit:
  orchestrator (`dfd.py`) or one of the sub-packages.
- Keep `build()` in `dfd.py` as the pipeline orchestrator.
- Update all import paths throughout the codebase and tests.
- Follow naming conventions from `doc/CONVENTIONS.md`: module names
  are lowercase nouns, path order is generic → specific.

**Inter-aspect dependencies:** Depends on B (constants in place), C
(CLI separated), and D (error handling streamlined) — all three reduce
the amount of code that must move. The filter tests from A are
essential because `handle_filters` is being relocated. Task F directly
enables H (function breakup within new modules) and J (renaming on
stable structure).

---

### H — Break up large functions

**Goal:** Split oversized functions into smaller, well-named units
within their (now properly located) modules. Function names must
follow the action-first convention defined in `doc/CONVENTIONS.md`.

**Actions anticipated:**

- `handle_filters()` (201 lines, 3 phases) → split into methods of a
  `FilterEngine` class, or into three top-level functions
  (`collect_kept_names`, `apply_filters`, `deduplicate_connections`).
  The choice depends on whether shared state (kept_names, replacement,
  skip_frames_for_names) is better modelled as instance attributes or
  passed explicitly.
- `Generator.generate_item()` (55 lines) → consider extracting the
  per-type DOT emission into a dispatch table or helper methods.
- `Generator.generate_connection()` (~70 lines) → similar treatment.
- `parser.check()` (86 lines, 3 validation passes) → consider
  splitting into `check_items`, `check_connections`, `check_frames`.
- `_parse_filter()` (99 lines) → evaluate whether the direction /
  flags / span parsing can be extracted into a helper.

**Inter-aspect dependencies:** Depends on F (code must be in its final
module before splitting). The tests from A (especially filter tests)
are the safety net. Task H enables I (testability) and J (renaming)
by creating smaller, more focused units.

---

### I — Improve testability (functional stages)

**Goal:** Make pipeline stages independently testable by reducing I/O
coupling and making data flow explicit.

**Actions anticipated:**

- `build()` currently does file I/O (writing output, calling
  Graphviz). Refactor so the core pipeline returns DOT text, and I/O
  is handled by the caller. This makes it possible to unit-test the
  full pipeline without touching the filesystem.
- Ensure each extracted module (filters, rendering) exposes a pure
  function: statements in → statements out (filters), statements in →
  DOT text out (rendering).
- Add unit tests that exercise each stage in isolation with
  programmatically constructed `model.Statements` (not just
  end-to-end `.dfd` → `.dot` comparisons).
- Consider whether `dependency_checker.check()` (which calls
  `scanner.scan` + `parser.parse` recursively) can be made more
  testable via dependency injection or by accepting pre-parsed data.

**Inter-aspect dependencies:** Depends on F and H (stages must be
properly separated and functions small enough to test in isolation).
May produce additional tests that strengthen the safety net
established in A.

---

### J — Align identifiers to glossary

**Goal:** Rename classes, methods, variables, and constants to match
the official terminology in `doc/SYNTAX.md`, making code and
documentation speak the same language.

**Actions anticipated:**

- Systematic audit of all identifiers against the glossary. The
  analysis found few critical mismatches (the codebase already uses
  "item" not "node" in most places), but a thorough pass is needed.
- Rename local variables where they use informal terms (e.g.
  `framed_items` is fine, but check for stale names that survived
  from earlier iterations).
- Avoid clashes with Python builtins/keywords (e.g. `filter`, `type`,
  `input` are already used as parameter names in some places —
  evaluate whether to rename them).
- Update comments and docstrings to match any renamed identifiers.
- This is the most mechanical task but also the most pervasive — every
  module will be touched.

**Inter-aspect dependencies:** Must come last. Renaming before
structural moves (F, H) would create unnecessary merge pain and
double work. By this point the module structure is stable, functions
are small and well-located, and the renames can be applied cleanly.
All tests from A (and I) validate that renames don't change behaviour.

---

## Dependency graph

```
A (tests)
├──► B (constants)
├──► D (error handling) ── uses A's error-message tests
├──► C (CLI entry point)
│
├──► F (module boundaries) ── uses A's filter tests
│    │
│    └──► H (break up functions) ── uses A's filter tests
│         │
│         ├──► I (testability)
│         └──► J (identifier alignment) ── uses all tests
```

B, C, D are independent of each other and can be done in any order
(or in parallel) after A. F depends on B+C+D being done (less code
to move). H depends on F. I and J depend on H and can be done in
either order.
