# 061 — Automate GitHub Releases from publish-to-pypi

**Date:** 2026-04-12
**Status:** PENDING

## Requirement

Create a script to publish GitHub Releases, integrated into the existing
PyPI publish workflow.

### 1. Release script

A script (`tools/publish-to-github.sh`) that:

- Reads the version from `CHANGES.md` (first `## Version X.Y.Z:` line).
- Tags the repo at the current HEAD according to the version.
- Creates a GitHub Release for that tag, including:
  - Source archive (tarball)
  - Wheel (`.whl`)
- Is idempotent on re-run:
  - Tag is repositioned to current HEAD.
  - GitHub Release is updated (or deleted and re-created).

### 2. Integration with publish-to-pypi

The Makefile target `publish-to-pypi` calls the new script **after** a
successful PyPI upload. PyPI enforces version uniqueness, so the GH release
is a secondary artifact that follows the PyPI publish.

### 3. Branch positioning

The script applies on the current branch. The user is responsible for being
on the correct branch (typically `main` after merging). The script does not
check or enforce branch.

### 4. Backfill

After implementation, the user will run the script to publish the current
version (1.16.7) as the latest GitHub Release.

## Design

### Implementation steps

1. **Create `tools/publish-to-github.sh`** — the release script:
   - Extract version from `CHANGES.md` (same logic as `setup.py`).
   - Extract the changelog entry for that version (lines between the first
     `## Version` heading and the next one) for the release body.
   - Build the distribution (`python3 setup.py sdist bdist_wheel` or
     equivalent) if `dist/` artifacts are not already present.
   - Tag: `git tag -f "v$VERSION"` then `git push origin "v$VERSION" --force`.
   - Release: use `gh release create` with `--notes` and attach the dist
     files. If the release already exists, delete it first
     (`gh release delete "v$VERSION" -y`) and re-create — simpler than
     trying to update assets.
   - Print a summary (version, tag, assets uploaded).

2. **Wire into Makefile** — chain in the `publish-to-pypi` target: call
   `tools/publish-to-github.sh` after `tools/publish-to-pypi.sh` succeeds.
   The PyPI script stays unchanged (does exactly what its name says).

3. **Test** — tamper `CHANGES.md` to declare a temporary test version
   (e.g. `0.0.0-test`), run the script, verify the GH release is created
   (leave it for user review), then restore `CHANGES.md`. The user will
   manually run the script to publish version 1.16.7.

### Key decisions

- **Tag format:** `v1.16.7` (with `v` prefix) — standard convention.
- **Changelog extraction:** parse `CHANGES.md` between consecutive
  `## Version` headings to get the release notes body.
- **Dist artifacts:** run `./tools/build.sh` so the script works
  independently (for testing and backfilling), not just after PyPI publish.
- **Idempotency:** delete-then-create is simpler and safer than
  update-in-place for GH releases with attached assets.
- **Branch check:** `publish-to-github.sh` enforces that the current branch
  is `main` (and the working tree is clean). Publishing from a feature
  branch is almost always a mistake, and the cost of the guard is near zero
  compared to the cost of a wrong release. Since we are only backfilling
  the latest version, there is no need to run from other branches.
