# 088 — Conventional commits and python-semantic-release

Date: 2026-09-18
Status: ONGOING

Issue: https://github.com/pbauermeister/dfd/issues/88

## Requirement

Adopt conventional commits and derive version, `CHANGES.md` entry,
release commit and tag from them (TODO item 10).

- **Commit format.** Commit messages and PR titles in Conventional
  Commits form `<type>[(scope)]!: <description>`. Enforced per commit
  by a `commit-msg` hook from `conventional-pre-commit`, installed by
  `make require`, and per PR title by
  `amannn/action-semantic-pull-request`. Repository setting changed to
  always take the squash title from the PR title. Issue numbers move
  from the title to a `Closes #N` line in the PR body.
- **Bump map** in `[tool.semantic_release]` of `pyproject.toml`:
  `feat` minor, `!` or `BREAKING CHANGE` major,
  `fix`/`perf`/`refactor`/`docs`/`test`/`build` patch,
  `chore`/`ci`/`style` none. `make help-cc` prints the map from that
  section.
- **Release.** `make release` runs `semantic-release version`, which
  computes the version, writes it into `pyproject.toml`, inserts the
  generated section into `CHANGES.md` above a marker line, commits and
  tags, then pushes. `release.yml` triggers on the tag; preflight
  checks the tag points at `main` and matches `pyproject.toml`.
  `--noop` gives the rehearsal. `setup.py` and the dynamic version are
  removed. The changelog is the tool's default output: one bullet per
  commit, grouped by type, PR linked.
- **Merge gate.** A PR whose type would raise the pending level on
  `main` is blocked until the pending changes are released. Merges at
  or below the pending level pass.
- **Docs and conventions.** `doc/RELEASING.md` and `CLAUDE.md`
  updated; the versioning convention gains the "none" level and loses
  `.postN`; the stray tag `v0.0.0.dev1` is deleted.

Trial on a throwaway clone (2026-09-17): python-semantic-release
10.6.2, 21 lines of TOML, produced the expected release commit,
changelog section and tag.

Decisions (2026-09-18):

- `docs` and `test` bump patch: docs ship in the package, and the
  current convention stays intact.
- `chore`, `ci` and `style` bump nothing. A version number promises a
  change in what the user installs or reads; these three never touch
  the wheel. This holds because the project is a tool installed on the
  user's computer. For a service, CI changes can have real if invisible
  effects (faster deploy, better migration) that deserve a release.
  Such commits still appear in the changelog of the next release.
  `.postN` disappears: packaging fixes are `build:`, patch.
- Gate: the pending level is `semantic-release --noop version --print`
  compared with the version in `pyproject.toml`; the incoming level is
  the PR title's type looked up in the bump map of `pyproject.toml`.
  `tools/conventional-commits.py` reads that map for both the gate and `make help-cc`.
- No NR fixtures: no code path of the tool changes.
- PR type review before merge (2026-09-19): the PR title's type must
  be at the highest bump level among the PR's commits and name the
  PR's purpose; the squash discards the inner types, and after the
  merge only history rewriting could fix the subject. `CLAUDE.md`
  codifies a quick review of the type as the last check before merge:
  the agent reminds it before suggesting a merge, and asks the user
  before merging a PR itself.
  Rationale to state there: devlog in the PR, squash merge and the PR
  title as the single conventional subject hold each other up; the
  devlog commits vanish at squash and stay out of the changelog, so
  the title is the only place where the PR's type is decided.

## Design

Ordered steps:

1. **Version and configuration.** Static `version` in
   `pyproject.toml`, `setup.py` removed, `[tool.semantic_release]`
   section (21 lines, as trialed), marker line in `CHANGES.md`,
   python-semantic-release and pre-commit in the `dev` dependency
   group, `make show-version`, `make help-cc` via `tools/conventional-commits.py`.
   `tools/changelog.py` adapted to the heading form `## vX.Y.Z (date)`
   (GitHub release notes). Stray tag `v0.0.0.dev1` deleted.
2. **Enforcement.** `.pre-commit-config.yaml` with the commit-msg hook,
   installed by `make require`. `pr-title.yml` workflow. Repository
   squash-title setting switched to "PR title" via `gh api`.
3. **Release path.** `tools/release.sh` runs `semantic-release version`
   and pushes commit and tag. `release.yml` triggers on `v*` tags;
   preflight checks the tag is on `main` and matches `pyproject.toml`.
   `doc/RELEASING.md` rewritten. `publish-to-github.py` adapted.
4. **Merge gate.** `merge-gate.yml` on `pull_request`, using
   `tools/conventional-commits.py`; the same assertion in release preflight.
4b. **Review fixes** (PR review of 2026-09-19): descriptive subcommand
   names, `release.sh` reduced to orchestration by two scripts.
5. **Conventions.** `CLAUDE.md` versioning and branching sections,
   the PR-type review before merge (agent reminds, asks before merging
   itself), TODO item 10 done. The PR retitle in CC form moved to
   step 2.

## Action plan

One subsection per step of the Design, written before the step starts.

### Step 1

Files:

- `pyproject.toml`: `version = "1.17.7"` replaces `dynamic`;
  `[tool.semantic_release]` section; `python-semantic-release` and
  `pre-commit` in the `dev` group; `cache-keys` entries for `setup.py`
  and `CHANGES.md` dropped.
- `setup.py` deleted; `doc/CONVENTIONS.md` line about it adjusted.
- `CHANGES.md`: marker line at the top.
- `tools/changelog.py`: `version` reads `pyproject.toml`; `notes`
  accepts both heading forms. `publish-to-github.py` unchanged (uses
  those two functions).
- `tools/smoke-test-install.sh`: version from `pyproject.toml`.
- `tools/conventional-commits.py` (new): `table` subcommand rendering the bump map.
  `Makefile`: `help-cc`, `show-version`.
- `uv.lock` updated by `uv sync`.

Commands: `uv sync`, `make format`, `make lint`, `make test`,
`make show-version`, `make help-cc`, `uv build` (wheel takes the
static version). Tag `v0.0.0.dev1` deleted locally and on `origin`
(irreversible; April leftover, referenced by no release).

Two commits: configuration and shim removal; tools and Makefile.
`release.yml` keeps working until step 3 (`changelog.py version`
still prints the latest version).

### Step 2

Finding (trial clone): with the repository's current squash setting
(`COMMIT_MESSAGES`) the squash body concatenates the branch commits,
and the tool parses conventional lines inside it as separate entries;
an inner `fix:` of a squashed `feat:` PR got its own bullet. Plain
body text is ignored. Hence the last two items below.

Files:

- `.pre-commit-config.yaml` (new): `compilerla/conventional-pre-commit`
  v4.4.0 on the `commit-msg` stage, explicit type list.
- `Makefile` `require`: `uv run pre-commit install --hook-type
  commit-msg` (no `core.hooksPath` in play).
- `.github/workflows/pr-title.yml` (new):
  `amannn/action-semantic-pull-request` v6.1.1, explicit type list,
  scope optional.
- `tools/conventional-commits.py`: `check` subcommand verifying that
  the type lists of the hook config and the workflow equal
  `allowed_tags` of `pyproject.toml` (pyyaml, already a dev dep);
  wired into `make lint` like `check-python-versions.py`.
- `pyproject.toml`: `parse_squash_commits = false` in
  `commit_parser_options`, so one PR is one entry whatever the body.
- Repository settings via `gh api -X PATCH`: squash title from the PR
  title (`PR_TITLE`), squash body from the PR body (`PR_BODY`, keeps
  `Closes #N` and lets a `BREAKING CHANGE:` footer in the body work).
  Reversible, outward-facing.
- PR #89 retitled in CC form now rather than in step 5, since the new
  workflow checks it: `build: adopt conventional commits and
  python-semantic-release`.

Commands: `uv sync`, hook install, hook trial (a non-conforming commit
message must be rejected, a conforming one accepted), `make lint`,
push and read the `pr-title` check on PR #89.

From this step on every commit on the branch is conventional, devlog
commits included (`docs: devlog 088 ...`).

Two commits: hook, Makefile, pyproject option; workflow, `check`
subcommand, lint wiring.

### Step 3

Files:

- `tools/release.sh`: same preconditions (main, clean, equal to
  `origin/main`); refuses when `show-version` equals the current
  version (nothing to release); runs `semantic-release version
  --no-push --no-vcs-release` (release commit + tag, local); shows
  the version and the new `CHANGES.md` section; asks `[y/N]` before the
  point of no return; on no, removes the local tag and resets to
  `origin/main`; on yes, pushes `main` and the tag, then watches the run
  the tag triggers.
- `.github/workflows/release.yml`: `on: push: tags: ["v*"]` is the
  release; `workflow_dispatch` (no inputs) is the dry run, any ref,
  stopping after TestPyPI. Preflight on a tag: the tagged commit is on
  `origin/main`, the tag equals `v` + `project.version`; PyPI/TestPyPI
  absence kept; the "tag does not exist" check goes. `github-release`
  creates the release on the existing tag (no `--target`).
- `doc/RELEASING.md` rewritten: procedure, workflow table, conventional
  commits (types via `make help-cc`, PR title = changelog line, hook),
  failure recovery by fixing forward (a tag without a release marks a
  failed attempt), dry run of a workflow change (`.devN` version in
  `pyproject.toml` on a branch, dispatch), local fallback (release
  commit and tag by `semantic-release version`, then the publish
  scripts).
- `tools/publish-to-github.py` and `tools/publish-to-pypi.sh`: header
  comments (version source), no logic change.

Trial: `tools/release.sh` end to end in the throwaway clone with a bare
repository as `origin` (the watch step fails there, expectedly); the
bare repository must receive the release commit on `main` and the tag.
`release.yml` parsed with pyyaml; `bash -n` on the script. The real
end-to-end is the first release after merge (1.17.8), then a dry-run
dispatch from a branch, as with #80.

Two commits: workflow and script; docs and header comments.

### Step 4

Files:

- `tools/conventional-commits.py`: two subcommands. `level` reads a
  commit message on stdin (subject, optional body) and prints its bump
  level: type looked up in the map, `!` after the type or scope and a
  `BREAKING CHANGE:` footer mean major, an unknown type is an error.
  `gate --current X --next Y` reads the PR message on stdin, derives
  the pending level of `main` from the two versions, the incoming
  level from the message, and fails when the incoming level is above
  a non-empty pending level ("release X first"). Pure logic, no git,
  no subprocess: the workflow supplies the versions.
- `tests/unit/test_conventional_commits.py`: parametrized unit tests
  of `level` and of the gate verdict table (loaded with importlib,
  the file name has a hyphen). Mutation smoke-test on the comparison.
- `.github/workflows/merge-gate.yml`: on `pull_request` (opened,
  edited, synchronize, reopened). Checks out `origin/main` with the
  whole history and tags, `uv sync`, `semantic-release --noop version
  --print` for the next version, `changelog.py version` for the
  current one, then `gate` with the PR title and body passed through
  environment variables (never interpolated into the shell).
- `tools/release.sh`: before the confirmation, lists the pending
  commits with their levels and warns when a lower level precedes a
  higher one (the gate was bypassed); a warning, not a failure, since
  the merge cannot be undone and the operator decides at `[y/N]`.
- `doc/RELEASING.md`: a "Merge gate" paragraph (rule, staleness: the
  check reflects `main` at the PR's last event; `release.sh` warns).
- Repository ruleset on `main` via `gh api`, to decide: require the
  `conventional` and `gate` checks, and branches up to date before
  merging, so a stale gate cannot be merged past. Without it both
  checks are advisory. Reversible.

Trial: in the throwaway clone, the workflow's command sequence on a
detached `origin/main` (the tool must accept a detached HEAD under
`match = ".*"`); `level` on titles with `!` and a breaking footer;
`gate` on the four rows of the verdict table.

One commit at the end of the step, per the new rule.

### Step 4b, review fixes

Review comments: subcommand names of `conventional-commits.py` must be
descriptive at call sites; the pending-commits loop and the run-watch
loop of `release.sh` deserve their own scripts, so the shell script
stays high-level. The same applies to `changelog.py` (`version`,
`notes`) and to the TestPyPI retry loop of `smoke-test-install.sh`.

Files:

- `tools/conventional-commits.py`: subcommands renamed
  `print-bump-table`, `check-type-lists`, `print-level-of-message`,
  `gate-pr-against-main`. `tools/changelog.py`: `print-version`,
  `print-notes`. Call sites: `Makefile` (2), `merge-gate.yml`,
  `release.yml` (2), `smoke-test-install.sh`, `release.sh`, docstrings.
  The unit tests call functions, unchanged.
- `tools/release-plan.py` (new): prints the current version, the next
  one (`semantic-release --noop version --print`), the commits since
  the last tag with their levels (the tool's `parse_level`, loaded
  with importlib as the tests do) and the level-order warning; exits
  non-zero when nothing bumps. Replaces the "compute" and "list" steps
  of `release.sh`.
- `tools/wait-for.sh <condition> <args>` (new): explicit waiting for
  a condition, one function per condition, one shared polling loop.
  `workflow-run <workflow> <ref>` prints the run id once the run
  exists; `testpypi-version <version>` returns once the index serves
  it (JSON endpoint), so `smoke-test-install.sh` installs once instead
  of retrying the install. Replaces both retry loops.
- `set-ex.sh` renamed `init-tracing.sh` (same place, sourced by every
  tool script): `set -o pipefail` added, `set -u` tried and kept if the
  trials pass. It keeps only what needs the tracing hack: `echo`,
  `banner`, `banner2`, `step`. No retry helper there.
- `tools/release.sh`: preconditions, `release-plan.py`,
  `semantic-release version`, show, confirm, push, wait for the run,
  `gh run watch`.

Trial: `release.sh` abort path in the throwaway clone (plan and
warning shown, tree restored); `wait-for.sh workflow-run` against the
CI run that the step's push triggers, then `gh run watch`;
`wait-for.sh testpypi-version` on a published version;
`make smoke-test-wheel`; `make lint`, `make test`.

One commit at the end of the step.
