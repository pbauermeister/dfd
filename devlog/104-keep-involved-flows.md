# 104 — Keep only the flows involved by a "keep" filter

Date: 2026-09-24
Status: PENDING
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

- Recalled: flags are letters in one group after the direction
  (`<>xf2`), combined per filter (`x` in either direction suppresses
  the anchors); a new option follows the grammar in place rather than
  opening a second one.
- Recalled (devlogs 100, 102): fixtures land before the code, goldens
  generated with the code in place, so that the history shows them
  failing; one check, one code path.

### 1.6 Set-based design

Triggers: an intent inherited from the issue (two open questions
named there); a thing that could live in two places (the path
membership, computed during traversal or as a pass over the kept set).
Mock-up: yes, in a throwaway worktree, the recommended options built
together (62 diff lines in `dsl/filters.py`, 7 in `dsl/parser.py`, 1
in `model.py`); `make test` on it green, no existing golden changed.
Design question: (a) the syntax of the option; (b) the computation of
path membership; (c), surfaced by the mock-up: what a keep filter
without the option contributes to the flows once one filter has it.
Options: one row per option; recommended: a1, b1, c1.

| Option | What differs                                                                                                                                                                                                | For                                                                                                                                                                                                                                           | Against                                                                                                                                                              |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a1     | A flag letter `p` in the existing group: `!<>p2 P4`, `!<xp*`. Parsed where `x` and `f` are, stored in `FilterNeighbors`, combined per filter like `x`                                                       | No new grammar, no new keyword; three lines in the parser; the doc row sits next to `x` and `f`                                                                                                                                               | One more letter to remember; the letter sits before the span (`p2`), which the doc's syntax line currently gets wrong (see decision 6)                               |
| a2     | A distinct filter keyword, `!!` ("only paths"): `!!<>2 P4`                                                                                                                                                  | Reads as a filter kind, whole-filter by construction                                                                                                                                                                                          | A new `Keyword` member, a parser dispatch branch, a `model.Only` subclass or field; one more prefix in a language of `!` and `~`; nothing gained over a flag         |
| a3     | A suffix on the span: `!<>2. P4` or `!<>2! P4`                                                                                                                                                              | Visually tied to the span it qualifies                                                                                                                                                                                                        | A regex change, cryptic, a third place where options live                                                                                                            |
| b1     | During traversal: `_collect_connected_names()` returns the connections it followed with the names; `_expand_neighbors_in_dir()` accumulates their identities wave by wave; a flow is on a path iff followed | One code path decides neighborhood and path membership, so reversed, undirected and layout-direction flows are handled once; `id()` survives the endpoint rewrite by replacement, which gives the invariant on groups for free; smallest diff | `_FilterDecisions` carries a set of object ids, an identity-based set rather than a value-based one (documented in place)                                            |
| b2     | Post-pass: after the kept names, recompute the wave layers per flagged filter and test each kept flow against the layer of its source end                                                                   | Traversal untouched                                                                                                                                                                                                                           | The direction rules (reversed, `BFLOW`/`UFLOW`, layout direction) exist twice and must be kept in sync; a second traversal per flagged filter                        |
| b3     | Hybrid: traversal records the per-wave name sets, a post-pass tests the flows against them                                                                                                                  | No object identities                                                                                                                                                                                                                          | Same two places as b2 for the direction rules; the rewrite by replacement happens after, so the test must be done on the original names, a subtlety b1 does not have |
| c1     | Once one keep filter carries `p`, a flow is kept iff both ends are kept and some flagged filter followed it; an unflagged keep filter adds names, no flows                                                  | One sentence in the doc; the union across flagged filters is the issue's "kept by another filter"; the mock-up shows it (below)                                                                                                               | An unflagged `! A B` next to a flagged filter shows A and B without their flow; the remedy is to flag that filter too (`!>p1 A`)                                     |
| c2     | An unflagged keep filter also re-allows the flows among its own selection (anchors and neighbors)                                                                                                           | `! P2 P6` next to `!<>p2 P4` shows `26`                                                                                                                                                                                                       | Flagging one filter changes what the others keep across their selections (cross-filter flows drop); a rule with two clauses; nothing in the issue asks for it        |

Mock-up, the issue's example with `!<>p2 P4` (option a1, b1, c1),
flows only, the unflagged run to the left:

```
!<>2 P4                      !<>p2 P4
"P2" -> "P3" [label="23"]    "P2" -> "P3" [label="23"]
"P3" -> "P4" [label="34"]    "P3" -> "P4" [label="34"]
"P6" -> "P7" [label="67"]    "P6" -> "P7" [label="67"]
"P7" -> "P4" [label="74"]    "P7" -> "P4" [label="74"]
"P2" -> "P6" [label="26"]
"P3" -> "P7" [label="37"]    "P3" -> "P7" [label="37"]
```

The same with `! P2 P6` added (question c, option c1): identical to
the right column; `26` stays out. A replacement group,
`!<p2 D G` then `~=G B C` over `A→B→C→D` and `D→B`: `G -> D` (the
rewired `cd`, on the path) kept, `D -> G` (the rewired `db`,
downstream) dropped; unflagged, both are kept. Undirected flows
(`<->`, `--`) are followed from either end as they are for names:
no particular treatment, as the issue supposed.

The slice that decides, `_apply_filters()` after the kept-set check:

```python
# skip flows off the traversed paths when a "p" flag was used
if path_ids is not None and id(conn) not in path_ids:
    continue
```

### 1.7 Spikes

None: every decision reads off the mock-up.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                    | Basis                                                  | Alternatives considered                                                                     |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 1   | The option is the flag letter `p` (paths) in the neighbors flag group                                                                                       | option a1                                              | a2, a3; letters `s` (strict), `l` (links): `p` names what is kept                           |
| 2   | `p` applies to the whole filter, wherever it is written: `!<p2 >2 X` equals `!<p2 >p2 X`; both directions' followed flows count                             | taste (recalled: `x` combines per filter the same way) | Per direction: `!<p2 >2` would drop the downstream flows it just selected under c1          |
| 3   | Path membership is recorded during traversal, by connection identity                                                                                        | option b1                                              | b2, b3                                                                                      |
| 4   | Flows are kept iff both ends are kept and, once one keep filter carries `p`, some flagged filter followed them; the "without" filter ignores the flag       | option c1; Non-goals for `~`                           | c2                                                                                          |
| 5   | `FilterNeighbors.only_paths: bool`, parsed once; `_FilterDecisions.path_ids: set[int] \| None`, `None` meaning no flag seen, the same shape as `kept_names` | rule: Type safety, `engineering/CONVENTIONS.md`        | A string flag carried downstream; an empty set meaning "no flag" (conflates with "no path") |
| 6   | The doc's syntax line `DIRECTION[SPAN][FLAGS]` is corrected to `DIRECTION[FLAGS][SPAN]`, which is what the parser and every example do (`<>xf2`)            | rule: the doc describes the code                       | Leave it, and let the new flag sit under a wrong line                                       |
| 7   | Fixtures 082–085 committed first, goldens generated with the feature in place; the pre-feature run fails on all four with "Unrecognized filter flag: p"     | taste (recalled: devlogs 100, 102)                     | Fixtures with the feature                                                                   |
| 8   | The parser hang on a bare `=` found by the mock-up is TODO item 20, not fixed here                                                                          | rule: Scope boundary                                   | Fix it on the way (a second purpose in a `feat` PR)                                         |

### 1.9 Acceptance criteria

1. Fixture 082, the issue's example with `!<>p2 P4`: the golden has
   flows `23`, `34`, `67`, `74`, `37` and not `26`.
2. Fixture 083, the same with `!>p1 P2` added: `26` is back, kept by
   the second filter's path.
3. Fixture 084, replacement group (`!<p2 D G`, `~=G B C`): `G -> D`
   kept, `D -> G` dropped.
4. Fixture 085, undirected flows (`<->`, `--`) on the path kept, a
   directed flow off the path dropped.
5. No existing golden changes: `make nr-test` before and after the
   feature commit differs only by 082–085.
6. Mutation smoke-test: with the identity check of decision 3
   disabled, 082–084 fail.
7. `tests/unit/test_parser.py`: `!<>p2 A` parses with `only_paths`
   set on both directions; `!<>z1 A` still raises (existing case).
8. `doc/README.md` § 7.3.3 lists `p` and carries the corrected
   syntax line; § 7.4.1.2 shows the option on the data pipeline with
   its image; `doc/SYNTAX.md` has the `"p" flag` row; `make doc`
   regenerates the images without error.
9. `make format`, `make lint`, `make test` pass; CI green on the PR.

## 2. Plan

### 2.1 Steps

**Step 1 — NR fixtures** (`test:`)

Files: `tests/non-regression/082-filter-only-paths.dfd` (the issue's
example), `083-filter-only-paths-two-filters.dfd`,
`084-filter-only-paths-replace.dfd`,
`085-filter-only-paths-undirected.dfd`, their `.dot` goldens;
`tests/RULES.md` (next number 086).

Actions:

1. Write the four fixtures, each with a header comment naming the
   issue and what the golden must show.
2. Generate the goldens with the feature code (the mock-up worktree,
   or step 2 done locally and stashed): `make nr-regenerate`, review
   with `make nr-review`.
3. Record the pre-feature failure: `make nr-test` on the fixtures
   alone fails with "Unrecognized filter flag: p".

Verify: `make nr-test` lists 082–085 as FAIL before step 2, the
other 88 PASS.

Commit: `test: NR fixtures 082-085 for the "p" filter flag (#104)`

**Step 2 — Feature** (`feat:`)

Files: `src/data_flow_diagram/model.py`,
`src/data_flow_diagram/dsl/parser.py`,
`src/data_flow_diagram/dsl/filters.py`, `tests/unit/test_parser.py`.

Actions:

1. `model.FilterNeighbors.only_paths: bool`; parser: `"p"` case in
   `_parse_neighbor_spec()`, the field initialised in the three
   constructors.
2. `filters.py` as the mock-up: `_collect_connected_names()` returns
   `(names, traversed)`; `_expand_neighbors_in_dir()` returns
   `(names, path_ids)`; `find_neighbors()` returns the ids when the
   filter carries the flag in either direction (decision 2);
   `_FilterDecisions.path_ids`; `_collect_kept_names()` unions them
   over the `Only` filters; `_apply_filters()` skips a flow off the
   paths after the kept-set check. Docstrings and the module
   docstring updated.
3. Unit test: `!<>p2 A` sets `only_paths` on both directions;
   `!<p2 A` on the upstream one only.
4. Mutation smoke-test (criterion 6), reverted.

Verify: `make format lint test` green, 89+4 NR PASS, no golden
diff outside 082–085.

Commit: `feat: "p" filter flag keeps only the flows on the traversed paths (#104)`

**Step 3 — Documentation** (`docs:`)

Files: `doc/README.md` (§ 7.3.3, § 7.4.1.2), `doc/SYNTAX.md`
(glossary row, § 7.3), `doc/img/` (regenerated images).

Actions:

1. § 7.3.3: syntax line corrected (decision 6), `p` row after `f`.
2. § 7.4.1.2: one example on the data pipeline, unflagged then
   flagged, with the dropped flow named in the comment.
3. `doc/SYNTAX.md`: the `"p" flag` row, § 7.3 in sync.
4. `make doc`; review the two new images.

Verify: `make test` (doc sync) green; the images open.

Commit: `docs: the "p" filter flag, syntax line corrected (#104)`

Step gates: 1 and 2 share one gate (2 generates 1's goldens); 3 is
its own.

### 2.2 Inventory

| File                                                    | Change                                                   |
| ------------------------------------------------------- | -------------------------------------------------------- |
| `src/data_flow_diagram/model.py`                        | `FilterNeighbors.only_paths`                             |
| `src/data_flow_diagram/dsl/parser.py`                   | `p` flag parsed, field initialised                       |
| `src/data_flow_diagram/dsl/filters.py`                  | traversal returns flows; decisions carry ids; apply skip |
| `tests/unit/test_parser.py`                             | flag parsing case                                        |
| `tests/non-regression/082..085-filter-only-paths-*.dfd` | fixtures                                                 |
| `tests/non-regression/082..085-filter-only-paths-*.dot` | goldens                                                  |
| `tests/RULES.md`                                        | next number 086                                          |
| `doc/README.md`                                         | § 7.3.3 row and syntax line; § 7.4.1.2 example           |
| `doc/SYNTAX.md`                                         | glossary row; § 7.3                                      |
| `doc/img/filter-only-paths*.svg`                        | generated                                                |
| `TODO.md`                                               | item 20 (parser hang), committed at scaffolding          |

### 2.3 Scope boundary

- The parser hang on a bare `=` (TODO item 20).
- The `~` filter and the flag: parsed and ignored there (decision 4);
  a subtractive use, if wanted, is an issue of its own.
- The "re-add by traversal" interaction of `~=` followed by `!`
  (a `!` after a replacement brings the replaced items back through
  traversal, since traversal reads the original statements): observed
  in the mock-up, pre-existing, unchanged; not filed, the doc's own
  example puts `!` before `~=`.

Approved: pending

## 3. Execution

### 3.1 Account

## 4. Delivery

### 4.1 Try it

Tried: pending

### 4.2 Test report

### 4.3 Verdict

**Recommendation:** accept | accept with reservations | reject

Rationale:

-

Reservations:

1.

### 4.4 Discussion

| #   | Point | Decision |
| --- | ----- | -------- |
| 1   |       |          |

Shipped: pending

## 5. Closure

### 5.1 Retrospective

| #   | Point                    | Agent | User |
| --- | ------------------------ | ----- | ---- |
| 1   | Process and template fit |       |      |

Process: <N> rounds before stop 1; <N> loops at stop 2; rework after
stop 1: none | <what>

Closed: pending

### 5.2 Forward-looking

### 5.3 Rule trace

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
