# 077 — TestPyPI Release Cycle

Date: 2026-09-16
Status: PENDING

Issue: https://github.com/pbauermeister/dfd/issues/77

## Requirement

#65 showed that install-time breakage (a missing dependency) is invisible
to the dev-venv test suite. The clean-venv wheel smoke test done manually
in #65 covers the built artifact. TestPyPI would also cover the publishing
path: twine upload, index metadata, pip resolution.

Proposal:

1. Script the clean-venv smoke test: build sdist + wheel, `pip install`
   the wheel into a fresh venv, run `data-flow-diagram --help` and a
   small render.
2. Add a TestPyPI stage: `twine upload -r testpypi`, then install
   `data-flow-diagram==<version>` from TestPyPI into a fresh venv and run
   the same smoke test.
3. Wire both into the release flow, so `make publish-to-pypi` runs them
   before the real upload (or as separate targets, to decide).

Open points:

- Token handling: separate `.token-test` file vs `~/.pypirc`.
- TestPyPI rejects re-uploads of a version, so a failed cycle needs a
  version bump before retry.
- `make install` (`--break-system-packages`) and
  `tools/install-locally.sh` (sudo `setup.py install`) are unrelated to
  the venv-based smoke test; out of scope unless aligned on purpose.

## Design

(to be agreed)
