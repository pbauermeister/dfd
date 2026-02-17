# Project Instructions

## DEVLOG.md

- `DEVLOG.md` is owned by Claude for recording analysis outcomes.
- Each new entry must begin with a heading consisting of a human-readable timestamp, title text, and a status tag: `[PENDING]`, `[ONGOING]`, `[DONE]`, or `[REJECTED]` (e.g., `## 2026-02-12 15:30 — Topic [PENDING]`).
- Status may be updated in-place on existing headings as work progresses.
- Immediately after the heading, include a one-line **prompt summary** in bold describing what was asked (e.g., `**Prompt:** Analyze the README for first-glance readability and suggest improvements.`).
- New entries are appended; existing entries must not be modified or removed.
- Only append to `CLAUDE.md` itself when explicitly requested by the user.

## Devlog

- For each feature or bug fix of non-trivial scope, create a file in `devlog/` named `NNN-short-description.md`.
- **NNN** is the GitHub issue number. The user must provide it. If the user also provides a short description, use it directly; otherwise, fetch the issue title from GitHub (`gh issue view NNN`) and derive a slug from it.
- The file must start with a title (`# NNN — Short Description`), a date, and a status (`PENDING`, `ONGOING`, `DONE`, or `REJECTED`).
- Include a **Requirement** section describing what was asked for, and a **Design** section describing the agreed-upon approach, before implementation begins.
- Update the status in-place as work progresses.

## Non-regression tests

- **Fixtures** (test inputs) live in `tests/non-regression/`: `.dfd`, `.part`, `.md` files.
- **Golden files** (expected outputs): `.dot` files. Standalone tests use `NNN-name.dot`; markdown tests use `NNN-name/output.dot` subdirectories.
- **Workflow:** `make nr-preview` → inspect SVGs → `make nr-approve` → commit fixtures and golden files together.
- `make nr-test` runs as part of `make test`. It compares regenerated DOT against golden `.dot` files.
- Test numbering follows `doc/README.md` section order. When adding a new test case, use the next available number (currently 027+).

## Formatting

- After generating or modifying Python code, run `make black` to apply the project's standard formatting (Black with `--skip-string-normalization --line-length 80`).
