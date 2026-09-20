# 090 — Script levels: naming rule, `runbooks/` and `tools/`

Date: 2026-09-19
Status: DONE

## Requirement

From TODO item 11 (conclusions of #88). Issue #90.

Codify in `doc/CONVENTIONS.md` the naming rule for scripts and Makefile
targets:

- verb-first for a single action read as a command (`update-docs.py`);
- topic-first for a family of two or more, grouped in listings and
  completion (`nr-test`, `require-system`);
- a noun with verb-first subcommands for a Python family in one program
  (`changelog.py print-notes`);
- object-first with no family behind it is the case to avoid.

Then apply the rule and the script levels of #88 (entry points /
runbooks / tools / prelude):

- Split the folders so that the level is an address: `runbooks/` for the
  orchestrators, `tools/` for the tools. Update every path.
- Doc scripts: become a `doc-` family or fold into one noun program.
- Audit the Makefile targets against the rule.
- Prelude `init-tracing.sh`: sourced mechanics only; decide its folder
  and whether it gains `set -u`.

Decided in discussion (2026-09-20):

- **Calling directory.** Every script is called from the project's
  home (the repository root): paths inside scripts are relative to it,
  the Makefile is the normal caller. Codified in `doc/CONVENTIONS.md`.
- **The renumberer stays a distinct script.** Measured against the
  existing tools, none fits (2026-09-20); it will become a standalone
  project: `discussions/md-titles-renumberer-tool.md`, TODO item 13.

Every rename is mechanical and inventory-driven: this file holds the
tables so the implementation can run unattended.

## Design

Revised in step 5: `runbooks/` became `recipes/` (see Design revision
below); the tables keep the step 1–4 names.

### Inventory and target

| Current                           | Level   | Target                            |
| --------------------------------- | ------- | --------------------------------- |
| `tools/release.sh`                | runbook | `runbooks/release.sh`             |
| `tools/publish-to-pypi.sh`        | runbook | `runbooks/publish-to-pypi.sh`     |
| `tools/publish-to-testpypi.sh`    | runbook | `runbooks/publish-to-testpypi.sh` |
| `tools/build.sh`                  | runbook | `runbooks/build.sh`               |
| `tools/lint.sh`                   | runbook | `runbooks/lint.sh`                |
| `tools/clean.sh`                  | runbook | `runbooks/clean.sh`               |
| `tools/make-doc.sh`               | runbook | `runbooks/make-doc.sh`            |
| `init-tracing.sh` (repo root)     | prelude | `tools/init-tracing.sh`           |
| `tools/changelog.py`              | tool    | unchanged                         |
| `tools/conventional-commits.py`   | tool    | unchanged                         |
| `tools/check-python-versions.py`  | tool    | unchanged                         |
| `tools/print-release-plan.py`     | tool    | unchanged                         |
| `tools/publish-to-github.py`      | tool    | unchanged                         |
| `tools/test-installation.sh`      | tool    | unchanged                         |
| `tools/wait-for.sh`               | tool    | unchanged                         |
| `tools/update-docs.py`            | tool    | `tools/doc-update-sections.py`    |
| `tools/gen-style-tables.py`       | tool    | `tools/doc-print-style-table.py`  |
| `tools/doc-renumber-md-titles.py` | tool    | unchanged (already `doc-` family) |

Decisions behind the table:

- **Prelude in `tools/`.** It is sourced by five runbooks and one tool
  (`test-installation.sh`), so it belongs to neither level's folder by
  use; it is mechanics below the tools, like plumbing, and the root
  stays uncluttered. Sourcing line becomes `. ./tools/init-tracing.sh`
  (scripts run from the repository root; no change there).
- **A `doc-` family of distinct tools**, topic-first, since the
  renumberer stays its own script (Pascal, 2026-09-20): `doc-` is the
  family, then the verb: `doc-update-sections.py` (the `<!-- AUTO -->`
  markers + prettier), `doc-print-style-table.py readme|syntax`,
  `doc-renumber-md-titles.py` (name kept). `make-doc.sh` stays a
  runbook (sequence of commands, no logic).
- **Runbook contents unchanged** except the sourcing path. `lint.sh`
  and `clean.sh` do not source the prelude today; left as they are.

### Makefile audit

Names, against the rule. One rename:

| Target                      | Rule                   | Verdict                                                                                                                                 |
| --------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `venv`, `venv-activate`     | family, topic-first    | unchanged                                                                                                                               |
| `require`, `require-system` | family, topic-first    | unchanged                                                                                                                               |
| `test`, `test-matrix`       | family, topic-first    | unchanged                                                                                                                               |
| `nr-review/regenerate/test` | family, topic-first    | unchanged                                                                                                                               |
| `publish-to-*`              | family, topic-first    | unchanged (`-gh` vs `-github.py`: kept)                                                                                                 |
| `help`, `help-cc`           | family, topic-first    | unchanged                                                                                                                               |
| `doc`, `readme`             | family, one member off | **`readme` → `doc-sections`**                                                                                                           |
| single actions              | verb-first             | unchanged (`format`, `lint`, `clean`, `install`, `uninstall`, `release`, `smoke-test-wheel`, `show-release-plan`, `black` alias, `all`) |

`readme` is stale since #71: it regenerates sections of `README.md`,
`doc/README.md` and `doc/SYNTAX.md`. Mentions to update: `Makefile`,
`tests/README.md`; `CHANGES.md` and old devlogs are history, untouched.

Recipes, from the folder split and the `doc-` family. Ten lines change;
the five recipes calling tools that stay in `tools/` do not:

| Target                | Line                             | Change                                 |
| --------------------- | -------------------------------- | -------------------------------------- |
| `lint`                | `uv run ./tools/lint.sh`         | `./runbooks/lint.sh`                   |
| `readme`              | target name                      | `doc-sections`                         |
| `readme`              | `uv run ./tools/update-docs.py`  | `./tools/doc-update-sections.py`       |
| `doc`                 | `doc: readme`                    | `doc: doc-sections`                    |
| `doc`                 | `uv run ./tools/make-doc.sh`     | `./runbooks/make-doc.sh`               |
| `release`             | `./tools/release.sh`             | `./runbooks/release.sh`                |
| `publish-to-testpypi` | `./tools/publish-to-testpypi.sh` | `./runbooks/publish-to-testpypi.sh`    |
| `publish-to-pypi`     | `./tools/publish-to-pypi.sh`     | `./runbooks/publish-to-pypi.sh`        |
| `clean`               | `./tools/clean.sh`               | `./runbooks/clean.sh`                  |
| `help`                | none                             | the help text follows the target names |

Unchanged recipes: `lint` (`check-python-versions.py`,
`conventional-commits.py`), `smoke-test-wheel` (`test-installation.sh`),
`show-release-plan`, `help-cc`, `publish-to-gh`.

### Path churn (exhaustive, from grep)

| File                                      | Change                                                                              |
| ----------------------------------------- | ----------------------------------------------------------------------------------- |
| `Makefile`                                | 10 lines, listed in the Makefile audit                                              |
| `.github/workflows/release.yml`           | none (`changelog.py`, `test-installation.sh` stay in `tools/`)                      |
| `.github/workflows/merge-gate.yml`        | none (`conventional-commits.py` stays)                                              |
| `pyproject.toml`                          | 1 comment: `runbooks/release.sh`                                                    |
| `runbooks/*.sh` (5 files)                 | sourcing line `. ./tools/init-tracing.sh`                                           |
| `tools/test-installation.sh`              | sourcing line                                                                       |
| `runbooks/release.sh`                     | calls `tools/print-release-plan.py`, `changelog.py`, `wait-for.sh`: unchanged paths |
| `runbooks/publish-to-pypi.sh`             | `./runbooks/publish-to-testpypi.sh`                                                 |
| `runbooks/publish-to-testpypi.sh`         | `./runbooks/build.sh`                                                               |
| `tools/doc-update-sections.py`            | subprocess path of `doc-print-style-table.py`                                       |
| `tools/init-tracing.sh`                   | header comment; drop unused `_here_`; `set -u`                                      |
| `tests/test_doc_sync.py`                  | generator path, docstring                                                           |
| `tests/unit/test_conventional_commits.py` | none                                                                                |
| `doc/CONVENTIONS.md`                      | "Tooling scripts" section rewritten                                                 |
| `doc/RELEASING.md`                        | one line naming `runbooks/release.sh` as its code twin                              |
| `TODO.md`                                 | item 11 → DONE (#90)                                                                |
| old devlogs, `CHANGES.md`                 | history, untouched                                                                  |

### Prelude and `set -u`

#88 planned `set -u` "kept if the trials pass"; it was not added. Audit
of the sourcing scripts: every `$VAR` is assigned before use
(`${1:?usage}` guards the positional ones; `ANSWER` comes from `read`).
Trials: run `build.sh`, `make-doc.sh`, `test-installation.sh
from-wheel`; `release.sh` and `publish-to-*.sh` cannot be trial-run
(they publish), so they get `bash -n` and the static audit only.

## Action plan

Four steps, one pushed commit each, `make format lint test` before each
commit. Steps 1–2 and 3–4 share one attended/unattended gate each. No
irreversible action: every rename is a `git mv`, no publishing script
is run.

**Step 1 — Conventions** (`docs:`)

Files: `doc/CONVENTIONS.md`, `doc/RELEASING.md`.

1. In "Tooling scripts", replace the first sentence's `tools/` and
   `tests/` by `runbooks/`, `tools/` and `tests/`.
2. Replace the "Script levels" paragraph by three paragraphs:

   > **Script levels.** Git's porcelain and plumbing is the model.
   > Makefile targets are the entry points. Runbooks (`runbooks/`:
   > `release.sh`, `publish-to-*.sh`, `build.sh`, `lint.sh`, `clean.sh`,
   > `make-doc.sh`) are orchestrators: named steps, one command each,
   > guards only, no loops or computation; `doc/RELEASING.md` is the
   > prose twin of `runbooks/release.sh`. Tools (`tools/`) do one
   > concern with explicit arguments, so that every call site is
   > self-explanatory. The prelude (`tools/init-tracing.sh`) holds
   > sourced mechanics only. Logic that appears in a runbook moves
   > down into a tool. The folder is the level's address.
   >
   > **Naming.** A single action is verb-first, read as a command
   > (`tools/print-release-plan.py`, `tools/test-installation.sh
from-wheel`, `make smoke-test-wheel`). A family of two or more is
   > topic-first, so that listings and completion group it (`nr-test`,
   > `require-system`, `tools/doc-update-sections.py`). A Python family
   > sharing its data is one program, a noun with verb-first
   > subcommands (`changelog.py print-notes`, `conventional-commits.py
gate-pr-against-main`). Object-first with no family behind it is
   > the case to avoid.
   >
   > **Calling directory.** Every script is called from the project's
   > home, the repository root: paths inside scripts are relative to
   > it, the prelude is sourced as `. ./tools/init-tracing.sh`, and
   > the Makefile is the normal caller. A script never `cd`s to find
   > itself.

3. `doc/RELEASING.md`, first paragraph, after the `make release`
   sentence: "`runbooks/release.sh` is the code twin of this page."
4. Commit: `docs: CONVENTIONS, script levels, naming and calling
directory`.

**Step 2 — Folder split** (`refactor:`)

Files: the 7 runbooks and the prelude (inventory table), `Makefile`
(recipe table, the 7 `runbooks/` lines), `pyproject.toml`,
`tools/test-installation.sh`, `runbooks/publish-to-pypi.sh`,
`runbooks/publish-to-testpypi.sh`, `tools/init-tracing.sh` header.

1. `mkdir runbooks`; `git mv` per the inventory table (7 runbooks,
   prelude to `tools/`).
2. Sourcing lines (6 files): `. ./init-tracing.sh` →
   `. ./tools/init-tracing.sh`.
3. Cross-calls: `publish-to-pypi.sh` → `./runbooks/publish-to-testpypi.sh`;
   `publish-to-testpypi.sh` → `./runbooks/build.sh`.
4. `Makefile`: the 7 `runbooks/` lines of the recipe table.
5. `pyproject.toml` comment: `runbooks/release.sh`.
6. Prelude header: "Shell prelude for the runbooks and tools ...
   `. ./tools/init-tracing.sh`".
7. Verify: `for f in runbooks/*.sh tools/*.sh; do bash -n $f; done`;
   `make lint test doc clean`; `make smoke-test-wheel`;
   `grep -rn 'tools/\(release\|publish-to-[pt]\|build\|lint\|clean\|make-doc\)\.sh\|\./init-tracing' --exclude-dir=devlog --exclude-dir=.venv --exclude=CHANGES.md .`
   is empty.
8. Commit: `refactor: split runbooks/ from tools/, prelude in tools/`.

**Step 3 — `doc-` family** (`refactor:`)

Files: `tools/update-docs.py` → `tools/doc-update-sections.py`,
`tools/gen-style-tables.py` → `tools/doc-print-style-table.py`,
`Makefile` (recipe table, the 3 `doc` lines), `tests/test_doc_sync.py`,
`tests/README.md`.

1. `git mv` the two tools.
2. `doc-update-sections.py`: docstring of `generate_style_table` and the
   subprocess path → `doc-print-style-table.py`.
3. `doc-print-style-table.py`: usage line in the docstring.
4. `Makefile`: `readme` → `doc-sections` (name and help text),
   `doc: doc-sections`, the `doc-update-sections.py` call.
5. `tests/test_doc_sync.py`: `GENERATOR` path and the docstring;
   `tests/README.md`: `make readme` → `make doc-sections`.
6. Verify: `make doc` then `git status` shows no change under `doc/`
   or `README.md`; `make test`;
   `grep -rn 'readme\|update-docs\|gen-style' Makefile tools tests`
   shows only `README.md` file names and the `readme|syntax` argument.
7. Commit: `refactor: doc- family of tools, target readme → doc-sections`.

**Step 4 — Prelude, closing** (`refactor:`)

Files: `tools/init-tracing.sh`, `TODO.md`, this devlog.

1. Prelude: drop `_here_=$(pwd)`; `set +x -e -u -o pipefail` on the
   first `set` line.
2. Trials (Prelude and `set -u`): `./runbooks/build.sh`,
   `./runbooks/make-doc.sh`, `make smoke-test-wheel`; `bash -n` on the
   three publishing runbooks and re-read them for unguarded `$VAR`.
3. `TODO.md` item 11: strike through, `— DONE (#90)`, keep the body.
4. Devlog status DONE, Outcome section (findings, if any).
5. Commit: `refactor: prelude with set -u; TODO item 11 done`.
6. `gh pr ready 91`; update the PR body with the four steps as a
   checklist (`gh api ... -X PATCH -f body=`, not `gh pr edit`).

**Step 5 — `recipes/`** (`refactor:`, added 2026-09-20 after the
Design revision)

Files: `runbooks/` → `recipes/`, `make-doc.sh` → `doc.sh`, `build.sh`
removed, `require-system.sh` new, `Makefile`, the two publish recipes,
`doc/CONVENTIONS.md`, `doc/RELEASING.md`, `pyproject.toml`, prelude
header, discussion file.

1. `git mv runbooks recipes`; `git mv recipes/make-doc.sh recipes/doc.sh`;
   `git rm recipes/build.sh`.
2. `Makefile`: `build: require clean lint test doc` in the Local group;
   `publish-to-testpypi: build`; `publish-to-pypi: publish-to-testpypi`;
   `require-system` body → `recipes/require-system.sh`; paths.
3. Publish recipes drop their call to the previous step (now a
   prerequisite); header comments say so.
4. Every recipe starts with a purpose comment (`clean`, `lint`, `doc`
   had none).
5. Conventions "Script levels" rewritten around the recipe rule; the
   other mentions of `runbooks/` follow.
6. Verify: `bash -n`; `make -n publish-to-pypi` shows the chain build →
   testpypi → pypi; `make build`; `make smoke-test-wheel`; sweep
   `grep -rn runbooks` finds only history.
7. Commit: `refactor: recipes/ replaces runbooks/, build target,
require-system recipe`; PR title and body updated.

PR title stays `refactor: ...` (highest level among the commits:
`refactor`, patch).

## Design revision: `recipes/`, not `runbooks/`

After step 4 (Pascal, 2026-09-20): `build.sh` was one `make` call, the
only script calling make, an upward dependency; and the Makefile was
missing the `build` target a developer expects before `make install`.
Turning `build` into a target with prerequisites showed the real shape
of the folder: of seven scripts only `release.sh` is a scenario a
reader runs from top to bottom; `lint.sh` is three of the five lint
commands, `make-doc.sh` the second half of `doc`, the publish scripts
lean on Makefile prerequisites. The Makefile holds the sequences,
because prerequisites are the make-native way to write them. The
scripts are recipe bodies, in make's own word.

Rule adopted (codified in `doc/CONVENTIONS.md`): `recipes/<target>.sh`
is the body of one target, named after it, called by make only, no
arguments; sequencing, guards and per-file loops, no computation;
calls go down only (Makefile → recipes → tools), a recipe never calls
make nor another recipe, so a sequence of targets is a prerequisite
list. Consequences: `build.sh` becomes the `build` target;
`publish-to-pypi` gets `publish-to-testpypi` as prerequisite instead
of calling it; `require-system`'s OS `case` moves to a recipe;
`test-matrix` stays in the Makefile because its loop body is a make
call; the loops of `doc.sh` are per-file sequencing, allowed. Every
recipe starts with a purpose comment.

## Outcome

Four steps, four commits, run unattended in one pass (2026-09-20).
Findings:

- The plan held: no step needed a decision. The one thing the churn
  table missed, two `make readme` mentions inside
  `tests/test_doc_sync.py` (docstring and assertion message), was
  caught by the step 3 sweep, as intended.
- `set -u` in the prelude passed all trials (`build.sh`,
  `make-doc.sh`, `smoke-test-wheel`); the three publishing runbooks
  assign every variable before use (static audit) and are exercised
  by the next release.
- Both GitHub workflows untouched: the two tools they call stayed in
  `tools/`.
- `ruff format` rewrapped one assertion in `tests/test_doc_sync.py`
  whose message grew with the target name; otherwise the renames are
  content-free.
- Measured cost of the split, for TODO item 15 and future moves: 6
  sourcing lines, 2 cross-calls, 8 Makefile lines, 1 comment.
- Step 5: the `runbooks/` name lasted one afternoon; the name described
  the ambition, the rule now describes the files. Two upward calls
  (`build.sh` → make, `publish-to-pypi.sh` → the TestPyPI script) became
  prerequisites.
- CI caught what the local trials could not: `make require-system` is
  run by the test jobs, never by `make build`, and its OS `case` used
  `echo` as the `||` fallback. In a recipe sourcing the prelude, `echo`
  is an alias carrying a `;`, so the fallback ran unconditionally and
  `set -u` failed on `save_flags` (the #88 limitation, seen then inside
  `$(...)`). Fixed with `printf`; the prelude header now states the
  rule; both branches trialed with fake `apt`/`sudo` on the PATH.
- Review (Pascal): the sudo fallback of `clean.sh` dates from 51baf71
  and a Docker-with-root context this project never had. The recipe is
  gone; `clean` is three one-line commands in the Makefile, within the
  recipe rule. Six recipes remain.
- The alias limitation has a real fix, a DEBUG trap turning tracing
  off before a helper runs (plain functions, no `;`): trialed, kept for
  its own task, `discussions/tracing-prelude-debug-trap.md`, TODO item 16.
