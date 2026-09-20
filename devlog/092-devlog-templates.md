# 092 — Devlog templates per task kind, set-based design gate

Date: 2026-09-20
Status: PENDING
Issue: #92 · PR: #93 · Branch: `doc/92-devlog-templates`
Task nature: task

## 1. Mandate

Approved: pending

### 1.1 Context

TODO item 14, with the conclusions of
`discussions/set-based-design.md` (the thread that followed #90). The
34 devlogs of the project share `Requirement` (31) and `Design` (29),
a third have `Outcome`, and the rest is one-off section names, because
no template exists. #88 and #90 showed that the preparatory phase
discovers invariants and taste bottom-up when a frame would ask for
them top-down, and that a mock-up of the supposed design would have
saved the `runbooks/` rework of #90.

This devlog is written with the template it introduces: it is the
mock-up of § 1.7, read as such at the design review.

### 1.2 Goal

`templates/devlog.md` and `templates/discussion.md` exist and are
what the scaffolding phase copies. The devlog template has a Mandate
approved in one round before step 1, a Plan and a Closure, with the
sections the discussion concluded on (context, goal, non-goals,
invariants, taste, decisions marked rule or taste, set-based design
gate, acceptance criteria, spikes; steps, inventory, scope boundary;
deviations, gate check, retrospective, forward-looking, rule trace),
sized by a task nature selector (task, refactor, analysis).
`CLAUDE.md` codifies the template, the approval gate and the set-based
design step of Phase 3. TODO item 14 is done.

### 1.3 Non-goals

- Retrofitting the 34 existing devlogs: history, left as written.
- A scaffolding tool (`tools/new-devlog.py`, a `make` target): the
  agent copies the file; a tool earns its place when copying goes
  wrong twice (YAGNI).
- Offloading `CLAUDE.md` (TODO item 15): this task edits the devlog
  section and Phase 3 in place; the split of the file is its own task.
- A review-attestation hook: the approval is a line in the Mandate,
  not a mechanism.
- Governance identifiers on rules (clause numbers): the rule trace
  cites sections by name.

### 1.4 Invariants

- The task start process of `CLAUDE.md` keeps its four phases; the
  template changes what Phase 2 creates and what Phase 3 records, not
  the phases.
- Devlog file names stay `NNN-short-description.md`, zero-padded, in
  `devlog/`; discussions stay in `discussions/`.
- Every Markdown file added is prettier-clean (VSCode auto-format
  produces no diff).
- `CLAUDE.md` is edited only where this task's mandate says so.

### 1.5 Taste

- Skeleton, not weight: a section that would read "none" on most
  tasks is optional, and the guidance stays in HTML comments that the
  copy deletes, so a filled devlog carries no boilerplate.
- Section numbers (§ 1.7) so that reviews can cite a section.
- Terse: the template's own text is guidance, not prose.

### 1.6 Design decisions

| #   | Decision                                                                                  | Basis                               | Alternatives considered                                                                       |
| --- | ----------------------------------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------- |
| 1   | Templates live in a top-level `templates/`, named `devlog.md`, `discussion.md`            | rule: naming (family, topic-first)  | `devlog/templates/` next to the numbered files; `devlog/TEMPLATE.md`                          |
| 2   | One devlog template with a task-nature selector, not one file per variant                 | taste                               | three files `devlog-task.md`, `devlog-refactor.md`, `devlog-analysis.md` (drift between them) |
| 3   | Top sections renamed `Mandate`, `Plan`, `Closure` (numbered 1–3)                          | taste                               | keep `Requirement`, `Design`, `Outcome` (31 / 29 / 10 files use them)                         |
| 4   | The approval gate is a line `Approved: <date>` under Mandate, set by the agent on the go  | taste                               | a review hook; a PR review event                                                              |
| 5   | Decisions are a table with a Basis column, rule or taste                                  | rule: set-based design (discussion) | prose bullets, as in #90                                                                      |
| 6   | Set-based design is a section of the Mandate with three lines: Triggers, Mock-up, Options | rule: set-based design (discussion) | a Phase 3 checklist only, outside the devlog                                                  |
| 7   | Rule trace with two verbs, applied and created, citing sections by name                   | taste                               | four verbs and clause identifiers                                                             |
| 8   | Analysis variant: Findings replaces Plan, Closure keeps forward-looking only              | taste                               | full structure for every nature                                                               |
| 9   | Discussions get their own short template                                                  | rule: discussions convention (#90)  | no template; discussions as analysis devlogs                                                  |

### 1.7 Set-based design

Triggers: a new container name (`templates/`); a new rule classifying
existing items (task natures over devlogs); a thing that could live in
two places (`templates/` or `devlog/`).
Mock-up: yes, on this branch (a docs task: the branch is the throwaway),
as `templates/devlog.md` plus this devlog, its first instance.
Options: none, because the two design questions the triggers name
(where the files live; one template or three) are readable in the
mock-up and decided in § 1.6 rows 1 and 2; to be confirmed at the
design review, which may still ask for the three-file option to be
materialized.

### 1.8 Acceptance criteria

1. `templates/devlog.md` and `templates/discussion.md` exist; both are
   prettier-clean.
2. This devlog follows `templates/devlog.md` section by section, with
   no guidance comment left.
3. `CLAUDE.md`: the section "devlog/NNN-short-description.md files"
   describes the template, the task natures and the approval line;
   Phase 2 step 3 says "copy `templates/devlog.md`"; Phase 3 carries
   the set-based design paragraph drafted in the discussion file; the
   `discussions/` folder is described in one bullet.
4. `make lint test` pass (nothing under test changes; the run proves
   nothing broke by accident).
5. TODO item 14 struck through, `— DONE (#92)`.

### 1.9 Spikes

None: every decision is decided by how the artifact reads.

## 2. Plan

### 2.1 Steps

**Step 1 — Templates** (`docs:`)

Files: `templates/devlog.md`, `templates/discussion.md`, this devlog.

1. Apply the design review's changes to the two templates.
2. Re-align this devlog with the final template (criterion 2).
3. Verify: `.venv/node_modules/.bin/prettier --check templates/*.md
devlog/092-*.md` clean.
4. Commit: `docs: devlog and discussion templates`.

**Step 2 — CLAUDE.md** (`docs:`)

Files: `CLAUDE.md`, `TODO.md`.

1. Replace the bullets of "devlog/NNN-short-description.md files" by
   the template description (natures, Mandate/Plan/Closure, approval
   line, the copy in Phase 2).
2. Phase 2 step 3: "copy `templates/devlog.md`, fill the header and
   § 1.1".
3. Phase 3: replace "recorded in the devlog's **Requirement** section"
   and "**Design** section" by the Mandate and Plan sections; append
   the set-based design paragraph from the end of
   `discussions/set-based-design.md`; add "the user approves the
   Mandate: the agent writes the date in `Approved:`".
4. Add a bullet on `discussions/` after the devlog section.
5. TODO item 14 to DONE.
6. Verify: `make lint test`; `grep -n 'Requirement\|Design\b' CLAUDE.md`
   shows only the intended mentions.
7. Commit: `docs: CLAUDE.md, devlog template, approval gate, set-based
design in Phase 3`.

**Step 3 — Closure** (`docs:`)

Files: this devlog.

1. § 3 filled; status DONE; PR ready.
2. Commit: `docs: devlog 092 closure`.

Steps 1–3 share one attended/unattended gate: docs only, reversible.

### 2.2 Inventory

| File                             | Change                                                    |
| -------------------------------- | --------------------------------------------------------- |
| `templates/devlog.md`            | new                                                       |
| `templates/discussion.md`        | new                                                       |
| `devlog/092-devlog-templates.md` | new, first instance of the template                       |
| `CLAUDE.md`                      | devlog section rewritten; Phase 2 step 3; Phase 3 bullets |
| `TODO.md`                        | item 14 done                                              |

### 2.3 Scope boundary

- Existing devlogs and discussions keep their structure.
- `CLAUDE.md` outside the named sections is untouched; its length is
  TODO item 15's concern.
- The Phase 4 step gate ("attended or unattended") is unchanged.

## 3. Closure

### 3.1 Deviations

### 3.2 Gate check

### 3.3 Retrospective

| #   | Point | Agent | User |
| --- | ----- | ----- | ---- |
| 1   |       |       |      |

### 3.4 Forward-looking

### 3.5 Rule trace

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
