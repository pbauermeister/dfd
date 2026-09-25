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

`merge B C : G` is a statement of its own, a substitution: the flows of B and
C are rewired to G, B and C become unavailable, the kept set is not
touched. It is processed in source order with the filters, because the
order carries meaning: `!` before `=` selects on the original graph and
then collapses, `=` before `!` selects on the grouped graph. The former
`~[SPEC] =G B C` still parses, as sugar for `merge B C : G` followed, when a
spec is given, by `~SPECx G`, with a deprecation warning on stderr; the
docs no longer show it. A filter naming an item that a previous filter
removed or a substitution replaced is an error. Chained substitutions
compose (`merge B C : G` then `merge G D : H` on `A→B→C→D` gives `A→H`). Every valid
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
  the keyword decides the split, and the `:` of a `merge` line is a
  line-level fact like the keyword; the term regexes know no siblings;
  the sequence rules live in the statement parser.
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
- Type safety (`engineering/CONVENTIONS.md`): a `Merge`
  dataclass, keyword-only calls, `assert_never` on the statement
  match.

Framed: 2026-09-25

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

Triggers: a new container name (`Merge`, the keyword `merge`); an
intent inherited from a prior task (#125's rules); one conceptual row
among mechanical churn (the desugaring's home).
Mock-up: yes, built in a throwaway worktree (`mockup/127`, kept as
the material of steps 1 and 2): the model, `_parse_merge()`, the
`parse()` loop yielding one statement or two, `_desugar_replacer()`,
`_ends()` and `_register_merge()`, the `Merge` case, the availability
set. The whole suite passes unchanged on it: 136 unit tests, every
golden byte-identical, the seven `~=` fixtures now going through the
desugaring. The slice that decides, the parser's side:

```python
def _parse_merge(source: model.SourceLine) -> model.Statement:
    """Parse merge ITEM [ITEM...] : REPLACER"""
    head, sep, tail = source.text.partition(":")
    if not sep:
        raise exception.DfdException("Expected ': REPLACER' after the items")
    names = head.split()[1:]
    replacers = tail.split()
    ...
    return model.Merge(source=source, names=names, replacer=replacers[0])


def _desugar_replacer(f, *, replacer, spec) -> list[model.Statement]:
    """The deprecated "~[SPEC] =R ITEMS": a merge, then the neighbors' removal."""
    merge = model.Merge(source=f.source, names=f.names, replacer=replacer)
    if spec is None:
        print_warning(f"'~=' is deprecated, write: {hint}")
        return [merge]
    f.neighbors_up.suppress_anchors = True      # the x flag: the group's
    f.neighbors_down.suppress_anchors = True    # neighbors, not the group
    without = model.Without(**f.__dict__); without.names = [replacer]
    print_warning(f"'~=' is deprecated, write: {hint}, then ~{spec_x} {replacer}")
    return [merge, without]
```

and `parse()` reads `for statement in parsed if isinstance(parsed, list)
else [parsed]:`. The pictures, on the try-it base (A and E feed B, B → C
→ D → F, G the group, H a super group):

| Case                                                      | Result                                                                                       |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `merge B C : G` then `~<x1 G`, and the sugar `~<1 =G B C` | identical: G → D → F, A and E removed; the warning reads `write: merge B C : G, then ~<x1 G` |
| the same, then `!>1 A`                                    | error: A no longer available (try-it case 2)                                                 |
| `merge B C : G` then `!>1 A`, and the sugar `~=G B C`     | A → G (case 3)                                                                               |
| `!>1 A B` then `merge B C : G`                            | A → G: the replacer takes the place of the kept member                                       |
| `!>1 A` then `merge C D : G`                              | A → B, untouched: nothing kept was merged                                                    |
| `merge B C : G` then `merge G D : H`                      | A → H, E → H, H → F: the chain, flat map                                                     |
| `merge G D : H` then `merge B C : G`                      | error: G no longer available (merged away)                                                   |
| `B -> X`, `merge B C : G`, `!!<1 D`, `! X`                | G → D only: the rewired stray flow G → X touching the strict selection is hidden             |
| `merge B C`, `merge : G`, `merge B C : B`                 | the three parse errors                                                                       |

Design question: where the desugaring of `~SPEC =G B C` lives.
Options: three, below; the mock-up decided option 1: the parser side is
forty lines, the model has no replacer field left, and filters.py has
one `Merge` case.

| Option                                                      | What differs                                                                                                                                                        | For                                                                                                             | Against                                                                                                                   |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1. The parser yields two statements for the deprecated line | `parse()` accepts a list from a statement parser; `Without.replaced_by` disappears from the model; `_parse_filter()` warns and returns `[Substitution, Without(x)]` | The model never sees the conflation again; filters.py handles one `Merge` case; the warning has the source line | `parse()` grows a list branch; both statements carry the same source line (fine for errors)                               |
| 2. filters.py desugars                                      | `Without.replaced_by` stays; `_collect_kept_names()` treats a `Without` with a replacer as substitution then removal                                                | No parser change beyond `=`                                                                                     | The conflation stays in the model and in the filter code; two code paths for one concept; the warning far from the source |
| 3. A pre-pass rewrites the source line                      | The sugar step rewrites `~<1 =G B C` into two source lines before parsing                                                                                           | Parser and model untouched by the deprecation                                                                   | The line-level sugar step learns term syntax (the spec, the replacer), against the parser scopes rule                     |

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

| #   | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                            | Basis                                                                                                                                                                                                                                                                                                                                                                                                            | Alternatives considered                                                                                                                                                                                       |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `merge ITEM [ITEM...] : REPLACER`, keyword `merge`, a `Merge` statement; the items first, then `:`, then the replacer, an item declared elsewhere                                                                                                                                                                                                                                                                                                   | user (stop 0 discussion): a substitution is not a filter, so a word keyword like every non-filter statement; `=` already means "a title follows" in `frame`; the rule adopted for the DSL: `:` introduces a name-first tail, a title needs no separator after a name, `=` stays for the nameless frame only. Anticipated, not built: `frame A B C : F1 Storage` and the one-shot `merge A B C : store G All DBs` | `=G B C` (a third meaning of `=`, a symbol for a non-filter); `replace G B C` (verb with inverted order); `process G = All DBs` for full consistency (breaks the basic declaration and drags the flow labels) |
| 2   | A substitution touches no kept set; it is ordered with the filters                                                                                                                                                                                                                                                                                                                                                                                  | user: order carries meaning, `!` then `=` collapses a selection, `=` then `!` selects on the grouped graph                                                                                                                                                                                                                                                                                                       | Process substitutions first, always (loses the `!`-first meaning of the doc example)                                                                                                                          |
| 3   | `~SPEC =G B C` is sugar for `merge B C : G` then `~SPECx G`; `~=G B C` alone for `merge B C : G`; a stderr warning names the new form                                                                                                                                                                                                                                                                                                               | user: compatibility without breaking; the `x` flag because the neighbors of the group are removed, not the group                                                                                                                                                                                                                                                                                                 | Break now (a major for one form fewer)                                                                                                                                                                        |
| 4   | Option 1: the parser yields the two statements                                                                                                                                                                                                                                                                                                                                                                                                      | option 1                                                                                                                                                                                                                                                                                                                                                                                                         | 2, 3 above                                                                                                                                                                                                    |
| 5   | Availability: an anchor removed by a previous `~` or substituted is an error, for `!` and `~` alike                                                                                                                                                                                                                                                                                                                                                 | user (case 2 of the try-it); SYNTAX.md § 7.4 rule 3 already says it; no fixture depends on the re-add                                                                                                                                                                                                                                                                                                            | Keep the re-add (today's `!` check against all names)                                                                                                                                                         |
| 6   | The substitution map is flat: registering `merge G D : H` resolves H through the map and rewrites every value G into H; one accessor gives a flow's ends to the traversal and to the strict flow collector                                                                                                                                                                                                                                          | user (the chain example); the invariant of § 1.4                                                                                                                                                                                                                                                                                                                                                                 | A resolve loop on every read; a rewrite of the statements after each `=` (option B of the #125 review, rejected: phase two relies on the untouched statements)                                                |
| 7   | A substitution's neighbors, in the sugar, are searched before the registration: the neighbors of the group as it stands                                                                                                                                                                                                                                                                                                                             | found at the #125 review: searched after, the anchors' flows already lead to the replacer and nothing is found                                                                                                                                                                                                                                                                                                   | Search from the replacer                                                                                                                                                                                      |
| 8   | The docs show `=` only: README § 7.3 gains "Substitution", § 7.4.2.2 uses it; SYNTAX.md § 7.2 loses `[=REPLACEMENT]`, a § 7.x "Substitution" and the glossary term                                                                                                                                                                                                                                                                                  | user: the docs do not mention the deprecated form                                                                                                                                                                                                                                                                                                                                                                | A "deprecated" note in the docs                                                                                                                                                                               |
| 9   | Fixtures: the eight files using `~=` migrate to `=`; one fixture keeps `~=` for the sugar (same DOT as its `=` twin); the try-it cases become fixtures (case 2 an error, case 3 the `A→Group` picture, block J); the chain; the strict stray flow after a substitution; `~ X` then `! X` as an error                                                                                                                                                | rule: fixtures lock accepted behavior; the pictures of the review are the acceptance                                                                                                                                                                                                                                                                                                                             | Keep `~=` in the fixtures (they would exercise the deprecated path only)                                                                                                                                      |
| 10  | Frames: the replacer inherits a frame only when every replaced item belongs to that one frame and the replacer is declared in none; otherwise it inherits nothing (the replaced items leave their frames, an emptied frame disappears). A replacer declared in a frame keeps it. The frame check of the checker ("is in multiple frames") is re-run on the filtered statements by `dfd.py`, so an inherited frame plus a declared one is that error | user (stop 0 discussion): unnamed frames cannot be chosen; measured on `main`: the replacer inherited every frame, an item in two clusters                                                                                                                                                                                                                                                                       | An error on any ambiguity; an option on `=`                                                                                                                                                                   |
| 11  | A substitution rewrites the kept set as it rewrites the flows: when a merged item is kept, the replacer takes its place (`!>1 A B` then `merge B C : G` shows A → G); when none is, the kept set is untouched                                                                                                                                                                                                                                       | mock-up: without it the group vanished silently after a keep filter, where `main` errors ("db_all" had to be listed in the doc example's `!`); a substitution is a rewrite of everything the merged names appear in                                                                                                                                                                                              | Require the replacer to be kept (an error); leave the group unkept                                                                                                                                            |
| 12  | The replacer must be available: merging into an item already merged away is an error; a chain is written forward (`merge B C : G` then `merge G D : H`)                                                                                                                                                                                                                                                                                             | mock-up (chain reversed): the replacer is an anchor like the others; resolving it silently would hide a mistake                                                                                                                                                                                                                                                                                                  | Resolve the replacer through the map                                                                                                                                                                          |

### 1.9 Acceptance criteria

1. `merge B C : G` parses to a `Merge`; `merge : G`, `merge B C :`,
   `merge B C`, `merge B C : B` and `merge B C : G H` raise; `~=G B C` and `~<1 =G B C` parse to the two statements and
   print one warning line naming the new form (unit, `capsys`).
2. Fixtures: the migrated eight render byte-identical DOT; the sugar
   twin renders as its `merge` twin; the try-it cases render as decided
   (case 2 an `-err-` fixture); the chain gives `A→H` and its reverse errors; a keep filter then a
   merge shows the replacer in place of the kept member; the strict
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

1. `Keyword.MERGE = "merge"`; `Merge(Statement)` with `names:
list[str]`, `replacer: str`; `Without` loses `replaced_by`.
2. `_parse_merge()`: the terms before `:` are the items, one at least,
   the one term after it the replacer, none of the items equal to it;
   registered in `_PARSERS`.
3. (merged into 2)
4. `parse()` accepts a statement parser returning a list; the
   post-parse match gets a `Merge` case and `assert_never`.
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

Commit: `feat: merge statement, the "~=" form desugared with a warning`

**Step 2 — Filters** (`feat:`)

Files: `dsl/filters.py`, `tests/unit/test_dfd.py`, fixtures.

Actions:

1. `_ends(conn, substitution)`: the one accessor; used by
   `_collect_connected_names()` and `_collect_flow_ids()`.
2. The flat map: `_register(substitution, replacer, names)` resolves
   the replacer and rewrites existing values.
3. `_collect_kept_names()`: a `Merge` case (register, mark the
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

1. README § 7.3: a "Merge" subsection (`merge ITEM... : REPLACER`,
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
| `src/data_flow_diagram/model.py`                                       | `Keyword.MERGE`, `Merge`; `Without.replaced_by` removed                                                     |
| `src/data_flow_diagram/dsl/parser.py`                                  | `=` mnemonic, `_parse_substitution()`, list-returning parsers, the deprecated form desugared with a warning |
| `src/data_flow_diagram/console.py`                                     | `print_warning()`                                                                                           |
| `src/data_flow_diagram/dsl/filters.py`                                 | accessor, flat map, `Merge` case, availability, replacer branch removed, frame inheritance rule             |
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
