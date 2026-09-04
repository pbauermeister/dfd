# 073 — Type-Safety Conventions

Date: 2026-09-04

Status: ONGOING

## Requirement

From GitHub issue #73, which came out of the #71 review discussion (PR #72).

Pascal treats Python as a fully type-safe language and accepts the overhead
(possibly complex types, inheritance, keyword-only signatures) for the
comprehensiveness and quality that lint-time checking brings. In particular:
never `dict[str, *]` for anything that is not string-indexed data. This is
tacit today; the task codifies it and aligns the code.

Decisions taken in discussion (all confirmed by the user):

- **Rule text lives in `doc/CONVENTIONS.md`**, new section "Type safety"
  placed between "Constants" and "Terminology". Full draft in Design below.
- **`CLAUDE.md` gets two small edits** (explicitly authorized): a pointer
  under "Naming and structure conventions", and a review-checklist line
  under "Implementation workflow" (self-review the diff against the Type
  safety section before marking a PR ready).
- **Parameter rules** (refined after the user questioned verbosity for 2–3
  mandatory parameters). Audit of `src/` at decision time: 91 functions,
  68 with 0–2 params, 5 with 3, 12 with 4, 6 with 5; only 3 use
  keyword-only params; ~60 call sites pass 3+ positional args, worst are
  `model.Connection(...)` with 8 and `model.Item(...)` with 6, where
  adjacent same-typed `str` params make a swap invisible to mypy.
  1. 1–3 parameters: positional, no rule.
  2. 4+ parameters: keyword-only, enforced with `*` in the signature.
  3. Booleans: always keyword at the call site, whatever the count.
  4. 3 parameters with adjacent same-typed params: keyword at call site,
     by judgment, not enforced.
  5. Dataclasses with 4+ fields: `kw_only=True` on the decorator (also
     lifts the "defaults last" constraint shaping the `Drawable`
     hierarchy).
- **Tooling**: mypy strict already enforces most of it. Ruff rules to
  adopt when TODO.md item 1 (ruff adoption) is done: ANN401 (no `Any` in
  annotations), PLR0913 (max positional args), FBT (boolean traps). Add
  this note to TODO.md item 1 in this task; do not adopt ruff here. No
  custom AST checker (dict-as-record is a judgment call, heuristics would
  be noisy).
- **Behavior byte-identical**: all 81 NR goldens must pass unchanged; no
  new NR fixtures. Unit tests that build model objects positionally (16
  call sites in `tests/unit/*.py` and `tests/conftest.py`) are updated
  to keywords.
- Refactor: PATCH bump to 1.17.2.
- Out of scope, still pending the user's go as a separate issue: derive
  CLI flags (`--background-color`, `--no-graph-title`) from the style
  registry (draft presented on 2026-09-04, not yet created).

## Design

### CONVENTIONS.md "Type safety" section (draft to insert)

```markdown
## Type safety

Python is treated as a fully type-safe language. The overhead of precise
types (dataclasses, enums, keyword-only signatures, possibly inheritance)
is accepted for the comprehensiveness and quality that lint-time checking
brings.

| Data shape                                  | Use                                     | Never                                 |
| ------------------------------------------- | --------------------------------------- | ------------------------------------- |
| Record with a fixed set of fields           | `@dataclass` (frozen when immutable)    | `dict[str, Any]`, positional `tuple`  |
| Closed set of tags or kinds                 | `Enum` / `StrEnum` members              | string literals, `Literal[...]`       |
| Data keyed by names from the input          | `dict[K, V]` with precise `K` and `V`   | `dict[str, Any]`, `dict[str, object]` |
| Dispatch on kind or class                   | `match` ending with `assert_never`      | `if kind == "...":` chains            |
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

Tooling: mypy runs in strict mode. Ruff rules ANN401, PLR0913 and FBT
enforce the `Any` and parameter rules once ruff is adopted (TODO.md).
```

(Table cells must be padded VSCode/prettier style; the draft above is
approximate, re-pad on insertion. Both doc files are prettier-clean;
`make readme` runs prettier on `doc/README.md`, `doc/SYNTAX.md` and
`README.md` only, so run `.venv/node_modules/.bin/prettier --check
doc/CONVENTIONS.md` by hand.)

### CLAUDE.md edits

- Under "Naming and structure conventions", add a key point:
  "**Type safety**: see the Type safety section of `doc/CONVENTIONS.md`
  — dataclasses for records, enums for tags, no `dict[str, *]` for
  non-string-indexed data, keyword-only from 4 parameters."
- Under "Implementation workflow", add a bullet: "Before marking a PR
  ready, self-review the diff against the Type safety section of
  `doc/CONVENTIONS.md`."

### TODO.md

Extend item 1 (ruff): "Enable ANN401 (no `Any` in annotations), PLR0913
(max positional arguments, threshold 3) and the FBT boolean-trap rules to
enforce the Type safety conventions (#73)."

### Code alignment (found by audit on 2026-09-04)

- `rendering/dot.py` `_item_to_html_dict` (line ~149) returns
  `dict[str, Any]`, consumed by `_attrib_to_dict` (line ~138): make it a
  small dataclass or precise types; check how the template formatting
  consumes it before choosing.
- `dsl/filters.py` `_collect_kept_names` (line ~133) returns
  `tuple[set[str] | None, set[str], dict[str, str], set[str]]`: replace by
  a frozen dataclass.
- `model.py`: `StyleFlags = dict[str, tuple[bool, str]]` → values become
  `StyleFlag(value: bool, doc: str)` dataclass (keys stay: DSL keywords
  are data); `StyleSpec.value: Any` → `bool | int | str | None`;
  `repr(o: Any)` keeps `Any` with a boundary comment.
- `dsl/parser.py` `_PARSERS: dict[str, Callable[...]]` → keyed by
  `model.Keyword`.
- Keyword-only (`*`) on the 18 functions with 4+ params: `cli.py`
  `write_output`, `handle_dfd_source`; `dfd.py` `build`;
  `dsl/dependency_checker.py` `check`; `dsl/filters.py`
  `_collect_connected_names`, `_expand_neighbors_in_dir`,
  `find_neighbors`, `_check_filter_names`, `_collect_frame_skips`,
  `_apply_filters`; `dsl/parser.py` `_make_connection_parser`,
  `_resolve_sugar`; `dsl/scanner.py` `scan`, `_scan`, `include`;
  `rendering/dot.py` `generate_dot`; `rendering/graphviz.py`
  `generate_image`. Update their call sites (~60, listed by an AST scan;
  re-run one when implementing).
- Booleans by keyword at remaining call sites (e.g. `options.debug`
  passed to `scanner.scan`).
- `kw_only=True` on dataclasses with 4+ fields: `model.SourceLine`,
  `Snippet`, `Item`, `Connection`, `Frame`, `FilterNeighbors`,
  `GraphDependency`, `StyleSpec`, `Options`; `markdown.SnippetContext`.
  Update constructor call sites in `src/` and the 16 in tests.

### Implementation steps

1. **Docs**: CONVENTIONS.md section, CLAUDE.md edits, TODO.md note.
   Check prettier on CONVENTIONS.md. Commit.
2. **Model dataclasses**: `kw_only=True` + call sites in src and tests;
   `StyleFlag`, `StyleSpec.value` union, `_PARSERS` keyed by `Keyword`.
   `make black`, `make lint`, `make test`. Commit.
3. **Records**: `_collect_kept_names` dataclass, `_item_to_html_dict`.
   Checks. Commit.
4. **Signatures**: keyword-only on the 18 functions, call sites, booleans
   by keyword. Checks. Commit.
5. **Wrap-up**: CHANGES.md 1.17.2, devlog Outcome + DONE, PR body,
   self-review against the new section, `gh pr ready`.

Each step is mechanical; the user chose unattended mode for #71 and will
be asked again per step here. NR goldens are the safety net throughout.
