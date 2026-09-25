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
resolve_star_endpoints(statements)

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
- Enums use singular nouns: `Keyword`.
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

- **Installed package** (`make install`, `make publish-to-pypi`): the
  console script entry point `data_flow_diagram:main` must resolve.
  After moving `main()` to `cli.py`, re-export it from `__init__.py`.
- **Local development** (`./data-flow-diagram`): the wrapper script
  imports `src.data_flow_diagram` and calls `main()`. Same re-export
  ensures this works.
- Package discovery is configured in `pyproject.toml`
  (`[tool.setuptools.packages.find]`, `where = ["src"]`), which
  auto-discovers sub-packages with `__init__.py` files. The version
  is a static `project.version`, bumped by `make release`; `make install` stamps a copy of the tree (`0+<branch>.git<hash>[.dirty]`, `tools/print-dev-version.py`: no base claimed, the hash names it), the checkout keeps the bare version.

## Constants

- **Configuration values** (defaults, thresholds): define in
  `config.py` with `UPPER_SNAKE_CASE` names.
- **Graphviz-specific constants** (templates, font specs, colours):
  define in `rendering/templates.py`.
- **DSL syntax literals** (sentinel values, directive keywords):
  define in `model.py` alongside the data types that use them.

## Type safety

Python is treated as a fully type-safe language. The overhead of precise
types (dataclasses, enums, keyword-only signatures, possibly inheritance)
is accepted for the comprehensiveness and quality that lint-time checking
brings.

| Data shape                                  | Use                                      | Never                                 |
| ------------------------------------------- | ---------------------------------------- | ------------------------------------- |
| Record with a fixed set of fields           | `@dataclass` (frozen when immutable)     | `dict[str, Any]`, positional `tuple`  |
| Closed set of tags or kinds                 | `Enum` / `StrEnum` members               | string literals, `Literal[...]`       |
| Data keyed by names from the input          | `dict[K, V]` with precise `K` and `V`    | `dict[str, Any]`, `dict[str, object]` |
| Dispatch on kind or class                   | `match` ending with `assert_never`       | `if kind == "...":` chains            |
| Values crossing an I/O boundary (JSON, CLI) | `Any` converted to typed objects at once | `Any` flowing into the pipeline       |

Rules:

- `dict[str, *]` is reserved for string-indexed data: item names, DSL
  keywords, file names. A dict whose keys are known identifiers is a
  record and must be a dataclass.
- A `tuple` is a record only when it is unpacked once at its single
  consumer; if read positionally in more than one place, make it a
  dataclass.
- `Any` is allowed only at boundaries and carries an inline comment
  naming the boundary.
- `Literal[...]` is for strings owned by an external API, not for
  internal tags.

Parameters:

- One to three parameters: positional, no rule.
- Four or more parameters: keyword-only, enforced with `*` in the
  signature.
- Booleans are always passed by keyword, whatever the parameter count.
- Three parameters with adjacent parameters of the same type: pass by
  keyword at the call site (judgment, not enforced).
- Dataclasses with four or more fields use `kw_only=True`.

Tooling: mypy runs in strict mode. Ruff rules ANN401, FBT and PLR0917
(`max-positional-args = 3`) enforce the `Any` and parameter rules.
PLR0917 counts positional parameters only, so keyword-only signatures
of any length pass.

## Tooling scripts

Scripts in `recipes/`, `tools/` and `tests/` are written in Python or
bash. Choose
by what the script mostly does:

- **Python** when there is string manipulation, non-trivial argument or
  option handling, or data encoding/decoding (YAML, JSON, TOML,
  Markdown sections). Use `argparse` and a real parser (e.g. pyyaml,
  from the `dev` dependency group), never regexes over structured
  formats. Type it as application code.
- **bash** when there is none of the above (or a few trivial regexes),
  and the script is about filesystem manipulation, process pipelines,
  or sequencing commands (`make`, `uv`, `gh`, `diff`).

This is more an art than a science: a script that starts as a command
sequence and grows string handling should be rewritten in Python rather
than accumulating `sed`/`awk`. When the choice is not obvious, or when
a script is about to switch language, the agent raises it and the
language is decided in discussion with the maintainer before writing
the script. A consistency check takes its expected values as arguments
(e.g. from the Makefile) rather than re-parsing their source, and fails
on a discrepancy without resolving it.

**Script levels.** Git's porcelain and plumbing is the model, with the
Makefile as the porcelain. Makefile targets are the entry points, and a
prerequisite list is how a sequence of targets is written. Recipes
(`recipes/<target>.sh`) are the bodies of targets that outgrew a few
one-line commands: one file per target, named after it, called by make
only, no arguments; a recipe sequences commands, with guards and loops
applying one command per file, and no computation. Tools (`tools/`) do
one concern with explicit arguments, so that every call site is
self-explanatory; they are called from recipes, workflows and tests.
The prelude (`tools/init-tracing.sh`) holds sourced mechanics only.
Recipes source it, and they are bash: tracing is the orchestrator's
view. A tool never traces; it prints its title as `--- title ---` and
its phases as `-- phase`, lighter than the recipes' banners, so that
the level of a line is readable in the output.
Calls go down only, Makefile to recipes to tools: a recipe never calls
make nor another recipe, and a target whose body calls make
(`test-matrix`) stays in the Makefile. Logic that appears in a recipe
moves down into a tool. Every recipe starts with a comment stating its
purpose. `engineering/RELEASING.md` is the prose of `make release`.

**Naming.** A single action is verb-first, read as a command
(`tools/print-release-plan.py`, `tools/test-installation.sh from-wheel`,
`make smoke-test-wheel`). A family of two or more is topic-first, so
that listings and completion group it (`nr-test`, `require-system`,
`tools/doc-update-sections.py`). A Python family sharing its data is
one program, a noun with verb-first subcommands (`changelog.py
print-notes`, `conventional-commits.py gate-pr-against-main`).
Object-first with no family behind it is the case to avoid.

**Calling directory.** Every script is called from the project's home,
the repository root: paths inside scripts are relative to it, the
prelude is sourced as `. ./tools/init-tracing.sh`, and the Makefile is
the normal caller. A script never `cd`s to find itself.

## Terminology

All identifiers, comments, and documentation must use the official
terminology defined in the glossary section of `doc/SYNTAX.md`. When
an identifier must differ from the glossary term (e.g. to avoid a
Python keyword clash), add a comment at the definition site explaining
the deviation.

## Language

All identifiers, comments, documentation, and commit messages use
**American English** (e.g. "neighbor", not "neighbour"; "color", not
"colour").

## Design philosophy

**YAGNI + open door**: Implement only what current needs require. Do not invent abstractions, base classes, hooks, or infrastructure for hypothetical future needs. However, structure the current solution so that natural future growth (splitting a file, adding a case, extending a module) requires no rework of the existing structure. Complexity must be justified by a present need, not a future one. Starting with a single file that can later be split into modules is a good example of this principle in action.

**Parser scopes** (decided at #123): the DSL parser has three scopes,
and each rule lives in exactly one. The line: the first word, the
keyword, decides how the rest is split; a filter splits its rest on
whitespace into terms, an item takes a name and leaves the rest as the
label, whitespace included, no quotes needed. The term: each term is
dissected by its own regex (`RX_FILTER_ARG` for a filter argument),
which knows nothing of its siblings. The sequence: how many terms of a
kind, in which order, before which names, belongs to the loop of the
statement parser, as the facts that span statements belong to the
checker. No scope reaches into another; a term regex that looked at a
sibling, or a line regex that knew term syntax, would leave rules with
no home. The scopes are fundamental: the DSL is extended so that they stay respected, never the other way round.

## Markdown formatting

- Match VSCode's table formatter exactly: pad every table cell so all
  cells in a column are the same width, and the separator dashes to the
  same width, so that the user's format-on-save produces no diff. Other
  elements follow CommonMark.

## Instruction files

The root `CLAUDE.md` is the project's instance: what the project is,
and a map "When / Read first" naming the document to read before
acting. It imports (`@`) `engineering/RULES.md`, the rules that apply
to every edit; everything else loads on demand, when the agent follows
a map row. A folder whose work has rules of its own holds them in
`<folder>/RULES.md`, named for what it holds so that humans read it
too, and the root's map names it; no folder `CLAUDE.md`, since the
harness's lazy load fires on its Read tool only, never on shell
commands, and the map row is the one mechanism that works in every
session mode. A new rule is a map row or a paragraph in the document
the map names, never a line in the root.

## Related documents

- **Commenting style**: `engineering/COMMENTING.md`
- **DSL syntax and glossary**: `doc/SYNTAX.md`
- **User documentation**: `doc/README.md`
