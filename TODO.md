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

Next number: 38

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

- [x] Dry run from a branch: `.devN` version in `pyproject.toml`,
      `gh workflow run release.yml --ref <branch>`; stops after
      TestPyPI, no tag checks (#113, 2026-09-24: run 36054992654,
      1.18.1.dev1 on TestPyPI; a first dispatch on a commit still at
      1.18.0 stopped in CI on an unresolvable action ref, the
      preflight was not reached).
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
- [ ] Bookkeeping-only PR with a bumping title: the gate blocks it
      with the hook's message (#117; provoke by editing the title of
      a devlog-only PR to `docs:`, then put it back).

### 13. Extract the Markdown titles renumberer into its own tool

`tools/doc-renumber-md-titles.py` becomes a standalone repository
and PyPI package, usable from several projects; then dfd consumes
it as a dev dependency from `make-doc.sh`. Brief, measured survey
of existing tools and requirements in
`discussions/md-titles-renumberer-tool.md` (from #90).

### 32. Remove the deprecated `~=` form

From #127 (2026-09-26): `~[SPEC] =R ITEMS` is desugared to `merge
ITEMS : R` (then `~SPECx R`) with a stderr warning; the docs no longer
show it. Its removal is a breaking change (major), to be done when a
major comes for a stronger reason: drop `_desugar_replacer()` and the
replacer branch of `_parse_filter()` in `dsl/parser.py`, fixture 094
(the sugar twin) and 089 (the bare `=`), the unit cases of the warning.
Constraint (2026-09-26): a breaking change, never proposed for a batch;
it waits for a major.

### 33. Code structure of the filters and the parser (from the review of #128)

Two comments at the review of #128, deferred to a task of their own
that touches code only, with no change to the tests:

- `dsl/filters.py` holds several concepts and its functions relay the
  same parameters (statements, the kept set, the merge map, the
  unavailable set): assess whether classes carry them better.
- `dsl/parser.py`: `parse()` tells a single statement from a list by
  `isinstance()`, a smell; assess a `match`, an abstract result type,
  or every parser returning a list. Also a naming convention telling a
  whole-line parser (`_parse_style`) from a part parser
  (`_parse_item_name`): a prefix per kind, or static methods of two
  classes.

### 37. A combinatorial matrix of fixtures for the filters

Raised at the review of #140 (2026-09-26). The neighborhood fixtures
(028 master, 110 to 112) cover cases by example; a matrix would cover
them by construction: arrow direction (drawn with or against the
flow), turns along a chain, constraint edges, the `x` and `f` flags,
spans 1, 2 and `*`, anchor position, for the stream and the layout
directions, and later the merge combinations. Evaluate the count and
prune by branch coverage: a case earns a row only if it exercises a
branch of `dsl/filters.py` that no other row does. Generating the
inputs programmatically is safe; the expected outputs are not, since
computing them means re-implementing the search, so the renders are
read once by hand and the goldens committed (the NR workflow). The
diagram of a matrix fixture reads as rows of disconnected chains, as
111 shows.
