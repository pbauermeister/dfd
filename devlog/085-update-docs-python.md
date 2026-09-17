# 085 — Rewrite `tools/update-docs.sh` in Python

Date: 2026-09-17
Status: DONE

Issue: https://github.com/pbauermeister/dfd/issues/85

## Requirement

`tools/update-docs.sh` replaces `<!-- AUTO:* -->` sections of Markdown
files with awk/sed and generates the CLI help and doc TOC: string
manipulation and Markdown section handling, which the "Tooling scripts"
convention (`doc/CONVENTIONS.md`) assigns to Python.

- Same sections (`cli-help`, `doc-toc` in `README.md`; `style-table` in
  `doc/README.md` and `doc/SYNTAX.md`), same markers, same prettier pass.
- Byte-identical output on the current docs (`tests/test_doc_sync.py`
  guards the style tables; `git diff` after `make readme` guards the
  rest).
- PATCH bump (1.17.7 entry).

## Design

Fast-pathed from TODO.md item 8 (Pascal, 2026-09-17), unattended.

`tools/update-docs.py`, typed as application code, replaces the bash
script (deleted):

- One generator function per section: CLI help (`./data-flow-diagram
  --help` as a subprocess, `COLUMNS=80` pinned so the argparse wrapping
  no longer depends on the caller's environment), doc TOC (level-2
  headings of `doc/README.md` → GitHub anchors, same rule as before:
  lowercase, keep `[a-z0-9 _-]`, spaces → `-`), style tables
  (`gen-style-tables.py readme|syntax` as a subprocess, as the doc-sync
  test runs it).
- `replace_section(text, name, content)` finds the marker lines and
  returns the new text; a missing marker warns on stderr and skips, as
  before.
- prettier from `$VENV/node_modules/.bin` (default `.venv`), skipped
  with a warning when absent.
- Makefile `readme` target calls the new script; devlog/071 references
  stay historical.
- CHANGES.md bullet in 1.17.7. TODO.md item 8 → DONE.

Steps:

1. Script + Makefile; run `make readme`, confirm empty `git diff` on the
   docs; delete the bash script; `make format lint test`.
2. CHANGES.md, TODO.md; PR ready.
