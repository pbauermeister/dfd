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

10. ~~Conventional commits and generated CHANGES.md~~ — DONE (#88)

    Adopt conventional commits (reconsidered 2026-09-17; was out of
    scope for #80) and generate the `CHANGES.md` entry at release time
    from the commits since the last tag, instead of writing it by hand.
    Decide at the same time when to publish: keep the manual
    `make release`, or release automatically on merge to `main` once
    the version bump and changelog are derived from the commits.
    Once the version no longer comes from `CHANGES.md`, drop the
    `setup.py` version shim left by item 5.

11. ~~Naming rules for tool scripts and Makefile targets~~ — DONE (#90)

    Codify in `doc/CONVENTIONS.md` when a name is verb-first
    (`update-docs.py`: a single action, read as a command), topic-first
    (`nr-test`, `require-system`: a family of two or more, grouped in
    listings and completion), or a noun with subcommands
    (`changelog.py notes`, `conventional-commits.py table`: a Python
    family in one program). Object-first with no family behind it is
    the case to avoid. Then apply: the doc scripts (`make-doc.sh`,
    `update-docs.py`, `gen-style-tables.py`,
    `doc-renumber-md-titles.py`) become a `doc-` family or fold into
    one program; audit the Makefile targets. Discussed in #88.

    Conclusions of #88 (2026-09-19) to apply at the same time:

    - Script levels, git's porcelain and plumbing as the model: Makefile
      targets are the entry points; orchestrators are runbooks in code
      (named steps, one command each, guards only, no loops or
      computation); tools do one concern with verb-first subcommands
      and explicit arguments so that every call site is
      self-explanatory (one tool per noun, subcommands for verbs
      sharing its data); preludes hold sourced mechanics only. Logic
      appearing in an orchestrator moves down into a tool.
    - Two folders make the levels an address: `runbooks/` for the
      orchestrators (`release.sh`, `publish-to-*.sh`, `build.sh`,
      `lint.sh`, `clean.sh`, `make-doc.sh`), `tools/` for the tools
      (the Python scripts, `wait-for.sh`; `smoke-test-install.sh` is
      the shell tool with a mode argument). `doc/RELEASING.md` is the
      prose runbook of `runbooks/release.sh`: same word on purpose.
      Path churn: Makefile, both workflows, sourcing lines.
    - The prelude `init-tracing.sh` (ex `set-ex.sh`, renamed in #88)
      keeps only what needs the tracing hack: `echo`, `banner`,
      `banner2`, `step`.
    - Codified tersely in `doc/CONVENTIONS.md`, "Tooling scripts", by
      #88; item 11 executes the folder split and the renames.

12. Exercise the release and merge-gate paths of #88

    Each case is ticked when it occurs naturally or is provoked on
    purpose; the first live release (1.17.8, 2026-09-19) covered
    "merge followed by a release right away".

    Release path (`make release`, `release.yml`):

    - [ ] Dry run from a branch: `.devN` version in `pyproject.toml`,
          `gh workflow run release.yml --ref <branch>`; stops after
          TestPyPI, no tag checks.
    - [ ] Nothing to release: only `chore`/`ci`/`style` or
          non-conventional commits since the last tag; the plan exits 1
          and the script stops before any commit.
    - [ ] Abort at the prompt: local release commit and tag removed,
          tree equal to `origin/main`.
    - [ ] A minor release (first `feat:` PR) and, when it comes, a
          major one (`!` or `BREAKING CHANGE:` footer in the PR body,
          which the squash setting carries into the commit).
    - [ ] Preflight refusal, provoked: a `v*` tag pushed on a commit
          that is not on `main` (delete the tag afterwards).
    - [ ] Recovery forward after a failed run past TestPyPI, when it
          happens: next patch, the failed tag left or deleted.

    Merge gate (`merge-gate.yml`, ruleset on `main`):

    - [ ] Merge not followed by a release: two patch PRs merged, then
          one release whose changelog lists both.
    - [ ] Blocked: a `feat:` PR while `main` has unreleased patch
          commits ("release X first"); release, then the check passes
          on the next PR event.
    - [ ] Allowed at or below: a `fix:` PR on a pending minor.
    - [ ] None-level pending counts as empty: a `chore:` commit on
          `main`, then a `feat:` PR passes.
    - [ ] A title edit re-runs `conventional` and `gate`; a
          non-conventional title blocks the merge button.
    - [ ] PR behind `main`: BEHIND state, "Update branch", checks rerun.

13. Extract the Markdown titles renumberer into its own tool

    `tools/doc-renumber-md-titles.py` becomes a standalone repository
    and PyPI package, usable from several projects; then dfd consumes
    it as a dev dependency from `make-doc.sh`. Brief, measured survey
    of existing tools and requirements in
    `discussions/md-titles-renumberer-tool.md` (from #90).

14. Devlog templates

    The devlogs are not uniform: over 34 files, `Requirement` and
    `Design` appear in 31 and 29, `Outcome` in 10, and the rest is
    one-off section names (`Analysis`, `Action plan`, `Verification`,
    `Progress`, `Lessons learned`, numbered variants, ...), because
    the project has no template. Define one, with mandatory and
    optional sections, in variants fitting the major kinds of tasks
    (feature or fix from an issue; refactoring with an inventory and a
    mechanical plan, as in #90; analysis or discussion, as in
    `discussions/`; summary or report, as in #55). Codify in
    `CLAUDE.md` "devlog/NNN-short-description.md files" and provide
    the templates as files the scaffolding phase copies.

15. Offload `CLAUDE.md`

    `CLAUDE.md` grows with every task (265 lines, 15 sections)
    and is loaded whole into every session, whatever the task. Offload
    it: per-folder `CLAUDE.md` files that Claude Code loads when it
    works in that folder (`tests/`, `tools/`, `runbooks/`, `devlog/`),
    or dedicated documents that the root file refers to by context
    (task start process, NR tests, release, conventions), keeping the
    root to the rules that apply everywhere. Measure the line counts
    before and after; keep the append-only rule for the root file.
