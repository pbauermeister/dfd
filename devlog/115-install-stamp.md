# 115 — `make install` stamps the version with the branch and revision

Date: 2026-09-24
Status: ONGOING
Issue: #115 · PR: #116 · Branch: `build/115-install-stamp`
Task nature: change
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 25 (removed in the first commit), raised at the delivery of
#104. Last of the batch of five build-related tasks of 2026-09-24
(24, 26, 18, 19, 25). Stacked on #113 (PR #114) for the `TODO.md`
neighbourhood; retargeted when it merges. Spiked before the go in an
isolated uv tool directory: a copy of the tree with the version
rewritten builds and installs, `--version` prints the label, a stale
`uv.lock` does not block a tool install.

### 1.2 Goal

`make install` installs the working tree as a uv tool whose version
is `X.Y.Z+<branch>.g<hash>[.dirty]`; the checkout, `make release` and
`release.yml` keep the bare version.

### 1.3 Design decisions

| #   | Decision                                                                                                                                                | Basis                                                                                                                           | Alternatives considered                                                                           |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 1   | Local label only, no `.devN`: `X.Y.Z+<branch>.g<hash>[.dirty]`                                                                                          | user (the go): the tree is X.Y.Z plus changes and sorts after it; `.dev` sorts before and needs the next version                | `X.Y.Z.devN+…` as the TODO wrote                                                                  |
| 2   | A scratch copy stamped and installed; the checkout untouched                                                                                            | user (the go), spiked                                                                                                           | setuptools-scm (replaces the pyproject version as source of truth, which semantic-release writes) |
| 3   | The copy is `git ls-files --cached --others --exclude-standard` through `tar`: tracked and untracked, `.gitignore` respected, deleted files skipped     | rule: the tree as it is, not the last commit (`git archive` drops uncommitted changes)                                          | `rsync` of the directory with an exclude list (a second copy of `.gitignore`)                     |
| 4   | The label computed by a tool (`tools/print-dev-version.py`, unit-tested), the recipe sequences copy, sed, install                                       | rule: CONVENTIONS.md "Script levels", no computation in a recipe                                                                | Everything in the recipe                                                                          |
| 5   | `dirty` from `git status --porcelain --untracked-files=no`: tracked changes only                                                                        | taste: an untracked scratch file is not a modified tree                                                                         | Untracked files count as dirty                                                                    |
| 6   | PR type `build:` (patch)                                                                                                                                | user (the go): a recipe is tooling, not bookkeeping                                                                             | `chore:` under #107's rule                                                                        |
| 7   | The simple form stays although a tree carrying a bumping commit prints the base it builds on, not the version it heads to                               | user (review, 2026-09-25): the stamp only tells a dev install apart; the hash names the base; semver compliance is not required | `next.dev0+label` when something bumps (from the release plan)                                    |
| 8   | `make uninstall` removes the tool whatever installed it: uv tool, pipx, pip in the current `python3`, each asked in turn; nothing found is not an error | user (review): after a dev install, the official release is reinstalled                                                         | `uv tool uninstall` only (the former target)                                                      |

### 1.4 Acceptance criteria

1. `make install` from a branch installs a tool whose `--version`
   carries the branch and the hash; `pyproject.toml` unchanged after.
2. `make uninstall` removes a uv tool, a pipx and a pip install, and
   says so when nothing is installed.
3. `tools/print-dev-version.py` unit-tested: separators to dots,
   runs collapsed, detached head, dirty suffix.
4. `make format lint test` green.

Approved: 2026-09-24

## 2. Execution

### 2.1 Account

- First commit: TODO 25 removed, filed as #115.
- `2925acd` build: the tool, the recipe, the Makefile target, a line
  in CONVENTIONS.md "Constraints", six unit cases. `ruff` refused a
  four-parameter test (PLR0917): keyword-only parameters, which
  pytest passes anyway.
- This devlog.
- Review loop (2026-09-25): `recipes/uninstall.sh` and the `uninstall`
  target reworded; decisions 7 and 8. Tried against three isolated
  installs (uv tool dir, `PIPX_HOME`, a seeded venv on the PATH): all
  three removed in one run, "nothing installed" on the second, the
  user's own install untouched; the closing PATH check warned about it,
  as it should for that isolated run.

## 3. Delivery

### 3.1 Try it

```bash
make install
data-flow-diagram --version   # 1.18.0+build.115.install.stamp.g<hash>
uv tool list | grep data-flow-diagram
make uninstall                # then: uv tool install data-flow-diagram
```

The user's current tool (1.17.9) is replaced; `make install` on
`main` after the merge gives `1.18.0+main.g<hash>` until the next
release, when `uv tool install data-flow-diagram` puts the bare
release back.

Tried: pending

### 3.2 Test report

1. The recipe run with `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR` in the job
   scratch directory (the user's tool untouched): `data-flow-diagram
1.18.0+build.115.install.stamp.g410ccef.dirty` (dirty: the recipe
   was untracked at that point); `pyproject.toml` still `1.18.0`
   (criterion 1).
2. Six cases green (criterion 2).
3. 125 pytest, 95 NR fixtures, lint and format clean (criterion 3).
4. The uninstall recipe run against isolated uv tool, pipx and pip
   installs: three "uninstalled" lines, then "nothing installed as
   data-flow-diagram" on a second run (criterion 4).

### 3.3 Verdict

**Recommendation:** accept

- The label is proven by an install; the release path is untouched
  (`recipes/release.sh`, `release.yml` read `pyproject.toml` as
  before).

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                   | Agent | User |
| --- | ------------------------------------------------------------------------------------------------------- | ----- | ---- |
| 1   | Process and template fit: fast track with a Try it stop, since the install touches the user's machine   | well  |      |
| 2   | The spike before the go settled the mechanism in one round; the TODO's `.devN` form was corrected by it | well  |      |

Process: 1 round before the go; no loop; rework after the go: none.

Closed: pending

### 4.2 Rule trace

| Source                                     | Rule                                                       | Verb (applied / created) |
| ------------------------------------------ | ---------------------------------------------------------- | ------------------------ |
| `engineering/CONVENTIONS.md` Script levels | Computation in a tool, sequencing in a recipe              | applied                  |
| `engineering/CONVENTIONS.md` Constraints   | `make install` stamps a copy, bare version in the checkout | created (sentence added) |
