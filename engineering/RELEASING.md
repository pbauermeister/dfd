# Releasing

The version, the `CHANGES.md` entry, the release commit and the tag are
derived from the conventional commits merged since the last release.
`make release` makes them locally and pushes the tag, which triggers the
`Release` GitHub Actions workflow (`.github/workflows/release.yml`). The
workflow publishes to PyPI and GitHub from a single build, after the
full CI suite passes on the tagged commit. `recipes/release.sh` is the
code twin of this page.

## Conventional commits

Every commit message and every PR title has the form
`<type>[(scope)]!: <description>`. The `commit-msg` hook installed by
`make require` checks commits; the `PR title` workflow checks PR
titles. Since PRs are squash-merged with the PR title as the commit
subject, the PR title is the line that reaches `main`: it is the
changelog entry of the PR and it decides the version bump.

| Type                                               | Bump  |
| -------------------------------------------------- | ----- |
| `feat`                                             | minor |
| `fix`, `perf`, `refactor`, `docs`, `test`, `build` | patch |
| `chore`, `ci`, `style`                             | none  |
| any type with `!`, or a `BREAKING CHANGE:` footer  | major |

`make help-cc` prints this table from `pyproject.toml`
(`[tool.semantic_release]`), the single source of truth. The version is
never edited by hand: `make release` derives it from the commits merged
since the last release. Types that bump nothing change nothing the user
installs; such commits wait for the next release and appear in its
changelog entry. This holds because the project is a tool installed on
the user's computer; for a service, CI changes can have real if
invisible effects that deserve a release.

A PR's type must be at the highest bump level among its commits and
name the PR's purpose: review the title before merging.

### Bookkeeping commits

A commit or a PR confined to paths that ship nothing is bookkeeping
and carries a type that bumps nothing, `chore` as a rule: `TODO.md`,
`CLAUDE.md`, `.claude/`, `devlog/`, `discussions/`, `engineering/`,
`templates/`. The list is `bookkeeping_paths` in `pyproject.toml`
(`[tool.conventional-commits]`, next to the bump map); the
`commit-msg` hook refuses a bumping type on such a commit, and
`ci.yml` skips a push or a PR confined to them (`paths-ignore` on its
`push` and `pull_request` triggers, kept equal to the list by `make
lint`; a PR is judged on all its files, so one shipping file runs the
suite; the merge gate and the PR-title check, required by the ruleset,
run on every event). `doc/` and the root `README.md` are
the product's manual and keep `docs` (patch). A bumping bookkeeping
commit on `main` forces an empty release before the next higher-level
PR (1.17.10, a `docs:` on `TODO.md`).

### Merge gate

Unreleased changes on `main` never span two levels, so that every
level is closed before the next one opens: the `Merge gate` check
(`.github/workflows/merge-gate.yml`) blocks a PR whose type would raise
the pending level of `main`, with the message "release X.Y.Z first".
Merges at or below the pending level pass; a `main` whose pending
commits bump nothing counts as empty. The check reflects `main` at the
PR's last event; the branch ruleset on `main` requires it to be green
and the branch to be up to date, and `make release` lists the pending
commits with their levels and warns if the order was broken.

## Procedure

1. Merge the PRs of the release into `main`. `make show-release-plan`
   prints the version they add up to and the commits with their bump
   levels; it fails when nothing bumps.
2. On a clean checkout of `main`, up to date with `origin/main`:

   ```
   make release
   ```

   This makes the release commit (version in `pyproject.toml` and
   `uv.lock`, generated `CHANGES.md` entry) and the tag `vX.Y.Z`
   locally, shows both, and asks before pushing. Answering no removes
   them again. Answering yes pushes `main` and the tag, then watches
   the workflow run the tag triggers.

3. When the run is green: the GitHub release exists on the tag with
   the changelog entry as notes, and the wheel and sdist are on PyPI.

## What the workflow does

Jobs run in sequence; each one needs the previous one.

| Job              | What                                                                                               |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| `ci`             | Calls `ci.yml`: tests and lint on every supported Python, wheel smoke test                         |
| `preflight`      | The tag names the `pyproject.toml` version and is on `main`; version absent from PyPI and TestPyPI |
| `build`          | `uv build`, wheel smoke test in a fresh venv, upload `dist/` as a run artifact                     |
| `testpypi`       | Upload to TestPyPI, install from there in a fresh venv, smoke test                                 |
| `pypi`           | Upload to PyPI                                                                                     |
| `github-release` | `gh release create` on the tag with the changelog notes and the same files                         |

Uploads use PyPI trusted publishing (OpenID Connect): the workflow
proves its identity to the index, and no API token exists anywhere.
The `testpypi` and `pypi` jobs run in GitHub environments of the same
names, which the trusted publisher registrations are pinned to.

## When a run fails

The tag and the release commit are on `origin` once `make release` has
pushed, and a version is never reused. Recovery is always forward: fix
on a branch, merge, `make release` again for the next version. A tag
without a GitHub release marks a failed attempt; it does no harm and
may be deleted (`git push origin --delete vX.Y.Z`, then locally).

- **At `pypi` or `github-release`, for a transient reason** (network,
  index lag): use "Re-run failed jobs" on the run's page. It reuses the
  run's commit and `dist/` artifact, so the same files get published.
- **At `github-release`, for a real reason:** PyPI already has the
  files. Finish locally: `uv build` on the tagged commit, then
  `make publish-to-gh`.

## Testing a change to the workflow

Once a change to `release.yml` is on `main`, it can be rehearsed from a
branch: set a throwaway `X.Y.Z.devN` version in `pyproject.toml` on the
branch, push, and dispatch the workflow by hand:

```
gh workflow run release.yml --ref <branch>
```

A manual dispatch is always a dry run: any ref, no tag checks, and it
stops after the TestPyPI rehearsal (`.devN` versions on TestPyPI are
harmless). Before the workflow file is on `main`, GitHub does not let it
be dispatched at all.

## Local fallback

If GitHub Actions is unavailable, the same steps run locally, in the
same order, with API tokens in `.token-test` and `.token` (gitignored):

```
uv run semantic-release version --no-push --no-vcs-release
git push origin main vX.Y.Z   # the workflow will fail or be skipped
make publish-to-pypi          # build, wheel smoke, TestPyPI, its smoke, PyPI
make publish-to-gh            # GitHub release on the tag, attaching that dist/
```

`make publish-to-gh` attaches what `make publish-to-pypi` just built
and uploaded; it does not rebuild.

## One-time setup: trusted publishers

Done once by the maintainer, on each index, under the project's
"Publishing" settings (`https://pypi.org/manage/project/data-flow-diagram/settings/publishing/`
and the same on `test.pypi.org`). Add a GitHub publisher with:

| Field            | Value                                           |
| ---------------- | ----------------------------------------------- |
| Owner            | `pbauermeister`                                 |
| Repository       | `dfd`                                           |
| Workflow name    | `release.yml`                                   |
| Environment name | `pypi` on pypi.org, `testpypi` on test.pypi.org |

The GitHub environments themselves already exist in the repository
(Settings → Environments); they carry no protection rules.
