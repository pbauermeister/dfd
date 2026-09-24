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

Next number: 22

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
- [ ] Blocked: a `feat:` PR while `main` has unreleased patch
      commits ("release X first"); release, then the check passes
      on the next PR event.
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
