# 098 — Offload CLAUDE.md into a root file plus on-demand documents

Date: 2026-09-22
Status: ONGOING
Issue: #98 · PR: #99 · Branch: `doc/98-offload-claude-md`
Task nature: refactor
Track: full
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 15, filed by #90. `CLAUDE.md` is 303 lines in 16 sections,
loaded whole into every session whatever the task; each process task
appends to it (#92: +21 lines, #96: the Stop 0 and fast track
paragraphs). Its "devlog/DEVLOG.md general file" section is stale since
`TODO.md` replaced that file. The pattern "CLAUDE.md points, a document
is the reference" already exists for the devlog template's guidance
comments, `doc/CONVENTIONS.md`, `doc/COMMENTING.md`, `doc/RELEASING.md`
and `tests/README.md`; this task extends it to the rest.

Loading facts, verified in the Claude Code memory documentation
(`code.claude.com/docs/en/memory`) before framing: the root
`CLAUDE.md`, parent-directory `CLAUDE.md` files, `@path` imports and
`.claude/rules/*.md` files without a `paths:` frontmatter all load at
launch, every session. Only two things load on demand: a `CLAUDE.md`
inside a subfolder, when Claude reads files there, and a rules file
with a `paths:` glob. The docs target under 200 lines per `CLAUDE.md`.
`/context` lists the loaded memory files and their token cost.

Section sizes at the start, in lines:

| Group                     | Sections                                                                                                                      | Lines |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----- |
| Task lifecycle            | Task start process 88, devlog files 19, discussions 9, branching and PR 43, task closing 13, implementation 24, versioning 21 | 217   |
| Coding conventions        | Design philosophy 16, naming 14, commenting 10, formatting 5, Markdown 3                                                      | 48    |
| Project-specific or stale | DEVLOG.md 9 (stale), tests 4, NR tests 9, import compatibility 14                                                             | 36    |

### 1.2 Goal

The root `CLAUDE.md` is the project's own instance, about 50 lines:
what the project is, its layout, import compatibility, a map table
"When / Read first", the reminder line, and an `@import` of the rules
that apply to every edit. `doc/` holds product documentation only. A
new `engineering/` folder holds how the project is built, generic to
the way of working: `RULES.md` (the always-on rules, imported by the
root), `PROCESS.md` (the task lifecycle, from task start to closing,
reached by an imperative pointer and loaded once when a task starts),
and `CONVENTIONS.md`, `COMMENTING.md`, `RELEASING.md` moved from `doc/`
with their pointers redirected. `tests/CLAUDE.md` holds the test rules
and loads lazily. The stale DEVLOG.md section is gone. Line counts and
`/context` figures before and after are recorded here. TODO item 15 is
done.

### 1.3 Non-goals

- Sharing the generic rules across projects (a directives library, and
  the choice between a plain document and a skill or plugin as its
  vehicle): a separate discussion, so that this task stays a split of
  the existing text. The split keeps the door open: generic documents
  carry no project-specific sentence.
- Changing the meaning of any rule: this is a move, and a rewording
  only where a section is stale or duplicates another document.
- Trimming `MEMORY.md`, which is over its load limit: same disease,
  separate housekeeping on `main`.
- Reworking `CONVENTIONS.md`, `COMMENTING.md`, `RELEASING.md` or
  `tests/README.md` beyond the move and the received text.
- Rewriting `doc/` paths in history files (`devlog/`, `discussions/`,
  `CHANGES.md`) and in the text of `TODO.md` items: they are records.

### 1.4 Invariants

- Every rule of the current `CLAUDE.md` is present in exactly one
  place after the split (rule kept, duplicate removed), checked by a
  per-section table in the Inventory.
- Whatever loads at launch stays under the docs' 200-line target and
  contains no procedure that only a task needs.
- The root file stays the append point: a new rule is either a map
  entry there or a paragraph in the document the map names.
- Always-on generic text is `@import`ed (loads at launch); on-demand
  documents are reached by a pointer the agent must follow ("read X
  before Y"), never by `@import`, which would load them anyway.
- What sits in `engineering/` is generic to the way of working, a seed
  for a later rules library; what is specific to this project sits in
  the root.
- Devlog process text is not placed under `devlog/`: a per-folder file
  loads only once a file there is read, which is after the process is
  needed.
- `doc/` is product documentation only; engineering documents live in
  `engineering/`; no live file (Makefile, workflows, recipes, tools,
  README, templates) keeps a `doc/` path to a moved file.
- Markdown formatting per CLAUDE.md "Markdown formatting" (padded
  tables); prettier-clean.

Framed: 2026-09-22

### 1.5 Taste

- Recalled: "CLAUDE.md points, the document is the reference" (#92,
  #96): the root names the document and the trigger, never restates.
- Recalled: one template, sections omitted, rather than two files to
  keep aligned (#96 decision 3): applies to containers too, no new
  folder for one file.
- Recalled: YAGNI + open door (CLAUDE.md "Design philosophy").
- Stated at stop 0 review: the root keeps only what is generic to the
  agent's work here; project specifics go to their own document. `doc/`
  is for product usage; engineering process gets its own folder.
- Stated at the second stop 0 review: `engineering/` should have a
  chance to become the seed of a rules library, so the always-on rules
  belong there too, and the project specifics in the root.

### 1.6 Set-based design

Triggers: a new container name (the lifecycle document, the engineering
folder, the per-folder file); an inventory classifying existing items
(16 sections); a thing that could live in two places (the lifecycle
document; the folder rules).
Mock-up: yes, the full split built in a throwaway worktree, since the
work is a move of text and the mock-up is the work minus the pointers.
The first mock-up (lifecycle at `doc/PROCESS.md`, root of 55 lines)
raised the two amendments of § 1.5 at stop 0 review; the second (root of
29 lines, `engineering/PROJECT.md`, rules in the root) raised the third;
the third is below.
Design question: the name of the engineering folder.
Options: five names, listings only.

| Option | What differs    | For                                                                    | Against                                              |
| ------ | --------------- | ---------------------------------------------------------------------- | ---------------------------------------------------- |
| A      | `engineering/`  | Says what it holds without a metaphor; pairs with `doc/` (use / build) | Long                                                 |
| B      | `handbook/`     | The GitLab-style name; would suit a later shared library               | A metaphor                                           |
| C      | `dev/`          | Short                                                                  | Ambiguous with tooling                               |
| D      | `process/`      | Names the main file                                                    | Too narrow once conventions and releasing live there |
| E      | `contributing/` | GitHub connotation                                                     | Single-file connotation; single author               |

Chosen: A (user, stop 0 review).

The mock-up, in lines at launch and on demand (`doc/README.md` and
`doc/SYNTAX.md` untouched):

| File                         | Before | After | Loaded          |
| ---------------------------- | ------ | ----- | --------------- |
| `CLAUDE.md`                  | 303    | 48    | at launch       |
| `engineering/RULES.md`       | 0      | 10    | at launch (`@`) |
| `engineering/PROCESS.md`     | 0      | 221   | on pointer      |
| `engineering/CONVENTIONS.md` | 265    | 276   | on pointer      |
| `engineering/RELEASING.md`   | 144    | 148   | on pointer      |
| `engineering/COMMENTING.md`  | 127    | 127   | on pointer      |
| `tests/CLAUDE.md`            | 0      | 14    | lazily          |

The root as it would read: a project paragraph; "Layout" (source,
`doc/`, `engineering/` and the task records, scripts); "Import
compatibility" verbatim; a six-row map table "When / Read first" (task
lifecycle, devlog template, conventions, commenting, tests, releasing);
the reminder line; `@engineering/RULES.md` as the last line. What the
mock-up surfaced: `tools/` and `recipes/` get no folder file, since the
current `CLAUDE.md` has no folder-bound rule for them (`CONVENTIONS.md`
"Script levels" holds them); `templates/devlog.md` cites `CLAUDE.md`
four times by section or phase; the moved documents are cited by 15
pointers in live files (Makefile, `pyproject.toml`, two workflows, two
recipes, the tracing prelude, `README.md`, `CONVENTIONS.md` itself), all
redirected by one `sed`; `RELEASING.md` and `CONVENTIONS.md` are not
generic yet (this project's publishing setup, this project's identifiers
as examples), which the seed will need a pass for, out of scope.

### 1.7 Spikes

None: the loading behavior comes from the documentation (§ 1.1); the
measurement of the token cost is an acceptance criterion run by the user
(`/context` is a session command).

### 1.8 Design decisions

| #   | Decision                                                                                                                                              | Basis                                                                                      | Alternatives considered                                                                                                                      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Engineering documents in `engineering/`; `doc/` keeps product documentation only; `CONVENTIONS.md`, `COMMENTING.md`, `RELEASING.md` move there        | option A; user (stop 0 review)                                                             | Leave the three in `doc/`; B to E                                                                                                            |
| 2   | Lifecycle in one file, `engineering/PROCESS.md`: task start, TODO.md, devlog and discussion files, branching, closing, implementation, tool vs script | taste: needed together at task start                                                       | Four files (multiplies the reads)                                                                                                            |
| 3   | Root = the project's instance: project paragraph, layout, import compatibility, map, reminder, `@engineering/RULES.md`                                | user (second stop 0 review): project specifics in the root, generic text in `engineering/` | Root of 29 lines with the rules and `engineering/PROJECT.md` (second mock-up); a top-level `PROJECT.md` (a second project file for 31 lines) |
| 4   | The three always-on rules in `engineering/RULES.md`, `@import`ed by the root so that they load at launch                                              | user (second stop 0 review); invariant: `@import` for always-on text                       | At the top of `PROCESS.md` (loaded only when a task starts; misses housekeeping edits)                                                       |
| 5   | YAGNI + open door and Markdown formatting become sections of `CONVENTIONS.md`                                                                         | taste: conventions, not project facts                                                      | Root always-on rules                                                                                                                         |
| 6   | The "Key points" summaries of naming and commenting are dropped; the map row is the pointer                                                           | invariant: one place per rule                                                              | Keep them (20 lines of duplicates at launch)                                                                                                 |
| 7   | Folder rules as `tests/CLAUDE.md` only; none for `tools/` and `recipes/`                                                                              | taste: colocated; YAGNI for the two                                                        | `.claude/rules/*.md` with `paths:` (a second container)                                                                                      |
| 8   | The stale DEVLOG.md section becomes a four-line "TODO.md" section in `PROCESS.md` (items appended, task items on the branch, no prettier on it)       | stale text rewritten; the prettier rule promoted from memory                               | Delete without replacement                                                                                                                   |
| 9   | Versioning: the two sentences `RELEASING.md` lacks are added there; the rest was a duplicate                                                          | invariant: one place per rule                                                              | Keep the section in the root                                                                                                                 |
| 10  | The devlog template's four `CLAUDE.md` citations and the 15 live `doc/` pointers are redirected; history files are not                                | invariant: no live stale pointer; non-goal: records                                        | Rewrite history files too                                                                                                                    |

### 1.9 Acceptance criteria

1. `CLAUDE.md` plus `engineering/RULES.md` is at most 60 lines at launch;
   `wc -l` before and after recorded.
2. Every section of the old `CLAUDE.md` has one destination in the
   Inventory, and no rule appears twice (grep of each rule's key phrase
   yields one file).
3. `grep -rn 'doc/CONVENTIONS\|doc/COMMENTING\|doc/RELEASING\|CLAUDE.md'`
   outside `devlog/`, `discussions/`, `CHANGES.md` and `TODO.md` item
   text shows only intended citations.
4. `/context` in a fresh session on `main` and on the branch: the
   memory-files cost, recorded here.
5. Behavioral check: a fresh session on the branch given "let us tackle
   TODO item N" reads `engineering/PROCESS.md` before acting.
6. A fresh session that edits a file under `tests/` has `tests/CLAUDE.md`
   loaded (`/context`).
7. prettier clean on every changed Markdown file; `make lint test` pass;
   `make doc` still works (it wipes `doc/img/`, untouched).
8. TODO item 15 marked done.

## 2. Plan

### 2.1 Steps

**Step 1 — The split** (`docs:`)

Files: `CLAUDE.md`; `engineering/PROCESS.md`, `engineering/RULES.md`,
`tests/CLAUDE.md` (new); `engineering/CONVENTIONS.md`, `COMMENTING.md`,
`RELEASING.md` (moved with `git mv`, edited); pointers in `Makefile`,
`pyproject.toml`, `.github/workflows/merge-gate.yml`, `release.yml`,
`recipes/release.sh`, `recipes/publish-to-pypi.sh`,
`tools/init-tracing.sh`, `README.md`, `templates/devlog.md`.

Actions:

1. `git mv` the three documents to `engineering/`.
2. Create `engineering/PROCESS.md` from the sections listed in the
   Inventory, text moved verbatim except the TODO.md section (decision 8)
   and the heading of the tool-vs-script section.
3. Create `engineering/RULES.md` (decision 4) and `tests/CLAUDE.md`
   (verbatim).
4. Append "Design philosophy" and "Markdown formatting" to
   `CONVENTIONS.md` (decision 5); add the two versioning sentences to
   `RELEASING.md` (decision 9).
5. Rewrite `CLAUDE.md` as in the mock-up (§ 1.6).
6. Redirect the pointers: one `sed` over the live files for the three
   `doc/` paths; the four citations in `templates/devlog.md` by hand.
7. Sweep (criterion 3) and fix every stale pointer outside history
   files.
8. `make format lint test`, prettier on the changed Markdown.

Verify: criteria 1, 2, 3, 7.

Commit: `docs: split CLAUDE.md into a map, engineering/ and tests/CLAUDE.md`

**Step 2 — Measure and record** (`docs:`)

Files: `devlog/098-offload-claude-md.md`, `TODO.md`.

Actions:

1. The user runs `/context` in a fresh session on `main` and on the
   branch (criterion 4), and the two checks of criteria 5 and 6; the
   agent records the figures and outcomes in § 4.2.
2. Mark TODO item 15 done.

Verify: criteria 4, 5, 6, 8.

Commit: `docs: record the context cost before and after #98; TODO item 15 done`

Both steps share one step gate.

### 2.2 Inventory

Produced by `grep -n '^## ' CLAUDE.md` on `main`.

| Old section (lines)                                   | Destination                                                               |
| ----------------------------------------------------- | ------------------------------------------------------------------------- |
| Task start process (88)                               | `engineering/PROCESS.md`, verbatim                                        |
| devlog/DEVLOG.md general file (9)                     | `engineering/PROCESS.md` "TODO.md" (4 lines, decision 8)                  |
| devlog/NNN-short-description.md files (19)            | `engineering/PROCESS.md`, verbatim                                        |
| discussions/ files (9)                                | `engineering/PROCESS.md`, verbatim                                        |
| Writing or modifying tests (4)                        | `tests/CLAUDE.md`, verbatim                                               |
| Non-regression tests (9)                              | `tests/CLAUDE.md`, verbatim                                               |
| Branching and PR workflow (43)                        | `engineering/PROCESS.md`, verbatim                                        |
| Task closing (13)                                     | `engineering/PROCESS.md`, verbatim                                        |
| Implementation workflow (24)                          | `engineering/PROCESS.md`, verbatim                                        |
| Design philosophy (16)                                | YAGNI: `CONVENTIONS.md` "Design philosophy"; tool vs script: `PROCESS.md` |
| Import compatibility (14)                             | root, verbatim                                                            |
| Naming and structure conventions (14)                 | root map row; rest dropped (decision 6)                                   |
| Commenting style (10)                                 | root map row; rest dropped (decision 6)                                   |
| Formatting (5)                                        | `engineering/RULES.md`, with the commit and append rules                  |
| Versioning convention (21)                            | `engineering/RELEASING.md` (two sentences); root map row                  |
| Markdown formatting (3)                               | `CONVENTIONS.md` "Markdown formatting", verbatim                          |
| `doc/CONVENTIONS.md`, `COMMENTING.md`, `RELEASING.md` | `git mv` to `engineering/`                                                |
| `templates/devlog.md` (4 citations)                   | pointers to `engineering/PROCESS.md`                                      |
| 15 `doc/` pointers in live files (§ 1.6)              | `engineering/` paths                                                      |

### 2.3 Scope boundary

- `MEMORY.md` over its load limit: housekeeping on `main`, not here.
- Sharing rules across projects: `discussions/`, a later task.
- The moved documents and `tests/README.md`: no restructuring;
  `tests/README.md` does not absorb `tests/CLAUDE.md` (the README is a
  guide, the folder file is the rule set).
- History files and `TODO.md` item text keep their `doc/` and
  `CLAUDE.md` citations.
- `TODO.md` numbering and the items' text: untouched except item 15.

<!-- Stop 1: the user approves Mandate and Plan. Nothing runs before. -->

Approved: 2026-09-22

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
