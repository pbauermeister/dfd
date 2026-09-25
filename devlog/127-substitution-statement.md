# 127 — Merge statement

Date: 2026-09-25
Status: PENDING
Issue: #127 · PR: #128 · Branch: `feature/127-substitution-statement`
Task nature: change
Track: full
Agent: Claude Fable 5.1 (to the mock-up), then Claude Opus 5.5

## 1. Mandate

### 1.1 Context

Origin: the review of PR #126 (issue #125, TODO 23), stopped as a dead
end (`devlog/125-filters-after-replacement.md`, REJECTED). `~=G B C`
conflates a substitution (flows of B and C rewired to G, B and C
unavailable) with a filter; every rule that fix had to decree exists
only because of that conflation. Issue #127 is the brief. Material:
branch `fix/125-filters-after-replacement` (rewired traversal, fixtures
093–096, the § 7.4.2.2 group-first example), `devlog/125-try-it/`.
Predecessors: #100, #104 (strict filter, flow ids), #123 (one neighbor
spec per filter; parser scopes in `engineering/CONVENTIONS.md`).

### 1.2 Goal

`merge B C : G` is a statement of its own: the flows of B and C are
rewired to G, B and C become unavailable. It is ordered with the
filters: `!` then `merge` selects on the original graph and collapses,
`merge` then `!` selects on the grouped graph. The former `~[SPEC] =G B
C` still parses, as sugar for `merge B C : G` then `~SPECx G`, with a
deprecation warning on stderr; the docs no longer show it. A filter
naming an item removed or merged earlier is an error. Chains compose.
Every valid fixture and doc diagram renders as before.

### 1.3 Non-goals

- Removing `~=`: a later major, with a stronger reason.
- `!=` or any keep-side substitution: a merge is not a filter.
- `[]`: TODO 30. A frame option on `merge`: decision 10 needs none.
- A replacer that is not a declared item; the one-shot declaring merge
  and named frames (anticipated by decision 1, not built).

### 1.4 Invariants

- Parser scopes: the keyword decides the split, the `:` of a `merge`
  line is a line-level fact; term regexes know no siblings; sequence
  rules live in the statement parser.
- Two-phase filters: phase one decides, phase two applies once. The
  merge map is read through one accessor by every reader and stays
  flat: a flow read through it has the ends a rewrite would write.
- Goldens of existing fixtures unchanged (no fixture or doc example
  re-adds, in a `!`, an item a `~` removed).
- Type safety: a `Merge` dataclass, keyword-only calls, `assert_never`.

Framed: 2026-09-25

### 1.5 Taste

- Recalled: one spec per filter (#123); concepts decided from pictures
  (#125); new accepted syntax decided by the user (#121).
- Stated: deprecate with a stderr warning rather than break.

### 1.6 Set-based design

Triggers: a new container name (`Merge`, keyword `merge`); an intent
inherited from #125; one conceptual row (where the desugaring lives).
Mock-up: built in the worktree `mockup/127` (material for steps 1–2).
The whole suite passes on it unchanged: 136 unit tests, every golden
byte-identical, the seven `~=` fixtures going through the desugaring.
Pictures on the try-it base (A and E feed B, B → C → D → F):

| Case                                                   | Result                                                            |
| ------------------------------------------------------ | ----------------------------------------------------------------- |
| `merge B C : G` + `~<x1 G`, and the sugar `~<1 =G B C` | identical: G → D → F; warning `write: merge B C : G, then ~<x1 G` |
| the same, then `!>1 A`                                 | error: A no longer available (try-it case 2)                      |
| `merge B C : G` + `!>1 A`, and the sugar `~=G B C`     | A → G (case 3)                                                    |
| `!>1 A B` then `merge B C : G`                         | A → G: the replacer takes the kept member's place                 |
| `merge B C : G` then `merge G D : H`; reversed         | A → H, E → H, H → F; reversed: error, G merged away               |
| `B -> X`, `merge B C : G`, `!!<1 D`, `! X`             | G → D only: the rewired stray flow G → X hidden                   |
| `merge B C`, `merge : G`, `merge B C : B`              | the three parse errors                                            |

Design question: where the desugaring of `~SPEC =G B C` lives.

| Option                          | For                                                                                       | Against                                               |
| ------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1. Parser yields two statements | the model loses `replaced_by`; one `Merge` case in filters.py; warning at the source line | `parse()` accepts a list (four lines)                 |
| 2. filters.py desugars          | no parser change                                                                          | the conflation stays in model and filters; two paths  |
| 3. Pre-pass rewrites the line   | parser and model untouched                                                                | the line level learns term syntax, against the scopes |

The mock-up decided option 1.

### 1.7 Spikes

- Warning: `print_warning()`, a yellow twin of `print_error()`; an NR
  fixture compares DOT only, so the text is locked by a unit test.
- Chain and strict reader: both wrong on `main` (#126 review); both
  become fixtures that fail there.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                                                                                                                                       | Basis                                                                                           | Alternatives considered                                                   |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | `merge ITEM [ITEM...] : REPLACER`, the replacer declared elsewhere. DSL rule: `:` introduces a name-first tail, a title after a name needs no separator, `=` only for the nameless frame. Anticipated: `frame A B C : F1 Storage`, `merge A B C : store G All DBs`             | user (stop 0): a word keyword, as every non-filter statement; `=` already marks a frame's title | `=G B C`; `replace G B C`; `process G = All DBs` (breaks the declaration) |
| 2   | A merge is ordered with the filters                                                                                                                                                                                                                                            | user: order carries meaning                                                                     | Merges first, always                                                      |
| 3   | `~SPEC =G B C` = `merge B C : G` + `~SPECx G`; `~=G B C` = `merge B C : G`; one stderr warning naming the new form                                                                                                                                                             | user: compatibility; `x` because the group's neighbors go, not the group                        | Break now                                                                 |
| 4   | Option 1                                                                                                                                                                                                                                                                       | mock-up                                                                                         | 2, 3                                                                      |
| 5   | An anchor removed by a `~` or merged is an error, for `!` and `~`                                                                                                                                                                                                              | user (try-it case 2); SYNTAX.md § 7.4 rule 3                                                    | Keep the re-add                                                           |
| 6   | Flat map (registering resolves and rewrites values); one accessor for the traversal and the strict flow collector                                                                                                                                                              | user (chain example); § 1.4                                                                     | Resolve loop; statement rewrite (option B, #125 review)                   |
| 7   | The sugar's neighbors are searched before the merge is registered                                                                                                                                                                                                              | #125 review: searched after, none are found                                                     | Search from the replacer                                                  |
| 8   | Docs: filters and merge stay in chapter 7, retitled "Filters and merge"; its opening and § 7.1 say both only serve to derive subgraphs or simplified graphs from a master graph; `~=` not mentioned                                                                            | user (stop 1)                                                                                   | Own chapter; a "deprecated" note                                          |
| 9   | The seven `~=` fixtures migrate; one sugar twin kept; the try-it cases, the chain, the strict stray flow, `~ X` then `! X` become fixtures                                                                                                                                     | rule: fixtures lock accepted behavior                                                           | Keep `~=` fixtures                                                        |
| 10  | Frames: the replacer inherits a frame only when all merged items are in that one frame and it is declared in none; else nothing, an emptied frame disappears; a framed replacer keeps its frame; the checker's frame check re-runs after the filters ("is in multiple frames") | user (stop 0); `main` put the replacer in every frame                                           | Error on ambiguity; an option                                             |
| 11  | A merge rewrites the kept set: a kept merged item is replaced by the replacer                                                                                                                                                                                                  | mock-up: the group vanished after a keep filter                                                 | Require the replacer kept                                                 |
| 12  | The replacer must be available; chains are written forward                                                                                                                                                                                                                     | mock-up: silent resolution would hide a mistake                                                 | Resolve through the map                                                   |

### 1.9 Acceptance criteria

1. Unit: `merge B C : G` parses; `merge : G`, `merge B C :`, `merge B
C`, `merge B C : B`, `merge B C : G H` raise; both sugar forms give
   the two statements and one warning line (`capsys`).
2. Fixtures: the seven migrations byte-identical; the sugar twin equals
   its `merge` twin; try-it case 2 an `-err-` fixture, case 3 A → G;
   the chain A → H, its reverse an error; keep then merge; the strict
   stray flow hidden; `~ X` then `! X` an error. Chain, strict and
   availability fixtures fail on `main`'s code.
3. The sugar `~<1 =G B C` removes A and E; fails under the mutation
   that searches after registration.
4. Frames: unambiguous inheritance (036's case), a group over two
   frames, a framed replacer, and the `-err-` double frame.
5. `make doc` leaves the pictures unchanged; `make format lint test`
   green; `tests/RULES.md` updated.

## 2. Plan

### 2.1 Steps

Steps 1 and 2 share one step gate: the suite is green only after both.

**Step 1 — Model and parser** (`feat:`). `model.py`: `Keyword.MERGE`,
`Merge(names, replacer)`, `Without` loses `replaced_by`.
`parser.py`: `_parse_merge()` split at `:`; `parse()` accepts a list;
`_desugar_replacer()` with the warning, the "one replacer" and "bare
`=`" errors kept. `console.py`: `print_warning()`. Unit cases of
criterion 1. Commit: `feat: merge statement, the "~=" form desugared
with a warning`.

**Step 2 — Filters** (`feat:`). `filters.py`: `_ends()` and
`_register_merge()`; the `Merge` case (decisions 5, 6, 11, 12); `Only`
and `Without` checked against the unavailable set; frame membership by
decision 10; `checker.py` frame check callable alone, re-run by
`dfd.py`. Fixtures of criteria 2–4 with the mutation smoke-tests.
Commit: `feat: merges ordered with the filters, one map read through
one accessor`.

**Step 3 — Docs and migration** (`docs:`). README § 7 as decision 8,
a "Merge" subsection in § 7.3, § 7.4.2.2 with `merge` plus the
group-first variant; SYNTAX.md § 7 intro, § 7.2 without the replacer,
a merge entry, § 7.4 rules; the seven fixtures migrated; `make doc`.
Commit: `docs: the merge statement, "~=" gone from the docs`.

**Step 4 — Try it** (`chore:`). The #125 try-it under the new code;
Delivery filled.

### 2.2 Inventory

| File                                   | Change                                                        |
| -------------------------------------- | ------------------------------------------------------------- |
| `model.py`                             | `Keyword.MERGE`, `Merge`; `Without.replaced_by` removed       |
| `dsl/parser.py`, `console.py`          | `_parse_merge()`, list-returning parsers, desugaring, warning |
| `dsl/filters.py`                       | accessor, flat map, `Merge` case, availability, frame rule    |
| `dsl/checker.py`, `dfd.py`             | frame check re-run after the filters                          |
| `doc/README.md`, `doc/SYNTAX.md`       | chapter 7 as decided                                          |
| `tests/non-regression/`, `tests/unit/` | migrations, sugar twin, new fixtures and unit cases           |

### 2.3 Scope boundary

`[]` (TODO 30); the removal of `~=` (a TODO item filed here when the
sugar lands); TODO 29 and 31.

Approved: pending
