# 092 — Devlog templates per task kind, set-based design gate

Date: 2026-09-20
Status: PENDING
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

One attended/unattended gate for the three steps: docs only.

### 2.2 Inventory

`templates/devlog.md`, `templates/discussion.md` (new); this devlog
(new); `CLAUDE.md` (devlog section, Phase 2 step 3, Phases 3–4);
`TODO.md` (item 14).

### 2.3 Scope boundary

Existing devlogs and discussions untouched; `CLAUDE.md` outside the
named places untouched (length: TODO item 15); the Phase 4 step gate
kept, stops added to it.

Approved: pending

## 3. Execution

### 3.1 Account

## 4. Delivery

### 4.1 Try it

Tried: pending

### 4.2 Test report

### 4.3 Verdict

**Recommendation:** pending

Rationale:

Reservations:

### 4.4 Discussion

| #   | Point | Decision |
| --- | ----- | -------- |
| 1   |       |          |

Shipped: pending

## 5. Closure

### 5.1 Retrospective

| #   | Point | Agent | User |
| --- | ----- | ----- | ---- |
| 1   |       |       |      |

Process: rounds before stop 1; loops at stop 2; rework after stop 1:

Closed: pending

### 5.2 Forward-looking

### 5.3 Rule trace

| Source | Rule | Verb (applied / created) |
| ------ | ---- | ------------------------ |
|        |      |                          |
