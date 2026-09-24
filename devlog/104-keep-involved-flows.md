# 104 — Keep only the flows involved by a "keep" filter

Date: 2026-09-24
Status: ONGOING
Issue: #104 · PR: #105 · Branch: `feature/104-keep-involved-flows`
Task nature: change
Track: full
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Issue #104. A neighbor filter (`!<>2 P4`) selects a set of names:
the anchors plus the nodes reached by successive waves of
connections, per direction and span
(`find_neighbors()` in `src/data_flow_diagram/dsl/filters.py`).
The connections are then kept by a single rule in `_apply_filters()`:
both ends in the kept set. A flow between two kept nodes therefore
survives even when it lies on no path that led to keeping them. In
the issue's example, two chains lead to P4 (`P1 → P2 → P3 → P4`,
`P5 → P6 → P7 → P4`) with cross flows `15`, `26`, `37`; `!<>2 P4`
keeps P2, P3, P6, P7 and every flow among them, including `26`
(P2 → P6), which is on no 2-hop path to P4, whereas `37` is (`37`
then `74`).

State of the code: the filter model is `Filter` with two
`FilterNeighbors` (up, down) carrying `distance`, `suppress_anchors`
(`x` flag), `layout_direction`, `suppress_frames` (`f` flag);
the flags are parsed in `dsl/parser.py` from a letter group after
the span. Neighbor expansion records names only: the connections
traversed are not kept. Predecessors: #101 and #103 (devlogs 100, 102) settled how rewired flows to replacement groups pass the kept
check.

### 1.2 Goal

A "keep" filter has an option under which only the flows lying on an
n-degree path from its anchors, in the direction and span the filter
states (upstream, downstream, left, right), are kept; the other flows
between kept nodes are dropped. In the issue's example the option
drops `26` and keeps `23`, `34`, `67`, `74`, `37`. With several keep
filters, a flow dropped by one is kept when another filter's path
traversal covers it. The syntax of the option and the way path
membership is computed are the two design questions of this task,
settled in § 1.6 Set-based design. The syntax reference in
`doc/README.md` § 7 documents the option; NR fixtures lock the
example and the multi-filter case in.

### 1.3 Non-goals

- Changing the default behavior: without the option, the kept-set
  rule stays as it is, so every existing diagram renders unchanged.
- The "without" filter (`~`): the issue asks for the keep filter; a
  subtractive counterpart, if wanted, is its own issue.
- Constraints (`-->` style, `Keyword.CONSTRAINT`): they define no
  neighborhood today and stay out of path traversal.
- A special treatment of undirected flows (`BFLOW`, `UFLOW`): the
  issue expects path traversal to handle them as it does for
  neighborhood; confirmed or refuted by the mock-up, a deviation
  becomes a design decision, not a new goal.

### 1.4 Invariants

- Filters compose as a sequence over one kept set (`doc/README.md`
  § 7.2): the option restricts flows, never names; the kept names of
  a filter are the same with and without the option.
- Replacement groups (`~=`) are nodes like any other for path
  traversal: a rewired flow is on a path when the flow it stands for
  is.
- `dsl/` imports from the parent package only
  (`CLAUDE.md` "Layout").
- Type safety per `engineering/CONVENTIONS.md`: the option is a
  field of the filter model, parsed once, no string flags carried
  downstream.

Framed: 2026-09-24 ("Confirmed")

### 1.5 Taste

- A new construct is easier to spot and remember as a keyword than
  as a letter: `!!` reads "like `!`, but stronger" (stop 0 review).
- Flags qualify the neighborhood and belong after the span
  (`<>2xf`), as the doc says and the examples contradict; a new flag
  would worsen that inconsistency (stop 0 review; TODO item 21).
- Recalled: fixtures land before the code, goldens generated with the
  code in place, so that the history shows them failing (devlogs
  100, 102); one check, one code path.

### 1.6 Set-based design

Triggers: an intent inherited from the issue (two open questions
named there); a thing that could live in two places (the path
membership, computed during traversal or as a pass over the kept set);
a new container name (the concept needed a name for the doc).
Mock-up: yes, in a throwaway worktree, twice: first a1+b1+c1 (62
diff lines in `dsl/filters.py`), then a2+b1+c3 after the stop 0
review (95 insertions, 25 deletions over `model.py`, `dsl/parser.py`,
`dsl/filters.py`); `make lint` and `make test` on the second green,
no existing golden changed.
Design questions: (a) the syntax of the option; (b) the computation
of path membership; (c), surfaced by the first mock-up: how a strict
filter composes with the other keep filters.
Options: one row per option; chosen: a2, b1, c3.

Vocabulary (decision 1): the **strict only filter** `!!`; the
**path flows** of a filter, the flows it followed to reach its
neighbors; the **stray flows**, flows between kept items that are on
no path.

| Option | What differs                                                                                                                                                                                                                                                                              | For                                                                                                                                                                                                                                       | Against                                                                                                                                                                                  |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a1     | A flag letter `p` (paths) in the existing group: `!<>p2 P4`, stored in `FilterNeighbors`, combined per filter like `x`                                                                                                                                                                    | Smallest diff: three parser lines; the doc row sits next to `x` and `f`                                                                                                                                                                   | One more letter and its mnemonic to remember; per direction by syntax but whole-filter by meaning, a rule to document; sits in a flag group whose order the doc and the code disagree on |
| a2     | A filter keyword `!!`: `!!<>2 P4`, `!! A B`. A `Keyword.ONLY_STRICT` member, `model.Only.strict: bool`, the space-insertion sugar tries the longest mnemonic first, a third `_PARSERS` entry                                                                                              | Reads "like `!`, but stronger"; whole-filter by construction; no flag, so the flag-order question is untouched; `~~` stays an error since removed items take their flows away                                                             | One more prefix in a language of `!` and `~`; 23 parser lines instead of 3                                                                                                               |
| a3     | A suffix on the span: `!<>2. P4` or `!<>2! P4`                                                                                                                                                                                                                                            | Visually tied to the span it qualifies                                                                                                                                                                                                    | A regex change, cryptic, a third place where options live                                                                                                                                |
| b1     | During traversal: `_collect_connected_names()` returns the connections it followed with the names; `_expand_neighbors_in_dir()` accumulates their identities wave by wave; a flow is a path flow iff followed                                                                             | One code path decides neighborhood and paths, so reversed, undirected and layout-direction flows are handled once; `id()` survives the endpoint rewrite by replacement, which gives the invariant on groups for free; smallest diff       | `_FilterDecisions` carries sets of object ids, identity-based rather than value-based (documented in place)                                                                              |
| b2     | Post-pass: after the kept names, recompute the wave layers per strict filter and test each kept flow against the layer of its source end                                                                                                                                                  | Traversal untouched                                                                                                                                                                                                                       | The direction rules (reversed, `BFLOW`/`UFLOW`, layout direction) exist twice and must be kept in sync; a second traversal per strict filter                                             |
| b3     | Hybrid: traversal records the per-wave name sets, a post-pass tests the flows against them                                                                                                                                                                                                | No object identities                                                                                                                                                                                                                      | Same two places as b2 for the direction rules; the rewrite by replacement happens after, so the test must run on the original names, a subtlety b1 does not have                         |
| c1     | Global mode: once one strict filter exists, a flow is kept iff both ends are kept and some strict filter followed it; a plain `!` adds names, no flows                                                                                                                                    | One sentence; the union across strict filters is the issue's "kept by another filter"                                                                                                                                                     | One `!!` flips what every plain `!` means (a mode switch); `! A B` next to a strict filter shows A and B without their flow; obtainable flow sets are unions of stars only (below)       |
| c2     | Local, between: a strict filter vetoes the flows _between_ the items it selects; its path flows and the flows between items a plain `!` selects together are allowed; allow beats veto                                                                                                    | No mode switch: with no `!!` nothing is vetoed; `! P2 P6` next to `!!<>2 P4` shows `26`                                                                                                                                                   | Two strict filters side by side show every flow between their neighborhoods, since such a flow is between no single selection; `!!` twice does not give a path-only diagram              |
| c3     | Local, touching: as c2, but a strict filter vetoes the flows _touching_ the items it selects, whoever brought the other end. Rule: a flow is shown iff both ends are kept and it is not vetoed, or is a path flow of some strict filter, or joins two items named together by a plain `!` | No mode switch; two strict filters compose into a path-only view; the items a `!!` selects show only their path flows, which is what "stronger" promises; plain `!` overrides pair by pair; order-free for flows, the fold stays on items | Two-clause rule for the doc (veto, and what beats it); one more set in the decisions (vetoed and allowed)                                                                                |

Runs of the second mock-up (a2, b1, c3), flows only. Base: the
issue's example.

```
!!<>2 P4                       !!<>2 P4  ! P2 P6                !!<2 P4  !!>1 P1
"P2" -> "P3" [label="23"]      "P2" -> "P3" [label="23"]        "P1" -> "P2" [label="12"]
"P3" -> "P4" [label="34"]      "P3" -> "P4" [label="34"]        "P2" -> "P3" [label="23"]
"P6" -> "P7" [label="67"]      "P6" -> "P7" [label="67"]        "P3" -> "P4" [label="34"]
"P7" -> "P4" [label="74"]      "P7" -> "P4" [label="74"]        "P6" -> "P7" [label="67"]
                               "P2" -> "P6" [label="26"]        "P7" -> "P4" [label="74"]
"P3" -> "P7" [label="37"]      "P3" -> "P7" [label="37"]        "P1" -> "P5" [label="15"]
                                                                "P3" -> "P7" [label="37"]
```

Left: `26` is a stray flow, dropped. Middle: `! P2 P6` names both
ends, `26` is back. Right: `12` is a path flow of the second filter,
shown; `56` touches P6 and is on no path, dropped although P5 and P6
are both kept (c2 would show it). `!!<2 P4` then `! P1` keeps P1
and drops `12`. A replacement group, `!!<2 D G` then `~=G B C` over
`A→B→C→D` and `D→B`: `G -> D` (the rewired `cd`, a path flow) kept,
`D -> G` (the rewired `db`) dropped. Undirected flows (`<->`, `--`)
are followed from either end as they are for names, no particular
treatment. The crossed pattern, `A→B`, `C→D` wanted and `A→D`,
`C→B` not, all four kept: `!! A B C D`, `! A B`, `! C D` gives
exactly `ab` and `cd`.

What is obtainable: every path set is a union of stars (the
out-flows or the in-flows of an item), so under c1 the crossed
pattern is never obtainable. Under c3 any set of item pairs is, by
one span-less `!!` over the items and one `! X Y` per wanted pair.
What no option obtains is separating two parallel flows between the
same pair of items: that needs a flow identity in the language, out
of scope.

The slice that decides, `_apply_filters()` after the kept-set check,
with `hidden_ids = vetoed_ids - allowed_ids`:

```python
# skip stray flows: vetoed by a strict filter, allowed by none
if id(conn) in hidden_ids:
    continue
```

### 1.7 Spikes

None: every decision reads off the mock-up.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                                                  | Basis                                           | Alternatives considered                                                                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1   | Vocabulary: strict only filter, path flows, stray flows; the doc and the glossary use these words                                                                                         | taste                                           | "focus" (says what the writer wants, not what the filter does), "restriction" (every filter restricts) |
| 2   | Syntax `!!`, whole-filter; `~~` is not a keyword                                                                                                                                          | option a2; Non-goals for `~`                    | a1, a3                                                                                                 |
| 3   | Path membership is recorded during traversal, by connection identity                                                                                                                      | option b1                                       | b2, b3                                                                                                 |
| 4   | Flow rule c3: vetoed if touching a strict selection; shown anyway if a path flow of some strict filter or joining two items a plain `!` selects together; evaluated on the final kept set | option c3                                       | c1, c2                                                                                                 |
| 5   | A filter's selection is its neighbors plus its anchors unless `x` suppresses them; the `f` flag is unaffected                                                                             | rule: the flags keep their meaning              | Anchors always in the selection (then `x` would veto flows at items the filter did not keep)           |
| 6   | Constraints (`-->`) are neither followed, vetoed nor allowed: they are layout hints and keep the classic rule                                                                             | Non-goals                                       | Veto them with the flows (a hidden flow's layout constraint would vanish with it)                      |
| 7   | `model.Only.strict: bool`; `Keyword.ONLY_STRICT = "!!"`; `_FilterDecisions.vetoed_ids`, `allowed_ids: set[int]`; the difference computed once in `handle_filters()`                       | rule: Type safety, `engineering/CONVENTIONS.md` | A subclass `OnlyStrict` (one field, one dispatch: a flag on the record is enough); a string mode       |
| 8   | Fixtures 082–087 committed first, goldens generated with the feature in place; the pre-feature run fails on all six with `Unrecognized keyword "!!"`                                      | taste (recalled: devlogs 100, 102)              | Fixtures with the feature                                                                              |
| 9   | The doc's flag-order line is left as it is; TODO item 21 asks the parser to accept the documented order                                                                                   | rule: Scope boundary                            | Fix the line to match the code (would enshrine the order the review found illogical)                   |
| 10  | The parser hang on a bare `=` found by the mock-up is TODO item 20, not fixed here                                                                                                        | rule: Scope boundary                            | Fix it on the way (a second purpose in a `feat` PR)                                                    |

### 1.9 Acceptance criteria

1. Fixture 082, the issue's example with `!!<>2 P4`: the golden has
   flows `23`, `34`, `67`, `74`, `37` and not `26`.
2. Fixture 083, the same with `! P2 P6` added: `26` is back.
3. Fixture 084, `!!<2 P4` and `!!>1 P1`: `12` and `15` shown, `56`
   and `26` dropped, P5 kept.
4. Fixture 085, replacement group (`!!<2 D G`, `~=G B C`): `G -> D`
   kept, `D -> G` dropped.
5. Fixture 086, undirected flows (`<->`, `--`) on the path kept, a
   directed flow off the path dropped.
6. Fixture 087, the crossed pattern: `ab` and `cd` only.
7. No existing golden changes: `make nr-test` before and after the
   feature commit differs only by 082–087.
8. Mutation smoke-test: with the skip of decision 4 disabled, 082–087
   fail.
9. `tests/unit/test_parser.py`: `!!<>2 A` and `!! A` parse as `Only`
   with `strict` set, `!<>2 A` with it unset; `~~ A` raises.
10. `doc/README.md` § 7.2 and § 7.3.1 describe the strict filter with
    the vocabulary of decision 1; § 7.4.1 shows it on the data
    pipeline with its image; `doc/SYNTAX.md` has the glossary rows
    and the `!!` form in § 7; `make doc` regenerates the images
    without error.
11. `make format`, `make lint`, `make test` pass; CI green on the PR.

## 2. Plan

### 2.1 Steps

**Step 1 — NR fixtures** (`test:`)

Files: `tests/non-regression/082-filter-strict.dfd` (the issue's
example), `083-filter-strict-plain-reallows.dfd`,
`084-filter-strict-two.dfd`, `085-filter-strict-replace.dfd`,
`086-filter-strict-undirected.dfd`, `087-filter-strict-crossed.dfd`,
their `.dot` goldens; `tests/RULES.md` (next number 088).

Actions:

1. Write the six fixtures, each with a header comment naming the
   issue and what the golden must show.
2. Generate the goldens with the feature code (step 2 done locally
   and stashed): `make nr-regenerate`, review with `make nr-review`.
3. Record the pre-feature failure: `make nr-test` fails on the six
   with `Unrecognized keyword "!!"`.

Verify: `make nr-test` lists 082–087 as FAIL before step 2, the
other 88 PASS.

Commit: `test: NR fixtures 082-087 for the strict only filter (#104)`

**Step 2 — Feature** (`feat:`)

Files: `src/data_flow_diagram/model.py`,
`src/data_flow_diagram/dsl/parser.py`,
`src/data_flow_diagram/dsl/filters.py`, `tests/unit/test_parser.py`.

Actions:

1. `Keyword.ONLY_STRICT`; `Only.strict`; parser: the sugar tries the
   longest mnemonic first and stops at the first match, `_parse_filter()`
   sets `strict`, `_PARSERS` entry.
2. `filters.py` as the mock-up: `_collect_connected_names()` returns
   `(names, followed)`; `_expand_neighbors_in_dir()` returns
   `(names, path_ids)`; `find_neighbors()` returns the path ids;
   `_collect_flow_ids(statements, names, *, touching)`;
   `_FilterDecisions.vetoed_ids`, `allowed_ids`, filled per `Only`
   filter (decision 4, 5, 6); `_apply_filters()` takes `hidden_ids`
   and skips a stray flow after the kept-set check. Docstrings and
   the module docstring updated.
3. Unit tests (criterion 9).
4. Mutation smoke-test (criterion 8), reverted.

Verify: `make format lint test` green, 88+6 NR PASS, no golden
diff outside 082–087.

Commit: `feat: strict only filter "!!" keeps only the path flows (#104)`

**Step 3 — Documentation** (`docs:`)

Files: `doc/README.md` (§ 7.2, § 7.3.1, § 7.4.1), `doc/SYNTAX.md`
(glossary, § 7), `doc/img/` (regenerated images).

Actions:

1. § 7.2: a paragraph on the strict filter and the flow rule in the
   vocabulary of decision 1; § 7.3.1: the `!!` form.
2. § 7.4.1: one example on the data pipeline, plain then strict,
   with the stray flow named in the comment.
3. `doc/SYNTAX.md`: glossary rows for the three terms, `!!` in § 7.
4. `make doc`; review the new images.

Verify: `make test` (doc sync) green; the images open.

Commit: `docs: the strict only filter "!!" (#104)`

Step gates: 1 and 2 share one gate (2 generates 1's goldens); 3 is
its own.

### 2.2 Inventory

| File                                               | Change                                                       |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `src/data_flow_diagram/model.py`                   | `Keyword.ONLY_STRICT`, `Only.strict`                         |
| `src/data_flow_diagram/dsl/parser.py`              | sugar for `!!`, `strict` set, dispatch entry                 |
| `src/data_flow_diagram/dsl/filters.py`             | traversal returns flows; vetoed and allowed sets; apply skip |
| `tests/unit/test_parser.py`                        | `!!` parsing cases, `~~` error                               |
| `tests/non-regression/082..087-filter-strict*.dfd` | fixtures                                                     |
| `tests/non-regression/082..087-filter-strict*.dot` | goldens                                                      |
| `tests/RULES.md`                                   | next number 088                                              |
| `doc/README.md`                                    | § 7.2 paragraph; § 7.3.1 form; § 7.4.1 example               |
| `doc/SYNTAX.md`                                    | glossary rows; § 7                                           |
| `doc/img/filter-strict*.svg`                       | generated                                                    |
| `TODO.md`                                          | items 20 (parser hang) and 21 (flag order), at scaffolding   |

### 2.3 Scope boundary

- The parser hang on a bare `=` (TODO item 20).
- The flag order, doc against code (TODO item 21).
- The `~` filter: `~~` is not a keyword and errors as today
  (`Name(s) unknown: ~`, the sugar splitting it as `~ ~`); a better
  message is not worth a branch of its own.
- Two parallel flows between the same pair that collapse into one
  after a replacement, one vetoed and one allowed: the first in
  source order decides, as the dedup does today.
- A keep filter after a replacement re-adds the replaced items as
  orphans, since traversal reads the original connections (TODO item
  23, a bug of its own, unaffected by strictness: path membership is
  by connection identity in either order).

Approved: 2026-09-24 ("Go!")

## 3. Execution

### 3.1 Account

- Step 1, `2b68430`: as planned, plus 088, an error fixture for `~~`
  (criterion 9's `~~` case cannot be a parser unit test: the error
  arises in the filter phase, "Name(s) unknown: ~"). Pre-feature
  failure differs from the plan's wording: the sugar splits `!!` into
  `! !` and the suite aborts at 082 with "Name(s) unknown: !<>2"
  (`nr-test.sh` is `set -e`). No existing golden changed.
- Step 2, `2dd016e`: as the mock-up. Two mutation smoke-tests instead
  of one: the stray-flow skip disabled fails 082 and 084–087, not 083
  (all its flows are shown anyway), so the plain reallow disabled was
  run too and fails 083 and 087. `make format lint test` green: 102
  pytest (97 + 5), 95 NR (88 + 7). Slip on the way: a `git checkout`
  meant to revert a mutation reverted the whole uncommitted
  `filters.py`; restored from the mock-up patch, the diff stat
  checked before and after. Lesson: mutate and revert with an exact
  text replacement, never with a checkout of a file carrying
  uncommitted work.
- Loop 1 after Shipped, `92ef2f4` (`docs:`): a minimal example in
  § 7.2, asked at the review of the shipped doc: two chains to C and a
  relaxed flow between them, then `!<1 C` (the neighborhood of C,
  stray flow included) and `!!<1 C` (what leads to C). Three images;
  renders verified as DOT (B C D kept in both, `stray flow` only in
  the plain one) and by eye; `make doc` and `make test` green. Then
  moved, at the user's request, from § 7.2 to the last Only-filter
  example, § 7.4.1.12 "The strict filter: path flows and stray flows": not fundamental
  enough for the concept section.
- Type safety note: `find_neighbors()` returns a three-tuple read in
  two places (`Only`, `Without`), a pre-existing shape extended by
  one element; a dataclass is the convention's answer if it grows
  again.
- Step 3, `238866f`: as planned, with one placement change: the
  example is § 7.4.1.7 "Same, but only the path flows", right after
  the `!<>2 proc_flow` example it is compared to, so one new image
  instead of two; `make doc` renumbered the later examples. Two stray
  flows hidden there, `db_params -> forecast` ("horizon") and
  `interact -> user`, verified by a DOT diff of a scratch render and
  by eye on both images. Slip on the way: a DOT-format markdown run
  inside `doc/` overwrote every `doc/img/*.svg` with DOT text, and a
  second one from the root wrote 22 files into the top-level `img/`;
  `make doc` restored the former, `git clean` on the untracked files
  the latter, `git status` clean but for the intended changes. Lesson:
  a markdown render writes where the fences say, relative to the
  working directory; render scratch copies from a scratch directory.
  `make test` green (doc sync).

## 4. Delivery

### 4.1 Try it

Loop 1 (after Shipped): `doc/README.md` § 7.4.1.12 closes the
Only-filter examples with a five-item example and its two filtered
forms; open
`doc/img/filter-strict-master.svg`, `filter-strict-plain.svg`,
`filter-strict.svg`.

The playground `devlog/104-try-it.dfd` (rendered: `104-try-it.svg`):
a 3 × 3 grid of items laid out top-down, column flows constrained,
row flows and two diagonals relaxed, plus a spare item Z for the
group variants. At its end, a menu of twelve filter blocks, A to L,
one active at a time; each block's comment states the item and flow
counts and names the flows that appear or vanish, all verified by a
DOT render. Blocks: plain baseline, strict, strict plus a pair, two
strict filters, strict plus a plain neighborhood, group after plain
and after strict, the crossed pattern by a span-less veto and by
paths, strict then removal, and the reversed group order (the TODO
item 23 illustration).

```bash
./data-flow-diagram devlog/104-try-it.dfd && xdg-open devlog/104-try-it.svg
make nr-review && xdg-open tests/non-regression/082-filter-strict.svg
xdg-open doc/img/filter-only-two.svg doc/img/filter-only-strict.svg
```

A first playground on the doc's data pipeline was replaced at the
user's request by lettered items and "source dest" flow labels, then
by the grid: a filter-free base one can read at a glance. On a grid,
a filter centred on the middle item with `<>2` has no stray flow at
all, every flow being on some two-flow path through the centre; the
baseline is therefore `!>2 A1`, from a corner.

Tried: 2026-09-24 (the playground, blocks A to L; "very nice!")

### 4.2 Test report

| #   | Criterion                                            | Proof                                                                                                                            |
| --- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 082: `23 34 67 74 37`, no `26`                       | golden `082-filter-strict.dot`, five `->` lines, none labelled 26                                                                |
| 2   | 083: `26` back                                       | golden, `"P2" -> "P6" [label="26"`                                                                                               |
| 3   | 084: `12`, `15` shown, `56`, `26` hidden, P5 kept    | golden, seven flows, `"P5"` item present                                                                                         |
| 4   | 085: `G -> D` kept, `D -> G` dropped                 | golden, one flow `"G" -> "D" [label="cd"`                                                                                        |
| 5   | 086: `ab bc cd bd` kept, `ca` dropped                | golden, four flows                                                                                                               |
| 6   | 087: `ab`, `cd` only                                 | golden, two flows                                                                                                                |
| 7   | No existing golden changed                           | `git status` after `make nr-regenerate`: only 082–088 untracked, `tests/RULES.md` modified                                       |
| 8   | Mutation smoke-test                                  | skip disabled: 082, 084–087 FAIL; plain reallow disabled: 083, 087 FAIL; both reverted                                           |
| 9   | Parser: `!!` strict, `!` not; `~~` errors            | 5 cases in `test_parse_filter_strictness`; 088 error fixture, `Name(s) unknown: ~`                                               |
| 10  | Doc: § 7.2, § 7.3.1, § 7.4.1.7 with image; SYNTAX.md | commit `docs:`; `make doc` exit 0; DOT diff of the example: exactly `db_params -> forecast`, `interact -> user`                  |
| 11  | format, lint, test; CI                               | `38 files left unchanged`, `All checks passed!`, `Success: no issues found in 30 source files`, 102 pytest, 95 NR; CI: see below |

CI on PR #105 at `e880300`: `conventional`, `smoke-test-wheel`,
`test (3.11, 3.12, 3.13)` pass; `gate` fails by design: main carries
the unreleased `docs:` commit `80e97b3` (patch level, 1.17.10
pending) and a `feat:` PR would raise it to minor. Reproduced locally
on a `main` worktree: "BLOCKED: a minor PR would raise the pending
patch level of main: release 1.17.10 first". 1.17.10 released from
main (only that commit), `main` merged into the branch (`b581c12`):
all six checks pass on `8d6f7d3` (Discussion 1).

### 4.3 Verdict

**Recommendation:** accept

Rationale:

- Every criterion has a proof in the table; the six nominal fixtures
  fail under one of two mutations, so each golden exercises the code
  it locks in.
- No existing golden or doc image changed: the default behavior is
  untouched, as the Non-goals require.
- The doc example is the neighbor of the plain example it extends,
  and its two hidden flows are named in the source comment.

Reservations: none. Two slips during execution (a file checkout, a
render in the wrong directory) were caught by `git status` and
`git diff --stat` before any commit; both are in the Account with
their lesson.

### 4.4 Discussion

| #   | Point                                                                                                                                                                                                                   | Decision                                                                                                         |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | The merge gate blocks the PR: main has an unreleased patch-level `docs:` commit, this PR is minor. First natural occurrence of the "Blocked" case of TODO item 12                                                       | Release 1.17.10 from main first, then the gate passes on the next PR event; the TODO 12 case ticked once it does |
| 2   | Four follow-ups found on the way: 20 (bare `=` hangs the parser), 21 (flag order, doc against code), 22 (several neighbor specs in one filter), 23 (group before or after the filter, orphans, kept-set initialisation) | Postponed, all recorded as TODO items on this branch with their direction                                        |
| 3   | The playground is a new kind of devlog artifact: a `.dfd` with a filter menu, committed with its SVG                                                                                                                    | Accept; the Try it section describes it, no template change                                                      |
| 4   | `~~ A` errors with "Name(s) unknown: ~", the sugar splitting it as `~ ~`; a clearer message would need the sugar to know `~~`                                                                                           | Accept as is (Scope boundary); revisit if TODO 22's doc task touches the sugar                                   |
| 5   | On a grid, a `<>2` filter from the centre has no stray flow: the strict filter shows its effect from a corner or with a direction. Worth a sentence in the doc?                                                         | Accept as is: the doc example (§ 7.4.1.7) is directional already and names its two stray flows                   |

Shipped: 2026-09-24 ("ship")

## 5. Closure

### 5.1 Retrospective

| #   | Point                                                                                                                                                                                                                 | Agent    | User |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: the stops fell where the template puts them; the Try it stop grew into the longest exchange of the task (three playgrounds) and produced two TODO items and the agreed direction of a third | well     |      |
| 2   | The first mock-up decided the wrong things: syntax and computation were the questions asked, and the composition rule (c) was the one that mattered; the stop 0 review caught it before any code                      | surprise |      |
| 3   | The composition rule was found by formulating the user's intuition as three predicates and testing them on the mock-up, then on a grid; the "obtainable sets" argument settled c1 against c3                          | well     |      |
| 4   | Two slips in execution, a file checkout over uncommitted work and a render in the wrong directory, both caught by `git status` before a commit; the lesson is in the Account                                          | not well |      |
| 5   | The merge gate blocked the PR on a `docs:` TODO.md commit: the rule worked as designed, and exposed that bookkeeping commits bump the version (TODO 24)                                                               | surprise |      |
| 6   | The playground as a committed artifact: a `.dfd` with a menu of blocks, each comment carrying the verified counts, was the fastest way for the user to see the rule; worth keeping as a pattern                       | well     |      |
| 7   | Devlog length: about 490 lines at closure against the 300 target, the option table and the runs being the bulk; the tables are not counted, the prose is near the budget                                              | tension  |      |

Process: 2 rounds before stop 1 (the stop 0 review reopened the
design); 3 loops at stop 2, 1 loop after stop 3 (the doc example) (playground rewritten twice at the user's
request, blocks added twice); rework after stop 1: none in the code,
the doc example moved from a new subsection to the neighbor of the
plain example.

<!-- Stop 4: the user fills their column. -->

Closed: pending

### 5.2 Forward-looking

- TODO items filed on this branch: 20 (bare `=` hangs the parser),
  21 (flag order, doc against code), 22 (several neighbor specs in
  one filter), 23 (group before or after the filter: orphans,
  kept-set initialisation, direction agreed), 24 (TODO.md commits
  bump nothing), 25 (`make install` version stamp). TODO 12: the
  "Blocked" gate case ticked, the "title edit re-runs the checks"
  case observed.
- The next tasks can rely on: `Only.strict` and `Keyword.ONLY_STRICT`
  in the model; `find_neighbors()` returning the path flow ids;
  `_collect_flow_ids()` for touching and joining sets; the vocabulary
  (strict only filter, path flows, stray flows) in the doc and the
  glossary; `devlog/104-try-it.dfd` as a filter playground.
- No template or `CLAUDE.md` change.

### 5.3 Rule trace

| Source                                   | Rule                                                                   | Verb (applied / created) |
| ---------------------------------------- | ---------------------------------------------------------------------- | ------------------------ |
| `engineering/PROCESS.md` Phase 3         | Stop 0 before any mock-up; the mock-up refines the frame in place      | applied                  |
| `engineering/CONVENTIONS.md` Type safety | Fields on the record, keyword-only signatures, no string modes         | applied                  |
| `tests/RULES.md`                         | Fixtures before the code; mutation smoke-test after adding NR fixtures | applied                  |
| `engineering/RELEASING.md` Merge gate    | A PR never raises the pending level of `main`: release first           | applied                  |
| `engineering/PROCESS.md` TODO.md         | Items that arise during a task are committed on the task branch        | applied                  |
