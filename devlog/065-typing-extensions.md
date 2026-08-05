# 065 — Crash on clean install: typing_extensions not found

Date: 2026-08-05

Status: PENDING

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

(To be agreed before implementation.)
