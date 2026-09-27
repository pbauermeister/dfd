# 145 — Declarations after a view statement join the view

Date: 2026-09-27
Status: PENDING
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

### 1.4 Acceptance criteria

1. `make format`, `make lint`, `make test` pass; the 118 existing
   goldens unchanged (no `nr-regenerate` on them).
2. The three new fixtures render as reviewed under `make nr-review`;
   the mutation smoke-test fails each.
3. `! A` then `process Z` keeps Z; `!>1 A` then `A -> Z` keeps Z by
   declaration, not by the walk (B, the earlier neighbor, kept too);
   `~ B` then `B -> Z` errors naming the removing line.
4. Both docs state the rules in § 7.5; `make doc` clean.

Approved: pending

## 2. Execution

### 2.1 Account

## 3. Delivery

### 3.1 Verdict

## 4. Closure

### 4.1 Retrospective

| #   | Point                    | Agent | User |
| --- | ------------------------ | ----- | ---- |
| 1   | Process and template fit |       |      |

Closed: pending

### 4.2 Rule trace
