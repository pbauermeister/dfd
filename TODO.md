# TODO

Recognized tasks are recorded as GitHub issues and managed in detail
in corresponding `devlog/NNN-*.md` files.

This file captures items as they arise during work, so nothing is
forgotten without diverting the current discussion or reasoning. Items
collected here can later be specified as tasks, grouped together, or
discarded. If a TODO item becomes significant effort, it must be
turned into a standard task (GH ticket, PR, devlog).

Items are headings numbered from the counter below, unique for the
life of the file: a new item takes the number and bumps the counter in
the same commit. An item is removed, not struck through, when its
issue is filed or when it is dropped; the commit message names the
issue or the reason, and `git log -S'### NN.' -- TODO.md` retrieves
the text. The numbers of removed items are never reused.

Next number: 26

## Won't do

### 1. Redesign DSL parser with a formal grammar (lark, PEG, ANTLR)

The DSL is one-statement-per-line by design — no nesting, no
precedence, no multi-line constructs. The current regex-based
scanner/parser is the right tool for this grammar. After the
refactoring (#34), the pipeline stages are clean and independently
modifiable. A formal parser would add a dependency and migration risk
for no proportional benefit. Revisit only if a future feature
genuinely requires multi-line syntax.

## TODO Items

### 12. Exercise the release and merge-gate paths of #88

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

- [x] Merge not followed by a release: two patch PRs merged, then
      one release whose changelog lists both (1.17.9, 2026-09-24:
      eight PRs and one direct commit since 1.17.8, all listed).
- [x] Blocked: a `feat:` PR while `main` has unreleased patch
      commits ("release X first"); release, then the check passes
      on the next PR event. Occurred on #105 (2026-09-24, "release
      1.17.10 first"); passed after the release and a merge of
      `main` into the branch.
- [ ] Allowed at or below: a `fix:` PR on a pending minor.
- [ ] None-level pending counts as empty: a `chore:` commit on
      `main`, then a `feat:` PR passes.
- [ ] A title edit re-runs `conventional` and `gate`; a
      non-conventional title blocks the merge button.
- [ ] PR behind `main`: BEHIND state, "Update branch", checks rerun.

### 13. Extract the Markdown titles renumberer into its own tool

`tools/doc-renumber-md-titles.py` becomes a standalone repository
and PyPI package, usable from several projects; then dfd consumes
it as a dev dependency from `make-doc.sh`. Brief, measured survey
of existing tools and requirements in
`discussions/md-titles-renumberer-tool.md` (from #90).

### 18. Skip GitHub Actions on commits that do not need them

`ci.yml` runs the full matrix on every push to `main` and every PR
event, including commits that touch only `devlog/`, `discussions/`,
`TODO.md` or `engineering/`. Add `paths-ignore` for those to the
`push` and `pull_request` triggers; `merge-gate.yml` and
`pr-title.yml` are cheap and must keep running (both are required
checks of the `main` ruleset, and a path-filtered required check
never reports, which blocks the merge button). `CI` is not a
required check, so filtering it is safe; keep `workflow_call`
unfiltered so `release.yml` still gates on it.

### 19. Clear the GitHub Actions deprecation annotations

Every run of `release.yml` (1.17.9, 2026-09-24) and `ci.yml` ends
with two warnings. Node 20 deprecation: `actions/checkout@v4`,
`actions/upload-artifact@v4`, `actions/download-artifact@v4` and
`astral-sh/setup-uv@v6` are forced onto Node 24; move to the
majors that target Node 24 (`checkout@v5`, `upload-artifact@v5`,
`download-artifact@v5`, latest `setup-uv`) in `release.yml`,
`ci.yml` and `merge-gate.yml`. Runner image: `ubuntu-latest`
migrates to Ubuntu 26 on 2026-10-19; pin `ubuntu-24.04` or verify
the suite on the new image before that date. Rehearse with the
`release.yml` dry run (`workflow_dispatch`, stops after TestPyPI),
never exercised so far.

### 20. A bare `=` in a filter statement hangs the parser

Found while mocking up #104 (devlog 104): `~= G B C` (space after
the replacer sign) never returns. In `_parse_filter()`
(`src/data_flow_diagram/dsl/parser.py`) `RX_FILTER_ARG` matches `=`
with an empty `replacer` group, which is falsy, so neither branch
consumes the argument and the `while args` loop spins. Fix: test the
group for `None`, not truthiness, and raise "replacer name expected"
on an empty one; add the robustness case to
`tests/unit/test_parser.py::test_check_raises` and an `-err-` NR
fixture.

### 21. Filter flag order: the doc says `<>2xf`, the parser wants `<>xf2`

Found at the stop 0 review of #104 (devlog 104). `doc/README.md`
§ 7.3.3 gives `DIRECTION[SPAN][FLAGS]`; `RX_FILTER_ARG` in
`src/data_flow_diagram/dsl/parser.py` and every example (`!<>xf2`)
put the flags before the span. The documented order is the logical
one (the span belongs to the direction, the flags qualify the
selection). Make the parser accept the flags on either side of the
span, migrate the examples and fixtures to the documented order, and
say in § 7.3.3 that both are accepted.

### 22. Several neighbor specs in one filter: undocumented, overwrite silent

Found at the stop 1 discussion of #104 (devlog 104). `_parse_filter()`
(`src/data_flow_diagram/dsl/parser.py`) consumes every leading
argument that matches a neighbor spec, so `!<1 >2 C` is one filter
with upstream span 1 and downstream span 2, equivalent to `!<1 C`
plus `!>2 C`. `doc/README.md` § 7.3 and `doc/SYNTAX.md` § 7 write one
`[NEIGHBOUR_SPEC]`, singular, and a second spec for the same
direction (`!<1 <3 C`) silently overwrites the first. Decide: document
the combined form and make the same-direction repeat an error, or
reject a second spec. Leaning: document it, it exists and is harmless.
Note for the doc: a flag or the `!!` strictness applies to the whole
filter, whichever spec carries it; different strictness per direction
is obtained by two filters.

### 23. A keep filter after a replacement re-adds the replaced items as orphans

Found at the stop 1 discussion of #104 (devlog 104). On `A→B→C→D`
with `~=G B C` then `!<2 D`, the traversal in
`_collect_connected_names()` (`src/data_flow_diagram/dsl/filters.py`)
reads the original connections, follows `cd` to C and `bc` to B, and
re-adds them to the kept set; the replacement map is permanent, so
their flows still go to G: B and C render as orphan items next to
G. `~=G B C` then `! B` does the same for an explicit anchor. The
documented order, `!` before `~=`, is unaffected. Fix: traversal and
anchors work on the current state, connections followed as rewired so
far (from D the traversal reaches G), and an anchor that names a
replaced item is an error like "no longer available". Two NR
fixtures, traversal and explicit anchor.

Design point raised at the Try it of #104: the natural reading is to
declare the group first and filter around it (`~=Z C G` then
`!<2 D Z`, block J of `devlog/104-try-it.dfd`), and the language
cannot express the neighborhood of a group today. A `~` as first
filter starts from the full set, so the `!` that follows narrows
nothing; a `!` first cannot anchor on Z, which has no flows before the
replacement; and `! Z` then `~=Z C G` errors, C and G being outside
the kept set. Traversal on the current state removes the orphans but
not the full-set start. Decide with the fix: a replacement as first
filter that does not fill the set, a `!` after `~` that narrows, or
another form. The doc's group example (§ 7.4.2.2) writes `!` first
and stays valid either way. Direction agreed at the Try it of #104: a
replacement is a rewiring, not a removal, so `~=` does not count as
the first filter that initialises the kept set; the `!` that follows
starts empty and traverses the rewired flows. The plain `~`-first
rule stays as documented, and both orders keep a meaning: `!` first
selects on the original graph and then collapses, `~=` first selects
on the grouped graph. Statement order carries meaning since filters
exist; before them it only steered the layout.

### 24. TODO.md commits must not bump the version

Found at the delivery of #104: `main` carried one commit, `docs:
TODO.md as numbered headings` (80e97b3), which bumps patch, so the
`feat:` PR #105 was blocked by the merge gate ("release 1.17.10
first") and 1.17.10 was released with no change to the package. A
change to `TODO.md`, on any branch, is bookkeeping: it must use a
type that bumps nothing (`chore`, `ci`, `style`; `make help-cc`).
Define the rule: `chore:` for `TODO.md` (and, to decide, for the
devlogs and `engineering/`, which do not ship either), in
`engineering/RELEASING.md` "Versioning convention" and in the
`commit-msg` hook if it can tell the paths; sweep the habit into
`engineering/PROCESS.md` where TODO commits are described. Check
whether `docs:` should keep bumping patch at all: the shipped doc
(`doc/`, `README.md`) is part of the package, the rest is not.

### 25. `make install` should stamp the version with the branch and revision

Raised at the delivery of #104. `make install` (`uv tool install
--reinstall .`) installs the current, unreleased tree, which is its
purpose: an official release is what `uv tool install
data-flow-diagram` or `pipx` pull from PyPI. Yet `--version` reports
the bare `MAJOR.MINOR.PATCH` of `pyproject.toml`, indistinguishable
from the last release. Stamp a development install with where it
comes from: the branch and the short hash, as a PEP 440 local version
label after a `.devN` segment, e.g.
`1.17.10.dev0+feature.104.keep.involved.flows.g294a988` (the label
allows letters, digits and dots; `-`, `_` and `/` normalise to dots).
Decide how: a dynamic version (`hatch-vcs` or `setuptools-scm` style,
from `git describe`) or a `make install` recipe that rewrites the
version in a scratch copy before installing. The release path
(`make release`, `release.yml`) must keep the bare version.
