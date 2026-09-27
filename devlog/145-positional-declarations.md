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

| #   | Decision                                                                                                                                                                                                                                                                              | Basis                                                    | Alternatives considered                              |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| 1   | The phase 1 loop knows its position: the known names, the walk and the flow collections read `statements[:position]`; phase 2 unchanged                                                                                                                                               | spike (measured)                                         | A graph built incrementally (#143's design, later)   |
| 2   | An item declared after a view statement is added to the kept set when one exists; before the first view statement nothing changes                                                                                                                                                     | rule 1 and 3 of #145                                     | Declarations always positional (drops `! A` after Z) |
| 3   | A connection declared after a view statement with an end in the unavailable record raises " Name(s) no longer available: B (removed at line N: ...)" from the filters, the same message as for an anchor                                                                              | user (taste, strict over silent drop)                    | Drop the flow as any flow with an unkept end         |
| 4   | A frame declared after a view statement is trimmed by phase 2 as today                                                                                                                                                                                                                | rule 3 of #145                                           | An error for a merged member                         |
| 5   | A merge still rewires every connection in phase 2, a flow declared after it included; its merged items are unavailable to a later connection (decision 3)                                                                                                                             | § 7.5 rule 6, unchanged                                  |                                                      |
| 6   | Fixtures, the next free numbers after 111 (`tests/RULES.md`): a declaration joining the view after `!` (item, flow, frame), the walk bounded by the position (`!>1 A` with a flow declared below), an `-err-` fixture for a connection to a removed item; mutation smoke-test on each | `tests/README.md` (rule)                                 | A unit test only                                     |
| 7   | Both docs, § 7.5: one paragraph stating the three rules; `doc/README.md` example built from the first fixture                                                                                                                                                                         | rule: a language rule is documented where the others are |                                                      |
| 8   | Commit type `fix:`, the author's reading of the current state                                                                                                                                                                                                                         | user                                                     | `feat:` (the #121 test: "was X possible before?")    |
| 9   | On the way: the one-frame check of a merge reads the frames declared above it too, plus the frames its replacers inherited; a frame declared below a merge is trimmed by phase 2 (decision 4)                                                                                         | rule 2 of #145, extended to frames                       | The frames of the whole file, as before              |

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

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- Criteria 1 to 4 met: 154 tests green, the goldens byte-identical,
  the three fixtures rendered and read, the mutation failing each,
  the rules in both docs.
- Reservation, not a criterion: an anchor declared below its filter
  now fails as "Name(s) unknown", the message of a name absent from
  the file. Precise enough for the rule, imprecise on the cause.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                                                  | Agent | User |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track after the spike, one work commit, no question raised on the way                                                                   | well  |      |
| 2   | The spike measured before the fix was decided: the change landed at the spike's size, and the goldens said nothing moved                                               | well  |      |
| 3   | Fixture 113 pins two rules in one diagram (the walk bounded, the declaration joining); a single-rule fixture would have shown the same output before and after the fix | well  |      |
| 4   | The frames of a merge read positionally too (decision 9): a small extension of the recorded decisions, taken without a pause, consistent with rule 2                   | well  |      |

Closed: pending

### 4.2 Rule trace

| Source            | Rule                                                              | Verb (applied / created) |
| ----------------- | ----------------------------------------------------------------- | ------------------------ |
| `tests/RULES.md`  | Mutation smoke-test after adding an NR fixture; numbering counter | applied                  |
| `tests/README.md` | An error fixture has a `.stderr` golden and no `.dot`             | applied                  |
| `doc/README.md`   | A language rule is documented where the others are (decision 7)   | applied                  |
