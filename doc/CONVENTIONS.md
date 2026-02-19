# Naming and Structure Conventions

This document defines the authoritative naming and structural
conventions for the `data_flow_diagram` package. It applies to all
new code and to code touched during refactoring.

## Functions and methods

**Action-first** (verb or verb\_object):

```python
# Good — action-first
handle_filters(statements)
generate_dot(gen, title, bg_color, statements)
extract_snippets(text)
find_neighbors(filter, statements, max_neighbors)
check_installed()

# Avoid — topic-first
filters_handle(statements)
dot_generate(gen, title, bg_color, statements)
snippets_extract(text)
```

Rules:

- Start with a verb: `parse`, `check`, `build`, `generate`, `find`,
  `handle`, `extract`, `remove`, `make`, `apply`, `collect`, `wrap`.
- Follow with the object when the verb alone is ambiguous:
  `generate_item`, not just `generate`.
- Private helpers use a leading underscore: `_parse_filter`,
  `_split_args`.
- Factory functions use `make_` or `_make_`: `_make_item_parser`.
- Avoid abbreviations except well-established ones (`repr`, `attrs`).
  Prefer `debug_print` over `dprint` in new code.

## Classes

**PascalCase, noun-based**, describing the data structure or role:

```python
Generator          # worker/role
FilterNeighbors    # data container
SourceLine         # data container
DfdException       # exception (noun + type suffix)
```

Rules:

- Abstract bases use semantic role names: `Statement`, `Drawable`.
- Concrete types use domain nouns: `Item`, `Connection`, `Frame`.
- Enums use singular nouns: `Keyword`, `StyleOption`.
- Type aliases use descriptive plurals: `Statements`, `SourceLines`.

## Modules (files)

**Lowercase, noun-based**, naming the domain or responsibility:

```python
scanner.py          # what it is, not what it does
parser.py
filters.py
rendering.py
templates.py
```

Rules:

- A module name answers "what is this about?", not "what does this
  do?". Use `filters`, not `handle_filters` or `filtering`.
- Prefer short, single-word names where possible.
- Use underscores only when a single word is ambiguous:
  `dependency_checker`.

## Packages (directories)

**Lowercase, noun-based**, grouping modules by domain. Path components
are ordered **generic to specific** (left to right):

```
data_flow_diagram/dsl/scanner.py
         ^            ^        ^
     package      domain    role
```

### Target package structure

```
src/data_flow_diagram/
    __init__.py             # package interface, re-exports main()
    cli.py                  # CLI: argument parsing, I/O dispatch
    config.py               # shared constants and defaults
    console.py              # debug/error output utilities
    exception.py            # DfdException class
    model.py                # data types, enums
    markdown.py             # markdown snippet extraction
    dfd.py                  # pipeline orchestrator (build)
    dsl/
        __init__.py
        scanner.py          # preprocessing: includes, line continuations
        parser.py           # DSL parsing: keyword dispatch, syntactic sugar
        checker.py          # statement validation: items, connections, frames
        filters.py          # filter engine: only/without, neighbors
        dependency_checker.py  # cross-document dependency validation
    rendering/
        __init__.py
        dot.py              # DOT code generation (Generator class)
        templates.py        # DOT template strings and font constants
        graphviz.py         # Graphviz binary invocation
```

Rationale:

- **`dsl/`** groups the DSL processing stages that transform
  source text into validated, filtered statements.
- **`rendering/`** groups everything related to producing DOT output
  and invoking Graphviz.
- Top-level modules (`cli`, `config`, `console`, `model`, `markdown`,
  `dfd`) are either infrastructure shared across packages or entry
  points that don't belong to a single stage.

### Constraints

The package structure must work in all installation modes:

- **pip install** (`make install`, `make publish-to-pypi`): the
  console script entry point `data_flow_diagram:main` must resolve.
  After moving `main()` to `cli.py`, re-export it from `__init__.py`.
- **Local development** (`./data-flow-diagram`): the wrapper script
  imports `src.data_flow_diagram` and calls `main()`. Same re-export
  ensures this works.
- `setup.py` uses `find_packages(where="src")`, which auto-discovers
  sub-packages with `__init__.py` files.

## Constants

- **Configuration values** (defaults, thresholds): define in
  `config.py` with `UPPER_SNAKE_CASE` names.
- **Graphviz-specific constants** (templates, font specs, colours):
  define in `rendering/templates.py`.
- **DSL syntax literals** (sentinel values, directive keywords):
  define in `model.py` alongside the data types that use them.

## Terminology

All identifiers, comments, and documentation must use the official
terminology defined in the glossary section of `doc/SYNTAX.md`. When
an identifier must differ from the glossary term (e.g. to avoid a
Python keyword clash), add a comment at the definition site explaining
the deviation.

## Related documents

- **Commenting style**: `doc/COMMENTING.md`
- **DSL syntax and glossary**: `doc/SYNTAX.md`
- **User documentation**: `doc/README.md`
