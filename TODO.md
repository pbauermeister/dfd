# TODO

Recognized tasks are recorded as GitHub issues and managed in detail
in corresponding `devlog/NNN-*.md` files.

This file captures items as they arise during work, so nothing is
forgotten without diverting the current discussion or reasoning. Items
collected here can later be specified as tasks, grouped together, or
discarded. If a TODO item becomes significant effort, it must be
turned into a standard task (GH ticket, PR, devlog).

## TODO Items

1. Evaluate ruff as linter/formatter

   **Prompt:** CI lint job takes 16s (mypy). Evaluate ruff as a faster
   alternative or complement. ruff handles style/import linting
   (10-100x faster than flake8/pylint) but does not replace mypy's type
   checking. Consider: ruff for style + mypy for types, or ruff alone
   if type checking is deemed low-value for this project.
