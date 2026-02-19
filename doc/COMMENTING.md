# Commenting Style Guide

This document defines the commenting conventions for the DFD codebase.
It is intended for developers and AI agents working on the code.

## Purpose

Comments represent the one-step-higher semantic level that makes code
understandable to humans and AIs alike. They are a prerequisite for safe
refactoring: a future developer (or agent) must be able to scan the comment
skeleton of a function and understand its structure without reading every line
of code. Stale or wrong comments are worse than none.

## Comment types

Three kinds of comments are used, at different granularities:

### 1. Chunk comments (primary)

A short `#` line placed before a logical group of lines inside a function
body, stating *what* that group accomplishes — not *how*. They partition the
function into scannable blocks.

```python
# validate filter names
names = set(f.names)
_check_names(names, all_names, prefix)

# add anchor names (suppressed by "x" flag: neighbors only)
if (
    not f.neighbors_up.suppress_anchors
    and not f.neighbors_down.suppress_anchors
):
    kept_names.update(f.names)
```

### 2. Phase headers

A chunk comment that marks a major section of a long function (>~30 LOC).
Prefixed with `# phase N:` to stand out when scanning. Use whenever a
function has two or more distinct stages.

```python
# phase 1: collect filtered names
for statement in statements:
    ...

# phase 2: apply filters to statements
new_statements: list[model.Statement] = []
...

# phase 3: deduplicate connections created by replacements
kept_new_statements = []
...
```

### 3. Intent comments (occasional)

One or more `#` lines — or a docstring sentence — explaining *why* a design
decision was made. Use sparingly, only when the reasoning would not be
recoverable from the code or the surrounding chunk comments.

```python
# An item in the only_names set may lose its connections and, if it is
# hidable, vanish (or, if in a frame, reappear as a basic item).
# To keep it, we make it non-hidable.
for statement in statements:
    ...
```

## Casing convention

- **Chunk comments and phase headers**: lowercase verb phrases.
  `# validate filter names`
- **Intent comments**: capitalized full sentences.
  `# An item in the only_names set may lose its connections…`

This visual distinction lets the eye tell *what* from *why* at a glance.

## Density

Target roughly one chunk comment per 5–10 lines of code. This is a
guideline, not a rigid rule:

- **Denser** (~1 per 5 lines) for intricate logic, multi-step algorithms,
  or code that manipulates several variables in concert.
- **Sparser** (~1 per 10+ lines) for straightforward code where names and
  structure already communicate intent (dataclass definitions, simple
  dispatch, boilerplate).
- **Phase headers** for any function with two or more distinct stages.

## What to comment

- The *purpose* of a code block — not a restatement of the code.
- Initialization sections that set up state for later use.
- Non-obvious defaults or fallbacks.
- DSL flag references (`"x"`, `"f"`) rather than re-explaining the full
  semantics (those live in `doc/SYNTAX.md`).

## What NOT to comment

- **Well-named functions and methods** already serve as signposts. A chunk
  comment above `_collect_frame_skips(f, names, downs, ups)` would duplicate
  the function name. Omit it.
- **Debug/logging lines** (`dprint(…)`) — they are infrastructure, not logic.
- **Single obvious lines** — e.g. `return result` at the end of a function.
- **Inline restatements of the code** — e.g. `x = x + 1  # increment x`.

## Terminology

Use official terms from the glossary in `doc/SYNTAX.md`. When a comment's
terminology differs from the identifier it annotates, prefer the official
term in the comment and fix the identifier.

Examples: use "item" (not "node"), "anchor" (not "listed item"), "kept set"
(not "kept names list").

## Reference example

`dsl/filters.py:_collect_kept_names` demonstrates the full range:

- Phase headers: `# phase 1: collect filtered names`
- Chunk comments: `# add anchor names (suppressed by "x" flag: …)`
- Intent comment: `# An item in the only_names set may lose its connections
  and, if it is hidable, vanish…`
- Omitted comment: no chunk comment above `_collect_frame_skips` call
  (function name is self-documenting).
