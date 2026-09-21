# 096 — Stop 0 and the fast track in the devlog template

Date: 2026-09-22
Status: DONE
Issue: #96 · PR: #97 · Branch: `doc/96-devlog-stop-0`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 17, from #94 (`devlog/094-tracing-prelude.md`, § 4.4 row 3,
§ 5.1 row 1): a `Framed:` stop was experimented there before the
mock-up, and rated "surprise" by the user for having been spotted
late. The fast track itself was asked during this task: a devlog for a
change to the devlog template would copy the file it edits, and the
record already existed in 094, yet the user wanted a short file for
the records. This devlog is the first instance of the fast form.

### 1.2 Goal

`templates/devlog.md` has five stops (`Framed:` after Invariants), a
`Track: full | fast` header line with the fast form defined, and a
budget restated on 092 and 094. CLAUDE.md Phase 2 fills Context to
Non-goals (Invariants for a refactor) at scaffolding, Phase 3 opens
with Stop 0, and a "Fast track" section states when and how. TODO
item 17 is done.

### 1.3 Design decisions

| #   | Decision                                                                                                       | Basis                                 | Alternatives considered                                |
| --- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------ |
| 1   | `Framed:` after § 1.4 Invariants: for a refactor the invariants are part of the frame the mock-up must satisfy | taste (#94, agent's call confirmed)   | After § 1.3 Non-goals                                  |
| 2   | Budget about 150 lines of prose, tables and listings not counted, about 300 at closure, marked "to revisit"    | measured: 092 (164/25), 094 (267/47)  | Keep 120; drop the budget                              |
| 3   | Fast track as a `Track:` header line and a guidance paragraph, not a second template file                      | taste: one template, sections omitted | `templates/devlog-fast.md` (two files to keep aligned) |
| 4   | Fast devlog written at closure, for the user's approval; earlier if the task inflates                          | user (this conversation)              | No devlog for fast tasks (no record); devlog at start  |

## 2. Execution

### 2.1 Account

- 1st commit: Stop 0 (template comment, `Framed:` line, five stops),
  budget, CLAUDE.md Phase 2 and 3, TODO item 17 struck through.
- 2nd commit: the fast track (template "Track", CLAUDE.md section)
  and this devlog, asked at the review of the first commit.

Approved: 2026-09-22

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- The diff is the one the issue describes; #94 exercised Stop 0 and
  this task exercises the fast form.
- Reservation carried as a note, not a blocker: the budget numbers rest
  on two devlogs.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                               | Agent | User |
| --- | ----------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: the fast form was defined and used in the same task       | well  | well |
| 2   | The fast track was called in conversation, not from a rule: the rule is now written | well  | well |

Process: 1 round before the go; the fast track and this file added
at the review of the diff.

Closed: 2026-09-22

### 4.2 Rule trace

| Source                  | Rule                                                       | Verb (applied / created) |
| ----------------------- | ---------------------------------------------------------- | ------------------------ |
| `templates/devlog.md`   | Stop 0, `Framed:` before any mock-up or spike              | created                  |
| `templates/devlog.md`   | Track full or fast; the fast form's sections and two stops | created                  |
| `CLAUDE.md`, Fast track | when the fast track applies and how it runs                | created                  |
