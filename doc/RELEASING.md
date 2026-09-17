# Releasing

Releases are made by the `Release` GitHub Actions workflow
(`.github/workflows/release.yml`), triggered by hand. It publishes the
version found in `CHANGES.md` to PyPI and GitHub from a single build,
after the full CI suite passes on the released commit.

## Procedure

1. Merge the PRs of the release into `main`. The top entry of
   `CHANGES.md` (`## Version X.Y.Z:`) is the version to release; it
   must have no tag yet and be on neither PyPI nor TestPyPI.
2. On a clean checkout of `main`, up to date with `origin/main`:

   ```
   make release
   ```

   This dispatches the workflow and watches it. The Actions tab of the
   repository offers the same "Run workflow" button.

3. When the run is green: `vX.Y.Z` is tagged, the GitHub release is
   created with the changelog entry as notes, and the wheel and sdist
   are on PyPI.

## What the workflow does

Jobs run in sequence; each one needs the previous one.

| Job              | What                                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| `ci`             | Calls `ci.yml`: tests and lint on every supported Python, wheel smoke test                            |
| `preflight`      | Ref is `main`; version read from `CHANGES.md`; no tag `vX.Y.Z`; version absent from PyPI and TestPyPI |
| `build`          | `uv build`, wheel smoke test in a fresh venv, upload `dist/` as a run artifact                        |
| `testpypi`       | Upload to TestPyPI, install from there in a fresh venv, smoke test                                    |
| `pypi`           | Upload to PyPI                                                                                        |
| `github-release` | `gh release create` with the changelog notes and the same files; this creates the tag                 |

Uploads use PyPI trusted publishing (OpenID Connect): the workflow
proves its identity to the index, and no API token exists anywhere.
The `testpypi` and `pypi` jobs run in GitHub environments of the same
names, which the trusted publisher registrations are pinned to.

## When a run fails

Nothing irreversible happens before the `pypi` job. Recovery depends
on where the run stopped:

- **Before the TestPyPI upload** (CI, preflight, build): fix, merge,
  run `make release` again.
- **At or after the TestPyPI smoke test, before PyPI:** the version is
  now on TestPyPI, which refuses re-uploads, so preflight will refuse
  it. Fix, bump to `X.Y.Z.post1` in `CHANGES.md`, release again.
- **At `pypi` or `github-release`, for a transient reason** (network,
  index lag): use "Re-run failed jobs" on the run's page. It reuses the
  run's commit and `dist/` artifact, so the same files get published.
- **At `github-release`, for a real reason:** PyPI already has the
  files. Finish locally: `uv build` on the released commit, then
  `make publish-to-gh`.

## Testing a change to the workflow

Once a change to `release.yml` is on `main`, it can be rehearsed from a
branch: give `CHANGES.md` a throwaway `X.Y.Z.devN` heading on the
branch, and dispatch with the `dry_run` input checked:

```
gh workflow run release.yml --ref <branch> -f dry_run=true
```

A dry run accepts any ref and stops after the TestPyPI rehearsal
(`.devN` versions on TestPyPI are harmless). Before the workflow file
is on `main`, GitHub does not let it be dispatched at all.

## Local fallback

If GitHub Actions is unavailable, the same steps run locally, in the
same order, with API tokens in `.token-test` and `.token` (gitignored):

```
make publish-to-pypi   # build, wheel smoke, TestPyPI, its smoke, PyPI
make publish-to-gh     # tag and GitHub release, attaching that dist/
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
