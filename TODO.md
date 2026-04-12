# TODO

Recognized tasks are recorded as GitHub issues and managed in detail
in corresponding `devlog/NNN-*.md` files.

This file captures items as they arise during work, so nothing is
forgotten without diverting the current discussion or reasoning. Items
collected here can later be specified as tasks, grouped together, or
discarded. If a TODO item becomes significant effort, it must be
turned into a standard task (GH ticket, PR, devlog).

## Won't do

1. Redesign DSL parser with a formal grammar (lark, PEG, ANTLR)

   The DSL is one-statement-per-line by design — no nesting, no
   precedence, no multi-line constructs. The current regex-based
   scanner/parser is the right tool for this grammar. After the
   refactoring (#34), the pipeline stages are clean and independently
   modifiable. A formal parser would add a dependency and migration risk
   for no proportional benefit. Revisit only if a future feature
   genuinely requires multi-line syntax.

## TODO Items

1. Replace Black and add ruff

   Replace `black` with `ruff format` (drop-in compatible, ~100x faster
   locally) and add `ruff check` for style/import linting that mypy
   doesn't cover (unused imports, style issues). mypy stays for type
   checking. Consolidates formatting and linting into one tool.

2. ~~Fix README images on PyPI~~ — DONE (ea4c197+)

   Replaced relative image paths in README.md with absolute GitHub raw
   URLs so images render on both GitHub and PyPI.
