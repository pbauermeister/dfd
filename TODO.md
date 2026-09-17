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

5. ~~Migrate package metadata to PEP 621~~ — absorbed into #79

   Move the `setup()` arguments of `setup.py` into a `[project]` table
   in `pyproject.toml` and drop `setup.cfg`. The version is parsed from
   `CHANGES.md`, which the table cannot express directly; a minimal
   `setup.py` or a version file kept in sync would remain. No change to
   the published packages; tooling hygiene only.

6. Harmonize GitHub and PyPI releases — task #80

   Single manually triggered GitHub Actions workflow, gated on the full
   test suite, one build, TestPyPI rehearsal, tag, PyPI via trusted
   publishing, GitHub release with the same files.

7. Generate CHANGES.md at release time

   Once #80 is in place: make CHANGES.md a generated product instead of
   the version source. On the manual decision to release (on `main`,
   gathering several merged PRs), the release workflow bumps a static
   version in `pyproject.toml` with `uv version --bump patch|minor`
   (bump chosen at trigger time; later possibly from PR labels),
   generates the changelog entry from the titles and summaries of the
   PRs merged since the last tag, commits both on `main`, then tags and
   publishes. Changelog texts come from PRs, not from commit messages.
   Raises the quality bar on PR titles and bodies.

   The decision to release stays manual. Out of scope: conventional
   commits (automated bump type and changelog grouping from commit
   prefixes) are explicitly not adopted for now, and not planned.
