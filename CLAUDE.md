# Project Instructions

`data-flow-diagram` compiles a text DSL into data flow diagrams (SA/SD
and SA/RT) rendered through Graphviz as SVG, PNG or PDF. Python 3.11+
(`StrEnum`), `uv` for the environment, `make` as the task layer,
Graphviz as the rendering backend.

## Layout

- `src/data_flow_diagram/`: `dfd.py` (orchestrator), `cli.py`,
  `model.py`, `config.py`; sub-packages `dsl/` (scanner, parser,
  checker, filters, dependency checker) and `rendering/` (dot,
  templates, graphviz). The sub-packages are independent siblings: both
  import from the parent, neither from the other.
- `doc/`: product documentation, `README.md` (syntax reference) and
  `SYNTAX.md` (glossary); `README.md` at the top level is the user-facing
  page.
- `engineering/`: how the project is built, generic to the way of
  working; `templates/`, `devlog/`, `discussions/`, `TODO.md`: the task
  records.
- `tests/`, `tools/`, `recipes/`: see `engineering/CONVENTIONS.md`
  "Script levels" and `tests/README.md`.

## Import compatibility

All internal imports must work in every calling context: the local dev
wrapper (`./data-flow-diagram`, imports `src.data_flow_diagram`), the
pip-installed console script (imports `data_flow_diagram`), and pytest
(`data_flow_diagram` via `src/` on `sys.path`). Relative imports satisfy
this because Python resolves them against the package hierarchy. When
adding sub-packages or moving modules, verify all three (`make test`
covers pytest; smoke-test the other two by hand).

## Map: read before acting

| When                                                         | Read first                                         |
| ------------------------------------------------------------ | -------------------------------------------------- |
| Starting, continuing or closing a task; branching, PR, merge | `engineering/PROCESS.md`, all of it                |
| Filling a devlog                                             | `templates/devlog.md` (guidance comments)          |
| Naming, structure, type safety, design, scripts, Markdown    | `engineering/CONVENTIONS.md`                       |
| Commenting code                                              | `engineering/COMMENTING.md`                        |
| Writing or changing a test                                   | `tests/README.md` (`tests/CLAUDE.md` loads itself) |
| Versioning, commit types, merge gate, releasing              | `engineering/RELEASING.md`                         |

Claude: if the user starts a task without following
`engineering/PROCESS.md`, briefly remind them of it.

@engineering/RULES.md
