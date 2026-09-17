# 079 — Migrate to uv

Date: 2026-09-17
Status: ONGOING

Issue: https://github.com/pbauermeister/dfd/issues/79

## Requirement

Trigger: the build and publish scripts run `setup.py sdist bdist_wheel`
directly, which emits a deprecation warning ("Please avoid running
setup.py directly. Instead, use pypa/build, pypa/installer or other
standards-based tools."). Setuptools will eventually drop command-line
support for setup.py.

Rather than only swapping the build command, migrate the project tooling
to uv. Pascal uses it happily in another project, and it removes the
venv handling burden spread over the Makefile and several scripts.

Decisions:

- Packaging metadata moves to a PEP 621 `[project]` table in
  `pyproject.toml`. CHANGES.md stays the version source: `version` is
  declared dynamic and a reduced `setup.py` supplies it. `setup.cfg` is
  deleted; its `license_files = LICENSE.txt` names a nonexistent file
  (the file is `LICENSE`), which is why wheels and sdists currently
  ship without the license.
- Dev tools become a uv dependency group with a committed `uv.lock`.
- `uv run` replaces venv activation in the Makefile and scripts;
  `uv build` replaces `setup.py sdist bdist_wheel`; `uv publish`
  replaces twine.
- Local install: user-wide, no sudo, isolated venv per tool. uv's
  `uv tool install` is chosen over pipx to avoid a second installer
  opinion; the README mentions pipx as an equivalent for users.
  `tools/install-locally.sh` (sudo `setup.py install`, referenced by
  nothing) is deleted.
- Test matrix: tox is dropped. uv downloads interpreters itself, so the
  matrix is a Makefile loop over `uv run --python X --isolated`, used by
  CI as well. Fewer dependencies, a handful of lines.
- The `venv` and `venv-activate` targets stay: Pascal uses them to create
  and enter the venv before starting VS Code. `uv sync` creates a
  standard `.venv` with `bin/activate`, so `venv` runs `uv sync` and
  keeps its hint; `venv-activate` is unchanged. `VENV` becomes a fixed
  `.venv` path (still used by the prettier lookup); the tox override was
  its only reason to be a variable.
- Scope guard: tooling only. No change to the tool's behavior, to how
  tests are written, or to the version source.

PATCH bump.

## Design

Facts:

- The current wheel and sdist contain no LICENSE (checked on the 1.17.4
  artifacts). Deleting `setup.cfg` restores setuptools' default
  `LICEN[CS]E*` glob.
- setuptools accepts a `[project]` table with `dynamic = ["version"]`
  supplied by `setup(version=...)` in `setup.py`; uv resolves dynamic
  metadata through the build backend, so `uv sync` and `uv build` work.
- setuptools ≥ 70.1 builds wheels without the `wheel` package;
  `build-system.requires` drops it.
- tox is not needed for building; `isolated_build` was only for tox's
  own use.
- `uv run --isolated --python X` syncs into a throwaway environment for
  that interpreter, leaving the project `.venv` untouched.

Steps:

1. **Packaging metadata.** `[project]` table (name, description,
   readme, requires-python, license, classifiers, keywords, urls,
   console script), `dynamic = ["version"]`, `[dependency-groups] dev`
   (pytest, mypy, ruff), `build-system` with setuptools ≥ 70.1 only.
   `setup.py` reduced to the version extraction. Delete `setup.cfg`.
   `uv lock`. Verify: `uv build` succeeds without the warning; the
   wheel and sdist contain LICENSE; METADATA matches the 1.17.4 wheel
   except for the version and license fields. **Checkpoint:** show the
   METADATA diff.
2. **Makefile and scripts.** `venv` → `uv sync` + activation hint;
   `venv-activate` unchanged; `_venv` removed; `require` → `uv sync` +
   npm prettier; `require-system` installs uv (official installer on
   Linux, Homebrew on macOS); every `. $(VENV)/bin/activate && cmd` →
   `uv run cmd`; `VENV := .venv`; `install` → `uv tool install --force .`;
   delete `tools/install-locally.sh`; `tools/build.sh` and
   `tools/smoke-test-install.sh` (`uv venv`, `uv pip install`);
   `tools/publish-to-testpypi.sh`, `tools/publish-to-pypi.sh` and
   `tools/publish-to-github.py` use `uv build` and `uv publish` (token
   via `UV_PUBLISH_TOKEN`, not echoed). prettier via npm unchanged.
   Verify: `make all`; `make smoke-test-wheel`.
3. **Test matrix and CI.** Delete `tox.ini`; add `make test-matrix`
   looping over `PYTHONS = 3.11 3.12 3.13`; `ci.yml` uses
   `astral-sh/setup-uv` and calls the Makefile targets, one parallel
   job per version (GitHub's own matrix, not `test-matrix`). The version
   list is thus duplicated: `make lint` passes `PYTHONS` to
   `tools/check-python-versions.py`, which parses `ci.yml` (pyyaml, dev
   group) and fails if the job matrix lists different versions. Verify: CI green on the three versions plus
   lint and wheel smoke test. **Checkpoint.**
4. **Docs.** README: user install via `uv tool install` (pipx
   equivalent), developer section; `doc/CONVENTIONS.md` packaging note;
   `tests/README.md` and CLAUDE.md wherever venv activation or tox is
   mentioned; `make readme`. TODO.md item 5 marked absorbed.
5. **Close.** Bump to 1.17.5 in CHANGES.md, devlog DONE, self-review,
   PR ready.
