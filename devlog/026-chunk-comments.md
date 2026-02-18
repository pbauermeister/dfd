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
discussions during Phase 1. These rules replace the "Commenting style"
section of `CLAUDE.md`.

### Purpose

Comments represent the one-step-higher semantic level that makes code
understandable to humans and AIs alike. They are a prerequisite for
safe refactoring: a future developer (or agent) must be able to scan
the comment skeleton of a function and understand its structure without
reading every line of code. Stale or wrong comments are worse than
none.

### Comment types

Three kinds of comments are used, at different granularities:

1. **Chunk comments** (primary) — a short `#` line placed before a
   logical group of lines inside a function body, stating *what* that
   group accomplishes. They partition the function into scannable
   blocks.

2. **Phase headers** — a chunk comment that marks a major section of a
   long function (>~30 LOC). Prefixed with `# phase N:` to make them
   visually distinct when scanning.

3. **Intent comments** — one or more `#` lines (or a docstring
   sentence) explaining *why* a design decision was made. Use only
   when the reasoning would not be recoverable from the code or the
   surrounding chunk comments.

### Casing convention

- **Chunk comments and phase headers**: lowercase verb phrases.
  Example: `# validate filter names`
- **Intent comments**: capitalized full sentences.
  Example: `# An item in the only_names set may lose its connections…`

This visual distinction lets the eye tell *what* from *why* at a
glance.

### Density

Target roughly one chunk comment per 5–10 lines of code. This is a
guideline, not a rigid rule:

- **Denser** (~1 per 5 lines) for intricate logic, multi-step
  algorithms, or code that manipulates several variables in concert.
- **Sparser** (~1 per 10+ lines) for straightforward code where names
  and structure already communicate intent (dataclass definitions,
  simple dispatch, boilerplate).
- **Phase headers** for any function with ≥2 distinct stages.

### What to comment

- The *purpose* of a code block — not a restatement of the code.
- Initialization sections that set up state for later use.
- Non-obvious defaults or fallbacks.
- DSL flag references (`"x"`, `"f"`) rather than re-explaining the
  full semantics (those live in `doc/SYNTAX.md`).

### What NOT to comment

- **Well-named functions and methods** already serve as signposts.
  A chunk comment above `_collect_frame_skips(f, names, downs, ups)`
  would duplicate the function name. Omit it.
- **Debug/logging lines** (`dprint(...)`) — they are infrastructure,
  not logic. Do not comment them.
- **Single obvious lines** — e.g. `return result` at the end of a
  function.
- **Inline comments restating the code** — e.g. `x = x + 1  # increment x`.

### Terminology

Use official terms from the glossary in `doc/SYNTAX.md`. When a
comment's terminology differs from the identifier it annotates, prefer
the official term in the comment; the identifier will be fixed in a
future refactoring. Example: use "item" (not "node"), "anchor" (not
"listed item"), "kept set" (not "kept names list").

### Reference example

`dfd.py:handle_filters` (lines 492–691) demonstrates the full range:

- Phase headers: `# phase 1: collect filtered names`
- Chunk comments: `# add anchor names (suppressed by "x" flag: …)`
- Intent comment: `# An item in the only_names set may lose its
  connections and, if it is hidable, vanish…`
- Omitted comment: no chunk comment above `_collect_frame_skips` call
  (function name is self-documenting).
