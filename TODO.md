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

1. ~~Replace Black and add ruff~~ — DONE (#75)

   `ruff format` replaces Black; `ruff check` runs before mypy in
   `make lint`, with ANN401, FBT and PLR0917 (not PLR0913, which also
   counts keyword-only parameters) enforcing `doc/CONVENTIONS.md`.

2. ~~Fix README images on PyPI~~ — DONE (ea4c197+)

   Replaced relative image paths in README.md with absolute GitHub raw
   URLs so images render on both GitHub and PyPI.

3. ~~Include TestPyPI in a full testing cycle~~ — DONE (#77)

   Extend the release testing cycle to upload to TestPyPI
   (`twine upload -r testpypi`) and install from there in a clean venv,
   as an end-to-end test of the publishing pipeline before the real
   PyPI upload. Context: #65 showed that install-time breakage (missing
   dependency) is invisible to the dev-venv test suite; the clean-venv
   wheel smoke test covers the artifact, TestPyPI would also cover the
   transport/publishing path.

4. ~~Build improvement~~ — task #79

   During the build, the below warning was seen. We shall update the
   build accordingly.

   ```
   ********************************************************************************
   Please avoid running ``setup.py`` directly.
   Instead, use pypa/build, pypa/installer or other
   standards-based tools.

   See https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html for details.
   ********************************************************************************
   ```

5. ~~Migrate package metadata to PEP 621~~ — DONE (#79)

   Move the `setup()` arguments of `setup.py` into a `[project]` table
   in `pyproject.toml` and drop `setup.cfg`. The version is parsed from
   `CHANGES.md`, which the table cannot express directly; a minimal
   `setup.py` or a version file kept in sync would remain. No change to
   the published packages; tooling hygiene only. Residue: `setup.py`
   stays as the version shim until item 10 changes where the version
   comes from.

6. ~~Harmonize GitHub and PyPI releases~~ — DONE (#80)

   Single manually triggered GitHub Actions workflow, gated on the full
   test suite, one build, TestPyPI rehearsal, tag, PyPI via trusted
   publishing, GitHub release with the same files.

8. ~~Rewrite `tools/update-docs.sh` in Python~~ — DONE (#85)

   It replaces `<!-- AUTO:* -->` sections of Markdown files with awk/sed
   and generates the CLI help and doc TOC: string manipulation and
   Markdown section handling, which the "Tooling scripts" convention
   (`doc/CONVENTIONS.md`) assigns to Python. Keep the same sections,
   markers and prettier pass; `tests/test_doc_sync.py` guards the
   output. Rewrite when it next needs to grow, not before.

9. ~~Make `--version`, `--help` and `-f dot` work without Graphviz~~ — DONE (#84)

   `cli.main()` calls `graphviz.check_installed()` before parsing the
   arguments, so every invocation needs `dot`, including the install
   smoke test (`tools/smoke-test-install.sh`, which only checks
   `--version` and a `-f dot` render). Move the probe to where Graphviz
   is actually invoked (rendering a non-DOT format); then drop the
   `make require-system` steps from the `build` and `testpypi` jobs of
   `release.yml` (added in PR #83).

10. Conventional commits and generated CHANGES.md

    Adopt conventional commits (reconsidered 2026-09-17; was out of
    scope for #80) and generate the `CHANGES.md` entry at release time
    from the commits since the last tag, instead of writing it by hand.
    Decide at the same time when to publish: keep the manual
    `make release`, or release automatically on merge to `main` once
    the version bump and changelog are derived from the commits.
    Once the version no longer comes from `CHANGES.md`, drop the
    `setup.py` version shim left by item 5.
