# 104 — Keep only the flows involved by a "keep" filter

Date: 2026-09-24
Status: PENDING
Issue: #104 · PR: #PPP · Branch: `feature/104-keep-involved-flows`
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

Framed: pending

### 1.5 Taste

### 1.6 Set-based design

Triggers: an intent inherited from the issue (two open questions
named there); a thing that could live in two places (the path
membership, computed during traversal or as a pass over the kept set).
Mock-up: pending stop 0
Design question: (a) the syntax of the option; (b) the computation of
path membership, per flow during traversal or as a post-pass over
kept nodes.
Options: pending stop 0

| Option | What differs | For | Against |
| ------ | ------------ | --- | ------- |
|        |              |     |         |

### 1.7 Spikes

### 1.8 Design decisions

| #   | Decision | Basis | Alternatives considered |
| --- | -------- | ----- | ----------------------- |
| 1   |          |       |                         |

### 1.9 Acceptance criteria

1.

## 2. Plan

### 2.1 Steps

**Step 1 — Name** (`type:`)

Files:

Actions:

1.

Verify:

Commit: `type: subject`

### 2.2 Inventory

| File | Change |
| ---- | ------ |
|      |        |

### 2.3 Scope boundary

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
