# Code structure of the application

Date: 2026-09-27
Status: PENDING
Origin: #143 (devlog `devlog/143-code-structure.md`), branch
`refactor/143-code-structure`.

**Prompt:** TODO 33 asks whether classes carry the concepts of
`dsl/filters.py` better than functions relaying the same parameters,
and how `dsl/parser.py` should tell one statement from several and
name its parsers by scope. The user extended the question to the whole
application code under `src/data_flow_diagram/`, the build, test and
tool scripts being for a later task: a thorough analysis, with the
proposals grouped by families of improvements, before any decision.

## 1. Method

The eighteen modules were read in full (3239 lines). An AST script
measured every function: lines, parameters, keyword-only parameters,
parameters relayed unchanged to a callee, parameters never read; and
every module: `isinstance`, `match`, `id()` and `__dict__` sites. Four
mock-ups were then built in scratch worktrees, one per question that
a listing decides, each run through `ruff format`, `ruff check`, mypy
strict, the unit suite (154 tests) and the NR suite (118 fixtures,
goldens byte-identical); the filters mock-up also had its `--debug`
output diffed against the base on the 107 diagram fixtures under a
fixed hash seed. The worktrees are disposable; the listings that
decide are quoted here.

The constraint that shapes every proposal: no test changes. The calls
the tests make pin a module, a name and a call form for each entry
point (`scanner.scan`, `parser.parse`, `checker.check`,
`filters.handle_filters`, `dependency_checker.check`, `dfd.build`,
`dfd.handle_options`, `dfd.remove_unused_hidables`,
`markdown.extract_snippets`, `rendering.dot.Generator` and
`generate_dot`, `main`, `parse_args`) and the fields of the model
classes the tests construct (`Item`, `Connection`, `Frame`, `Snippet`,
`SourceLine`, `Options`, `GraphOptions`, `GraphDependency`) with
`Keyword` members as item and connection types. A proposal that a
test pins is marked "blocked" and goes to § 5.

## 2. Measurements

| Module                      | Lines | Functions | Classes | 4+ params | Relays (max hops) | Idioms                       |
| --------------------------- | ----- | --------- | ------- | --------- | ----------------- | ---------------------------- |
| `cli.py`                    | 264   | 6         | 0       | 2         | 1                 |                              |
| `dfd.py`                    | 177   | 6         | 0       | 1         | 1                 | `match` 5, `getattr/setattr` |
| `model.py`                  | 421   | 7         | 24      | 1         | 0                 | `isinstance` 1               |
| `exception.py`              | 67    | 6         | 1       | 0         | 1                 |                              |
| `console.py`                | 39    | 4         | 0       | 0         | 0                 | `global`                     |
| `markdown.py`               | 91    | 3         | 1       | 0         | 0                 |                              |
| `config.py`                 | 13    | 0         | 0       |           |                   |                              |
| `dsl/scanner.py`            | 143   | 3         | 0       | 3         | 2                 |                              |
| `dsl/parser.py`             | 610   | 19        | 0       | 2         | 1                 | `isinstance` 1, `__dict__` 3 |
| `dsl/checker.py`            | 134   | 5         | 0       | 0         | 1                 | `match` 4                    |
| `dsl/filters.py`            | 670   | 20        | 1       | 8         | 4                 | `isinstance` 4, `id()` 6     |
| `dsl/dependency_checker.py` | 117   | 3         | 0       | 1         | 1                 |                              |
| `rendering/dot.py`          | 343   | 19        | 1       | 1         | 1                 | `match` 4, `__dict__` 1      |
| `rendering/graphviz.py`     | 33    | 1         | 0       | 1         | 0                 | `sys.exit` 2                 |
| `rendering/templates.py`    | 105   | 0         | 0       |           |                   |                              |

"4+ params" counts functions with four or more parameters (all
keyword-only, per the convention); "relays" is the longest chain of a
parameter passed unchanged from function to function.

The relay chains of `dsl/filters.py`, the TODO's first finding, measured:

| Parameter    | Chain                                                                                                                 | Hops |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | ---- |
| `statements` | `handle_filters` → `_collect_kept_names` → `find_neighbors` → `_expand_neighbors_in_dir` → `_collect_connected_names` | 4    |
| `merged`     | `_collect_kept_names` → `find_neighbors` → `_expand_neighbors_in_dir` → `_collect_connected_names` → `_ends`          | 4    |
| `merged`     | `_collect_kept_names` → `_collect_flow_ids` → `_ends`; `handle_filters` → `_apply_filters` → `_merge_frame_items`     | 2    |
| `debug`      | `handle_filters` → `_collect_kept_names` → `find_neighbors`, where it is never read                                   | 2    |
| `source`     | each case of `_collect_kept_names` → three or four checks                                                             | 1    |

`_collect_kept_names` is 200 lines and carries eight loop variables
(`kept_names`, `only_names`, `replacement`, `unavailable`, `frame_of`,
`inherited_frames`, `skip_frames_for_names`, `vetoed_ids`,
`allowed_ids`), each mutated by one to three of the three statement
cases. Devlog 047 (lesson 5) ruled against a class when the module
was 260 lines and the state "flowed linearly"; the same lesson gives
the criterion for a class, "shared mutable state accumulating across
calls", which is the state of the module today.

Public functions with no caller outside their module: `find_neighbors`
(filters), `parse_drawable_attrs` (parser), `include` (scanner),
`find_item` (dependency checker), `wrap` (dot), `resolve_star_endpoints`,
`get_style_int` and `apply_style` (dfd), `write_output`,
`handle_markdown_source` and `handle_dfd_source` (cli),
`make_snippets_params` and `check_snippets_unicity` (markdown, called
by cli only). Parameters never read: `debug` in `find_neighbors`,
`style` in `Generator.generate_style`.

Strict optional typing (`mypy --strict` without the recipe's
`--no-strict-optional`) raises zero errors on `src/`: the exemption
serves the tests only, a note for the scripts task.

## 3. Families of proposals

Each family states the finding, the options with a mock-up where a
listing decides, and a recommendation. The basis of each
recommendation is a convention (cited) or a measurement; a taste
decision is marked as such for the user.

### 3.1 Family A: the filters' concepts as objects

**Finding.** `dsl/filters.py` mixes five concepts, each spread over
functions that relay the same parameters (§ 2): the merges (a flat
map, the ends of a flow read through it, the frame a replacer
inherits), the neighborhood search over the merged graph, the
selection (the kept set, the "only" anchors, the unavailable names
with their cause, three checks), the flow gate of the strict filters
(vetoed and allowed flow ids), and the frame skips of the `f` flag.
The driver loop mutates all of them.

**Options.**

| Option | What differs                                                                                      | For                                                                                         | Against                                                                                     |
| ------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| A0     | Status quo                                                                                        | Nothing to review                                                                           | The relays and the 200-line loop stay; every new filter rule adds a parameter to the chain  |
| A1     | One class holding the eight variables, every helper a method (the `FilterEngine` of 047)          | The relays vanish                                                                           | A 500-line class of twenty methods; the concepts stay mixed, now behind `self`              |
| A2     | Concept objects (`_Merges`, `_Graph`, `_Selection`, `_FlowGate`) passed to module functions       | Each concept has a home and a docstring                                                     | The three statement cases become functions of four objects: the relay returns, one hop deep |
| A3     | A2 plus a driver class `_Filtering` holding the objects, the three cases as its methods (mock-up) | Concepts have a home, the cases read as `self.selection.remove(...)`, no relay past one hop | Six classes in one module                                                                   |

**Mock-up (A3).** The module as it reads, classes and methods only:

```
_cause(what, source) -> str
_frame_of_items(statements) -> dict[str, Frame]
class _Merges          the substitutions so far, flat; the frame a replacer inherits
    merged_names, resolve(name), ends(conn), touches(conn), register(*, names, replacer),
    check_one_frame(*, names, source) -> Frame | None, inherit(replacer, frame), frame_items(frame)
class _Graph           the connections read through the merges
    neighbors(filter) -> (downs, ups, path_ids), flow_ids(names, *, touching)
    _expand(*, anchors, fn, down), _adjacent(*, names, down, layout)
class _Selection       the kept set and the unavailable names with their cause
    check_known, check_available, check_kept, check_kept_for_merge, remove(names, cause), resolve(merges)
class _FlowGate        vetoed_ids, allowed_ids, hidden_ids
class _FilterDecisions kept_names, only_names, merges, skip_frames_for_names, hidden_ids (frozen)
class _Filtering       phase 1: run() -> _FilterDecisions; _only(f), _merge(m), _without(f), _skip_frames(f, ...)
_mark_non_hidable(statements, only_names)
_apply_filters(statements, decisions) -> (statements, replaced)      phase 2
_deduplicate_connections(statements, replaced)                        phase 3
handle_filters(statements, *, debug=False)                            unchanged
```

Measured against the base: 670 to 591 lines; functions with four or
more parameters 8 to 1 (`_skip_frames`); longest function 200 to 80
lines (`_apply_filters`, unchanged in substance) and 44 (`_only`); no
parameter relayed past one hop; `find_neighbors` private and without
the unread `debug`; the two `_check_filter_names` calls that could
only fail on an unknown name collapsed into `check_known`. All four
checks green, 118 goldens identical, `--debug` output identical on
the 107 diagram fixtures.

**Recommendation.** A3. Basis: devlog 047, lesson 5, applied to
today's measurement (shared mutable state accumulating across the
loop); CONVENTIONS "Classes" (a role name for the driver, data
containers for the rest); YAGNI + open door (each class can move to a
module of its own without rework, which answers the question of a
package split: not now, § 3.2).

### 3.2 Family B: one module or a package for the filters

**Finding.** With A3 the module holds six classes and five functions,
591 lines: the largest module of the package, as it was.

| Option | What differs                                                                      | For                                                  | Against                                                                                                                             |
| ------ | --------------------------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| B0     | One module, a class per concept                                                   | Nothing moves; the tests' import holds               | The largest module stays the largest                                                                                                |
| B1     | `dsl/filters.py` plus `dsl/neighbors.py` (`_Graph`, the search)                   | The search is the one part with no filter rule in it | Two modules for one stage; `neighbors` must know `_Merges`                                                                          |
| B2     | A package `dsl/filters/` with `merges.py`, `graph.py`, `selection.py`, `apply.py` | Every concept a file                                 | `filters.handle_filters` stays importable only through `__init__` re-export; the CONVENTIONS tree changes; 591 lines do not need it |

**Recommendation.** B0, revisited when a concept grows (the open
door). Basis: YAGNI + open door; the test import
`from data_flow_diagram.dsl import filters` holds either way.

### 3.3 Family C: the parser's result type and its names by scope

**Finding.** `parse()` tells one statement from a list by
`isinstance(parsed, list)`; the one parser returning a list is
`_parse_filter`, for the deprecated `~[SPEC] =R ITEMS` that
`_desugar_replacer` turns into a `merge` and a `~` statement (TODO 32
removes it at a major). The module names its whole-line parsers
(`_parse_style`), its term parsers (`_parse_item_name`) and its
post-parse passes (`parse_drawable_attrs`, `_parse_item_external`)
alike, while CONVENTIONS "Parser scopes" gives each rule one scope.
Three constructions of an all-off `FilterNeighbors`, and `model.Filter`
instantiated as a temporary then splatted into `Only` or `Without`.

**Options for the result type.**

| Option | What differs                                                                                          | For                                                                                      | Against                                                                                                                                                                                                     |
| ------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C0     | Status quo                                                                                            |                                                                                          | The `isinstance`                                                                                                                                                                                            |
| C1     | Every parser returns `list[Statement]` (mock-up)                                                      | One type in the table; the loop needs no test; +32 lines with the record and the factory | Eight parsers wrap one statement in a list for the sake of one deprecated form                                                                                                                              |
| C2     | `match parsed: case list(): ...`                                                                      | The smallest edit                                                                        | A dispatch on the container, the same smell in another syntax                                                                                                                                               |
| C3     | A result type, `Parsed` with `.statements`                                                            | Named                                                                                    | A wrapper around a list                                                                                                                                                                                     |
| C6     | The `~=` desugared as text in the sugar stage, every parser returns one statement (mock-up, reverted) | The root cause gone; the lists disappear                                                 | The sugar stage walks the terms with `RX_FILTER_ARG` (a scope violation), the leading-terms loop and one error duplicated (12 lines), one warning reordered before an error, 674 lines against 669: no gain |

**Mock-up.** C1 then the naming, both green on the four checks and
the 118 goldens; C6 built, measured, and restored to the state
before it. The module as it reads (Part 2), by section:

```
parse(source_lines, shared_options=None) -> (Statements, GraphDependencies, Attribs)
# sugar stage: text to canonical text
_desugar_line(src_line) -> str
_desugar_arrow(*, src_line, op, keyword, relaxed_keyword=None) -> str
_format_keyword_line(verb, args) -> str
# term parsers: one term, its own regex
_split_terms(dfd_line, n, *, last_is_optional=False) -> list[str]
_read_item_name(name) -> (str, bool)
_make_no_neighbors() -> FilterNeighbors
_read_neighbor_spec(m, arg) -> (FilterNeighbors, bool, bool)
# line parsers: dispatched by keyword, all -> list[Statement]
_parse_style, _parse_attrib, _parse_merge, _parse_frame, _parse_filter
_make_item_parser(keyword) -> _LineParser          (closure parse_item)
_make_connection_parser(*, keyword, reversed, relaxed, swap) -> _LineParser
class _ParsedFilter(names, neighbors_up, neighbors_down, replacer, spec)   frozen
_desugar_replacer(source, parsed) -> list[Statement]
# post-parse passes: one statement, in place
_extract_drawable_attrs(drawable) -> None
_extract_external_reference(item, dependencies) -> None
_PARSERS: dict[Keyword, _LineParser]
```

Naming scheme applied: a verb per scope (`_parse_` reserved to the
whole line, `_read_` for a term, `_split_` for the cut of the line
into terms, `_extract_` for a pass over a parsed statement,
`_desugar_` for the text stage), which keeps the action-first rule of
CONVENTIONS and the dispatch table reading `Keyword.STYLE:
_parse_style`. The alternative, a scope noun after the verb
(`_parse_line_style`, `_parse_term_neighbor_spec`,
`_finish_item_external`), reads as "parse the line named style" and
is longer at every call site. Two classes of static methods, the
review's other suggestion, would namespace the same functions behind
`_Line.style(...)` and `_Term.item_name(...)`: Python's namespace for
functions is the module, and a class with no state is the case the
YAGNI rule names. The sections carry a two-line banner each stating
the scope's rule. Lines 610 to 669 (+27 of banners, +32 of C1).

**Recommendation.** C1 with the naming by verb, and `_desugar_replacer`
renamed `_build_replacer_statements` since it works on parsed terms;
C6 rejected: the lists vanish for free when TODO 32 removes `~=`.
Basis: CONVENTIONS "Parser scopes" and "Functions and methods"
(rule); the choice of verbs is a taste row for the user.

### 3.4 Family D: typing precision and identity of the model

**Finding.** Four symptoms of one cause, a model typed wider than its
values: `dsl/filters.py` keeps sets of `id(connection)` and
`id(frame)` (six sites) because the statement dataclasses compare by
value and are unhashable; `rendering/dot.py` closes two `match` on
`Keyword` with `case _: raise DfdException("Unsupported ...")` where
CONVENTIONS "Type safety" wants `assert_never`, because `Item.type`
and `Connection.type` are typed `Keyword` (28 members, of which 7 and
6 are valid); the idiom `match statement: case model.Item() as item:
pass; case _: continue` selects a class from the list at ten sites;
and `rendering/dot.py` copies an item by `model.Item(**item.__dict__)`.
`Keyword.STAR` is a kind of item and never a keyword of a line, the
same widening seen from the enum.

**Mock-up.** Four parts, each green on the four checks and the
118 goldens; the worktree holds them all (7 files, +197/−174).

| Part | Change                                                                                                                                                                                                                            | Result                                                                                                                                                                                                                                                                         |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| D1   | `@dataclass(eq=False)` on `Base`, `Statement` and its ten subclasses: identity semantics, hashable; `Snippet`, `SourceLine`, `Options`, `GraphDependency` keep value equality (the tests compare `Snippet` with `==`)             | The six `id()` sites become sets of `Connection` and a `dict[str, Frame]`; `_check_one_frame` four lines shorter. Nothing in `src` or `tests` compares statements with `==`. Each subclass must repeat `eq=False`, since `@dataclass` regenerates `__eq__`: a review-time rule |
| D2   | `ItemType = Literal[Keyword.PROCESS, ..., Keyword.STAR]`, `ConnectionType = Literal[Keyword.FLOW, ..., Keyword.CONSTRAINT]`; `Item.type: ItemType`, `Connection.type: ConnectionType`; both `case _: raise` become `assert_never` | Load-bearing: removing the `UFLOW` case is a mypy error. Two annotations in `parser.py` follow (`_make_item_parser(keyword: ItemType)`, the connection factory). The tests' `model.Keyword.PROCESS` type-checks                                                                |
| D3   | `model.items_of`, `connections_of`, `frames_of`: one-line typed generators                                                                                                                                                        | Ten sites rewritten (checker three, dfd, dependency checker, filters five), net 22 lines fewer; the eight dispatch loops stay                                                                                                                                                  |
| D4   | `dataclasses.replace(item)` for the copy; `getattr`/`setattr` in `resolve_star_endpoints` replaced by two explicit branches and a `_declare_star` helper                                                                          | `dfd.py` 25 lines longer for the stars: explicit, typed                                                                                                                                                                                                                        |

**The blocked design.** Split enums `ItemKind` and `ConnectionKind`
run (a `StrEnum` member compares by value) but the tests construct
`model.Item(type=model.Keyword.PROCESS, ...)` and mypy runs over
`tests/`: `tests/unit/test_pipeline.py` lines 222, 230, 247, 255,
279, 301, 326, 334, 365 (`Item`), 263, 342 (`Connection`) and 373
(`Frame`). Listed in § 5.

**Options for D2.**

| Option | What differs                                     | For                                                              | Against                                                                                                                                                                                                    |
| ------ | ------------------------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D2a    | Status quo: `case _: raise`                      | No convention question                                           | The convention's rule unmet; a new kind fails at run time on the first diagram using it                                                                                                                    |
| D2b    | `Literal[...]` subsets of the one enum (mock-up) | Exhaustiveness proven by mypy; the tests untouched; twelve lines | CONVENTIONS "`Literal[...]` is for strings owned by an external API": here the members are enum members, the `Literal` is a type-level subset, which the rule did not foresee; the rule needs one sentence |
| D2c    | Split enums                                      | The cleanest model                                               | Blocked by the tests (§ 5)                                                                                                                                                                                 |

**Recommendation.** D1, D3, D4 as they are; D2b now with the
convention amended ("a `Literal` of enum members names a subset of an
enum; it is not a string tag"), D2c filed for the task that may touch
the tests. Basis: CONVENTIONS "Type safety" (rule, `assert_never`);
the `Literal` row is a taste decision for the user, since it amends
the convention.

### 3.5 Family E: the home of each stage

**Finding.** CONVENTIONS "Target package structure" names `dfd.py`
the orchestrator, `model.py` the data types, `dsl/` the stages from
text to filtered statements. Today `dfd.py` (177 lines) holds four
stages beside `build`: the stars, the hidables, the style options
and their conversion; `model.py` holds 150 lines of style-registry
machinery (`StyleKind`, `StyleSpec`, `_build_style_specs`,
`STYLE_SPECS`) next to the statements; and the star stage reads its
name format from `rendering/templates`, the one place where `dfd`
reaches into the rendering package for a parse-time value.

**Mock-up.** Two moves, both green on the four checks, the 118
goldens and the dev wrapper; `dfd.py` 177 to 100 lines.

| Part | Change                                                                                                                                                                                                                                                                                                                        | Result                                                                                                                                                                                                        |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1   | `styles.py` (top level): `StyleKind`, `StyleSpec`, `_build_style_specs`, `STYLE_SPECS`, `get_style_int`, `apply_style`. `GraphOptions` and its field declarations stay in `model` (they are the dataclass's own metadata; moving them makes a cycle). `dfd.handle_options` stays (test-pinned) and calls `styles.apply_style` | No re-export; `styles` imports `model` and `exception`. One reader retargeted, `tools/doc-print-style-table.py`, a one-line consequence in the scripts (the doc-sync test runs it as a subprocess and passes) |
| E2   | `dsl/stars.py`: `resolve_star_endpoints`, unchanged signature; `templates.STAR_ITEM_FMT` becomes `config.ITEM_STAR_NAME_FMT` next to `ITEM_STAR_ATTRS`                                                                                                                                                                        | `dfd.py` imports neither `config` nor `templates`; the resolve stage of `build`'s docstring has its module                                                                                                    |
| E3   | `remove_unused_hidables` to `dsl/filters.py` (the `?` is an implicit filter run after the explicit ones)                                                                                                                                                                                                                      | Blocked: `tests/unit/test_pipeline.py` lines 237, 270, 286 call `dfd.remove_unused_hidables`. A wrapper kept for the tests would be a re-export in disguise: not done, § 5                                    |

The orchestrator after E1 and E2, as the body of `build` reads:

```
lines = scanner.scan(...)
statements, dependencies, attribs = parser.parse(lines)
dependency_checker.check(...)
items_by_name = checker.check(statements)
statements = stars.resolve_star_endpoints(statements, items_by_name)
statements = filters.handle_filters(statements)
checker.check_frames(statements, items_by_name)
statements = remove_unused_hidables(statements)
statements, graph_options = handle_options(statements)
... title, background, Generator, generate_dot
```

**Options.**

| Option  | What differs                     | For                                                                      | Against                                                        |
| ------- | -------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------- |
| E0      | Status quo                       | Nothing moves                                                            | The orchestrator keeps four stages; the model keeps a registry |
| E1+E2   | The mock-up                      | `dfd.py` reads as the pipeline; each module answers "what is this about" | Two new modules in the CONVENTIONS tree; one tool line         |
| E1 only | The registry out, the stars stay | The smaller change                                                       | `dfd` still reads `rendering/templates` for a parse-time name  |

**Recommendation.** E1 and E2; E3 filed. Basis: CONVENTIONS
"Modules" and "Target package structure" (rule); the star constant
follows CONVENTIONS "Constants" (parse-time values in `config.py`).

### 3.6 Family F: the process boundaries

**Finding.** Three mechanisms live below the CLI that belong to it.
`rendering/graphviz.py` exits the process (`sys.exit(2)` when
Graphviz is missing, `sys.exit(1)` when it rejects the DOT) and prints
the numbered DOT listing to stderr, while `cli.main` is the module
that owns exits and the `ERROR:` prefix. The debug flag exists twice:
a global set by `cli` and read by `dprint`, and a `debug` parameter or
an `Options` object threaded through `scanner.scan`, `parser.parse`,
`filters.handle_filters`, `find_neighbors` (unread there) and
`dependency_checker.check`, guarding only the cost of building the
dump arguments. `DfdException.__bool__` makes `if errors: raise
errors` read as "if there is an exception".

**Mock-up.** Green on the four checks and the 118 goldens.

| Part | Change                                                                                                                                                                                                                                                                                                                                                                                       | Result                                                                                                                                                                                     |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| F1   | `DfdException.exit_code = 1`; `GraphvizException(DfdException)` with `exit_code` and an optional `dot_text`; `generate_image` raises, `cli.main` prints the listing when present, then `ERROR: ...`, then exits with the code                                                                                                                                                                | Stderr byte-identical and the same exit codes on both paths, provoked (a missing engine binary, restored after; a DOT Graphviz rejects); `graphviz.py` imports neither `sys` nor `console` |
| F2   | The global is the one mechanism: the guards read `console.debug`; `scan`, `parse`, `handle_filters`, `find_neighbors` lose their `debug` or `options` parameter (no test passes them); `dependency_checker.check` keeps `options` (six tests pass it) and takes over the `no_check_dependencies` gate from `build`; `Options.debug` stays (constructed by the tests), written and never read | 42 lines over five files; `--debug` output identical on fixtures 016 and 110 (2314 lines, fixed hash seed)                                                                                 |

**Options for F2.**

| Option | What differs                                                                     | For                                                          | Against                                                                                                           |
| ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| F2a    | The global alone (mock-up)                                                       | One mechanism; five signatures shorter; the unread flag gone | A module global, set once by `cli`; `Options.debug` becomes write-only                                            |
| F2b    | The parameter alone: `dprint` takes no global, every dump site receives the flag | No global state                                              | The relay the TODO complains of, extended to every stage; the tests' calls without `debug=` need a default anyway |

**Recommendation.** F1; F2a; the `__bool__` of the exception
replaced by a named query in the same step (family H, 14). Basis:
CLAUDE.md's layout (`cli.py` is the I/O module); F2 is a taste
decision, a global being the thing the type-safety preference
tolerates least, so the row is open for the user.

### 3.7 Family G: names against the conventions

**Finding.** A sweep of every identifier against CONVENTIONS
"Functions and methods", "Classes" and the glossary. Mechanical, one
table; the tests pin the public ones marked so.

| Where                     | Today                                                               | Issue                                                                   | Proposal                                                                         |
| ------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `filters.py`              | `_collect_kept_names` returns `_FilterDecisions`                    | The name says names, the function returns decisions                     | Gone with A3 (`_Filtering.run`)                                                  |
| `filters.py`, `dfd.py`    | `handle_filters`, `handle_options`                                  | "handle" says nothing of the effect                                     | Pinned by the tests: kept; a docstring says "apply"                              |
| `filters.py`              | `find_neighbors`, public                                            | No caller outside                                                       | Private, a method of `_Graph` (A3)                                               |
| `parser.py`               | `parse_drawable_attrs`, public                                      | No caller outside; a post-parse pass named like a parser                | Family C                                                                         |
| `scanner.py`              | `include`, public; `scan` without docstring; `l` as a loop variable | No caller outside; an ambiguous single letter                           | `_include`, a docstring, `line`                                                  |
| `dependency_checker.py`   | `find_item`, public                                                 | No caller outside                                                       | `_find_item`                                                                     |
| `dot.py`                  | `wrap`, public; `_get_item` a one-line indirection                  | No caller outside; a wrapper that adds nothing                          | `_wrap`; inline the lookup                                                       |
| `dot.py`                  | `Generator.append(line, statement)`                                 | "append" hides the echo comment it emits                                | `emit`                                                                           |
| `markdown.py`             | `make_snippets_params` returns `SnippetContexts`                    | The name and the type disagree                                          | `make_snippet_contexts`                                                          |
| `exception.py`            | `_mk_prefix`                                                        | Abbreviation ("avoid abbreviations")                                    | `_make_prefix`                                                                   |
| `console.py`              | `dprint`, `set_debug`, module global `debug`                        | "prefer `debug_print` in new code" (CONVENTIONS); a global read by name | Family F decides the mechanism; the name follows it                              |
| `model.py`                | `repr(o)` shadows the builtin; `Base.__repr__` duplicates it        | Two spellings of one dump                                               | One: `Base.__repr__`, and `dprint(statement)` at the two call sites              |
| `model.py`                | `Options` (CLI) next to `GraphOptions` (style)                      | The unqualified name is the less central one                            | `CliOptions`; pinned by the tests as `model.Options`: kept, documented           |
| `model.py`                | `Keyword.STAR`                                                      | A kind of item, never a keyword of a line                               | Family D                                                                         |
| `rendering/dot.py`        | `import templates as TMPL`                                          | A module aliased in upper case                                          | `from . import templates`, or `tmpl`                                             |
| `filters.py`, `parser.py` | `f`, `fn`, `m`, `conn`                                              | One-letter names for the objects of the loop                            | `filter_`? No: `f` for a `Filter` reads fine in a 40-line method; kept, judgment |

**Recommendation.** Apply the table's proposals in one mechanical
step, except the pinned names and the rows that another family
absorbs. Basis: CONVENTIONS "Functions and methods" (rule).

### 3.8 Family H: small smells, one line each

Found by the sweep, none worth a family; each is a few lines, applied
in the step of the family whose file it touches.

| #   | Where                        | Smell                                                                                                                           | Fix                                                                                                                                                                                                                                        |
| --- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `filters.py`                 | `debug` relayed to `find_neighbors` and never read                                                                              | Gone with A3                                                                                                                                                                                                                               |
| 2   | `filters.py`                 | `_check_filter_names` called twice with `in_names=all_names`: only its "unknown" branch can fire                                | Gone with A3 (`check_known`)                                                                                                                                                                                                               |
| 3   | `filters.py`                 | `_resolve_distance`, a five-line function for one conditional                                                                   | Gone with A3 (inlined with a comment)                                                                                                                                                                                                      |
| 4   | `parser.py`                  | `FilterNeighbors(distance=0, suppress_anchors=False, ...)` written three times                                                  | A default factory (family C mock-up)                                                                                                                                                                                                       |
| 5   | `parser.py`                  | `model.Only(**f.__dict__, ...)`, `model.Without(**f.__dict__)`: `Filter` instantiated as a temporary, then splatted             | A parsed-spec record, the subclass built from it (family C)                                                                                                                                                                                |
| 6   | `parser.py`                  | `_apply_syntactic_sugars`: nine `if re.fullmatch(...)` branches, one per arrow, each calling `_resolve_sugar` with two keywords | A table `(pattern, keyword, relaxed_keyword)` and one loop; the arrows become data next to `Keyword`                                                                                                                                       |
| 7   | `parser.py`                  | `if new_line: return new_line else: return src_line`                                                                            | `return new_line or src_line`                                                                                                                                                                                                              |
| 8   | `parser.py`                  | `Keyword(word)` in a `try` catching `ValueError` and `KeyError` to say "unrecognized keyword"                                   | `_PARSERS.get(...)`: a `StrEnum` lookup by value is the `try`; kept, or a `Keyword.of(word)` helper                                                                                                                                        |
| 9   | `dot.py`                     | `generate_style` and `case model.Style()` in `generate_dot`: dead, `handle_options` removes every `Style` before rendering      | Delete both                                                                                                                                                                                                                                |
| 10  | `dot.py`                     | `copy = model.Item(**item.__dict__)`                                                                                            | `dataclasses.replace(item)` (family D mock-up)                                                                                                                                                                                             |
| 11  | `dot.py`                     | `RX_NUMBERED_NAME` a class attribute of `Generator`, the other regex a module constant                                          | A module constant                                                                                                                                                                                                                          |
| 12  | `dfd.py`                     | `getattr(conn, attr)` / `setattr(conn, attr, ...)` over `("src", "dst")`                                                        | Explicit code (family D mock-up)                                                                                                                                                                                                           |
| 13  | `dfd.py`                     | `apply_style` ends in `setattr(options, spec.field, value)`                                                                     | The registry boundary; kept with the comment naming it (CONVENTIONS "Any at boundaries")                                                                                                                                                   |
| 14  | `exception.py`               | `DfdException.__bool__` true once `add()` was called: `if errors: raise errors` reads as "if there is an exception"             | `has_errors()` or a separate accumulator (family F)                                                                                                                                                                                        |
| 15  | `exception.py`               | `if src.line_nr is None` on an `int` field: dead under strict optional                                                          | Delete the branch                                                                                                                                                                                                                          |
| 16  | `markdown.py`                | `input_fp.name = snippet.output` on a `StringIO`; a `FIXME` about streaming that no task carries                                | The name goes in `SnippetContext` only; the FIXME becomes a TODO item or is dropped                                                                                                                                                        |
| 17  | `cli.py`                     | `handle_markdown_source(options, provenance, input_fp)` positional, `handle_dfd_source(*, ...)` keyword-only                    | Both keyword-only (three parameters of two types: judgment row of the convention)                                                                                                                                                          |
| 18  | `cli.py`                     | `write_output` decides three times on `fmt == "dot"` and `output_path == "-"`                                                   | Kept; a table of four cases would not read better                                                                                                                                                                                          |
| 19  | `config.py` / `templates.py` | `ITEM_EXTERNAL_ATTRS`, `ITEM_STAR_ATTRS`, `FRAME_DEFAULT_ATTRS` are Graphviz attribute strings under `config`                   | CONVENTIONS "Constants" puts Graphviz-specific values in `templates.py`, parse-time values in `config.py`: these are both; kept in `config` (the parser reads them, `dsl/` must not import `rendering/`), the rule amended with the reason |
| 20  | `model.py`                   | `Connection.signature()` dumps the dataclass to JSON to compare flows after a rewrite                                           | A tuple of the compared fields; or identity plus `(type, src, dst, text, attrs, reversed, relaxed)`                                                                                                                                        |
| 21  | `dsl/scanner.py`             | `scan(...)` builds a default provenance `SourceLine` that `cli.handle_dfd_source` and `markdown` also build                     | One factory `SourceLine.root(raw_text)` in `model`                                                                                                                                                                                         |

## 4. Dependencies between the families, and an order

The families share files, so the order follows what each builds on,
then the files they touch (the rule of the chained batches):

1. **D1, D3, D4** first: identity of the statements, the typed
   generators and the explicit copies are foundations the filters and
   the checker then use (`model.py`, `checker.py`,
   `dependency_checker.py`, `dfd.py`, `dot.py`, `filters.py`).
2. **A** on those foundations: the filters rewritten with sets of
   connections instead of ids and `connections_of` in `_Graph`
   (`filters.py` only).
3. **C** with **D2**: the parser's result type, record, factory and
   names; the two `ItemType`/`ConnectionType` annotations of the
   factories and the `assert_never` in `dot.py` (`parser.py`,
   `model.py`, `dot.py`).
4. **E, F**: the stage homes and the process boundaries (`dfd.py`,
   new `styles.py` and `dsl/stars.py`, `config.py`, `templates.py`,
   `graphviz.py`, `exception.py`, `cli.py`, `scanner.py`, and the
   signatures of `parse` and `handle_filters`; one line of
   `tools/doc-print-style-table.py`).
5. **G, H** last: the naming sweep and the small smells, mechanical,
   once the files have settled.

Five steps, one pushed commit each, `refactor:` for the PR. Every
step ends with the four checks and the `--debug` diff of step A's
method. The mock-ups are the drafts of steps 1 to 4, to be redone on
the branch in this order rather than merged from the worktrees, since
each was built on the base and they overlap in `filters.py`,
`model.py` and `dfd.py`.

## 5. What the tests pin

Proposals a test line blocks, for a task allowed to edit the tests:

| Proposal                                                                 | Pinned by                                                                                                              |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| D2c: `ItemKind` and `ConnectionKind` enums in place of `Keyword` subsets | `tests/unit/test_pipeline.py` 222, 230, 247, 255, 263, 279, 301, 326, 334, 342, 365, 373 (`model.Keyword.X` as a type) |
| E3: `remove_unused_hidables` to `dsl/filters.py`                         | `tests/unit/test_pipeline.py` 237, 270, 286                                                                            |
| G: `handle_filters` and `handle_options` renamed for their effect        | `tests/unit/test_dfd.py`, `test_pipeline.py` (fifteen calls)                                                           |
| G: `model.Options` renamed `CliOptions`                                  | `tests/unit/test_pipeline.py` 51, 54                                                                                   |
| F2: `dependency_checker.check` without `options`                         | `tests/unit/test_pipeline.py` 439, 458, 477, 496, 514, 533                                                             |

A wrapper or a re-export kept for the tests' sake would hide the
pin; none is proposed.

## Executive summary

The TODO's two findings hold and generalize: the filters relay four
parameters through four hops and mutate eight loop variables, the
parser's list result exists for one deprecated form, and the same
widening shows in the model (`id()` sets, `case _: raise`, ten
class-selection loops), the orchestrator (four stages in `dfd.py`)
and the boundaries (exits in `rendering`). Eight families, four
mock-ups, all green on 154 unit tests and 118 goldens: the filters as
six concept classes (670 to 591 lines, four-parameter functions 8 to
1), uniform parser results with names by scope, identity semantics
and typed selection in the model, `styles.py` and `dsl/stars.py`
extracted, Graphviz's exits moved to the CLI, one debug mechanism.
Rejected with numbers: the text-level desugaring of `~=` (a scope
violation for no size gain) and a filters package. Three structural
proposals are pinned by fifteen test lines and wait for a task that
may edit the tests.

## Outcomes and measures

- The Plan of `devlog/143-code-structure.md`: five steps in the
  order of § 4, decided at stop 1 with the taste rows (D2b's `Literal`
  subset, F2's global, the parser verbs).
- `engineering/CONVENTIONS.md`, in the step that ships each: the
  package tree gains `styles.py` and `dsl/stars.py`; "Type safety"
  gains the sentence on a `Literal` of enum members; "Constants" says
  why Graphviz attribute strings read at parse time stay in
  `config.py`; "Parser scopes" names the verbs per scope.
- A TODO item for § 5, the test-pinned structure.
- For the scripts task: `--no-strict-optional` is unneeded on `src/`;
  `tools/doc-print-style-table.py` reads the registry from `styles`.
