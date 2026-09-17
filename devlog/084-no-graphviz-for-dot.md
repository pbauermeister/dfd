# 084 — Make `--version`, `--help` and `-f dot` work without Graphviz

Date: 2026-09-17
Status: PENDING

Issue: https://github.com/pbauermeister/dfd/issues/84

## Requirement

`cli.main()` calls `graphviz.check_installed()` before parsing the
arguments, so every invocation needs `dot`, including the install smoke
test (`tools/smoke-test-install.sh`, which only checks `--version` and a
`-f dot` render).

- Probe Graphviz only where it is invoked (rendering a non-DOT format).
  `--version`, `--help`, `-f dot` and DSL error reporting work without
  Graphviz.
- Same error message and exit status (2) as today when `dot` is missing
  and a rendered format is requested.
- Drop the `make require-system` steps from the `build` and `testpypi`
  jobs of `release.yml` (added in PR #83), and from the `smoke-test-wheel`
  job of `ci.yml`, which runs the same smoke test.
- PATCH bump: 1.17.7.

## Design

Fast-pathed from TODO.md item 9 (Pascal, 2026-09-17), unattended.

- `graphviz.generate_image()` catches `FileNotFoundError` from
  `subprocess.run` and reports `"Graphviz" seems not installed` with
  exit status 2. `check_installed()` and its call in `cli.main()` are
  removed: the probe was a second process spawn for the same
  information. In markdown mode the first rendered snippet reports the
  error.
- `cli.main()` parses the arguments first; `--version` and `--help`
  never touch Graphviz.
- `doc/CONVENTIONS.md` example list: `check_installed()` replaced by
  another action-first name.
- Tests (`tests/unit/test_cli.py`, unit/regression): with `PATH` emptied,
  `--version` exits 0, `-f dot` on stdin prints DOT, and an SVG render
  exits 2 with the Graphviz error on stderr.
- `release.yml`, `ci.yml`: remove the Graphviz install steps of the
  smoke-test jobs; `tools/smoke-test-install.sh` header keeps its
  "No Graphviz needed" claim, now true.
- CHANGES.md: new 1.17.7 entry. TODO.md item 9 → DONE.

Steps:

1. Code + tests + conventions example; `make format lint test`.
2. Workflows, CHANGES.md, TODO.md; PR ready.
