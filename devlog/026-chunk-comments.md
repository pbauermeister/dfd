# 026 — Add more chunk and intent comments

**Date:** 2026-02-18

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/26

## Requirement

Add chunk and intent comments across the project to make the codebase
ready for a future large-scale refactoring. Comments must be accurate,
helpful, and at a density of roughly one chunk comment per 5–10 lines
of code (as specified in CLAUDE.md).

This density is a guideline, not a hard rule. It may be tuned during
this task, and it may vary across code sections — denser for intricate
algorithms, sparser for straightforward or self-evident code.

## Plan

### Phase 1 — Model function: `dfd.py:handle_filters`

Improve chunk comments in `handle_filters` (lines 492–687, 147 LOC,
currently 20 chunk comments) to represent the ideal commenting level.

- Analyze the code and assess whether existing chunk comments are both
  correct and helpful; fix any that are misleading or redundant.
- Add new chunk comments where the purpose of a code block is not
  obvious from names alone.
- Treat inner function definitions and their names as semantic
  signposts (like chunk comments), so avoid duplicating what a
  well-named inner function already communicates.
- User reviews the result.

### Phase 2 — Codify the commenting style

From the model function, extract a concise text characterizing the
style and usage of comments. This becomes the reference for all
subsequent commenting work. The rules must serve the goal of making
future refactoring safe and fast.

### Phase 3 — Apply to the whole project

Using the codified rules, add chunk and intent comments to every
source file in `src/data_flow_diagram/`.

## Analysis: `handle_filters` current state

The function has three phases, already marked by phase-header comments:

1. **Collect filtered names** (lines 515–598): iterates all
   statements, processing `Only` and `Without` filters to build the
   set of names to keep (`kept_names`).
2. **Apply filters** (lines 613–672): iterates statements again,
   skipping/adjusting items, connections, and frames based on
   `kept_names` and `replacement`.
3. **Remove duplicate connections** (lines 674–685): deduplicates
   connections that were created by replacement.

### Existing chunk comments (20)

| Line | Comment                                              | Verdict                        |
| ---- | ---------------------------------------------------- | ------------------------------ |
| 515  | `# collect filtered names`                           | Good — phase header            |
| 543  | `# all Only names must be valid`                     | Good                           |
| 547  | `# add names from this Only statement`               | Good                           |
| 556  | `# add neighbors`                                    | Good                           |
| 570  | `# all Without names must be valid`                  | Good                           |
| 579  | `# remove names from this Without statement`         | Good                           |
| 587  | `# remove neighbors`                                 | Good                           |
| 600  | `# A node in the only_names set may lose…` (2 lines) | Good — intent comment          |
| 613  | `# apply filters`                                    | Good — phase header            |
| 620  | `# skip nodes that are not in the only list`         | Good                           |
| 628  | `# …skip connections if both ends are replaced`      | Inline, not chunk — acceptable |
| 629  | `# replace any end`                                  | Good                           |
| 636  | `# skip connections if either src or dst…`           | Good                           |
| 644  | `# apply replacements`                               | Good                           |
| 650  | `# skip frames if none of the items…`                | Good                           |
| 656  | `# adjust frame items by removing…`                  | Good                           |
| 663  | `# skip frames if they contain items…`               | Good                           |
| 670  | `# keep statement`                                   | Good                           |
| 674  | `# remove duplicate connections due to replacements` | Good — phase header            |

### Gaps identified

- **Lines 495–509** — initialization of `all_names`, `kept_names`,
  `only_names`, and the `_check_names` inner function: no comments.
- **Lines 510–513** — `replacement` dict and `skip_frames_for_names`
  set: no comments.
- **Lines 523–536** — `_collect_frame_skips` inner function defined
  mid-loop: no chunk comment introducing it.
- **Line 609** — `kept_names` fallback to `all_names`: important
  default, no comment.

## Phase 2: Commenting style rules

Extracted from the model function (`dfd.py:handle_filters`) and
discussions during Phase 1. The full rules are published in
**`doc/COMMENTING.md`**; CLAUDE.md references that file.

## Phase 3: Apply to the whole project

Applied chunk comments, docstrings, and terminology alignment to all
10 source files in `src/data_flow_diagram/`:

| File                   | Changes                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `__init__.py`          | Sharpened chunk comments in `run()`, fixed typo in docstring      |
| `console.py`           | Fixed "debuhg" typo in docstring                                  |
| `dependency_checker.py`| Condensed docstring, improved chunk comments, removed TODO        |
| `dfd.py`               | Added docstrings + chunk comments to `build`, Generator methods, `remove_unused_hidables`, `handle_options`, `find_neighbors`; removed TODO lines |
| `dfd_dot_templates.py` | Added section comment for font constants                          |
| `dot.py`               | Added chunk comments, removed dead commented-out line             |
| `markdown.py`          | Added docstring to `extract_snippets`                             |
| `model.py`             | Fixed typo, aligned FilterNeighbors + constants to glossary terms |
| `parser.py`            | Added docstrings to 4 functions, chunk comments throughout `_parse_filter` and `_apply_syntactic_sugars` |
| `scanner.py`           | Improved chunk comments, added docstring to `_scan`               |
