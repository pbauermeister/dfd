# NNN — Short description

Date: YYYY-MM-DD
Status: PENDING
Issue: #NNN · PR: #PPP · Branch: `<prefix>/NNN-short-description`
Task nature: change | refactor | analysis
Agent: <model name and version>

<!--
Devlog template (see CLAUDE.md "devlog/NNN-short-description.md files").
Copy, fill, delete the sections marked optional that do not apply and
every guidance comment. Omitted sections are not left as placeholders:
renumber, and cite a section by number and title ("§ 1.6 Design
decisions"), the title being the stable identifier. Budget: Mandate
and Plan about 120 lines, the whole file about 250 at closure; cite a
convention instead of restating its rationale. Four chapters, three stops for user approval: after the
Plan (before any execution), after the Execution (the user tries the
work, and the discussion settles what is complemented now and what is
postponed), and at the Retrospective (after the agent's verdict). Between the stops the agent writes and runs autonomously to
the depth the Plan's gates allow. Task nature selects the variant:
  change    feature or fix from an issue: all of Mandate and Plan.
  refactor  driven by an inventory and a mechanical plan: as change,
            with § 1.4 Invariants and § 2.2 Inventory mandatory.
  analysis  study, survey or report: § 1.1–1.4, § 1.9, then a Findings
            chapter replaces Plan and Execution; Delivery keeps § 4.3
            and § 4.4; Closure keeps § 5.2.
-->

## 1. Mandate

<!-- Everything the user must read to approve the work, before any of
it runs. Approved together with the Plan, at the end of § 2. -->

### 1.1 Context

<!-- Where the task comes from (TODO item, discussion, issue), the
predecessors it builds on, the state it starts from. -->

### 1.2 Goal

<!-- What is true once the task is done, in one paragraph. -->

### 1.3 Non-goals

<!-- What is deliberately left out, each with the reason, so that a
skip is a decision and not an omission. -->

### 1.4 Invariants

<!-- Rules that every option must satisfy: call directions, naming
rules, compatibility. Cite the convention when one exists. Mandatory
for refactor; write "none beyond the conventions" otherwise. -->

### 1.5 Taste

<!-- Preferences of the maintainer that are not rules yet: stated
before they are discovered by contradiction. Optional. -->

### 1.6 Design decisions

<!-- One row per decision. Basis is "rule: <name>" when a convention
decides it, "taste" when the maintainer's preference does. The
reviewer reads the taste rows; the rule rows are checked by the
agent. -->

| #   | Decision | Basis | Alternatives considered |
| --- | -------- | ----- | ----------------------- |
| 1   |          |       |                         |

### 1.7 Set-based design

<!-- Triggers present (new container name; inventory classifying
existing items; a thing that could live in two places; an intent
inherited from a prior task; ambition vocabulary; one conceptual row
among mechanical churn; a decision depending on a tool, a layout or
data)? Then: Mock-up: yes, <where>, or no, because. Options: none,
because, or the design question and the two or three options, each in
a throwaway worktree. The design review picks one and the reason goes
to § 5.3 as a created rule. -->

Triggers: none
Mock-up: no, because
Options: none, because

### 1.8 Acceptance criteria

<!-- Numbered, each checkable by a command or a diff; ticked in
§ 4.2. Include the standing ones: make format lint test pass; NR
fixtures and mutation smoke-test when fixtures change. -->

1.

### 1.9 Spikes

<!-- Measured trials that a decision depends on (a tool's behavior, a
layout, data): what is run, in a throwaway clone under the job scratch
directory, and what number decides. Optional; "none" when every
decision is decided by how the artifact reads. -->

## 2. Plan

### 2.1 Steps

<!-- One pushed commit per step. Each step lists its files, its
numbered actions, its verification commands with the pass condition,
and its commit subject in conventional form. Steps that share one
attended/unattended gate say so. -->

**Step 1 — Name** (`type:`)

Files:

1.
2. Verify:
3. Commit: `type: subject`

### 2.2 Inventory

<!-- Every file created, moved, renamed or edited, with the change in
one phrase. Mandatory for refactor; the grep that produced it is
cited so that the sweep at each step can repeat it. -->

| File | Change |
| ---- | ------ |
|      |        |

### 2.3 Scope boundary

<!-- What this branch does not touch even if friction appears, and
where each such item goes (a TODO item on this branch). -->

<!-- Stop 1. The user approves Mandate and Plan; the agent writes the
date. Nothing runs before. -->

Approved: pending

## 3. Execution

### 3.1 Account

<!-- Terse. Per step: "as planned", or the notable and unexpected
things (a sweep that caught a miss, a trial that failed, a decision
taken on the way and its basis). Findings that become rules go to
§ 5.3. -->

## 4. Delivery

<!-- The basis of the ship decision, read in one sitting: what the
work looks like, what the tests say, what the agent recommends; then
the discussion in which the user decides. -->

### 4.1 Try it

<!-- How the user uses, demos or sees the work: the commands to run,
the file to open, the image to look at, the diff to read. Illustrate
when a picture says it (an SVG, a listing, a before/after). -->

### 4.2 Test report

<!-- The acceptance criteria of § 1.8, ticked, with the command output
that proves each; make format lint test; CI status of the PR; tests
that bit during the task, if any. -->

### 4.3 Verdict

<!-- The agent's self-assessment, not the decision: written before the
user reads § 4.4, it is the valve against overclaiming. A criterion
not proven is a reservation, not a tick. A reservation that outlives
the task becomes a TODO item. -->

**Recommendation:** accept | accept with reservations | reject

Rationale:

- <criterion met, test green, property achieved>

Reservations (for "with reservations"; for "reject", what must change):

1.

Rounds: <design rounds before stop 1>; rework after stop 1: none | <what>

### 4.4 Discussion

<!-- Where the results are discussed and the ship decision is taken:
the demo, what surfaced unexpectedly, what remains an issue. One row
per point, with the decision: complement now (a step added to § 2.1,
then back to § 3.1 and a new § 4), postpone (a TODO item, filed on
this branch), or accept as is. -->

| #   | Point | Decision |
| --- | ----- | -------- |
| 1   |       |          |

<!-- Stop 2. The user has tried the work, read the test report and the
verdict, and the discussion is settled; the agent writes the date.
Then the PR is marked ready. -->

Reviewed: pending

## 5. Closure

### 5.1 Retrospective

<!-- One row per point worth remembering; the agent gives its verdict,
the user gives theirs: well, not well, surprise, tension, don't care. -->

| #   | Point | Agent | User |
| --- | ----- | ----- | ---- |
| 1   |       |       |      |

<!-- Stop 3. The user fills their column; the agent writes the date. -->

Reviewed: pending

### 5.2 Forward-looking

<!-- Follow-ups filed (TODO items, issues, discussions), and what the
next tasks can now rely on. -->

### 5.3 Rule trace

<!-- Conventions applied (cite the section) and conventions created
by this task (the sentence added, and where). Two verbs only. -->

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
