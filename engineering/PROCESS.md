# Task process

The lifecycle of a task, from its origin to its closure. `CLAUDE.md`
points here; this file is the reference. Sections are cited by title.

## Task start process

When starting a non-trivial task, follow these phases in order.

### Phase 1 — Task origin

Two paths:

- **From devlog:** The user references a `devlog/DEVLOG.md` section (or other
  high-level devlog) and the desired chapter. The agent drafts a GitHub issue
  title and body from that content and presents it to the user for confirmation
  before creating it (`gh issue create`). This is a good opportunity to
  reconsider whether the task still applies.
- **From GitHub issue:** The user provides a GitHub issue number whose
  description contains the specs.

### Phase 2 — Scaffolding

The agent performs these steps in sequence:

1. Fetch the issue title and description (`gh issue view NNN`).
2. Create a branch named `<prefix>/NNN-short-description` (prefix: `fix`,
   `feature`, `refactor`, `doc`, or `test`).
3. Copy `templates/devlog.md` to `devlog/NNN-short-description.md`; fill the
   header, then Context, Goal and Non-goals (and Invariants for a
   refactor) from the issue and its brief.
4. Commit the devlog file on the branch; when the task comes from a
   `TODO.md` item, remove the item in the same commit (see "TODO.md").
5. Open a **draft** PR against `main` (`gh pr create --draft`) with a minimal
   body (link to the devlog file, `Closes #NNN`) and a title in conventional
   form (`<type>: <description>`, see "Versioning convention"): the `PR title`
   check runs on drafts too, and the title becomes the squash commit subject.

### Phase 3 — Specification refinement

Agent and user discuss until the specs are clear:

- **Stop 0.** The user confirms the frame (Context, Goal, Non-goals,
  Invariants); the agent writes the date in `Framed:`. No mock-up or
  spike runs before. The mock-up may then refine the frame in place.
- The agent fills the rest of the Mandate and the Plan per the template's
  guidance comments (set-based design, spikes, decisions marked rule or
  taste) and presents them once, with the mock-up built and the spikes run.
- Reflect together on whether new NR test fixtures are needed. If yes, add
  "create NR fixtures" as the first step.
- Once specs are agreed, update the PR body to reflect the refined requirements
  (may include checklists).
- **Stop 1.** The user approves Mandate and Plan; the agent writes the date
  in `Approved:` and sets the status to `ONGOING`. Nothing runs while
  `Approved:` is pending.

### Phase 4 — Implementation

After stop 1, the agent implements per the Plan's steps and the rules in
"Implementation workflow", accounting for each step in the Execution chapter.

Before starting each step, the agent:

1. Lists all actions the step will involve (files to create/modify, commands
   to run, permissions needed).
2. Offers the user the choice to let the step run **unattended** (the agent
   proceeds autonomously through the entire step, stopping only if a question
   or unexpected problem arises) or **attended** (the agent stops at each
   sub-action for validation).

This way the user can grant autonomy for straightforward steps and keep
tighter control over sensitive or uncertain ones.

Three more stops follow, at the places the template marks: `Tried:` (after
Try it; the user may mandate a loop), `Shipped:` (the ship decision, after
the test report, the verdict and the discussion; then the PR is marked
ready), `Closed:` (after the Retrospective; status `DONE`). The template's
guidance comments are the reference for what each stop needs.

### Fast track

When the decisions are already recorded (a brief, a prior devlog, a
TODO item) and the work is small with no design question, the user may
call the fast track: issue, branch and PR as in Phase 2 but without
the devlog; everything agreed in conversation; the work runs
unattended after one go; the devlog is written at closure in its fast
form (see the template's "Track") and committed on the branch for the
user's approval before the merge. If the discussion or the work
inflate, the agent writes the devlog then and the full track resumes
at the stop reached.

Claude: if the user starts a task without following this process, briefly
remind them of it.

## TODO.md

- `TODO.md` holds the items not yet assigned to a task, appended, with
  the context they arose in. An item is a heading numbered from the
  file's `Next number:` counter, bumped in the same commit; numbers are
  unique for the life of the file and never reused. An item that arises
  during a task is committed on the task branch (see "Branching and PR
  workflow").
- An item is removed, not struck through, when its issue is filed
  (Phase 2, alongside the devlog) or when it is dropped; the commit
  message names the issue or the reason. The git history of the file and
  the devlog carry the record.

## devlog/NNN-short-description.md files

- For each task of non-trivial scope, a file in `devlog/` named
  `NNN-short-description.md` is copied from `templates/devlog.md` during the
  task start process (phase 2). **NNN** is the GitHub issue number,
  zero-padded; the slug is the user's short description, else derived from
  the issue title.
- The template's guidance comments are the reference for the structure, the
  task natures, the five stops (`Framed:`, `Approved:`, `Tried:`,
  `Shipped:`, `Closed:`, dated lines the agent fills on the user's go,
  never before)
  and the budget; the copy replaces them by content. Sections are cited by
  number and title.
- Status: `PENDING` until stop 1, `ONGOING` after it, `DONE` at stop 4,
  `REJECTED` when abandoned.
- A template fix that a retrospective calls for is committed on the task's
  branch when it is a comment or a pointer; a structural change becomes a
  TODO item. The template's history is the process history.

## discussions/ files

- Analysis that outgrew a task and belongs to no devlog (a spin-off brief
  for another repository, a design kept for a dedicated task, a recorded
  exchange) goes to `discussions/<topic>.md`, copied from
  `templates/discussion.md`, written on the branch it originated from so
  that history retraces it. It ends with an executive summary and the
  outcomes or measures that follow.

## Branching and PR workflow

For every non-trivial fix or feature (i.e. anything with a `devlog/NNN-*.md`
file), the branch and draft PR are created during the task start process
(phase 2):

1. Branch is named `<prefix>/NNN-short-description` (prefix: `fix`, `feature`,
   `refactor`, `doc`, or `test`).
2. A **draft** PR is opened against `main` immediately, so the work is visible
   from the start. The PR body starts minimal (link to devlog), is updated
   after specification is agreed (may include checklists), and may be updated
   again when the PR is marked ready (to account for changes decided during
   implementation).
3. All implementation work — including the `devlog/NNN-*.md` file — is committed
   on that branch.
4. When implementation is complete, mark the PR as ready for review
   (`gh pr ready`).
5. **Review the PR title's type before any merge.** The title is squashed
   into the one commit that reaches `main`: it is the PR's changelog line and
   it decides the version bump. Its type must be at the highest bump level
   among the PR's commits and name the PR's purpose (a feature that needed
   two fixes on the way is `feat`). The purpose often drifts during the
   work; after the merge only a history rewrite could correct it. The agent
   reminds this review before suggesting a merge, and asks the user before
   merging a PR itself.
6. Merge (or ask the user to merge) only after the PR is approved, CI passes,
   and the `conventional` and `gate` checks are green on an up-to-date branch
   (the ruleset on `main` requires them; see the merge gate in
   `engineering/RELEASING.md`).

Devlog in the PR, squash merge and the PR title as the single conventional
subject hold each other up: the devlog commits vanish at squash and stay out
of the changelog, so the title is the only place where the PR's type is
decided.

Direct commits to `main` are reserved for housekeeping (TODO item removals,
`CLAUDE.md` edits) that does not warrant a PR. A `TODO.md` item that arises
during a task is committed on the task branch, not on `main`: it shows the
context it originated in and how the pressure on the task was released, and
while the branch is being worked on it serves as a reservation. Every commit
message, everywhere, is in conventional form: the `commit-msg` hook installed
by `make require` enforces it.

## Task closing

After the PR is merged:

1. Switch to `main` and pull.
2. Close the GitHub issue (`gh issue close NNN`).
3. Update `MEMORY.md` with anything noteworthy from the task: completed
   milestones, architectural decisions, new conventions, or design
   preferences that emerged from discussion.
4. Show the release plan (`make show-release-plan`: next version and the
   commits since the last release with their bump levels) and ask whether
   to release now (`make release`, see `engineering/RELEASING.md`).

## Implementation workflow

When implementing an approved plan:

- **One pushed commit per step of the Plan.** During a step, commit freely:
  these granular commits are the safety net while the work is fluid.
  At the end of the step, once `make format`, `make lint` and `make test`
  pass, squash the step's commits into one (`git reset --soft` to the
  step's base, one commit) whose body carries the step summary and the
  findings, and push. The Mandate and the Plan land as one devlog
  commit at scaffolding. The PR's commit list then reads as a table of
  contents of the steps, whether the user reviews step by step or all at
  once. Squash before pushing, so it is a local rewrite; if save points
  were pushed mid-step, the step-end squash costs one
  `git push --force-with-lease` by the user, after a backup ref.
- **Stop and ask** before continuing when: (a) the next step depends on validating the current result, (b) a decision is needed that was not resolved in the plan, or (c) something unexpected is discovered.
- Otherwise, proceed autonomously through the remaining steps and commit as you go.
- **Before each step** (as described in Phase 4), list all actions the step
  will involve — files to create/modify, commands to run, and any dangerous or
  irreversible actions — so the user can make an informed unattended/attended
  choice.
- Before marking a PR ready, self-review the diff against the Type safety
  section of `engineering/CONVENTIONS.md`.

## Established tool vs bespoke script

Measure, don't estimate. When a choice is between using an established
tool for a fraction of what it does and writing a small script, settle
it with a quick trial rather than opinions: try the tool in a throwaway
clone (under the job scratch directory, never the real repo) with a
draft configuration and fake inputs; show the configuration and the
produced artifact verbatim, and note what the tool dropped or warned
about. Then state the balance in numbers: lines of configuration against
lines of code plus tests, upgrade churn against ownership. The default
leans to the established tool, but a configuration heading toward ~60
lines reopens the debate. The balance is questioned every time, not
applied by reflex.
