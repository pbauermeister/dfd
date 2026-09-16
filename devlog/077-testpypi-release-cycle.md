# 077 — TestPyPI Release Cycle

Date: 2026-09-16
Status: ONGOING

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

Facts:

- `--format dot` renders without Graphviz, so the smoke test can diff an
  NR fixture against its golden file.
- `--version` uses `importlib.metadata`, so in a fresh venv it proves the
  installed distribution's version.
- twine is in the venv; real PyPI uses a `.token` file; no `~/.pypirc`.
- No runtime dependencies, so TestPyPI installs can use `--no-deps`.

Decisions:

- Chain the TestPyPI stage into `publish-to-pypi.sh`; any failure stops
  before the real upload. Each attempt consumes the version on TestPyPI,
  which is fine since a failed attempt needs a bump anyway.
- No `--skip-existing` on the TestPyPI upload (it would silently test a
  stale upload). Dev-time validation uses a throwaway `1.17.4.dev1`
  heading in an uncommitted `CHANGES.md` edit.
- TestPyPI token in a gitignored `.token-test` file, mirroring `.token`.
- No NR fixtures: diagram behavior is untouched.

Steps:

1. `tools/smoke-test-install.sh wheel|testpypi`: fresh venv in a temp
   dir; install the local wheel from `dist/` or
   `data-flow-diagram==<version>` from TestPyPI (with retries, the index
   lags after upload); check `--version`; render an NR fixture with
   `-f dot` and diff against its golden file; delete the venv.
2. `make smoke-test-wheel`: build sdist + wheel, run the script in wheel
   mode. Add to the CI workflow.
3. `make publish-to-testpypi`: `twine upload -r testpypi` with
   `.token-test`, then run the script in testpypi mode.
4. Chain into `publish-to-pypi.sh`: build, wheel smoke test, TestPyPI
   upload + smoke test, real PyPI upload, GitHub release.
5. Bump to 1.17.4, `CHANGES.md` entry, note in the publish script header.
