# 127 — Substitution statement

Date: 2026-09-25
Status: PENDING
Issue: #127 · PR: #128 · Branch: `feature/127-substitution-statement`
Task nature: change
Track: full
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Origin: the review of PR #126 (issue #125, TODO 23), stopped as a dead
end on 2026-09-25 (`devlog/125-filters-after-replacement.md`, status
REJECTED). The fix of the orphan pictures after `~=` ran into a
conceptual flaw: `~=G B C` conflates a substitution (the flows of B
and C rewired to G, B and C unavailable) with a filter, and every rule
that fix had to decree (a leading `~=` does not initialise the kept
set, whether it takes neighbors, what a later `!` may name) exists
only because of that conflation. The review's own questions (why a map
rather than a rewrite; what of chained replacements; why no neighbors
on a leading `~=`) and the pictures of `devlog/125-try-it/` led to the
concept; issue #127 is its brief. Material: the branch
`fix/125-filters-after-replacement` (the traversal through the
rewiring, `_check_not_replaced()`, fixtures 093–096, the README
§ 7.4.2.2 group-first example and image, the deferred-reading
experiment), left on origin unmerged. Predecessors: #100 (flows between
two replaced groups), #104 (the strict filter and its flow ids), #123
(one neighbor specification per filter; the parser scopes,
`engineering/CONVENTIONS.md` "Design philosophy").

### 1.2 Goal

`=G B C` is a statement of its own, a substitution: the flows of B and
C are rewired to G, B and C become unavailable, the kept set is not
touched. It is processed in source order with the filters, because the
order carries meaning: `!` before `=` selects on the original graph and
then collapses, `=` before `!` selects on the grouped graph. The former
`~[SPEC] =G B C` still parses, as sugar for `=G B C` followed, when a
spec is given, by `~SPECx G`, with a deprecation warning on stderr; the
docs no longer show it. A filter naming an item that a previous filter
removed or a substitution replaced is an error. Chained substitutions
compose (`=G B C` then `=H G D` on `A→B→C→D` gives `A→H`). Every valid
diagram of the fixtures and the docs renders as before, in the new
form.

### 1.3 Non-goals

- Removing `~=`: the sugar keeps every existing diagram valid; the
  removal is a later major, with a stronger reason.
- `!=` or any keep-side substitution: a substitution is not a filter,
  it has no side.
- A symmetrical layout neighborhood `[]`: TODO 30, its own feature.
- Substituting with a name that does not exist as an item: the
  replacer stays a declared item, as today (`process G Group`).
- A frame option on `=`: the frame rule (decision 10) needs no switch,
  and frame removal by selection is the `f` flag of the filters.

### 1.4 Invariants

- Parser scopes (`engineering/CONVENTIONS.md` "Design philosophy"):
  the keyword decides the split; `=G` is split as `!A` is, a space
  inserted after the mnemonic; the term regexes know no siblings; the
  sequence rules live in the statement parser.
- The two-phase filter design (`filters.py`): phase one decides, the
  kept set, the substitution map, the flow-id sets; phase two applies
  once. The map is read through one accessor by every reader of phase
  one, and stays flat: reading a flow through it gives the ends a
  rewrite would have written (the invariant that makes the lazy map
  equal to a rewrite).
- Statement order carries meaning since filters exist (#104); a
  substitution is ordered with them.
- Goldens of the existing fixtures do not change, except where the
  availability rule turns a re-add into an error (none found: no
  fixture or doc example names, in a `!`, an item a previous `~`
  removed).
- Type safety (`engineering/CONVENTIONS.md`): a `Substitution`
  dataclass, keyword-only calls, `assert_never` on the statement
  match.

Framed: pending

### 1.5 Taste

- Recalled (#123): one specification per filter; a DRY form that
  multiplies test combinations is refused.
- Recalled (#125 review): a concept is decided from pictures, not
  prose; the try-it cases are the acceptance pictures.
- Recalled (#121): adding accepted syntax is said in the draft and
  decided by the user; here the new syntax is the point, and the
  sugar is the compatibility.
- Stated (#125 review): deprecate with a stderr warning rather than
  break.

### 1.6 Set-based design

Triggers: a new container name (`Substitution`, the keyword `=`); an
intent inherited from a prior task (#125's rules); one conceptual row
among mechanical churn (the desugaring's home).
Mock-up: yes, in a throwaway worktree, before stop 1: the model
dataclass, the `parse()` loop accepting one line to yield two
statements, the `=` mnemonic in `_apply_syntactic_sugars()`, a
`Substitution` case in `_collect_kept_names()`, and the try-it cases
rendered.
Design question: where the desugaring of `~SPEC =G B C` lives.
Options: three, below; the recommended one is option 1.

| Option                                                      | What differs                                                                                                                                                        | For                                                                                                                    | Against                                                                                                                   |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1. The parser yields two statements for the deprecated line | `parse()` accepts a list from a statement parser; `Without.replaced_by` disappears from the model; `_parse_filter()` warns and returns `[Substitution, Without(x)]` | The model never sees the conflation again; filters.py handles one `Substitution` case; the warning has the source line | `parse()` grows a list branch; both statements carry the same source line (fine for errors)                               |
| 2. filters.py desugars                                      | `Without.replaced_by` stays; `_collect_kept_names()` treats a `Without` with a replacer as substitution then removal                                                | No parser change beyond `=`                                                                                            | The conflation stays in the model and in the filter code; two code paths for one concept; the warning far from the source |
| 3. A pre-pass rewrites the source line                      | The sugar step rewrites `~<1 =G B C` into two source lines before parsing                                                                                           | Parser and model untouched by the deprecation                                                                          | The line-level sugar step learns term syntax (the spec, the replacer), against the parser scopes rule                     |

### 1.7 Spikes

- Warning channel: `console.print_error()` writes to stderr, red on a
  terminal; a `print_warning()` twin (yellow) is one function. A
  non-`-err-` NR fixture compares the DOT only, so the warning text is
  locked by a unit test with `capsys`, not by a fixture.
- Chain and strict reader: reproduced on `main` at the #126 review
  (`~=G B C` then `~=H G D` renders A and H with no flow; a rewired
  stray flow touching a strict selection is shown). Both become
  fixtures that fail on `main`.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                            | Basis                                                                                                                                      | Alternatives considered                                                                                                                                        |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `=REPLACER ITEM [ITEM...]`, keyword `=`, a `Substitution` statement; `=G` split by the mnemonic rule like `!A`                                                                                                                                                                                                                                                                                                                                      | user (the #125 review): a substitution is not a filter                                                                                     | A word keyword (`replace G B C`): the DSL's statement operators are symbols (`!`, `~`); `=` is already the replacer sign                                       |
| 2   | A substitution touches no kept set; it is ordered with the filters                                                                                                                                                                                                                                                                                                                                                                                  | user: order carries meaning, `!` then `=` collapses a selection, `=` then `!` selects on the grouped graph                                 | Process substitutions first, always (loses the `!`-first meaning of the doc example)                                                                           |
| 3   | `~SPEC =G B C` is sugar for `=G B C` then `~SPECx G`; `~=G B C` alone for `=G B C`; a stderr warning names the new form                                                                                                                                                                                                                                                                                                                             | user: compatibility without breaking; the `x` flag because the neighbors of the group are removed, not the group                           | Break now (a major for one form fewer)                                                                                                                         |
| 4   | Option 1: the parser yields the two statements                                                                                                                                                                                                                                                                                                                                                                                                      | option 1                                                                                                                                   | 2, 3 above                                                                                                                                                     |
| 5   | Availability: an anchor removed by a previous `~` or substituted is an error, for `!` and `~` alike                                                                                                                                                                                                                                                                                                                                                 | user (case 2 of the try-it); SYNTAX.md § 7.4 rule 3 already says it; no fixture depends on the re-add                                      | Keep the re-add (today's `!` check against all names)                                                                                                          |
| 6   | The substitution map is flat: registering `=H G D` resolves H through the map and rewrites every value G into H; one accessor gives a flow's ends to the traversal and to the strict flow collector                                                                                                                                                                                                                                                 | user (the chain example); the invariant of § 1.4                                                                                           | A resolve loop on every read; a rewrite of the statements after each `=` (option B of the #125 review, rejected: phase two relies on the untouched statements) |
| 7   | A substitution's neighbors, in the sugar, are searched before the registration: the neighbors of the group as it stands                                                                                                                                                                                                                                                                                                                             | found at the #125 review: searched after, the anchors' flows already lead to the replacer and nothing is found                             | Search from the replacer                                                                                                                                       |
| 8   | The docs show `=` only: README § 7.3 gains "Substitution", § 7.4.2.2 uses it; SYNTAX.md § 7.2 loses `[=REPLACEMENT]`, a § 7.x "Substitution" and the glossary term                                                                                                                                                                                                                                                                                  | user: the docs do not mention the deprecated form                                                                                          | A "deprecated" note in the docs                                                                                                                                |
| 9   | Fixtures: the eight files using `~=` migrate to `=`; one fixture keeps `~=` for the sugar (same DOT as its `=` twin); the try-it cases become fixtures (case 2 an error, case 3 the `A→Group` picture, block J); the chain; the strict stray flow after a substitution; `~ X` then `! X` as an error                                                                                                                                                | rule: fixtures lock accepted behavior; the pictures of the review are the acceptance                                                       | Keep `~=` in the fixtures (they would exercise the deprecated path only)                                                                                       |
| 10  | Frames: the replacer inherits a frame only when every replaced item belongs to that one frame and the replacer is declared in none; otherwise it inherits nothing (the replaced items leave their frames, an emptied frame disappears). A replacer declared in a frame keeps it. The frame check of the checker ("is in multiple frames") is re-run on the filtered statements by `dfd.py`, so an inherited frame plus a declared one is that error | user (stop 0 discussion): unnamed frames cannot be chosen; measured on `main`: the replacer inherited every frame, an item in two clusters | An error on any ambiguity; an option on `=`                                                                                                                    |

### 1.9 Acceptance criteria

1. `=G B C` parses to a `Substitution`; `= G B C`, `=G` alone, `=G G`
   raise; `~=G B C` and `~<1 =G B C` parse to the two statements and
   print one warning line naming the new form (unit, `capsys`).
2. Fixtures: the migrated eight render byte-identical DOT; the sugar
   twin renders as its `=` twin; the try-it cases render as decided
   (case 2 an `-err-` fixture); the chain gives `A→H`; the strict
   stray flow after a substitution is hidden; `~ X` then `! X` errors.
   The chain, the strict and the availability fixtures fail on `main`
   (mutation smoke-test by the pre-fix code).
3. `make doc` regenerates the README images with the `=` form, the
   § 7.4.2.2 pictures unchanged.
4. `make format lint test` green; `tests/RULES.md` next number
   updated; mypy sees `assert_never` on the statement match.
5. The sugar `~<1 =G B C` on the try-it base removes A and E (the
   neighbors of the group as it stands): a fixture, failing under the
   mutation that searches after the registration.
6. Frames: three fixtures, the unambiguous inheritance (036's case),
   a group spanning two frames (the replacer unframed, no frame kept,
   the frames keep their other members), a framed replacer with a
   framed group (its own frame only); and an `-err-` fixture for the
   framed replacer that would also inherit.

## 2. Plan

### 2.1 Steps

**Step 1 — Model and parser** (`feat:`)

Files: `model.py`, `dsl/parser.py`, `console.py`,
`tests/unit/test_parser.py`.

Actions:

1. `Keyword.SUBSTITUTE = "="`; `Substitution(Statement)` with
   `replacer: str`, `names: list[str]`; `Without` loses `replaced_by`.
2. `_apply_syntactic_sugars()`: `=` joins the mnemonics that get a
   space inserted (longest first, `!!` before `!`).
3. `_parse_substitution()`: replacer then one name at least, none
   equal to the replacer; registered in `_PARSERS`.
4. `parse()` accepts a statement parser returning a list; the
   post-parse match gets a `Substitution` case and `assert_never`.
5. `_parse_filter()`: the replacer form warns through
   `console.print_warning()` ("line N: `~=` is deprecated: write `=G B
C`, then `~<1x G` for the neighbors") and returns the two
   statements; the "one replacer per filter" and "bare `=`" errors
   stay.
6. Unit cases: criterion 1.

Verify: `make format lint`; `uv run pytest tests/unit/test_parser.py`
green; the NR suite still green (the filters still accept the old
model? no: step 2 lands the filter side, so the suite is green at the
end of step 2; steps 1 and 2 share one step gate).

Commit: `feat: substitution statement "=", the "~=" form desugared with a warning`

**Step 2 — Filters** (`feat:`)

Files: `dsl/filters.py`, `tests/unit/test_dfd.py`, fixtures.

Actions:

1. `_ends(conn, substitution)`: the one accessor; used by
   `_collect_connected_names()` and `_collect_flow_ids()`.
2. The flat map: `_register(substitution, replacer, names)` resolves
   the replacer and rewrites existing values.
3. `_collect_kept_names()`: a `Substitution` case (register, mark the
   names unavailable, kept set untouched); `Only` and `Without` check
   their anchors against the unavailable set (removed by a `~`, or
   substituted); the `Without` case loses its replacer branch; the
   neighbor search of a `Without` reads through the map.
4. Phase two: reads the same map; frame membership by decision 10
   (inherit when unambiguous, else drop the replaced names); `dfd.py`
   re-runs the checker's frame check after the filters.
5. Fixtures (decisions 9 and 10, criteria 5 and 6) and their goldens; the mutation smoke-test
   against `main`'s `filters.py` for the chain, the strict stray flow
   and the availability error.

Verify: `make format lint test` green; `make nr-test` after the
smoke-test.

Commit: `feat: substitutions ordered with the filters, one map read through one accessor`

**Step 3 — Docs and migration** (`docs:`)

Files: `doc/README.md`, `doc/SYNTAX.md`, `README.md` if it shows a
filter, the eight `~=` files, `tests/RULES.md`.

Actions:

1. README § 7.3: a "Substitution" subsection (`=REPLACER ITEM...`,
   ordered with the filters, both orders' meanings); § 7.3.2 without
   the replacer; § 7.4.2.2 in the new form, plus the group-first
   variant from the #125 branch.
2. SYNTAX.md: § 7.2 without `[=REPLACEMENT]`; a "Substitution" entry;
   § 7.4 rules: availability, substitution ordered, chains.
3. The eight files to `=`; `make doc`.

Verify: `make doc` changes the two README images only where the
example text changed (none expected); `make test` green.

Commit: `docs: the substitution statement, the "~=" form gone from the docs`

**Step 4 — Try it and closure** (`chore:`)

The try-it of #125 rendered under the new code: case 1 unchanged,
case 2 the error, case 3 the picture; the devlog's Delivery filled.

### 2.2 Inventory

| File                                                                   | Change                                                                                                      |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `src/data_flow_diagram/model.py`                                       | `Keyword.SUBSTITUTE`, `Substitution`; `Without.replaced_by` removed                                         |
| `src/data_flow_diagram/dsl/parser.py`                                  | `=` mnemonic, `_parse_substitution()`, list-returning parsers, the deprecated form desugared with a warning |
| `src/data_flow_diagram/console.py`                                     | `print_warning()`                                                                                           |
| `src/data_flow_diagram/dsl/filters.py`                                 | accessor, flat map, `Substitution` case, availability, replacer branch removed, frame inheritance rule      |
| `src/data_flow_diagram/dsl/checker.py`, `src/data_flow_diagram/dfd.py` | the frame check callable on its own, re-run after the filters                                               |
| `doc/README.md`, `doc/SYNTAX.md`                                       | § 7.3 and § 7.4 as decided                                                                                  |
| `tests/non-regression/`                                                | eight migrations, one sugar twin, the new fixtures                                                          |
| `tests/unit/test_parser.py`, `tests/unit/test_dfd.py`                  | the cases of criteria 1 and 2                                                                               |
| `tests/RULES.md`                                                       | next number                                                                                                 |

### 2.3 Scope boundary

- `[]`: TODO 30.
- The removal of `~=`: a later major; a TODO item filed on this
  branch when the sugar lands, so the debt has a number.
- The lint-blocking hook (TODO 29) and the batch process (TODO 31):
  not this branch.

Approved: pending
