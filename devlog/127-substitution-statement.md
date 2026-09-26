# 127 — Merge is a statement of its own

Date: 2026-09-25
Status: DONE
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

| #   | Decision                                                                                                                                                                                                                                                                                                                                     | Basis                                                                                                                                        | Alternatives considered                                                   |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | `merge ITEM [ITEM...] : REPLACER`, the replacer declared elsewhere. DSL rule: `:` introduces a name-first tail, a title after a name needs no separator, `=` only for the nameless frame. Anticipated: `frame A B C : F1 Storage`, `merge A B C : store G All DBs`                                                                           | user (stop 0): a word keyword, as every non-filter statement; `=` already marks a frame's title                                              | `=G B C`; `replace G B C`; `process G = All DBs` (breaks the declaration) |
| 2   | A merge is ordered with the filters                                                                                                                                                                                                                                                                                                          | user: order carries meaning                                                                                                                  | Merges first, always                                                      |
| 3   | `~SPEC =G B C` = `merge B C : G` + `~SPECx G`; `~=G B C` = `merge B C : G`; one stderr warning naming the new form                                                                                                                                                                                                                           | user: compatibility; `x` because the group's neighbors go, not the group                                                                     | Break now                                                                 |
| 4   | Option 1                                                                                                                                                                                                                                                                                                                                     | mock-up                                                                                                                                      | 2, 3                                                                      |
| 5   | An anchor removed by a `~` or merged is an error, for `!`, `~` and `merge` alike, and the message names the cause: "no longer available: A (removed at line 5: ~<x1 G)", "(merged into H at line 4: merge G D : H)"                                                                                                                          | user (try-it case 2; review: the old message blamed the filters where a reader saw the merge)                                                | Keep the re-add; a generic message                                        |
| 6   | Flat map (registering resolves and rewrites values); one accessor for the traversal and the strict flow collector                                                                                                                                                                                                                            | user (chain example); § 1.4                                                                                                                  | Resolve loop; statement rewrite (option B, #125 review)                   |
| 7   | The sugar's neighbors are searched before the merge is registered                                                                                                                                                                                                                                                                            | #125 review: searched after, none are found                                                                                                  | Search from the replacer                                                  |
| 8   | Docs: filters and merge stay in chapter 7, retitled "Filters and merge"; its opening and § 7.1 say both only serve to derive subgraphs or simplified graphs from a master graph; `~=` not mentioned                                                                                                                                          | user (stop 1)                                                                                                                                | Own chapter; a "deprecated" note                                          |
| 9   | The seven `~=` fixtures migrate; one sugar twin kept; the try-it cases, the chain, the strict stray flow, `~ X` then `! X` become fixtures                                                                                                                                                                                                   | rule: fixtures lock accepted behavior                                                                                                        | Keep `~=` fixtures                                                        |
| 10  | Frames: the merged items are in one frame or all unframed, else an error ("Cannot merge items from different frames: B (F1), C (no frame)"); the replacer takes their place in that frame, an emptied frame disappears; a replacer declared in another frame is then in two: the checker's frame check, re-run after the filters, reports it | user (stop 0, then the review of the pictures: a group taken out of its frames "as if" was wrong; an error preferred to dropping the frames) | Inherit nothing on a split; drop the frames                               |
| 11  | A merge rewrites the kept set: the replacer takes the merged items' place; once a kept set exists, a merge names kept items only ("Name(s) not kept, cannot be merged: C")                                                                                                                                                                   | user (review of the pictures): an item not kept no longer exists for the statements that follow, so it cannot be merged                      | Merge whatever is kept, ignore the rest (the first wording)               |
| 12  | The replacer must be available; chains are written forward                                                                                                                                                                                                                                                                                   | mock-up: silent resolution would hide a mistake                                                                                              | Resolve through the map                                                   |

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

Approved: 2026-09-25

## 3. Execution

### 3.1 Account

- Steps 1 and 2 (one gate, unattended): the mock-up's source carried
  over as is, then completed: `_check_not_merged()` ("merged by a
  previous statement: G (into H)"), the frame rule in phase two
  (`_inherited_frames()`, `_merge_frame_items()`), `checker.check_frames()`
  public and re-run by `dfd.py`. Decision 10 reworded to the user's
  rule: the first wording excluded a framed replacer from inheriting,
  which made the double-frame error unreachable.
- Fixture 036's golden changed by one line: the old code listed `S0`
  twice in Frame 1 (it removed items while iterating over them); the
  rendered layout is identical (`dot -Tplain`). Regenerated; the
  approved stop condition named this case, accepted as a duplicate
  with no effect.
- Fixtures 093–106 on a part `093-filter-merge-master.part`; `assert_never`
  not added: the statement matches of the pipeline are not exhaustive
  by design.
- Mutation smoke-tests, one per mechanism, each biting (flat map 099;
  strict collector 101; removal through the merges 094–096; keep after
  removal 096, 098, 102; replacer in place of a kept member 098; frame
  rule 104). Two slips of mine on the way: an error fixture that
  succeeds under a mutation leaves a stray `.dot` that makes the runner
  abort silently, and one hand run without `-o` overwrote 098's golden;
  both found and repaired, the runs redone.
- Step 3 (unattended): chapter 7 of both docs as decision 8; the
  README's own § 7.2 example re-added a removed item, which decision 5
  forbids: rewritten as the availability rule. The group example no
  longer lists the super DB in its keep filter (decision 11 makes it
  take the merged DBs' place) and renders the same image; the
  merge-first variant gets `img/filter-merge-first.svg`. The seven
  fixtures migrated, their goldens byte-identical; fixture 094 stays
  the sugar twin. TODO 32 filed for the removal of `~=`.
- Step 4: `devlog/127-try-it/`, the three cases of #125 in both forms
  and two more (keep then merge, the chain), rendered.

- Review (2026-09-26): the master of the merge fixtures becomes a
  fixture of its own, `093-filter-merge-master.dfd`, with its golden
  and its SVG under `make nr-review`, so the filtered pictures can be
  compared with it; the basic case is `093-filter-merge-basic`. The
  two code-structure comments (classes in `filters.py`, the
  `isinstance()` in `parse()` and the line/part parser naming) go to
  TODO 33, a code-only task.

- Review of the pictures (2026-09-26), four points, all taken:
  the availability message names the statement that removed or merged
  the item (decision 5; fixture 064's golden changes accordingly);
  a merge names kept items only once a kept set exists (decision 11;
  098 rewritten with `!>2 A`, 108 the error); items from different
  frames cannot be merged (decision 10; 104 and 109 errors, 105 the
  framed replacer with unframed items; a framed replacer still inherits,
  so 106 keeps its double-frame error); the reviewer's case `merge B C
: G` then `!>x1 A` is fixture 107, G alone. Four mutations, each
  biting. The `Frame` dataclass is unhashable: frames compared by `id()`.

## 4. Delivery

### 4.1 Try it

```bash
xdg-open doc/img/filter-replace.svg doc/img/filter-merge-first.svg
                                  # the README's group example, both orders
xdg-open devlog/127-try-it/2-merge.svg    # no such file: case 2 is an error
./data-flow-diagram devlog/127-try-it/2-sugar.dfd   # the error, and the warning
./data-flow-diagram devlog/127-try-it/1-sugar.dfd   # the warning names the new form
xdg-open devlog/127-try-it/1-merge.svg devlog/127-try-it/3-merge.svg \
         devlog/127-try-it/4-keep-then-merge.svg devlog/127-try-it/5-chain.svg
make nr-review                    # fixtures 093-106, the frame cases 103-106
```

Tried: 2026-09-26 (the fixtures and their pictures reviewed twice, the second review after four points were taken)

### 4.2 Test report

1. Unit: `test_parse_merge`, five parse-error cases, the two
   deprecated forms with their warning (`capsys`): green.
2. Fixtures 093–106 as decided (Account); the seven migrations
   byte-identical; 094 equals 095 but for the title; mutations per
   mechanism bite (Account). Chain, strict and availability cases fail
   on `main`'s code by construction: `main` has no `merge`.
3. The sugar removes A and E (094); the mutation that ignores the
   merges in the neighbor search fails 094, 095 and 096.
4. Frames: 103 (inherit), 104 and 109 (split, mixed: errors), 105
   (framed replacer, unframed items), 106 (double frame: error).
5. `make doc`: one new image, no other changed; 144 pytest, 114 NR
   fixtures, lint and format clean; RULES.md 110+.

### 4.3 Verdict

**Recommendation:** accept with reservations

- Every decision has a fixture, and the try-it cases of #125 render as
  the review decided, in both forms.

Reservations:

1. Fixture 036's golden moved by one line (a duplicated frame member
   the old code produced); the rendered layout is identical. Fixture
   064's golden carries the new availability message.
2. The `-err-` runner leaves a stray `.dot` when an error fixture
   succeeds, which hides the failure behind a silent abort; met twice
   during the mutation runs. A TODO item if you want it fixed.

### 4.4 Discussion

| #   | Point                                                   | Decision                                                               |
| --- | ------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1   | 036's golden line; 064's message                        | accept as is: a duplicated frame member gone, the cause in the message |
| 2   | The runner's stray `.dot` on a succeeding error fixture | postpone: TODO 34                                                      |

Ready: 2026-09-26

## 5. Closure

### 5.1 Retrospective

| #   | Point                                                                                                                                              | Agent    | User       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------- |
| 1   | Process and template fit: full track; stop 0 held a real design round (keyword, grammar rule, frames) and the mock-up decided the option in one go | well     | well       |
| 2   | The mock-up passed the whole suite unchanged before stop 1: the desugaring made the old fixtures the first test of the new statement               | well     | well       |
| 3   | The review of the pictures reversed two decisions taken from the mock-up (11: kept items only; 10: one frame or error): pictures decide, not code  | well     | well       |
| 4   | Stop rule miss of my own: a changed golden (036) was accepted by me at a step gate meant to stop; right in substance, wrong in form                | not well | ended well |
| 5   | The NR runner's stray `.dot` cost two reruns and a lost golden before I understood it; the mutation loop had no cleanup                            | not well | not well   |
| 6   | Prose: the review found AI tells in my doc text; the author's style rules now shape doc/ prose, and TODO 35 makes a project sheet of them          | surprise | well       |
| 7   | The devlog went to 321 lines and was trimmed to 180 on request; pasting the mock-up slice was the excess                                           | tension  | don't care |

Process: 1 round before stop 0; 1 round before stop 1; 2 loops at the review (the pictures, the prose); rework after stop 1: decisions 10 and 11.

Closed: 2026-09-26

### 5.2 Forward-looking

- TODO 32: remove `~=` at a later major. TODO 33: the code-structure
  comments (classes in filters.py, the parser's result type and naming).
  TODO 34: the NR runner's stray `.dot`. TODO 35: a style sheet for the
  project's prose.
- The next tasks can rely on: a `Merge` statement in the model; one
  accessor for a flow's ends in phase one; an unavailable set with the
  cause of each name; the frame check callable after the filters;
  fixtures 093–109 on a master of their own.
- Leftovers to delete: the `mockup/127` worktree and branch; the
  `fix/125-filters-after-replacement` branch on origin, consumed.

### 5.3 Rule trace

| Source                                             | Rule                                                                | Verb (applied / created) |
| -------------------------------------------------- | ------------------------------------------------------------------- | ------------------------ |
| `engineering/CONVENTIONS.md` "Design philosophy"   | Parser scopes: `:` a line-level fact, term regexes know no siblings | applied                  |
| `doc/SYNTAX.md` § 7.3, § 7.5                       | Merge semantics, availability with cause, one frame or error        | created                  |
| `engineering/PROCESS.md` "Implementation workflow" | Stop when a golden changes                                          | applied late (row 4)     |
| `tests/RULES.md`                                   | Mutation smoke-test per mechanism                                   | applied                  |
| Author's style rules (TODO 35)                     | Full clauses, glosses, pivots; no em-dash, no elliptic apposition   | applied                  |
