# 2026-02-14 — Refactor DSL keyword constants into StrEnum [DONE]

**Prompt:** Refactor the string constants (STYLE..WITHOUT) in model.py into a string-backed enum, with intermediate steps to replace hardcoded strings and add connection-variant constants.

Three incremental steps were applied:

1. **Replace hardcoded string literals** (parser.py): 6 dispatch-table keys (`"flow.r"`, etc.) and 10 keyword strings in `apply_syntactic_sugars()` were replaced with references to model constants. The stale FIXME about a circular dependency was removed. The `"!~"` character check was replaced with `(model.ONLY, model.WITHOUT)`.

2. **Add connection-variant constants** (model.py): introduced `_REVERSED`/`_RELAXED` building blocks and 10 new constants (`FLOW_REVERSED`, `FLOW_RELAXED`, `FLOW_REVERSED_RELAXED`, `CFLOW_*`, `BFLOW_RELAXED`, `UFLOW_RELAXED`, `SIGNAL_*`, `CONSTRAINT_REVERSED`). Updated parser.py dispatch table and `apply_syntactic_sugars()` — the latter was refactored with a `resolve(keyword, relaxed_keyword)` helper to eliminate repetitive `q`/`parts`/`fmt` boilerplate.

3. **Consolidate into `class Keyword(StrEnum)`** (model.py): all 27 keyword constants (17 base + 10 variants) gathered into a single enum. Consumer files (parser.py, dfd.py, dependency_checker.py) updated to use `Keyword.MEMBER` access. `StrEnum` membership means values remain usable as plain strings for parsing, comparison, hashing, and serialization.

Files changed: `model.py`, `parser.py`, `dfd.py`, `dependency_checker.py`. Output verified identical (smoke test).
