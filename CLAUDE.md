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
3. Create `devlog/NNN-short-description.md` with the **Requirement** section
   populated from the issue description.
4. Commit the devlog file on the branch.
5. Open a **draft** PR against `main` (`gh pr create --draft`) with a minimal
   body (link to the devlog file).

### Phase 3 — Specification refinement

Agent and user discuss until the specs are clear:

- All decisions are recorded in the devlog's **Requirement** section.
- Reflect together on whether new NR test fixtures are needed. If yes, add
  "create NR fixtures" as the first implementation step.
- Agree on ordered implementation steps; record them in the devlog's **Design**
  section. Steps may include intermediate checkpoints where the agent stops
  for user validation or decision.
- Once specs are agreed, update the PR body to reflect the refined requirements
  (may include checklists).

### Phase 4 — Implementation

On explicit user confirmation, the agent updates the devlog status from
`PENDING` to `ONGOING`, commits, and begins implementing per the agreed steps
and the rules in "Implementation workflow".

Before starting each step, the agent:

1. Lists all actions the step will involve (files to create/modify, commands
   to run, permissions needed).
2. Offers the user the choice to let the step run **unattended** (the agent
   proceeds autonomously through the entire step, stopping only if a question
   or unexpected problem arises) or **attended** (the agent stops at each
   sub-action for validation).

This way the user can grant autonomy for straightforward steps and keep
tighter control over sensitive or uncertain ones.

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

- For each feature or bug fix of non-trivial scope, a file in `devlog/` named
  `NNN-short-description.md` is created during the task start process (phase 2).
- **NNN** is the GitHub issue number. If the user provides a short description,
  use it directly; otherwise, derive a slug from the issue title.
- The file must start with a title (`# NNN — Short Description`), a date, and
  a status (`PENDING`, `ONGOING`, `DONE`, or `REJECTED`).
- Include a **Requirement** section describing what was asked for, and a
  **Design** section describing the agreed-upon approach (including ordered
  implementation steps), before implementation begins.
- Update the status in-place as work progresses.

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
5. Merge (or ask the user to merge) only after the PR is approved and CI passes.

Direct commits to `main` are reserved for trivial changes (`.postN`-level) that
do not warrant a PR.

## Task closing

After the PR is merged:

1. Switch to `main` and pull.
2. Close the GitHub issue (`gh issue close NNN`).
3. Update `MEMORY.md` with anything noteworthy from the task: completed
   milestones, architectural decisions, new conventions, or design
   preferences that emerged from discussion.

## Implementation workflow

When implementing an approved plan:

- Complete work in **logical units** and commit each one separately, so changes are traceable at medium granularity (not one giant commit, not one commit per file).
- **Stop and ask** before continuing when: (a) the next step depends on validating the current result, (b) a decision is needed that was not resolved in the plan, or (c) something unexpected is discovered.
- Otherwise, proceed autonomously through the remaining steps and commit as you go.
- **Before each step** (as described in Phase 4), list all actions the step
  will involve — files to create/modify, commands to run, and any dangerous or
  irreversible actions — so the user can make an informed unattended/attended
  choice.

## Design philosophy

**YAGNI + open door**: Implement only what current needs require. Do not invent abstractions, base classes, hooks, or infrastructure for hypothetical future needs. However, structure the current solution so that natural future growth (splitting a file, adding a case, extending a module) requires no rework of the existing structure. Complexity must be justified by a present need, not a future one. Starting with a single file that can later be split into modules is a good example of this principle in action.

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

## Commenting style

Full rules are in **`doc/COMMENTING.md`**. Key points:

- **Chunk comments** (lowercase verb phrases): state *what* a block does. Target ~1 per 5–10 lines.
- **Phase headers** (`# phase N:`): mark major sections of long functions.
- **Intent comments** (capitalized sentences): explain *why*, used sparingly.
- Use official terminology from the glossary in `doc/SYNTAX.md`.
- Do not comment well-named functions, debug lines, or obvious code.

## Formatting

- After generating or modifying Python code, run `make black` to apply the project's standard formatting (Black with `--skip-string-normalization --line-length 80`).
- After generating or modifying Python code, run `make lint` to catch type errors. Fix all mypy errors before committing.

## Versioning convention

Versions follow `MAJOR.MINOR.PATCH` with an optional `.postN` suffix:

- Bump `PATCH` for user-facing changes: bug fixes, new features, doc additions.
- Use `.postN` only for publishing/packaging fixes and trivial wording corrections
  (e.g. fixing a typo in `README.md`, a broken PyPI upload, a CI script tweak)
  that do not affect the tool's behaviour or documentation content.

## Markdown formatting

- When writing Markdown, match the output of VSCode's table formatter exactly: **pad every table cell with spaces so all cells in a column are the same width**, and pad the separator row dashes (`---`) to the same width. This prevents meaningless diff noise when the user's editor auto-formats on save. Other Markdown elements (headings, lists, blank lines) follow standard CommonMark conventions.
