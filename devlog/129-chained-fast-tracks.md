# 129 — Codify the chained fast tracks

Date: 2026-09-26
Status: DONE
Issue: #129 · PR: #130 · Branch: `doc/129-chained-fast-tracks`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 31 (removed in the first commit), raised after the build
batch of 2026-09-24 (#107 to #117) and the filter batch of 2026-09-25
(#119 to #125), both judged a success by the user. First of the batch
31, 29, 34, 35 of 2026-09-26, off `main`; the three others dogfood
the section while it is under review, so this task is reviewed and
closed last, an inversion of the closing rule decided at the go.

### 1.2 Goal

A section "Chained fast tracks" in `engineering/PROCESS.md`, next to
"Fast track": the upfront assessment with disposable decision drafts,
the chained unattended runs, the ordering and stacking rules, the
sequential reviews and what they may do. No new template.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                  | Basis                                                      | Alternatives considered                            |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| 1   | One section of three numbered phases (assessment, runs, reviews), about 40 lines, right after "Fast track", which points to it                            | TODO 31: "codify it lightly"                               | A page of its own under `engineering/`; a template |
| 2   | Closing order = tackling order unless the assessment says otherwise; a task that shares files is stacked on the previous task in the closing order        | practice of the two batches; this batch's inversion (rule) | Always stack the whole batch                       |
| 3   | The decision drafts are a scratch artifact, never committed; the decisions taken go to the fast devlogs                                                   | TODO 31 (taste)                                            | Commit the drafts under `discussions/`             |
| 4   | The review may approve, loop or stop; a stopped task ends `REJECTED`, devlog to `main` by a direct `chore:` commit, branch kept on `origin`               | #125 (rule)                                                | Delete the branch of a stopped task                |
| 5   | Retarget the next PR to `main` before merging its base; merge `main` forward after each merge; adjacent `TODO.md` removals conflict and resolve to "gone" | build batch, the stacked-PR base deletion lesson (rule)    | Rebase the stack                                   |

### 1.4 Acceptance criteria

1. The section reads in `engineering/PROCESS.md`; "Fast track" points
   to it; prettier clean.
2. The three tasks that follow in the batch run by it.

Approved: 2026-09-26 (the go for the batch)

## 2. Execution

### 2.1 Account

- First commit: TODO 31 removed, filed as #129.
- `fef6d7a` chore: the section and the pointer in "Fast track".
- This devlog.
- Review loop (2026-09-26): the ordering rule sharpened in the
  section (a task whose output the others apply closes first), after
  the review of #136 moved the style sheet to the head of the batch;
  the model and token budgeting asked at the review filed as TODO
  item 36, to be discussed.
- Review loop (2026-09-26), before its own review: what the three
  closures taught, folded in. Verification is shown even unattended
  (test report, tests where a harness exists: the reviews of #132
  and #134); a devlog push re-runs the required checks (#134's
  merge); a `TODO.md` conflict resolved from `main`'s file undoes
  the branch's edits, twice on this batch (item 29 re-added on 133,
  item 36 dropped on 129). The ordering sentence reflowed.
- Review loop (2026-09-26), the hiccups report: nine hiccups, two
  causes (the order, the TODO removals per branch). Amendments: the
  issues filed and the TODO items removed in one commit on `main`
  at the go, stacking reserved for files of substance; a closure as
  one sequence; a row that lowers verification is an open row; an
  irreversible step runs alone (Implementation workflow).

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept, after the three dogfooding tasks are
reviewed: what they show about the section is folded in here before
the merge.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                                                                                     | Agent    | User       |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------- |
| 1   | Process and template fit: fast track for a section written from a recorded shape                                                                                                                          | well     | well       |
| 2   | The assessment of this batch was drafted before the section existed and served as its test: the phases were read off it                                                                                   | well     | well       |
| 3   | The assessment ordered by kind and shared files and missed the dependency between outputs: the style sheet, written last, applied to the three texts before it; the user saw it at the first review       | not well | ended well |
| 4   | Removing each TODO item on its branch made `TODO.md` the one shared file: three conflicts on the forward merges, two resolutions that undid the branch's edits, stacking that existed for that file alone | not well | ended well |
| 5   | Chained shell commands ran on after a failure (a force push, an issue comment): the exit of a pipeline is its last command's                                                                              | not well | ended well |

Process: 1 round before the go (the assessment); 3 loops from the reviews of the batch (the ordering rule; the closures' lessons; the hiccups report); its own review: 1 round, the hiccups report.

Closed: 2026-09-26

### 4.2 Rule trace

| Source                                       | Rule                                                      | Verb (applied / created) |
| -------------------------------------------- | --------------------------------------------------------- | ------------------------ |
| `engineering/PROCESS.md` Fast track          | PR first, agreed in conversation, unattended, fast devlog | applied                  |
| `engineering/PROCESS.md` Chained fast tracks | Assessment, chained runs, sequential reviews              | created                  |
