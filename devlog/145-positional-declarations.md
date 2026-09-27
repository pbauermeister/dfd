# 145 — Declarations after a view statement join the view

Date: 2026-09-27
Status: ONGOING
Issue: #145 · PR: #146 · Branch: `fix/145-positional-declarations`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Found at the analysis of #143 (`discussions/code-structure.md`),
while designing the graph as a first-class object: a filter selects
from the complete master whatever the source order, so `! A` then
`process Z` drops Z, and the walk of `!>1 A` reads a flow declared
below it. The author reads the order as positional and calls the
current state a bug. Prior to #143, which builds its graph on the
fixed semantics. Issue #145 is the brief; the spike of 2026-09-27
(21 lines added, 15 removed in the phase 1 loop of `dsl/filters.py`,
118 goldens identical) showed the fix is local: phase 2 stays the
final pass.

### 1.2 Goal

A view statement (filter or merge) acts on the master as declared
so far, and a declaration after it joins the current view. Three
rules, in § 7.5 of both docs: a declaration before the first view
statement belongs to the master only; a view statement's anchors
and walk read the statements before it; a declaration after a view
statement joins the master and the view, a connection whose end is
removed or merged away being an error that names the cause. Every
existing golden byte-identical; three fixtures pin the rules.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                                                                                                                                                                                                                                                                 | Basis                                                                                                         | Alternatives considered                                                                                |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1   | The phase 1 loop knows its position: the known names, the walk and the flow collections read `statements[:position]`; phase 2 unchanged                                                                                                                                                                                                                                                                  | spike (measured)                                                                                              | A graph built incrementally (#143's design, later)                                                     |
| 2   | An item declared after a view statement is added to the kept set when one exists; before the first view statement nothing changes                                                                                                                                                                                                                                                                        | rule 1 and 3 of #145                                                                                          | Declarations always positional (drops `! A` after Z)                                                   |
| 3   | A connection declared after a view statement names items of the view: an end declared above it that is not kept, removed or merged away is an error, with the messages of an anchor ("no longer available due to previous filters", "no longer available: B (removed at line N: ...)"); an end declared below joins the view at its declaration                                                          | user (review of 2026-09-27: "should be error", the silent drop refused)                                       | Drop the flow as any flow with an unkept end (the first version: an error for removed and merged only) |
| 4   | A frame declared after a view statement names items of the view, as a connection does (decision 3): a member declared above it that is not kept, removed or merged away is an error, the same messages; a member declared below joins at its declaration                                                                                                                                                 | user (second review of 2026-09-27: the three frame cases of the findings folder, "error: B no longer exists") | Trimmed by phase 2 as today (the first version, kept until the review)                                 |
| 5   | A merge still rewires every connection in phase 2, a flow declared after it included; its merged items are unavailable to a later connection (decision 3)                                                                                                                                                                                                                                                | § 7.5 rule 6, unchanged                                                                                       |                                                                                                        |
| 6   | Fixtures, the next free numbers after 111 (`tests/RULES.md`): 112 a declaration joining the view after `!` (item, flow, frame), 113 a declaration below joining beyond the walk's reach, `-err-` 114 a flow to a removed item, 115 a flow to an item the walk did not reach (the walk bounded by the position), 116 a frame member not kept, 117 a frame member merged away; mutation smoke-test on each | `tests/README.md` (rule)                                                                                      | A unit test only                                                                                       |
| 7   | Both docs, § 7.5: one paragraph stating the three rules; `doc/README.md` example built from the first fixture                                                                                                                                                                                                                                                                                            | rule: a language rule is documented where the others are                                                      |                                                                                                        |
| 8   | Commit type `fix:`, the author's reading of the current state                                                                                                                                                                                                                                                                                                                                            | user                                                                                                          | `feat:` (the #121 test: "was X possible before?")                                                      |
| 10  | An anchor or a replacer declared below its view statement fails as "Name(s) unknown"; the message stays                                                                                                                                                                                                                                                                                                  | user (second review: "the stderr is correct")                                                                 | "declared below, at line N"                                                                            |
| 11  | A merge into an item with declared connections stays legal: the flow collapses to a self-loop and is dropped, as #100 decided at its Try it (fixtures 078, 079)                                                                                                                                                                                                                                          | rule: a decision of #100, its goldens; the review's take recorded for a task of its own                       | An error "replacer already connected" (tried: 078 and 079 fail)                                        |
| 9   | On the way: the one-frame check of a merge reads the frames declared above it too, plus the frames its replacers inherited; a frame declared below a merge is trimmed by phase 2 (decision 4)                                                                                                                                                                                                            | rule 2 of #145, extended to frames                                                                            | The frames of the whole file, as before                                                                |

### 1.4 Acceptance criteria

1. `make format`, `make lint`, `make test` pass; the 118 existing
   goldens unchanged (no `nr-regenerate` on them).
2. The three new fixtures render as reviewed under `make nr-review`;
   the mutation smoke-test fails each.
3. `! A` then `process Z` keeps Z; `!>1 A` then `A -> Z` keeps Z by
   declaration, not by the walk (B, the earlier neighbor, kept too);
   `~ B` then `B -> Z` errors naming the removing line.
4. Both docs state the rules in § 7.5; `make doc` clean.

Approved: 2026-09-27 (the go)

## 2. Execution

### 2.1 Account

- `46b32cd` fix: the phase 1 loop enumerates its position and reads
  `statements[:position]` for the known names, the walk, the flow
  collections and the frames of a merge; an item after a view
  statement joins the kept set; a connection after one goes through
  the availability check. 43 lines added, 12 removed (the spike's
  shape plus decision 9 and the docstrings). 154 tests green, the 118
  goldens untouched (no `nr-regenerate`, the three new goldens written
  one by one). Fixtures on the 093 master: 112 `! A B` then Z, `A ->
Z`, `frame Z D` (frame trimmed to Z); 113 Y above `!>1 A`, Z below,
  `A -> Y` and `B -> Z` below (Y and its flow out, Z and its flow in);
  114 `~ B` then `B -> Z`. Mutations, each reverted by its inverse
  edit, the file's checksum equal after: item not joining fails 112
  and 113; the walk reading the whole file fails 113; the connection
  check skipped fails 114 ("expected to fail but succeeded"). README
  § 7.5 with the example on the strict-filter master (the same shape
  as 112), SYNTAX § 7.5 one paragraph; `make doc` clean, the
  renumberer and the sections idempotent. `tests/RULES.md` counter to 115.
- This devlog.
- Review loop (2026-09-27): Pascal read the review folder and refused
  the silent drop of `A -> Y` in 113 ("should be error: Y no longer
  available, and was neither kept by a `! Y`"). Decision 3 extended:
  the ends of a connection declared after a view statement, when
  declared above it, must be in the view, checked with the anchor
  check of `~` (same message); an end declared below joins at its
  declaration, since a connection may name an item declared later
  (measured: `A -> B` then the items renders). 113 rewritten to the
  joining case alone, 115 the error; the goldens still identical.
  Mutation (the connection's names emptied): 114 and 115 succeed
  where they must fail; a first, broader mutation on the four
  `kept_names` guards failed six fixtures. Rule 3 reworded in both
  docs; counter to 116.
- Second review loop (2026-09-27): twelve cases run on the branch and
  on `main` (frames below a view statement, a replacer or an anchor
  declared below, a strict filter then a flow below, stars, two
  filters with a declaration between) found three points; Pascal
  read them in a findings folder. Frames aligned with flows (decision
  4): one `_check_in_view` for both, 112 rewritten to `frame Z B`,
  116 and 117 the errors, the README example too. Decision 10, the
  message kept. Decision 11: the "replacer already connected" error
  was implemented and failed 078 and 079, the self-loop fixtures of
  #100; removed, the goldens identical again. Mutation (the frame's
  names emptied): 116 and 117 succeed where they must fail. Counter
  to 118.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- Criteria 1 to 4 met: 154 tests green, the goldens byte-identical,
  the three fixtures rendered and read, the mutation failing each,
  the rules in both docs.
- An anchor declared below its filter fails as "Name(s) unknown":
  a reservation at first, settled by decision 10.
- After the loop: a flow declared after a view statement is either in
  the view or an error, never dropped, and a frame the same; the drop
  and the trim of phase 2 stay for the statements declared above.
- Open, for a task of its own: a merge into a connected item
  (decision 11).

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                                                                                                                     | Agent    | User       |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------- |
| 1   | Process and template fit: fast track after the spike, one work commit, no question raised on the way                                                                                                                                      | well     | well       |
| 2   | The spike measured before the fix was decided: the change landed at the spike's size, and the goldens said nothing moved                                                                                                                  | well     | well       |
| 3   | The review folder (093 first, dfd/dot/stderr and SVG) got the disagreement in one reading: fixture 113 mixed a rule with a silent drop that the picture made visible; one loop, the rule sharpened                                        | well     | well       |
| 5   | The second bug of the issue was found by chance; enumerating the statement kinds after a view statement and running them on both sides found the frame gap in one pass: do the enumeration before the first fixture, not after the review | not well | ended well |
| 4   | The frames of a merge read positionally too (decision 9): a small extension of the recorded decisions, taken without a pause, consistent with rule 2                                                                                      | well     | well       |

Closed: pending

### 4.2 Rule trace

| Source            | Rule                                                              | Verb (applied / created) |
| ----------------- | ----------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`  | Mutation smoke-test after adding an NR fixture; numbering counter | applied                  |
| `tests/README.md` | An error fixture has a `.stderr` golden and no `.dot`             | applied                  |
| `doc/README.md`   | A language rule is documented where the others are (decision 7)   | applied                  |
