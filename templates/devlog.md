# NNN — Short description

Date: YYYY-MM-DD
Status: PENDING
Issue: #NNN · PR: #PPP · Branch: `<prefix>/NNN-short-description`
Task nature: task | refactor | analysis

<!--
Devlog template (see CLAUDE.md "devlog/NNN-short-description.md files").
Copy, fill, delete the sections marked optional that do not apply and
every guidance comment. Section numbers stay stable so that reviews can
cite "§ 1.7". Task nature selects the variant:
  task      feature or fix from an issue: all of Mandate and Plan.
  refactor  driven by an inventory and a mechanical plan: as task, with
            § 1.5 Invariants and § 2.2 Inventory mandatory.
  analysis  study, survey or report: § 1.1–1.4, § 1.9, then a Findings
            section replaces Plan; Closure keeps § 3.4 only.
-->

## 1. Mandate

<!-- Approved by the user before step 1 runs; the approval is recorded
in the line below. Everything the user must read to decide is here. -->

Approved: pending

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
to § 3.5 as a created rule. -->

Triggers: none
Mock-up: no, because
Options: none, because

### 1.8 Acceptance criteria

<!-- Numbered, each checkable by a command or a diff; ticked in
§ 3.2. Include the standing ones: make format lint test pass; NR
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

## 3. Closure

### 3.1 Deviations

<!-- What was done differently from the plan and why. "None" is a
valid entry. -->

### 3.2 Gate check

<!-- The acceptance criteria of § 1.8, ticked, with the command output
that proves each; CI status of the PR. -->

### 3.3 Retrospective

<!-- One row per point worth remembering; the agent and the user each
give a verdict: well, not well, surprise, tension, don't care. -->

| #   | Point | Agent | User |
| --- | ----- | ----- | ---- |
| 1   |       |       |      |

### 3.4 Forward-looking

<!-- Follow-ups filed (TODO items, issues, discussions), and what the
next tasks can now rely on. -->

### 3.5 Rule trace

<!-- Conventions applied (cite the section) and conventions created
by this task (the sentence added, and where). Two verbs only. -->

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
