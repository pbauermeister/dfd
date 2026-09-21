# 094 — Tracing prelude without aliases (DEBUG trap)

Date: 2026-09-21
Status: PENDING
Issue: #94 · PR: #PPP · Branch: `refactor/94-tracing-prelude`
Task nature: refactor
Agent: Claude Fable 5.1

<!--
Devlog template (see CLAUDE.md "devlog/NNN-short-description.md files").
Copy, fill, delete the optional sections that do not apply and every
guidance comment. An omitted section leaves no placeholder: renumber,
and cite a section by number and title ("§ 1.8 Design decisions"),
the title being the stable identifier; these guidance comments refer
by title only. Budget: Mandate and Plan about
120 lines, the whole file about 250 at closure; cite a convention
instead of restating its rationale. Status follows CLAUDE.md: PENDING
until stop 1, ONGOING after it, DONE at stop 4.

Five chapters and four stops. A stop is a dated line that the agent
fills on the user's go, never before: Approved (after the Plan, before
any execution), Tried (after Try it; the user may mandate a loop),
Shipped (the ship decision, once no loop is requested and the test
report is in), Closed (after the Retrospective). A loop adds steps to
Steps, is accounted in Account and refreshes Try it. The Mandate is presented once,
with the mock-up built and the spikes run, so that stop 1 is one
round. Between the stops the agent writes and runs autonomously, to
the depth the step gates (attended or unattended, CLAUDE.md Phase 4)
allow.

Task nature selects the variant:
  change    feature or fix from an issue: all of Mandate and Plan.
  refactor  driven by an inventory and a mechanical plan: as change,
            with Invariants and Inventory mandatory.
  analysis  study, survey or report: Context, Goal, Non-goals,
            Acceptance criteria, then a Findings chapter replaces Plan
            and Execution; Delivery keeps Verdict and Discussion;
            Closure keeps Retrospective and Forward-looking.
-->

## 1. Mandate

<!-- Everything the user must read to approve the work, before any of
it runs. Approved together with the Plan, at the end of the Plan. -->

### 1.1 Context

TODO item 16, issue #94; brief with the candidate prelude, its trials
and the migration in `discussions/tracing-prelude-debug-trap.md`
(from #90). The helpers of `tools/init-tracing.sh` (`echo`, `banner`,
`banner2`, `step`) are aliases carrying a `;`: as an operand of `||`
or `&&`, or inside `$(...)`, the second command runs unconditionally
and `set -u` fails on `save_flags`. Bit #88 in `$(...)` and #90 in
the fallbacks of `recipes/require-system.sh` (CI run 35513228401);
workaround in place: `printf` in list context and a rule in the
prelude header. Six scripts source the prelude (`recipes/doc.sh`,
`release.sh`, `require-system.sh`, `publish-to-pypi.sh`,
`publish-to-testpypi.sh`, `tools/test-installation.sh`); the two
publishing recipes carry `#!/bin/sh`.

### 1.2 Goal

<!-- What is true once the task is done, in one paragraph. -->

### 1.3 Non-goals

<!-- What is deliberately left out, each with the reason, so that a
skip is a decision and not an omission. -->

### 1.4 Invariants

<!-- Rules that every option must satisfy: call directions, naming
rules, compatibility. Cite the convention when one exists. Mandatory
for refactor, optional otherwise. -->

### 1.5 Taste

<!-- Preferences of the user that are not rules yet, stated before
they are discovered by contradiction: what the user says at the
mandate review, and what the agent recalls from past decisions, marked
"recalled". Optional. -->

### 1.6 Set-based design

<!-- Done before the decisions are written, so that they are read off
an artifact and not off prose. Triggers: a new container name; an
inventory classifying existing items; a thing that could live in two
places; an intent inherited from a prior task; ambition vocabulary;
one conceptual row among mechanical churn. Any of them: build the
mock-up of the supposed design in a throwaway worktree and paste here
the smallest slice that decides (a listing, the entry-point file as it
would read, one sample). If the mock-up leaves a design question open:
name it, build two or three options in their own worktrees, one row
each below, and recommend one; the Plan is written for the
recommended option and redone if the user picks another at stop 1.
The reason the user gives is the rule: written here, promoted to the
convention by the step that ships it, traced in Rule trace. These lines
stay even when all say "none": the skip is a decision. Before stop 1
the agent re-reads the Mandate as a reviewer: does each name describe
the files, which direction does each call go, which existing file
violates the new rule. Set-based design decides where the heavy work
goes: a short exploration of the alternatives and partial mock-ups,
before the investment. It pays most when the outcome is complex and
dependent (many files, forms, generated artifacts). Refining the chosen
design is not its job: that is the Try it loop. -->

Triggers: none
Mock-up: no, because
Design question: none
Options: none, because

| Option | What differs | For | Against |
| ------ | ------------ | --- | ------- |
|        |              |     |         |

### 1.7 Spikes

<!-- A decision that depends on a tool's behavior, a layout engine or
data is decided by a measured trial, not a mock-up: what is run, in a
throwaway clone under the job scratch directory, and what number
decides. Omit when every decision reads off the artifact. -->

### 1.8 Design decisions

<!-- One row per decision, read off the mock-up and the spikes. Basis
is "rule: <name>" when a convention decides it, "taste" when the
user's preference does, "option <n>" when Set-based design decided it. The user
reads the taste rows; the agent checks each rule row against the
convention it cites. -->

| #   | Decision | Basis | Alternatives considered |
| --- | -------- | ----- | ----------------------- |
| 1   |          |       |                         |

### 1.9 Acceptance criteria

<!-- Numbered, each checkable by a command or a diff; ticked in
Test report. Include the standing ones: make format lint test pass; NR
fixtures and mutation smoke-test when fixtures change. -->

1.

## 2. Plan

### 2.1 Steps

<!-- One pushed commit per step. Each step lists its files, its
numbered actions, its verification commands with the pass condition,
and its commit subject in conventional form. Steps that share one
step gate (attended or unattended) say so. -->

**Step 1 — Name** (`type:`)

Files:

Actions:

1.

Verify:

Commit: `type: subject`

### 2.2 Inventory

<!-- Every file created, moved, renamed or edited, with the change in
one phrase. Mandatory for refactor, where the grep that produced it is
cited so that the sweep at each step can repeat it. -->

| File | Change |
| ---- | ------ |
|      |        |

### 2.3 Scope boundary

<!-- What this branch does not touch even if friction appears, and
where each such item goes (a TODO item on this branch). -->

<!-- Stop 1: the user approves Mandate and Plan. Nothing runs before. -->

Approved: pending

## 3. Execution

### 3.1 Account

<!-- Terse. Per step: "as planned", or the notable and unexpected
things (a sweep that caught a miss, a trial that failed, a decision
taken on the way and its basis). A rule discovered on the way goes to
Rule trace. -->

## 4. Delivery

<!-- The basis of the ship decision, in order: what the work looks
like, what the tests say, what the agent recommends, the discussion in
which the user decides. -->

### 4.1 Try it

<!-- How the user uses, demos or sees the work: the commands to run,
the file to open, the image to look at, the diff to read. Illustrate
when a picture says it (an SVG under `devlog/img/`, a listing, a
before/after). A try is something run, opened or read, never
imagined; a dry run counts only when executed. Omit the section and
stop 2 when there is nothing to try. -->

<!-- Stop 2: the user tries the work, and either mandates a loop or
lets the delivery proceed. -->

Tried: pending

### 4.2 Test report

<!-- The Acceptance criteria, ticked, with the command output
that proves each; make format lint test; CI status of the PR; a test
that caught a real error during the task, if any. -->

### 4.3 Verdict

<!-- The agent's self-assessment, not the decision: written before the
user reads Discussion, it is the valve against overclaiming. A criterion
not proven is a reservation, not a tick. A reservation that outlives
the task becomes a TODO item. -->

**Recommendation:** accept | accept with reservations | reject

Rationale:

- <criterion met, test green, property achieved>

Reservations (for "with reservations"; for "reject", what must change):

1.

### 4.4 Discussion

<!-- Where the ship decision is taken, once no loop is requested and
the test report is in: what surfaced unexpectedly, what remains an
issue. One row per point, with the decision: postpone (a TODO item,
filed on this branch) or accept as is; a "complement now" here is a
loop. -->

| #   | Point | Decision |
| --- | ----- | -------- |
| 1   |       |          |

<!-- Stop 3: the ship decision, once the discussion is settled. Then
the PR is marked ready. -->

Shipped: pending

## 5. Closure

### 5.1 Retrospective

<!-- One row per point worth remembering; the agent gives its rating,
the user gives theirs: well, not well, surprise, tension, don't care.
The first row is standing: "process and template fit", the friction
met with this template. A fix that is a guidance comment or a pointer
is applied on this branch and listed in Forward-looking; a fix that
changes the structure (a chapter, a stop) becomes a TODO item. The
process line carries the measures the discussion of set-based design
asked for. -->

| #   | Point                    | Agent | User |
| --- | ------------------------ | ----- | ---- |
| 1   | Process and template fit |       |      |

Process: <N> rounds before stop 1; <N> loops at stop 2; rework after
stop 1: none | <what>

<!-- Stop 4: the user fills their column. -->

Closed: pending

### 5.2 Forward-looking

<!-- Follow-ups filed (TODO items, issues, discussions), template and
CLAUDE.md fixes made on this branch, and what the next tasks can now
rely on. -->

### 5.3 Rule trace

<!-- Conventions applied (cite the section) and conventions created
by this task (the sentence added, and where). Two verbs only. -->

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
