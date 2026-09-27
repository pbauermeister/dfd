# 143 — Code structure of the application

Date: 2026-09-27
Status: PENDING
Issue: #143 · PR: #PPP · Branch: `refactor/143-code-structure`
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

- The API the tests call keeps its module, name and signature:
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
