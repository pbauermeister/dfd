# 092 — Devlog templates per task kind, set-based design gate

Date: 2026-09-20
Status: ONGOING
Issue: #92 · PR: #93 · Branch: `doc/92-devlog-templates`
Task nature: change
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 14; conclusions in `discussions/set-based-design.md`. No
template exists: over 34 devlogs, `Requirement` and `Design` are
near-universal, `Outcome` in a third, the rest one-off names. #88 and
#90 discovered invariants and taste bottom-up; a mock-up would have
saved the `runbooks/` rework. Rules inherited from a formal devlog
practice elsewhere (titles as identifiers, line budget, verdict shape,
stop rule) come from its recorded incidents. This devlog is the first
instance of the template: the mock-up of § 1.6.

### 1.2 Goal

`templates/devlog.md` and `templates/discussion.md` exist and are what
Phase 2 copies. The devlog has five chapters (Mandate, Plan,
Execution, Delivery, Closure), four user stops (after the Plan; after Try
it, which may send the work back for another loop; the ship decision,
once no loop is requested and the test report is in; at the
Retrospective), a task-nature selector (change, refactor, analysis)
and a line budget. `CLAUDE.md` codifies the template, the stops and
the set-based design step of Phase 3. TODO item 14 is done.

### 1.3 Non-goals

- Retrofitting existing devlogs: history.
- A scaffolding tool or `make` target: the agent copies (YAGNI).
- Offloading `CLAUDE.md` (TODO item 15).
- A review-attestation hook: three tension rows elsewhere.
- Clause identifiers and a trace vocabulary; resource accounting.

### 1.4 Invariants

- The four phases of the task start process stay; the template changes
  what Phase 2 creates and what Phases 3–4 record.
- File names `NNN-short-description.md` in `devlog/`; `discussions/`
  unchanged.
- Every added Markdown file is prettier-clean.
- `CLAUDE.md` edited only where § 2.1 step 2 says.

### 1.5 Taste

- Skeleton, not weight: guidance in HTML comments the copy deletes; a
  section reading "none" on most tasks is optional.
- Sections cited by number and title; terse.

### 1.6 Set-based design

Triggers: new container name (`templates/`); a rule classifying
existing items (natures); a thing that could live in two places.
Mock-up: yes, on this branch (docs task, the branch is the throwaway):
`templates/devlog.md`, and this devlog as its first instance. The
slice that decides, the outline of the template:

```
1. Mandate    Context, Goal, Non-goals, Invariants, Taste,
              Set-based design, Spikes, Design decisions,
              Acceptance criteria
2. Plan       Steps, Inventory, Scope boundary        Approved:
3. Execution  Account
4. Delivery   Try it  Tried:   Test report, Verdict, Discussion
                                                      Shipped:
5. Closure    Retrospective  Closed:   Forward-looking, Rule trace
```

Design question: none open after the mock-up; the two the triggers
named (where the files live; one template or three) read off it and
are decision rows 1–2.
Options: none, because both questions are decided by reading; the
user may still ask for the three-file option materialized.

### 1.7 Spikes

None: every decision reads off the artifact.

### 1.8 Design decisions

| #   | Decision                                                                                                                                                                      | Basis                                        | Alternative                                                          |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| 1   | Top-level `templates/`: `devlog.md`, `discussion.md`                                                                                                                          | rule: naming, topic-first family             | `devlog/templates/`                                                  |
| 2   | One devlog template with a nature selector                                                                                                                                    | taste                                        | three files, drift between them                                      |
| 3   | Chapters `Mandate`, `Plan`, `Execution`, `Delivery`, `Closure`, numbered                                                                                                      | user review 2026-09-20                       | `Requirement`, `Design`, `Outcome`                                   |
| 4   | Each stop is a dated line (`Approved:`, `Reviewed:`) the agent writes on the go                                                                                               | taste                                        | a hook; a PR review event                                            |
| 5   | Decisions table with a Basis column, rule or taste                                                                                                                            | rule: set-based design                       | prose bullets (#90)                                                  |
| 6   | § 1.6 Set-based design precedes the decisions: triggers, mock-up slice pasted, design question, options table; decisions are read off it                                      | rule: set-based design                       | a Phase 3 checklist only; decisions before the mock-up (first draft) |
| 7   | Rule trace with two verbs, sections cited by name                                                                                                                             | taste                                        | four verbs, clause identifiers                                       |
| 8   | Analysis nature: Findings replaces Plan and Execution; Closure keeps § 4.2, § 4.4                                                                                             | taste                                        | full structure for every nature                                      |
| 9   | Discussion template ends with an executive summary and outcomes                                                                                                               | rule: discussions convention; user review    | none                                                                 |
| 10  | Execution holds a terse account; a Delivery chapter holds Try it, Test report, Verdict and the Discussion where the ship decision is taken, contiguous, before stop 2         | user review 2026-09-20; chapter split: taste | try-it in Execution, verdict and gate check in Closure               |
| 11  | Verdict shape: recommendation, rationale, reservations; the process measures (rounds, loops, rework) as a line of the Retrospective                                           | user review; shape inherited                 | free-form verdict; measures inside the verdict                       |
| 12  | Titles are the identifiers, numbers local; omitted sections renumber                                                                                                          | inherited rule (numbering-gap incident)      | fixed numbers with gaps                                              |
| 13  | Four stops, each a dated line: `Approved:` (Plan), `Tried:` (may loop; omitted when nothing to try), `Shipped:` (test report, verdict, discussion), `Closed:` (Retrospective) | user review 2026-09-20                       | one approval at the Mandate (first mock-up)                          |
| 14  | Natures `change`, `refactor`, `analysis`; header line `Agent:`                                                                                                                | taste                                        | `task` as a name; no provenance                                      |
| 15  | Stop rule "nothing runs while `Approved:` is pending" lives in `CLAUDE.md`                                                                                                    | inherited rule (two gate violations)         | the line in the file alone                                           |

### 1.9 Acceptance criteria

1. Both templates exist, prettier-clean.
2. This devlog follows `templates/devlog.md` section by section, no
   guidance comment left, within the budget.
3. `CLAUDE.md`: devlog section describes template, natures, chapters,
   stops, stop rule, budget; Phase 2 step 3 copies the template;
   Phase 3 ends at stop 1 with the set-based design paragraph; Phase 4
   names stops 2 and 3; one bullet on `discussions/`.
4. `make lint test` pass.
5. TODO item 14 `— DONE (#92)`.

## 2. Plan

### 2.1 Steps

**Step 1 — Templates** (`docs:`): apply the design review to both
templates; re-align this devlog; verify `prettier --check
templates/*.md devlog/092-*.md`; commit `docs: devlog and discussion
templates`.

**Step 2 — CLAUDE.md** (`docs:`): rewrite the bullets of
"devlog/NNN-short-description.md files"; Phase 2 step 3 → copy the
template; Phase 3 → Mandate and Plan, the set-based design paragraph
parked in `discussions/set-based-design.md`, stop 1 and the stop rule;
Phase 4 → stops 2 to 4 (Tried, Shipped, Closed), the budget; a `discussions/` bullet; TODO
item 14 done. Verify `make lint test`, `grep -n 'Requirement\|Design\b'
CLAUDE.md` shows only intended mentions. Commit `docs: CLAUDE.md,
devlog template, stops, set-based design in Phase 3`.

**Step 3 — Execution, Delivery, Closure** (`docs:`): § 3 to § 5
filled, stops 2 to 4, status DONE, PR ready. Commit `docs: devlog 092
execution and closure`.

**Step 4 — Deduplicate** (`docs:`, loop mandated at stop 2): the
template's guidance comments are the reference; `CLAUDE.md` points to
them instead of repeating them (Phase 3 one bullet plus stop 1; Phase 4
one paragraph naming stops 2 to 4; devlog section three bullets); the
comments refer to sections by title, never by number. Verify: `grep -c
'§ [0-9]' templates/devlog.md CLAUDE.md` gives 1 and 0; `CLAUDE.md`
delta against `main` about +12 lines. Commit `docs: CLAUDE.md points
to the template's guidance; titles, not numbers`.

**Step 5 — Process fit** (`docs:`, loop mandated at stop 2): the
Set-based design comment states what the phase is for and that
refining is the Try it loop's job; a try is never imagined; the
Retrospective gets a standing "process and template fit" row and the
two fix paths (comment or pointer on the branch, structure as a TODO
item); `CLAUDE.md` one bullet for the fix paths. Commit `docs:
template, process fit row and fix paths`.

One attended/unattended gate for the steps: docs only.

### 2.2 Inventory

`templates/devlog.md`, `templates/discussion.md` (new); this devlog
(new); `CLAUDE.md` (devlog section, Phase 2 step 3, Phases 3–4);
`TODO.md` (item 14).

### 2.3 Scope boundary

Existing devlogs and discussions untouched; `CLAUDE.md` outside the
named places untouched (length: TODO item 15); the Phase 4 step gate
kept, stops added to it.

Approved: 2026-09-20

## 3. Execution

### 3.1 Account

- Step 1: no diff. The templates were finalized during the design
  review (six revisions before stop 1: structure note, fresh-eyes
  review, terminology, set-based flow); the mock-up devlog was
  re-aligned at each. Empty commit skipped.
- Step 2: as planned. `CLAUDE.md` 265 → 311 lines (+46): the Phase 3
  set-based paragraph and the four stops are the bulk; TODO item 15's
  concern, noted for § 4.4. `devlog/img/` not created: on first use.
- Step 3: stop 2 taken on this devlog itself; the user mandated a
  loop: `CLAUDE.md` repeated the template's guidance (+46 lines), a
  second copy to maintain; and the comments cited sections by number
  while the header said numbers are local.
- Step 4 (loop): as planned; `CLAUDE.md` back to about +12 against
  `main`, 1 numbered reference left in the template (the citation
  example), 0 in `CLAUDE.md`.
- Step 5 (loop): as planned. Two observations at stop 2: the loops
  since stop 1 refine one design, which is the Try it loop's job, not
  set-based design's (there was nothing to choose between); and
  "try it mentally" was the prose-and-imagination decision the method
  argues against, so the template is tested by use and the mechanism
  to act on the friction is what this task delivers.

## 4. Delivery

### 4.1 Try it

- Read `templates/devlog.md` as the file a scaffolding copy would
  start from; then this devlog as its filled instance.
- Read the `CLAUDE.md` diff after the loop: `git diff main -- CLAUDE.md`
  (Phase 2 step 3, Phase 3, Phase 4, the two sections after the
  DEVLOG.md one; +18 net lines, every pointer to the template).
- The template is tested by the next tasks, not imagined here;
  friction lands in the standing first row of each Retrospective.

Tried: 2026-09-21

### 4.2 Test report

1. ✅ `templates/devlog.md`, `templates/discussion.md` exist;
   `prettier --check templates/*.md devlog/092-*.md CLAUDE.md`: clean.
2. ⚠️ Section list of this devlog equals the template's (`diff` of the
   heading lists: empty); 0 guidance comments left. Budget: Mandate +
   Plan 163 lines against about 120; file 247 against about 250. Over
   on the first, by the inline mock-up slice (14 lines) and the two
   loop steps (17 lines).
3. ✅ `CLAUDE.md`: Phase 2 copies the template; Phase 3 one bullet plus
   stop 1 with the rule; Phase 4 names stops 2 to 4; devlog section
   points to the template, states the status rule and the fix paths;
   `## discussions/ files` present. `git diff main --stat`: +43 −22.
   Numbered references: 0 in `CLAUDE.md`, 1 in the template (the
   citation example).
4. ✅ `make lint`: clean; `make test`: 96 passed. CI on PR #93 at
   098970d: conventional, gate, smoke-test-wheel, test 3.11/3.12/3.13
   all pass.
5. ✅ `TODO.md`: `14. ~~Devlog templates~~ — DONE (#92)`.

No test caught an error during the task: nothing under test changed.

### 4.3 Verdict

**Recommendation:** accept with reservations

Rationale:

- Criteria 1, 3, 4, 5 proven by command output above.
- The template survived its first instance: every section answered,
  four stops dated, two loops recorded per the loop rule, and the
  loops themselves produced two template rules (reference by title,
  the standing row) through the mechanism the template prescribes.

Reservations:

1. Criterion 2, budget: Mandate + Plan at 163 lines. The overrun is the
   inline mock-up slice, which the method wants, and the loop steps,
   which the loop rule wants. Either the budget is too tight for a
   task with loops, or loop steps should be accounted more tersely.
   Data from the next tasks decides; the standing row carries it.
2. One task nature tested (change), no real options, no spike. Fit for
   refactor and analysis, and the options table, are untested by
   construction; deferred to use by the user's decision at stop 2.
3. `CLAUDE.md` grew by 21 net lines; TODO item 15's concern, not this
   task's.

### 4.4 Discussion

| #   | Point                                                                                   | Decision                                                              |
| --- | --------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Budget overrun of Mandate + Plan (reservation 1)                                        | accept as is; revisit the budget after five tasks                     |
| 2   | Refactor and analysis natures, options table, spikes untested (reservation 2)           | accept as is; tested by use, standing row collects the friction       |
| 3   | `CLAUDE.md` +21 lines                                                                   | postponed: TODO item 15                                               |
| 4   | `CLAUDE.md` "devlog/DEVLOG.md general file" section is stale (file replaced by TODO.md) | postponed: fold into TODO item 15 (out of this task's scope boundary) |

Shipped: 2026-09-21

## 5. Closure

### 5.1 Retrospective

| #   | Point                                                                                                                                                               | Agent    | User |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: every section answered on the first instance; two loops recorded as steps; stop 2 mandated both of them                                   | well     |      |
| 2   | The mandate was presented once, but reworked six times before stop 1 (structure, fresh eyes, terminology, set-based flow); each pass improved it, none was a rewind | well     |      |
| 3   | Redundancy between `CLAUDE.md` and the template was written by the agent and caught by the user at stop 2                                                           | not well |      |
| 4   | "Try it mentally" written by the agent, the very thing the method rejects                                                                                           | not well |      |
| 5   | Inherited rules (titles as identifiers, budget, verdict shape, stop rule) came from the other project's incidents at zero cost                                      | well     |      |
| 6   | Budget: the loop steps and the inline slice broke it on the first instance                                                                                          | surprise |      |
| 7   | Edits by string replacement on prettier-formatted tables failed silently twice; regex on the row number fixed it                                                    | not well |      |

Process: 7 rounds before stop 1 (1 structure, 4 fresh-eyes and
terminology, 2 set-based flow); 2 loops at stop 2; rework after stop 1:
none.

Closed: pending

### 5.2 Forward-looking

### 5.3 Rule trace

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
