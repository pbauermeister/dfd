# 052 — Align identifiers to glossary

**Date:** 2026-02-19

**Status:** DONE

**Issue:** https://github.com/pbauermeister/dfd/issues/52

## Requirement

Systematic audit and rename of identifiers (classes, methods, variables,
constants) to match the official terminology in `doc/SYNTAX.md`, making code
and documentation speak the same language.

This is the final task in the refactoring strategy (#34, section J).

### Scope

- Audit all identifiers against the glossary in `doc/SYNTAX.md`.
- Rename local variables where they use informal terms.
- Evaluate identifiers that clash with Python builtins/keywords (`filter`,
  `type`, `input`) and rename where appropriate.
- Update comments and docstrings to match any renamed identifiers.
- Every module will be touched — this is mechanical but pervasive.

### Acceptance criteria

- All identifiers use glossary terms from `doc/SYNTAX.md`.
- `make black && make lint && make test` passes.
- No functional changes — purely renaming.

### Decisions

- **Spelling:** Standardize on American English (`neighbor`, not `neighbour`)
  everywhere — code identifiers, comments, documentation, test fixtures.
- **`filter` parameter:** Keep as-is — it directly matches the domain concept
  and the `model.Filter` class.
- **Rename unclear locals:** `nreverse` → `use_layout_direction`,
  `find_down` → `search_downstream`.
- **NR fixtures:** No new fixtures needed. Two existing `.stderr` golden files
  must be updated (error message wording changes). NR `.dfd` fixture comments
  will be updated for spelling but produce identical `.dot` output.

## Design

### Complete rename inventory

**Constants (model.py, templates.py):**

| Current             | New                  | Rationale                               |
| ------------------- | -------------------- | --------------------------------------- |
| `NODE_STAR`         | `ENDPOINT_STAR`      | Glossary: "endpoint", not "node"        |
| `STAR_NODE_FMT`     | `STAR_ITEM_FMT`      | Glossary: "item", not "node"            |

**Dataclass fields (model.py → FilterNeighbors):**

| Current       | New                  | Rationale                              |
| ------------- | -------------------- | -------------------------------------- |
| `no_anchors`  | `suppress_anchors`   | Glossary: "suppress anchors"           |
| `no_frames`   | `suppress_frames`    | Glossary: "suppress frames"            |
| `layout_dir`  | `layout_direction`   | Glossary: "direction"                  |

**Local variables:**

| Current      | New                      | File(s)                              |
| ------------ | ------------------------ | ------------------------------------ |
| `point`      | `endpoint`               | `checker.py`, `dfd.py`              |
| `nreverse`   | `use_layout_direction`   | `filters.py`                        |
| `find_down`  | `search_downstream`      | `filters.py`                        |

**Python builtin shadowing:**

| Current   | New            | File                   |
| --------- | -------------- | ---------------------- |
| `input`   | `source_text`  | `scanner.py`           |
| `format`  | `fmt`          | `graphviz.py`          |

**Comments/debug output:**

| Current text                             | New text                                     | File                   |
| ---------------------------------------- | -------------------------------------------- | ---------------------- |
| `"ONLY: adding nodes:"`                  | `"ONLY: adding items:"`                      | `filters.py:166`       |
| `"WITHOUT: removing nodes:"`             | `"WITHOUT: removing items:"`                 | `filters.py:203`       |
| "DOT node declaration"                   | "DOT declaration"                            | `rendering/dot.py:67`  |
| "star nodes"                             | "star items"                                 | `rendering/dot.py:226` |

**Error messages (checker.py):**

| Current                                  | New                                                     |
| ---------------------------------------- | ------------------------------------------------------- |
| `'links to "{point}"'`                   | `'connects to "{endpoint}"'`                            |
| `'may not link to two stars'`            | `'may not connect two anonymous endpoints'`             |

**Spelling standardization (British → American):**

All occurrences of "neighbour(s)" → "neighbor(s)" in:
- Source code comments and docstrings
- `doc/SYNTAX.md`, `doc/README.md`, `doc/CONVENTIONS.md`, `doc/COMMENTING.md`
- NR fixture `.dfd` comments
- Unit test comments

**NR golden files to update:**
- `tests/non-regression/050-err-missing-ref.stderr` (error message wording)
- `tests/non-regression/051-err-double-star.stderr` (error message wording)

### Implementation steps

1. **Rename model constants and dataclass fields + propagate to all source
   modules.** All Python source changes in one pass: field renames, constant
   renames, local variable renames, comment fixes, debug output fixes, error
   message fixes.

2. **Update documentation.** All `.md` files: spelling standardization
   (neighbour → neighbor), update code examples referencing renamed fields.

3. **Update test files.** NR fixture comments (`.dfd`), NR golden `.stderr`
   files, unit test comments. Run `make nr-regenerate` to confirm `.dot`
   outputs are unchanged.

4. **Verify.** `make black && make lint && make test`. Mutation smoke-test on
   the two `.stderr` golden files (inject old error message, confirm NR
   fails, revert).
