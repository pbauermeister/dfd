# 071 — Streamline Style Options

Date: 2026-09-03

Status: PENDING

## Requirement

From GitHub issue #71: defining a new `style` option requires manual,
mechanical edits in several places. Make one place the dense source of
truth (type, default, DSL keyword, explanation) and derive or generate the
rest.

Audit of the current state: six edit sites in five files per option.

| Site                                     | File            |
| ---------------------------------------- | --------------- |
| `DEFAULT_*` constant                     | `config.py`     |
| `GraphOptions` field                     | `model.py`      |
| `StyleOption` enum member                | `model.py`      |
| `match` case in `handle_options`         | `dfd.py`        |
| Row in the per-diagram style table 2.5.1 | `doc/README.md` |
| Row in the styles table 4                | `doc/SYNTAX.md` |

Decisions taken with the user:

- **Single source of truth is the `GraphOptions` field declaration.** The
  DSL keyword(s) and the doc string are attached as `dataclasses.field`
  metadata via a small helper; type and default come from the field itself.
  Everything else is derived: the keyword registry, the generic
  `handle_options`, and the two documentation tables.
- **Fold the defaults**: the style-related `DEFAULT_*` constants in
  `config.py` are removed; the field default is the default.
  `doc/CONVENTIONS.md` is updated accordingly. The `StyleOption` enum is
  removed (it was referenced only by `handle_options`).
- **One doc string per option**, shared by both tables. `doc/SYNTAX.md`
  derives its "Value" and default columns from the field type and default.
  SYNTAX wording changes slightly as a consequence.
- **Docs are generated** into `<!-- AUTO:... -->` marker sections of
  `doc/README.md` and `doc/SYNTAX.md`, reusing the mechanism of
  `tools/update-readme.sh`, under `make readme` / `make doc`.
- **After insertion, the doc files are reformatted with prettier** so that
  manual edits in VSCode (prettier autoformatter) create no meaningless
  diffs. Both files are already prettier-clean today, so this is a safety
  net. Prettier is installed by `make require` (into the venv directory via
  npm, not globally); `make require-system` adds `npm`.
- **Drift guard is a pytest test**: it regenerates the tables in memory
  and compares them to the marker sections of both doc files. It needs no
  Node, so `make test` and CI are unaffected.
- **Behavior is byte-identical**: DOT output and error messages
  (`Unsupported style "..."`, `get_style_int` errors) do not change, so the
  existing 81 NR fixtures are the safety net. No new NR fixtures.
- **CLI flags stay out of scope.** Deriving `--background-color` /
  `--no-graph-title` (and possibly more) from the same metadata is a
  feature with its own product decisions; it becomes a separate task. This
  task only leaves the door open: the registry exposes name, kind, default,
  and doc for every option.
- Refactor: PATCH bump to 1.17.1.

## Design

### Registry (`model.py`)

```python
@dataclass
class GraphOptions:
    is_vertical: bool = style(False, flags={
        "vertical":   (True,  "Layouts flows in the vertical direction."),
        "horizontal": (False, "Layouts flows in the horizontal direction (the default)."),
    })
    item_text_width: int = style(20, name="item-text-width",
        doc="Sets the items labels wrapping to use N chars columns.")
    background_color: str | None = style(None, name="background-color",
        doc="Sets a graph background color as per https://graphviz.org/docs/attr-types/color/.")
    ...
```

- `style()` wraps `dataclasses.field(default=..., metadata=...)`.
- `StyleSpec(field, kind, value, doc)` with `kind` in `flag | int | str`,
  inferred from the resolved type hint (`bool` → flag, `int` → int, else
  str). `value` is the fixed value for flags, the default otherwise.
- `STYLE_SPECS: dict[str, StyleSpec]` is built once at import from
  `dataclasses.fields(GraphOptions)` and `typing.get_type_hints`.

### Generic `handle_options` (`dfd.py`)

One registry lookup (unknown keyword → same "Unsupported style" error),
one three-way branch on `kind` (flag → fixed value, int →
`get_style_int`, str → raw value), one `setattr`.

### Doc generation (`tools/`)

- `tools/gen-style-tables.py`: imports the model, prints the README table
  (`Style statement | Effect`) or the SYNTAX table
  (`Option | Value | Effect`) as padded Markdown, selectable by argument.
- `tools/update-readme.sh` becomes `tools/update-docs.sh`: `replace_section`
  takes a file path; new sections `style-table` in `doc/README.md` and
  `doc/SYNTAX.md`; after replacement, runs
  `$VENV/node_modules/.bin/prettier --write` on the touched files.
- Makefile: `require` adds `npm install --prefix $(VENV) prettier@3`;
  `require-system` adds `npm` to the apt/brew lists; `readme` target calls
  the renamed script.

### Drift guard (`tests/`)

Integration test (placement per `tests/README.md`): for each doc file,
extract the marker section, compare to the generator output.

### Implementation steps

1. **Registry + generic handler.** `model.py` (helper, spec, registry,
   fold defaults, drop enum), `config.py` (drop style constants),
   `dfd.py` (generic `handle_options`), `doc/CONVENTIONS.md`.
   `make black`, `make lint`, `make test` — all 81 NR goldens must pass
   unchanged. **Checkpoint**: user reviews the registry declaration style.
2. **Doc generator + markers + prettier.** `tools/gen-style-tables.py`,
   `tools/update-docs.sh`, markers in both docs, Makefile changes. Run
   `make readme`; **checkpoint**: user reviews the resulting doc diff
   (SYNTAX wording changes).
3. **Drift test** in `tests/`. Mutation smoke-test: alter one doc string
   in the registry, confirm the test fails, revert.
4. **Wrap-up.** `CHANGES.md` 1.17.1, PR body update, `gh pr ready`.
5. **Follow-up issue** for CLI flag derivation, opened after merge.
