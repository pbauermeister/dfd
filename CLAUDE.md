# Project Instructions

## Task kickoff checklist

When starting a non-trivial task, provide as many of these as applicable:

1. **GitHub issue number** — needed for the devlog file name (`devlog/NNN-*.md`).
2. **Scope boundary** — which doc sections, files, or features are in scope. Explicit lists prevent missed items (e.g. "all examples in doc/README.md sections E and F").
3. **Developer workflow** — how you intend to use the result (preview, approve, commit, clean). Helps Claude design scripts that fit your actual workflow, not an assumed one.
4. **Naming/ordering conventions** — if output must follow a specific order or naming scheme, state it upfront (e.g. "number test cases to match doc section order").
5. **Terminology** — if the domain has specific terms (fixtures, golden files, etc.), mention them early so documentation stays consistent.

Claude: if the user starts a task without covering these points, briefly remind them of this checklist.

## devlog/DEVLOG.md general file

- `devlog/DEVLOG.md` is owned by Claude for recording analysis outcomes that are still under discussion, before they become a task tracked by specific `NNN-short-description.md` files.
- Each new entry must begin with a heading consisting of a human-readable timestamp, title text, and a status tag: `[PENDING]`, `[ONGOING]`, `[DONE]`, or `[REJECTED]` (e.g., `## 2026-02-12 15:30 — Topic [PENDING]`).
- Status may be updated in-place on existing headings as work progresses.
- Immediately after the heading, include a one-line **prompt summary** in bold describing what was asked (e.g., `**Prompt:** Analyze the README for first-glance readability and suggest improvements.`).
- New entries are appended; existing entries must not be modified or removed.
- Only append to `CLAUDE.md` itself when explicitly requested by the user.

## devlog/NNN-short-description.md files

- For each feature or bug fix of non-trivial scope, create a file in `devlog/` named `NNN-short-description.md`.
- **NNN** is the GitHub issue number. The user must provide it. If the user also provides a short description, use it directly; otherwise, fetch the issue title from GitHub (`gh issue view NNN`) and derive a slug from it.
- The file must start with a title (`# NNN — Short Description`), a date, and a status (`PENDING`, `ONGOING`, `DONE`, or `REJECTED`).
- Include a **Requirement** section describing what was asked for, and a **Design** section describing the agreed-upon approach, before implementation begins.
- Update the status in-place as work progresses.

## Writing or modifying tests

Before adding or changing any test, read `tests/README.md`. It defines: how to classify a test (unit / integration / non-regression; nominal / edge / robustness / regression), where to place it, how to run it in isolation, and how it gets picked up by the full suite (`make test`).

## Non-regression tests

- **Fixtures** (test inputs) live in `tests/non-regression/`: `.dfd`, `.part`, `.md` files.
- **Golden files** (expected outputs): `.dot` files. Standalone tests use `NNN-name.dot`; markdown tests use `NNN-name/output.dot` subdirectories.
- **Workflow:** `make nr-preview` → inspect SVGs → `make nr-approve` → commit fixtures and golden files together.
- `make nr-test` runs as part of `make test`. It compares regenerated DOT against golden `.dot` files.
- Test numbering follows `doc/README.md` section order. When adding a new test case, use the next available number (currently 027+).

## Branching and PR workflow

For every non-trivial fix or feature (i.e. anything with a `devlog/NNN-*.md`
file), work on a dedicated branch and open a pull request:

1. Create a branch named `<prefix>/NNN-short-description` before writing any code,
   where `<prefix>` reflects the kind of work: `fix`, `feature`, `refactor`,
   `doc`, or `test`.
2. Commit all implementation work — including the `devlog/NNN-*.md` file — on
   that branch.
3. Open a PR against `main` when the work is ready for review.
4. Merge (or ask the user to merge) only after the PR is approved and CI passes.

Direct commits to `main` are reserved for trivial changes (`.postN`-level) that
do not warrant a PR.

## Implementation workflow

When implementing an approved plan:

- Complete work in **logical units** and commit each one separately, so changes are traceable at medium granularity (not one giant commit, not one commit per file).
- **Stop and ask** before continuing when: (a) the next step depends on validating the current result, (b) a decision is needed that was not resolved in the plan, or (c) something unexpected is discovered.
- Otherwise, proceed autonomously through the remaining steps and commit as you go.
- **At plan-approval time**, declare every permission category the implementation will need using `allowedPrompts` in `ExitPlanMode`, so the user can grant all permissions upfront and implementation can run unattended. Each entry should name the affected files or targets where known (e.g. `"delete tests/unit_tests.py, tests/inputs.py (irreversible)"`), and explicitly flag dangerous or irreversible actions.

## Design philosophy

**YAGNI + open door**: Implement only what current needs require. Do not invent abstractions, base classes, hooks, or infrastructure for hypothetical future needs. However, structure the current solution so that natural future growth (splitting a file, adding a case, extending a module) requires no rework of the existing structure. Complexity must be justified by a present need, not a future one. Starting with a single file that can later be split into modules is a good example of this principle in action.

## Naming and structure conventions

Full rules are in **`doc/CONVENTIONS.md`**. Key points:

- **Functions**: action-first (`verb_object`), e.g. `handle_filters`, `generate_dot`.
- **Classes**: PascalCase nouns, e.g. `Generator`, `FilterNeighbors`.
- **Modules**: lowercase nouns (domain/role), e.g. `scanner`, `filters`.
- **Packages**: generic → specific path order, e.g. `pipeline/scanner.py`.
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
