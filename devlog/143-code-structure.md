# 143 — Code structure of the application

Date: 2026-09-27
Status: PENDING
Issue: #143 · PR: #144 · Branch: `refactor/143-code-structure`
Task nature: refactor
Track: full
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO 33, from the review of #128: `dsl/filters.py` holds several
concepts and its functions relay the same parameters (assess classes);
`dsl/parser.py` tells one statement from a list by `isinstance()`
(assess a `match`, a result type, or a list always) and names a
whole-line parser like a part parser (assess a prefix per kind, or
two classes). Extended at filing to the whole application code under
`src/data_flow_diagram/`; the build, test and tool scripts are for a
later task. Predecessor: #47 (devlog 047, lesson 5) rejected a
`FilterEngine` class when `filters.py` was 260 lines; it is 670 today,
after #100 to #137. The user mandated the analysis before stop 0:
proposals grouped by families, built on measurements and mock-ups in
scratch worktrees, presented in one round with the frame. The
analysis is `discussions/code-structure.md`; this file keeps the
decisions.

### 1.2 Goal

The retained proposals are applied, one step per family, and the
application reads as one design: each concept has one home, the
parameters that a chain of functions relays travel as one object, a
dispatch on kind is a `match` ending with `assert_never`, and the
names say the scope they parse. No test changes, every golden is
byte-identical, the three import contexts work.

### 1.3 Non-goals

- The build, test and tool scripts (`recipes/`, `tools/`, `tests/`,
  the Makefile): a later task, per the user's extension of the scope.
- Any change of behavior or of the DSL, including the removal of
  `~=` (TODO 32, a major) and the debug output's format (open,
  § 1.5).
- A test changed, added or removed: the TODO's constraint. A proposal
  that needs one is rejected or postponed, never bent around.
- The documentation of the DSL (`doc/`): untouched; the package tree
  in `engineering/CONVENTIONS.md` follows a module move, which is
  bookkeeping.

### 1.4 Invariants

- Every call the tests make stays valid, module, name and arguments:
  `scanner.scan`, `parser.parse`, `checker.check`,
  `filters.handle_filters`, `dependency_checker.check` (with
  `file_texts`), `dfd.build`, `dfd.handle_options`,
  `dfd.remove_unused_hidables`, `markdown.extract_snippets`,
  `rendering.dot.Generator` and `generate_dot`, `main`, `parse_args`,
  and the `model` classes the tests construct with their fields
  (`Item`, `Connection`, `Frame`, `Only`, `Without`, `Merge`,
  `FilterNeighbors`, `Style`, `Snippet`, `SourceLine`, `Options`,
  `GraphOptions`, `GraphDependency`, `Keyword`, `Statements`).
- Every golden (`.dot`, `.stderr`) byte-identical: error texts, the
  `~=` warning and the DOT echo comments included.
- The three import contexts of `CLAUDE.md` ("Import compatibility");
  `dsl/` and `rendering/` import from the parent only.
- `engineering/CONVENTIONS.md`: naming, type safety, parser scopes,
  YAGNI + open door; `engineering/COMMENTING.md` for the comments.
- `make format`, `make lint`, `make test` green at every step.

Framed: pending

### 1.5 Taste

- Debug output (`dprint` lines): open. Kept byte for byte, or free to
  change with the structure (no golden pins it). Recalled: the
  `--debug` flag is the author's own tool.
- Recalled (047, lesson 5): explicit parameters between module-level
  functions over `self`-mediated state when the state flows linearly;
  a class when shared mutable state accumulates across calls
  (`Generator`). The analysis measures which case `filters.py` is now.
- Recalled (#73): Python as a fully type-safe language; a record is a
  dataclass, a closed set an enum, a dispatch a `match` ending with
  `assert_never`.

### 1.6 Set-based design

Triggers: an inventory classifying existing items; a thing that could
live in two places (the stages, the style registry); a new container
name (`_Merges`, `styles.py`, `dsl/stars.py`); an intent inherited
from a prior task (047's ruling on classes).
Mock-up: yes, four, in scratch worktrees, each green on ruff, mypy
strict, the 154 unit tests and the 118 goldens; the listings that
decide are in `discussions/code-structure.md` § 3, the families and
their options there. The user mandated the mock-ups before stop 0.
Design question: which option per family; the taste rows below.
Options: per family, in the discussion; summarized here.

| Family                      | Options              | Recommended  | Decides                                                        |
| --------------------------- | -------------------- | ------------ | -------------------------------------------------------------- |
| A filters' concepts         | A0 A1 A2 A3          | A3           | six concept classes, a driver class; 670 to 591 lines          |
| B filters module or package | B0 B1 B2             | B0           | one module, revisited when a concept grows                     |
| C parser result and names   | C0 C1 C2 C3 C6       | C1           | lists always; verbs per scope; C6 rejected on the scopes rule  |
| D model typing and identity | D1 D2a D2b D2c D3 D4 | D1 D2b D3 D4 | `eq=False`, `Literal` subsets, typed generators, `replace`     |
| E stage homes               | E0, E1+E2, E1        | E1+E2        | `styles.py`, `dsl/stars.py`; E3 test-pinned                    |
| F process boundaries        | F1, F2a F2b          | F1 F2a       | Graphviz exits in `cli`; the global as the one debug mechanism |
| G names                     | one table            | apply        | mechanical, pinned names kept                                  |
| H small smells              | 21 rows              | apply        | in the step of the family whose file they touch                |

### 1.7 Spikes

None: every decision reads off a listing, a count or a diff.

### 1.8 Design decisions

Rows marked taste are the user's; the rest cite the convention.

| #   | Decision                                                                                                                                           | Basis                                                          | Alternatives considered                        |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------- |
| 1   | Filters: A3, concept classes and a driver class                                                                                                    | 047 lesson 5 re-measured (rule); CONVENTIONS "Classes"         | A1 one class; A2 objects passed to functions   |
| 2   | Filters stay one module                                                                                                                            | YAGNI + open door (rule)                                       | B1, B2                                         |
| 3   | Parser: every line parser returns a list; a frozen parsed-spec record; a no-neighbors factory                                                      | C1 (option); CONVENTIONS "Type safety" (a record, not a splat) | C2, C3, C6 (rejected, § 3.3 of the discussion) |
| 4   | Parser names: `_parse_` for a line, `_read_` for a term, `_split_` for the cut, `_extract_` for a pass, `_desugar_` for the text stage             | taste (the review asked for a prefix or classes)               | A scope noun after the verb; two classes       |
| 5   | Statements compare by identity (`eq=False` on `Base`, `Statement` and its subclasses)                                                              | D1 (option); the `id()` sets are the symptom                   | Keep `id()`                                    |
| 6   | `ItemType` and `ConnectionType` as `Literal` subsets of `Keyword`; `assert_never` closes the two dispatches; CONVENTIONS amended with one sentence | taste (amends a convention)                                    | D2a status quo; D2c split enums, test-pinned   |
| 7   | `items_of`, `connections_of`, `frames_of` in `model`                                                                                               | D3 (option), ten sites, net −22 lines                          | Keep the idiom                                 |
| 8   | `styles.py` and `dsl/stars.py`; `STAR_ITEM_FMT` to `config`                                                                                        | CONVENTIONS "Target package structure", "Constants" (rule)     | E0; E1 only                                    |
| 9   | Graphviz raises, `cli.main` exits; same stderr and codes                                                                                           | CLAUDE.md layout, `cli.py` is the I/O module (rule)            | Status quo                                     |
| 10  | The global is the one debug mechanism; `debug`/`options` parameters dropped where no test passes them                                              | taste (a global against the type-safety preference)            | F2b the parameter alone                        |
| 11  | Naming sweep and 21 smells applied in the step of their file; pinned names kept                                                                    | CONVENTIONS "Functions and methods" (rule)                     |                                                |
| 12  | The debug output stays byte-identical (checked under a fixed hash seed), since the mock-ups showed it costs nothing                                | taste, § 1.5 closed                                            | Free to change                                 |

### 1.9 Acceptance criteria

1. `make format`, `make lint`, `make test` pass at every step; no file
   under `tests/` differs from `main`.
2. `make nr-test`: 118 fixtures pass, goldens byte-identical (no
   `nr-regenerate` on the branch).
3. `--debug` output identical to `main` on the 107 diagram fixtures
   under `PYTHONHASHSEED=0`.
4. The three import contexts: `make test` (pytest), the dev wrapper
   on a fixture, the wheel's console script (`make smoke-test-wheel`
   or the installed script on a fixture).
5. Measured on the branch: `dsl/filters.py` has one function with
   four or more parameters and no parameter relayed past one hop;
   `parse()` has no `isinstance`; `src/` has no `id(`, no `__dict__`,
   no `getattr`/`setattr` on a statement, no `sys.exit` outside
   `cli.py`, no `case _: raise` on a kind.
6. `tests/unit/test_pipeline.py` lines listed in § 5 of the
   discussion are untouched; the pinned proposals are in a TODO item.

## 2. Plan

### 2.1 Steps

One pushed commit per step; the steps share one gate (unattended),
each ends with the four checks and criterion 3's diff.

**Step 1 — Model foundations** (`refactor:`): D1, D3, D4. Files:
`model.py`, `dsl/checker.py`, `dsl/dependency_checker.py`, `dfd.py`,
`dsl/filters.py` (the `id()` sites), `rendering/dot.py`.

**Step 2 — Filters as concept classes** (`refactor:`): A3 on step 1,
smells 1 to 3. Files: `dsl/filters.py`.

**Step 3 — Parser result and names** (`refactor:`): C1, the naming,
D2 (`model.py`, `rendering/dot.py`, the two factory annotations),
smells 4 to 8, CONVENTIONS "Type safety" and "Parser scopes"
sentences. Files: `dsl/parser.py`, `model.py`, `rendering/dot.py`,
`engineering/CONVENTIONS.md`.

**Step 4 — Stage homes and boundaries** (`refactor:`): E1, E2, F1,
F2a, smells 12 to 16, 19, 21; CONVENTIONS tree and "Constants".
Files: `dfd.py`, `styles.py` (new), `dsl/stars.py` (new),
`config.py`, `rendering/templates.py`, `rendering/graphviz.py`,
`exception.py`, `cli.py`, `dsl/scanner.py`, `dsl/parser.py`,
`dsl/filters.py`, `dsl/dependency_checker.py`,
`tools/doc-print-style-table.py` (one line), `engineering/CONVENTIONS.md`.

**Step 5 — Names and small smells** (`refactor:`): G, the remaining
rows of H, the TODO item of § 5. Files: as the tables say.

### 2.2 Inventory

Produced by `tools/`-free greps quoted in the discussion (§ 2 script,
`grep -rn "id(\|__dict__\|getattr\|setattr\|sys.exit"`); the sweep
at each step repeats them.

| File                             | Change                                                                                         |
| -------------------------------- | ---------------------------------------------------------------------------------------------- |
| `model.py`                       | `eq=False`; `ItemType`, `ConnectionType`; `items_of` and siblings; registry out; `repr` folded |
| `styles.py`                      | New: the style registry and `apply_style`, `get_style_int`                                     |
| `dsl/stars.py`                   | New: `resolve_star_endpoints`                                                                  |
| `dfd.py`                         | Orchestrator only, plus the two test-pinned stages                                             |
| `dsl/filters.py`                 | Six classes, three functions, `handle_filters`                                                 |
| `dsl/parser.py`                  | Lists, record, factory, names by scope, sugar table, sections                                  |
| `dsl/checker.py`                 | Typed generators                                                                               |
| `dsl/dependency_checker.py`      | Typed generators; the gate; `_find_item`                                                       |
| `dsl/scanner.py`                 | `debug` out; `_include`; docstring; `line`                                                     |
| `rendering/dot.py`               | `assert_never`; `replace`; dead `Style` branch out; names                                      |
| `rendering/graphviz.py`          | Raises `GraphvizException`                                                                     |
| `rendering/templates.py`         | `STAR_ITEM_FMT` out                                                                            |
| `config.py`                      | `ITEM_STAR_NAME_FMT` in                                                                        |
| `exception.py`                   | `exit_code`, `GraphvizException`, `has_errors()`, `_make_prefix`                               |
| `cli.py`                         | Exits and the DOT listing; keyword-only `handle_markdown_source`                               |
| `console.py`                     | The name the debug decision gives it                                                           |
| `markdown.py`                    | `make_snippet_contexts`; the `StringIO` name                                                   |
| `engineering/CONVENTIONS.md`     | Tree, "Type safety", "Constants", "Parser scopes"                                              |
| `tools/doc-print-style-table.py` | Reads `styles.STYLE_SPECS`                                                                     |
| `TODO.md`                        | The test-pinned item                                                                           |

### 2.3 Scope boundary

Not touched even if friction appears: any file under `tests/` (§ 5
of the discussion goes to a TODO item); `doc/`; the scripts beyond the
one line of `tools/doc-print-style-table.py`; the DSL and its error
texts; `~=` (TODO 32).

Approved: pending

## 3. Execution

### 3.1 Account

## 4. Delivery

### 4.1 Try it

Tried: pending

### 4.2 Test report

### 4.3 Verdict

### 4.4 Discussion

Ready: pending

## 5. Closure

### 5.1 Retrospective

| #   | Point                    | Agent | User |
| --- | ------------------------ | ----- | ---- |
| 1   | Process and template fit |       |      |

Closed: pending

### 5.2 Forward-looking

### 5.3 Rule trace
