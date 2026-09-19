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
  `tools/cc.py` reads that map for both the gate and `make help-cc`.
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
   group, `make version-show`, `make help-cc` via `tools/cc.py`.
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
   `tools/cc.py`; the same assertion in release preflight.
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
- `tools/cc.py` (new): `table` subcommand rendering the bump map.
  `Makefile`: `help-cc`, `version-show`.
- `uv.lock` updated by `uv sync`.

Commands: `uv sync`, `make format`, `make lint`, `make test`,
`make version-show`, `make help-cc`, `uv build` (wheel takes the
static version). Tag `v0.0.0.dev1` deleted locally and on `origin`
(irreversible; April leftover, referenced by no release).

Two commits: configuration and shim removal; tools and Makefile.
`release.yml` keeps working until step 3 (`changelog.py version`
still prints the latest version).
