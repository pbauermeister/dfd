# 061 — Automate GitHub Releases from publish-to-pypi

**Date:** 2026-04-12
**Status:** PENDING

## Requirement

Create a script to publish GitHub Releases, integrated into the existing
PyPI publish workflow.

### 1. Release script

A script (`tools/publish-to-github.py`) that:

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

1. **Create `tools/publish-to-github.py`** — the release script:
   - Extract version from `CHANGES.md` (same logic as `setup.py`).
   - Extract the changelog entry for that version (lines between the first
     `## Version` heading and the next one) for the release body.
   - Build the distribution via `./tools/build.sh` (default). A
     `--no-rebuild` flag skips the build and reuses existing `dist/`
     artifacts (used by the Makefile when chaining after PyPI publish).
   - Tag: `git tag -f "v$VERSION"` then `git push origin "v$VERSION" --force`.
   - Release: use `gh release create` with `--notes` and attach the dist
     files. If the release already exists, delete it first
     (`gh release delete "v$VERSION" -y`) and re-create — simpler than
     trying to update assets.
   - Print a summary (version, tag, assets uploaded).

2. **Wire into Makefile** — chain in the `publish-to-pypi` target: call
   `tools/publish-to-github.py` after `tools/publish-to-pypi.sh` succeeds.
   The PyPI script stays unchanged (does exactly what its name says).

3. **Test** — tamper `CHANGES.md` to declare a temporary test version
   (e.g. `0.0.0-test`), run the script, verify the GH release is created
   (leave it for user review), then restore `CHANGES.md`. The user will
   manually run the script to publish version 1.16.7.

### Key decisions

- **Tag format:** `v1.16.7` (with `v` prefix) — standard convention.
- **Changelog extraction:** parse `CHANGES.md` between consecutive
  `## Version` headings to get the release notes body.
- **Dist artifacts:** default runs `./tools/build.sh` so the script works
  independently. `--no-rebuild` skips the build and reuses `dist/` — used
  by the Makefile when chaining after `publish-to-pypi.sh` which already
  built everything.
- **Idempotency:** delete-then-create is simpler and safer than
  update-in-place for GH releases with attached assets.
- **Branch check:** by default, the script enforces that the current branch
  is `main` and the working tree is clean. A `--no-check` flag disables
  the branch check entirely (for backfilling from detached HEAD at older
  commits). The script is written in Python using `argparse` for option
  parsing.
