# 065 — Crash on clean install: typing_extensions not found

Date: 2026-08-05

Status: ONGOING

## Requirement

From issue [#65](https://github.com/pbauermeister/dfd/issues/65):

When `data-flow-diagram` is installed in a clean venv
(`pip install data_flow_diagram`), running it crashes at startup with
`ModuleNotFoundError: No module named 'typing_extensions'`.

- The only use is `from typing_extensions import Literal` in
  `src/data_flow_diagram/console.py`.
- `setup.py` declares `install_requires=[]`, so nothing pulls in
  `typing_extensions`.
- Dev environments mask the bug because `make require` installs
  `typing_extensions` explicitly.

### Mandated fix

Do **not** add `typing_extensions` as a dependency. Instead, remove the need
for it:

1. In `console.py`, replace `from typing_extensions import Literal` with
   `from typing import Literal` (stdlib since Python 3.8; the project requires
   3.11+).
2. Drop `typing_extensions` from the `make require` pip install list in the
   Makefile.
3. Verify with `make black`, `make lint`, `make test`, and a clean-venv smoke
   test of the installed package.

This is a user-facing bug fix → PATCH version bump.

## Design

Agreed implementation steps:

1. Change `console.py` to `from typing import Literal`; remove
   `typing_extensions` from the `make require` pip install list in the
   Makefile.
2. Run `make black`, `make lint`, `make test`.
3. Clean-venv smoke test: build the package, `pip install` it into a fresh
   venv, run `data-flow-diagram --help` and a small render.
4. Bump version to 1.16.8, update `CHANGES.md`.

No new NR fixtures: the change does not touch diagram-generation behavior;
the clean-venv smoke test covers the actual failure mode.
