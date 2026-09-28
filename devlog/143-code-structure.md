# 143 — The graph and the derivation of the view

Date: 2026-09-27
Status: PENDING
Issue: #143 · PR: #144 · Branch: `refactor/143-code-structure`
Task nature: refactor
Track: full
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO 33, from the review of #128: `dsl/filters.py` holds several
concepts and its functions relay the same parameters; extended at
filing to the whole application code. The user mandated an analysis
before stop 0, `discussions/code-structure.md`: eight families of
proposals (A to H) on measurements and four mock-ups. At its review
(2026-09-27) he reshaped the design: the graph, a data structure the
code never had, is the head family (I), and #143 is the graph and the
derivation of the view only. Family A (the filters' concepts as
classes) is absorbed by the derivation; B to H wait in TODO 41 with
the discussion as their brief. Predecessors: #47 rejected a
`FilterEngine` when the module was 260 lines; #100, #104, #127, #137
and #145 brought it to 736, the last one patching the positional
semantics of § 7.5 with `statements[:position]` slices.

### 1.2 Goal

A `Graph` (top-level `graph.py`) carries the items, connections and
frames, and the view stage is a derivation that folds the statements
into the current view, per the user's model (discussion § 3.2): a
declaration joins the view; a keep filter walks the view and fills a
keep list, realized at the next statement of another kind; a `~` and
a merge derive the next view from the current one. The semantics
that follow (discussion § 3.3) are pinned by one fixture each and
stated in § 7.5 of both docs; the glossary gains view, view statement
and derivation. `filters.py` loses its side tables, its second pass
and its in-place mutations; the existing goldens stay byte-identical.

### 1.3 Non-goals

- Families B to H: TODO 41, the discussion § 4 to § 6 as the brief.
- Name reuse after a `~` or a merge (consequence 6): dropped by the
  user on 2026-09-28; the checker's duplicate-name error stays.
- An audit log of the disappearances: the tombstones (name to cause,
  the last record wins) suffice, same date.
- The graph as the carrier through the whole pipeline (checker, star
  resolution, generator): the tests pin the statement list (TODO 40);
  this task builds the graph in the view stage.
- TODO 38 (a merge into a connected item), TODO 32 (`~=`), TODO 37
  (the fixture matrix).
- The existing tests and fixtures: untouched. New fixtures only.

### 1.4 Invariants

- Every call the tests make stays valid, module, name and arguments:
  `scanner.scan`, `parser.parse`, `checker.check`,
  `filters.handle_filters`, `dependency_checker.check`, `dfd.build`,
  `dfd.handle_options`, `dfd.remove_unused_hidables`,
  `markdown.extract_snippets`, `rendering.dot.Generator`,
  `generate_dot`, `main`, `parse_args`, and the `model` classes the
  tests construct with their fields.
- The 124 existing goldens (`.dot`, `.stderr`) byte-identical.
- The three import contexts of `CLAUDE.md` ("Import compatibility");
  `dsl/` and `rendering/` import from the parent only, `graph.py` is
  a top-level module.
- The positional rules 1 to 3 of § 7.5 (#145) hold.
- `engineering/CONVENTIONS.md` and `COMMENTING.md`; `make format`,
  `make lint`, `make test` green at every step.

Framed: pending

### 1.5 Taste

- The user's model is the specification, in his words (discussion
  § 3.2). His rule of thumb from #145: a statement after a view
  statement names items of the view or is an error, never a silent
  drop.
- Fixtures: few, readable, on the 093 master, one per rule of the
  model. Traces: equivalent, not identical. The line count before and
  after is a Try it item.
- Recalled (047, lesson 5): a class when shared mutable state
  accumulates across calls. Recalled (#73): a record is a dataclass,
  a dispatch a `match` ending with `assert_never`.

### 1.6 Set-based design

Triggers: a new container name (`Graph`, `_KeepList`); a thing that
could live in two places (the walk, in the master or in the view); an
intent inherited from a prior task (047's ruling).
Mock-up: yes, three, in one scratch worktree, each green on ruff,
mypy strict, 154 unit tests and 124 goldens (discussion § 3.4).
Design question: which view the walks read, and what state the
derivation keeps.
Options: the three mock-ups.

| Option | What differs                                                                            | For                                                      | Against                                                  |
| ------ | --------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| 1      | The kept set as an immutable `_View` per statement; walks in the master                 | Small change of the semantics                            | The side tables stay (merges, gate, inherited frames)    |
| 2      | Master graph, pending selection, realized current view; walks in the master             | Today's semantics kept                                   | Two graphs to keep consistent; an `ends` reader          |
| 3      | The user's model: the current view only, walks in it, keep list, tombstones (recommend) | No side table, no second pass, no mutation; TODO 39 gone | Changes the language where a filter follows a realization |

### 1.7 Spikes

Ten probes on the 093 master, run on `main` (1.19.1) and on mock-up 3
with `--no-graph-title`, DOT and SVG on both sides in
`/tmp/dfd-review-143/` (discussion § 3.3): six differ as the model
predicts, two are identical, two found consequences 7 and 8.

### 1.8 Design decisions

Rows marked taste are the user's; the rest cite the convention.

| #   | Decision                                                                                                                                          | Basis                                                                | Alternatives considered                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------- |
| 1   | `graph.py` at the top level: a frozen `Graph` of items by name, connections, frames; `with_element`, `names`, `frame_of`, `adjacent`, `flows_touching` | user ("the most important factoring"); CLAUDE.md layout (rule)       | A graph inside `dsl/`; the statement list   |
| 2   | The derivation per the user's model, option 3; vocabulary view, view statement, derivation, three glossary rows                                   | taste                                                                | Options 1 and 2                             |
| 3   | Adjacent keep filters are one compound; a keep list is realized at a `~`, a merge, a declaration or the end                                       | taste (the model)                                                    | A realization at every statement            |
| 4   | A keep filter naming an item the view dropped is an error, with the message of `~` ("no longer available due to previous filters")                 | taste (user, 2026-09-28: explicit over implicit) | A no-op                                     |
| 5   | Consequences 1 to 4 are the language: one fixture each, a § 7.5 sentence in both docs                                                             | taste                                                                | A prior fix PR                              |
| 6   | Consequences 7 and 8 (a frame the view dropped stays dropped through a merge) are the model's, one fixture each                                   | taste (user, 2026-09-28: a removed frame never comes back; a replacer stays in the frame of the items it replaces) | Reproduce the old behavior                  |
| 7   | Consequence 6 dropped; tombstones, no audit log                                                                                                   | user, 2026-09-28                                                     | Name reuse; an audit log                    |
| 8   | Statements compare by identity (`eq=False` on `Base`, `Statement` and its subclasses): the derivation keeps sets of connections                    | option D1 of the discussion; the `id()` sets are the symptom (rule)  | Keep `id()`                                 |
| 9   | `handle_filters` keeps its signature and returns the view's elements in source order, the other statements passed through                        | the tests pin it (rule)                                              | Return the graph (TODO 40)                  |
| 10  | Traces equivalent: one "Items to keep" block per derivation                                                                                       | taste                                                                | Byte-identical traces                       |
| 11  | TODO 39 removed in the step that closes it; TODO 41 filed for B to H                                                                              | PROCESS.md "TODO.md" (rule)                                          |                                             |
| 12  | The PR is a `fix:`: the old behaviors are model flaws with missing tests, not features                                                  | user, 2026-09-28; RELEASING.md | `feat:`, `refactor:`                                 |

### 1.9 Acceptance criteria

1. `make format`, `make lint`, `make test` pass at every step; no
   file under `tests/` that exists on `main` differs from `main`.
2. `make nr-test`: the 124 existing goldens byte-identical, the new
   fixtures pass, each caught by a mutation smoke test.
3. The three import contexts: `make test`, the dev wrapper on a
   fixture, the installed script on a fixture.
4. Measured on the branch: `src/` has no `id(` and no
   `statements[:position]`; `dsl/filters.py` mutates no statement
   (`conn.src =`, `frame.items =`, `item.hidable =` absent);
   `filters.py` plus `graph.py` under 600 lines (736 today).
5. The ten probes give the mock-up 3 column of the discussion § 3.3
   on the branch.
6. § 7.5 of `doc/README.md` and `doc/SYNTAX.md` and the glossary state
   the model; the doc sync test passes.

## 2. Plan

### 2.1 Steps

One pushed commit per step; the steps share one gate (unattended),
each ends with the four checks.

**Step 1 — The graph and the derivation** (`refactor:`)

Files: `model.py`, `graph.py` (new), `dsl/filters.py`,
`engineering/CONVENTIONS.md` (the package tree), `TODO.md` (39 out).

Actions: `eq=False` on the statement classes (mock-up 3's diff);
`graph.py` and `filters.py` from mock-up 3, reviewed against
`COMMENTING.md`; the tree gains `graph.py`; TODO 39 removed.

Verify: the four checks; 124 goldens identical; the greps of
criterion 4; the probes rerun from the review folder.

**Step 2 — Fixtures and documentation** (`fix:`, decision 12)

Files: `tests/non-regression/118-*` to `125-*` (`.dfd`, `.dot` or
`.stderr`), `doc/README.md`, `doc/SYNTAX.md`, `doc/img/` if a doc
example changes.

Actions: one fixture per row of § 3.3 on the 093 master (c1a, c1b
error, c2, c3, c4, c6, c7, c8), its comment naming the rule; goldens
generated, the SVGs gathered in the review folder for Try it; a
mutation smoke test per fixture; § 7.5 rewritten in both docs (rules
1 to 3 kept, the model's rules added); three glossary rows.

Verify: `make nr-test`; the mutation caught; `make test` (doc sync).

**Step 3 — Try it material** (`chore:`)

Files: `devlog/143-*.md`, the PR body.

Actions: the review folder refreshed from the branch (probes, SVGs,
traces of 037 and 098 old and new); the line counts before and after
in Try it; the Account.

### 2.2 Inventory

Produced by reading mock-up 3's diff against the base and
`grep -rn "id(\|statements\[:" src`.

| File                         | Change                                                                                       |
| ---------------------------- | -------------------------------------------------------------------------------------------- |
| `model.py`                   | `eq=False` on `Base`, `Statement` and the ten subclasses; the `Merge` docstring reworded      |
| `graph.py`                   | New: `Element`, `Graph` (`empty`, `build`, `with_element`, `names`, `frame_of`, `adjacent`, `flows_touching`) |
| `dsl/filters.py`             | Rewritten: `_KeepList`, `_Derivation`, `_deduplicate_flows`, `handle_filters`                |
| `engineering/CONVENTIONS.md` | The package tree gains `graph.py`                                                            |
| `TODO.md`                    | 39 removed (closed by step 1); 41 added at scaffolding                                        |
| `tests/non-regression/`      | Eight new fixtures with goldens, 118 to 125                                                  |
| `doc/README.md`              | § 7.5 rewritten                                                                              |
| `doc/SYNTAX.md`              | § 7.5 rewritten; glossary rows view, view statement, derivation                              |

### 2.3 Scope boundary

Not touched even if friction appears: any file under `tests/` that
exists on `main`; `dfd.py`, `checker.py`, `rendering/` (the graph
reaches them with TODO 40); the parser and the DSL syntax; `~=`
(TODO 32); the merge into a connected item (TODO 38).

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
