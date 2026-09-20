# Project Instructions

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
   header and § 1.1 Context from the issue.
4. Commit the devlog file on the branch.
5. Open a **draft** PR against `main` (`gh pr create --draft`) with a minimal
   body (link to the devlog file, `Closes #NNN`) and a title in conventional
   form (`<type>: <description>`, see "Versioning convention"): the `PR title`
   check runs on drafts too, and the title becomes the squash commit subject.

### Phase 3 — Specification refinement

Agent and user discuss until the specs are clear:

- The agent fills the Mandate (§ 1) and the Plan (§ 2) of the devlog and
  presents them once, with the mock-up built and the spikes run. Every
  decision is a row of § 1.8 Design decisions, marked rule or taste; the
  user reads the taste rows.
- Set-based design (§ 1.6): when the requirement shows a trigger (a new
  container name; an inventory classifying existing items; a thing that
  could live in two places; an intent inherited from a prior task; ambition
  vocabulary; one conceptual row among mechanical churn), the agent builds
  a mock-up of the supposed design in a throwaway worktree and pastes the
  smallest slice that decides into § 1.6. When the mock-up leaves a design
  question open, the agent builds two or three options in their own
  worktrees, compares them in § 1.6 and recommends one; the user picks one
  at stop 1, stating why, and the why is recorded as a rule. Otherwise
  § 1.6 says "none, because": the skip is a decision. Options are thrown
  away too; the Plan is written for the chosen one. A decision that
  depends on a tool, a layout or data is settled by a spike (§ 1.7), not a
  mock-up.
- Reflect together on whether new NR test fixtures are needed. If yes, add
  "create NR fixtures" as the first step of § 2.1.
- Steps (§ 2.1) may include intermediate checkpoints where the agent stops
  for user validation or decision.
- Once specs are agreed, update the PR body to reflect the refined requirements
  (may include checklists).
- **Stop 1.** The user approves Mandate and Plan; the agent writes the date
  in `Approved:` and sets the status to `ONGOING`. Nothing runs while
  `Approved:` is pending.

### Phase 4 — Implementation

After stop 1, the agent implements per the steps of § 2.1 and the rules in
"Implementation workflow", accounting for each step in § 3.1.

Before starting each step, the agent:

1. Lists all actions the step will involve (files to create/modify, commands
   to run, permissions needed).
2. Offers the user the choice to let the step run **unattended** (the agent
   proceeds autonomously through the entire step, stopping only if a question
   or unexpected problem arises) or **attended** (the agent stops at each
   sub-action for validation).

This way the user can grant autonomy for straightforward steps and keep
tighter control over sensitive or uncertain ones.

Three more stops follow the execution, each a dated line the agent fills on
the user's go:

- **Stop 2, `Tried:`** after § 4.1 Try it: the user tries the work and may
  mandate a loop (steps added to § 2.1, accounted in § 3.1, § 4.1
  refreshed). Omitted when there is nothing to try.
- **Stop 3, `Shipped:`** once no loop is requested and § 4.2 Test report and
  § 4.3 Verdict are written: the discussion of § 4.4 settles what is
  postponed (a TODO item on the branch) and what is accepted as is. Then
  the PR is marked ready.
- **Stop 4, `Closed:`** after § 5.1 Retrospective, where the user fills
  their column; the status becomes `DONE`.

Claude: if the user starts a task without following this process, briefly
remind them of it.

## devlog/DEVLOG.md general file

- `devlog/DEVLOG.md` is owned by Claude for recording analysis outcomes that are still under discussion, before they become a task tracked by specific `NNN-short-description.md` files.
- Each new entry must begin with a heading consisting of a human-readable timestamp, title text, and a status tag: `[PENDING]`, `[ONGOING]`, `[DONE]`, or `[REJECTED]` (e.g., `## 2026-02-12 15:30 — Topic [PENDING]`).
- Status may be updated in-place on existing headings as work progresses.
- Immediately after the heading, include a one-line **prompt summary** in bold describing what was asked (e.g., `**Prompt:** Analyze the README for first-glance readability and suggest improvements.`).
- New entries are appended; existing entries must not be modified or removed.
- Only append to `CLAUDE.md` itself when explicitly requested by the user.

## devlog/NNN-short-description.md files

- For each task of non-trivial scope, a file in `devlog/` named
  `NNN-short-description.md` is copied from `templates/devlog.md` during the
  task start process (phase 2). **NNN** is the GitHub issue number,
  zero-padded; the slug is the user's short description, else derived from
  the issue title.
- Five chapters: Mandate, Plan, Execution, Delivery, Closure; the task nature
  (`change`, `refactor`, `analysis`) selects the sections, as the template's
  guidance comments say. Sections are cited by number and title; omitted
  sections leave no placeholder.
- Four stops, each a dated line the agent fills on the user's go, never
  before: `Approved:` (after the Plan), `Tried:` (after Try it), `Shipped:`
  (the ship decision), `Closed:` (after the Retrospective). Status:
  `PENDING` until stop 1, `ONGOING` after it, `DONE` at stop 4, `REJECTED`
  when abandoned.
- Budget: Mandate and Plan about 120 lines, the whole file about 250 at
  closure; cite a convention instead of restating its rationale.
- Illustrations go under `devlog/img/`.

## discussions/ files

- Analysis that outgrew a task and belongs to no devlog (a spin-off brief
  for another repository, a design kept for a dedicated task, a recorded
  exchange) goes to `discussions/<topic>.md`, copied from
  `templates/discussion.md`, written on the branch it originated from so
  that history retraces it. It ends with an executive summary and the
  outcomes or measures that follow.

## Writing or modifying tests

Before adding or changing any test, read `tests/README.md`. It defines: how to classify a test (unit / integration / non-regression; nominal / edge / robustness / regression), where to place it, how to run it in isolation, and how it gets picked up by the full suite (`make test`).

## Non-regression tests

- **Fixtures** (test inputs) live in `tests/non-regression/`: `.dfd`, `.part`, `.md` files.
- **Golden files** (expected outputs): `.dot` files. Standalone tests use `NNN-name.dot`; markdown tests use `NNN-name/output.dot` subdirectories.
- **Workflow:** `make nr-review` → inspect SVGs / error output → `make nr-regenerate` → commit fixtures and golden files together.
- `make nr-test` runs as part of `make test`. It compares regenerated output against golden files.
- Test numbering follows `doc/README.md` section order. When adding a new test case, use the next available number (currently 027+).
- **Mutation smoke-test:** After adding or changing NR fixtures, verify they are effective by introducing a tiny, deliberate mutation in the code path under test, running `make nr-test` to confirm the relevant fixtures fail, then reverting the mutation. This guards against golden files that silently pass because they don't actually exercise the intended code.

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
   `doc/RELEASING.md`).

Devlog in the PR, squash merge and the PR title as the single conventional
subject hold each other up: the devlog commits vanish at squash and stay out
of the changelog, so the title is the only place where the PR's type is
decided.

Direct commits to `main` are reserved for housekeeping (TODO status flips,
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
   to release now (`make release`, see `doc/RELEASING.md`).

## Implementation workflow

When implementing an approved plan:

- **One pushed commit per step of § 2.1.** During a step, commit freely:
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
  section of `doc/CONVENTIONS.md`.

## Design philosophy

**YAGNI + open door**: Implement only what current needs require. Do not invent abstractions, base classes, hooks, or infrastructure for hypothetical future needs. However, structure the current solution so that natural future growth (splitting a file, adding a case, extending a module) requires no rework of the existing structure. Complexity must be justified by a present need, not a future one. Starting with a single file that can later be split into modules is a good example of this principle in action.

**Established tool vs bespoke script — measure, don't estimate**: When
a choice is between using an established tool for a fraction of what it
does and writing a small script, settle it with a quick trial rather
than opinions: try the tool in a throwaway clone (under the job scratch
directory, never the real repo) with a draft configuration and fake
inputs; show the configuration and the produced artifact verbatim, and
note what the tool dropped or warned about. Then state the balance in
numbers: lines of configuration against lines of code plus tests,
upgrade churn against ownership. The default leans to the established
tool, but a configuration heading toward ~60 lines reopens the debate.
The balance is questioned every time, not applied by reflex.

## Import compatibility

All internal imports must work in **every** calling context:

- **Local dev wrapper** (`./data-flow-diagram`) — imports `src.data_flow_diagram`
- **pip-installed package** (`data-flow-diagram` console script) — imports `data_flow_diagram`
- **pytest / test scripts** — imports `data_flow_diagram` via `src/` on `sys.path`

Relative imports (`from .. import X`, `from . import Y`) satisfy this
because Python resolves them against the package hierarchy, not the
calling script. When adding sub-packages or moving modules, verify all
three contexts pass (`make test` covers pytest; manual smoke-test covers
the other two).

## Naming and structure conventions

Full rules are in **`doc/CONVENTIONS.md`**. Key points:

- **Functions**: action-first (`verb_object`), e.g. `handle_filters`, `generate_dot`.
- **Classes**: PascalCase nouns, e.g. `Generator`, `FilterNeighbors`.
- **Modules**: lowercase nouns (domain/role), e.g. `scanner`, `filters`.
- **Packages**: generic → specific path order, e.g. `dsl/scanner.py`.
- **Constants**: `UPPER_SNAKE_CASE` in their designated module.
- Use official terminology from `doc/SYNTAX.md` in all identifiers.
- **Type safety**: see the Type safety section of `doc/CONVENTIONS.md`
  — dataclasses for records, enums for tags, no `dict[str, *]` for
  non-string-indexed data, keyword-only from 4 parameters.

## Commenting style

Full rules are in **`doc/COMMENTING.md`**. Key points:

- **Chunk comments** (lowercase verb phrases): state _what_ a block does. Target ~1 per 5–10 lines.
- **Phase headers** (`# phase N:`): mark major sections of long functions.
- **Intent comments** (capitalized sentences): explain _why_, used sparingly.
- Use official terminology from the glossary in `doc/SYNTAX.md`.
- Do not comment well-named functions, debug lines, or obvious code.

## Formatting

- After generating or modifying Python code, run `make format` to apply the project's standard formatting (`ruff format`, configured in `pyproject.toml`).
- After generating or modifying Python code, run `make lint` to catch lint and type errors (`ruff check`, `ruff format --check`, then mypy). Fix all errors before committing.

## Versioning convention

Versions follow `MAJOR.MINOR.PATCH`. The version is never edited by hand:
`make release` derives it from the conventional commits merged since the
last release (`doc/RELEASING.md`), through the bump map of `pyproject.toml`
(`make help-cc` prints it):

- `feat` bumps `MINOR`: a new feature, even a minor one, non-breaking.
- A type with `!`, or a `BREAKING CHANGE:` footer, bumps `MAJOR`.
- `fix`, `perf`, `refactor`, `docs`, `test`, `build` bump `PATCH`: bug
  fixes, refactorings, documentation, tests, build and packaging changes.
- `chore`, `ci`, `style` bump nothing: they change nothing the user
  installs or reads, so they wait for the next release and appear in its
  changelog entry. This holds because the project is a tool installed on
  the user's computer; for a service, CI changes can have real if invisible
  effects that deserve a release.

Unreleased changes on `main` never span two levels: a PR whose type would
raise the pending level is blocked by the merge gate until the pending
changes are released, so every level is closed before the next one opens.

## Markdown formatting

- When writing Markdown, match the output of VSCode's table formatter exactly: **pad every table cell with spaces so all cells in a column are the same width**, and pad the separator row dashes (`---`) to the same width. This prevents meaningless diff noise when the user's editor auto-formats on save. Other Markdown elements (headings, lists, blank lines) follow standard CommonMark conventions.
