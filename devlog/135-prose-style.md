# 135 — A prose style sheet for the project's documents

Date: 2026-09-26
Status: DONE
Issue: #135 · PR: #136 · Branch: `doc/135-prose-style`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 35 (removed in the first commit), raised at the review of
#128 where the agent's doc prose carried "AI smells", its shape agreed
the same day. Written last in the batch 31, 29, 34, 35 of 2026-09-26, stacked on
#133 (PR #134); at the review the user moved it first, since its
rule applies to the three others, so the branch was rebuilt off
`main` with its own commits (backup ref `refs/backup/doc-135-stacked`)
and PR #136 retargeted. Source: the author's blog-post
style rules (`~/dev-pb/on-ai/style/authorial-style-rules.md`, out of
the repo), a signature guide for posts with anecdotes, humor and
storytelling, of which a subset fits technical documentation.

### 1.2 Goal

`engineering/PROSE-STYLE.md`, about a hundred lines: "The Elements of
Style" taken as read; the departures kept on purpose; the rules of the
book to press; the forms preferred; the tells of generated text with
their plain form; a check before delivering. The root map and
`CONVENTIONS.md` "Markdown formatting" point to it.

### 1.3 Design decisions

| #   | Decision                                                                                                                               | Basis                                                                            | Alternatives considered                               |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | File name `engineering/PROSE-STYLE.md`                                                                                                 | user (the go): "style" alone collides with the DSL statement and the commit type | `STYLE.md`; `PROSE.md`; a section of `CONVENTIONS.md` |
| 2   | Scope: every prose text of the repo, PR and commit bodies included; code comments stay with `COMMENTING.md`; American spelling kept    | TODO 35 (rule)                                                                   | `doc/` only                                           |
| 3   | The book is cited, not repeated: the sheet holds the deltas (departures, rules to press, forms, tells) and stays under a hundred lines | TODO 35, the author a proponent of the book (rule)                               | A self-contained guide                                |
| 4   | The tells as a two-column table, tell and plain form, since a tell is recognized faster than a rule is applied                         | taste                                                                            | A prose list                                          |
| 5   | The blog rules' voice devices (anecdote hook, humor, "I", ellipsis, italics, warm close) left out, named once as staying with the blog | TODO 35: "the subset that fits" (rule)                                           | A tone dial for the devlogs                           |
| 6   | The map row is allowed by the TODO's explicit request; `RULES.md` untouched                                                            | `engineering/RULES.md` third rule                                                | A line in `RULES.md`                                  |

### 1.4 Acceptance criteria

1. The sheet reads in under a hundred lines, no em-dash in it, prettier
   clean; map row and pointer in place.
2. The batch's own prose (PROCESS.md section, three devlogs) passes
   the tells table at the reviews.

Approved: 2026-09-26 (the go for the batch)

## 2. Execution

### 2.1 Account

- First commit: TODO 35 removed, filed as #135.
- `3718814` chore: the sheet (97 lines, zero em-dashes by grep), the
  map row, the pointer (criterion 1).
- This devlog. Criterion 2 is for the reviews.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- The sheet is the deltas to a book the author knows; the reviews of
  #130, #132 and #134 are its first application.

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                                                                                                                   | Agent    | User |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: fast track for a document whose shape was agreed before the batch                                                                                                                             | well     |      |
| 2   | The sheet was written last in the batch, so the three earlier texts were written without it: a task whose output is a rule for the others closes first, and the assessment should have ordered it so (folded into #129) | not well |      |

Process: 1 round before the go (the batch assessment); 1 loop at the review (the closing order, no change to the sheet).

Closed: 2026-09-26

### 4.2 Rule trace

| Source                       | Rule                                          | Verb (applied / created) |
| ---------------------------- | --------------------------------------------- | ------------------------ |
| `engineering/RULES.md`       | `CLAUDE.md` appended on explicit request only | applied (TODO 35 asked)  |
| `engineering/PROSE-STYLE.md` | The prose style sheet                         | created                  |
