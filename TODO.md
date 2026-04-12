# TODO

Recognized tasks are recorded as GitHub issues and managed in detail
in corresponding `devlog/NNN-*.md` files.

This file captures items as they arise during work, so nothing is
forgotten without diverting the current discussion or reasoning. Items
collected here can later be specified as tasks, grouped together, or
discarded. If a TODO item becomes significant effort, it must be
turned into a standard task (GH ticket, PR, devlog).

## TODO Items

1. Replace Black and add ruff

   Replace `black` with `ruff format` (drop-in compatible, ~100x faster)
   and add `ruff check` for style/import linting. mypy stays for type
   checking — ruff doesn't cover that. This consolidates formatting and
   linting into one tool, speeds up CI, and simplifies the toolchain.
