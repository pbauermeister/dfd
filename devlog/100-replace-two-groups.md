# 100 — Replacement flows between two replaced groups

Date: 2026-09-23
Status: ONGOING
Issue: #100 · PR: #PPP · Branch: `fix/100-replace-two-groups`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

Issue #100: with two `~=` replacements in one diagram (`~=AB A B`,
`~=CD C D`), the flows between the two groups vanish instead of
becoming flows between the replacers. The issue suspects a single-pass
implementation; reading `src/data_flow_diagram/dsl/filters.py` shows
the mapping is collected in phase 1 and applied in phase 2 already.
The cause is the guard in `_apply_filters()` that skips a connection
whose two endpoints are both replaced, meant to drop the self-loop of
an intra-group flow, but written without checking that both map to
the same replacer.

### 1.2 Goal

A flow between two items of different replaced groups is rendered
between their replacers. A flow whose two ends collapse to one item
after replacement is dropped, as before. Two NR fixtures lock it in;
both fail on the code before the fix.

### 1.3 Design decisions

| #   | Decision                                                                                                   | Basis                          | Alternatives considered                                                      |
| --- | ---------------------------------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------- |
| 1   | Rewrite the endpoints first, then skip when `src == dst`: one condition covers same-group and replacer-as-endpoint | rule: simplest correct condition | Compare `replacement.get(src) == replacement.get(dst)` (misses `A -> AB`) |
| 2   | Fixtures committed before the fix, so that the history shows them failing                                  | user (this conversation)       | Fixtures and fix in one commit                                               |
| 3   | Two fixtures: 077 the issue's example verbatim, 078 the edge cases (intra-group flows, flow to a replacer) | taste                          | One fixture with everything (less legible as a repro)                       |

## 2. Execution

### 2.1 Account

Approved: 2026-09-23

## 3. Delivery

### 3.1 Try it

Tried: pending

### 3.2 Verdict

## 4. Closure

### 4.1 Retrospective

| #   | Point                    | Agent | User |
| --- | ------------------------ | ----- | ---- |
| 1   | Process and template fit |       |      |

Process:

Closed: pending

### 4.2 Rule trace

| Source          | Rule                                                        | Verb (applied / created) |
| --------------- | ----------------------------------------------------------- | ------------------------ |
| `tests/RULES.md` | Mutation smoke-test after adding NR fixtures                | applied                  |
