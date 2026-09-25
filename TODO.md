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

Next number: 32

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

### 28. Examine Dependabot for the actions and the dev dependencies

Raised at the review of #114 (2026-09-25): four actions had drifted
a year, and the surprise was not the bumps but the rules underneath
(setup-uv's immutable releases, no moving major tag past v7). Regular
small updates are cheaper than one accumulated migration. Examine
the pros and cons of `.github/dependabot.yml`: the `github-actions`
ecosystem, grouped so the actions arrive as one PR, weekly or
monthly; a `uv` entry for the dev dependency group and the pre-commit
hook revision; PRs typed `chore(deps):` (none-level, CI runs on their
push). Against: bot noise, a merge each time, the review of release
notes on a major still by hand. Decide the pinning policy with it:
current major or exact tag for actions, release notes read on a major.

### 29. A lint failure must block mechanically

Raised at the review of #120 (2026-09-25): a commit with a `ruff`
error (a duplicated test, F811) reached the remote because the agent
ran `make lint` and did not read its exit. The rule "format, lint,
test before pushing" (`engineering/RULES.md`) is manual. To discuss
how to make it mechanical: a pre-commit hook running `make lint` on
the staged Python files (the hook framework is installed for the
commit-msg stage already), a pre-push hook, or CI as a required
check (which #111 made a matter of the push-only trigger). Weigh the
delay at each commit against the value.

### 30. A symmetrical layout neighborhood `[]`

Raised at the review of #124 (2026-09-25). `<>` is the symmetrical
stream neighborhood; the layout counterpart `[]` (left and right) is
not in the grammar (`RX_FILTER_ARG` accepts `<>`, `<`, `>`, `[`,
`]`) and is refused as an unknown name. Since #123 a filter takes one
neighborhood specification, so `[1` and `]1` on the same items need
two filters; `[]` would be the one-filter form. New syntax, `feat:`
(minor): after the pending patch release. Fixture, README § 7.3.3,
SYNTAX.md § 7.3.

### 31. Codify the batch of chained fast-track tasks

Tried twice on 2026-09-24 and 2026-09-25 (the build batch 24, 26,
18, 19, 25 and the filter batch 20, 21, 22, 23) and judged a success
by the user. The shape: a set of small, well-framed items (TODO
items, a brief); an upfront assessment with disposable mandate drafts
that surfaces the decisions to take, taken in one exchange; then the
tasks run chained and unattended, one branch stacked on the previous
when they touch the same files, issues and PRs numbered in sequence,
each stopped at "ready for review"; then the reviews, sequential and
interactive, each merged before the next (retarget the next PR to
`main` before merging its base; merge `main` forward into the rest);
the review may loop a task or stop it, that stop being the valve the
mandate anticipates (#125 ended REJECTED, #121 cancelled, both by
the review). Codify it lightly: a short section in
`engineering/PROCESS.md` next to "Fast track", the decision drafts as
a scratch artifact, the ordering and merge rules, what the review may
do. No new template.
