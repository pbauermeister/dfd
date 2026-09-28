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

Next number: 43

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
- [x] A minor release (first `feat:` PR): 1.19.0 (2026-09-27, #127
      and #137, run 36307877125, PyPI and the GitHub release
      published). Still open: a major one (`!` or `BREAKING CHANGE:`
      footer in the PR body, which the squash setting carries into
      the commit).
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
- [x] Allowed at or below: #140 (`feat:`) passed on the pending minor
      of #127 (2026-09-27), the "at" case; a `fix:` PR on a pending
      minor, the "below" case, not yet seen.
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

### 38. A merge into a connected item (from the review of #145)

At the second review of #145 the author read `merge B C : D` with
`C -> D` declared above as an error, "D has connections", where the
tool collapses the flow to a self-loop and drops it, as #100 decided
at its Try it (fixtures 078 and 079, "a flow to the replacer itself").
The two readings contradict each other; the error was implemented on
the branch of #145 and removed once 078 and 079 failed (decision 11 of
its devlog). To settle: is a replacer an item declared for the group
(then a connection declared to it above the merge is an error, and
078 and 079 change) or any item (the current rule)? A rule change is
breaking for the two fixtures' shape.

### 39. A neighbor walk re-adds an item removed by a `~` (from #143)

Found at the analysis of #143 (2026-09-27), still there after #145:
`~ B` then `!>1 A` with `A -> B` keeps B, since the neighbors found
by the walk join the kept set without the availability check that
anchors go through (`_check_available`). The strict reading of § 7.5
rule 4 would skip a removed neighbor, or refuse the walk; to settle
with a fixture on the 093 master. Related: TODO 38.

### 40. Structure that the tests pin (from #143)

`discussions/code-structure.md` § 6 lists the proposals that a test
line blocks, since #143 changes no test: `ItemKind` and
`ConnectionKind` enums in place of the `Literal` subsets of `Keyword`
(`tests/unit/test_pipeline.py`, twelve constructions with
`model.Keyword.X` as a type), `remove_unused_hidables` moved to the
filters (three calls), `handle_filters` and `handle_options` renamed
for their effect (fifteen calls), `model.Options` renamed
`CliOptions` (two), `dependency_checker.check` without `options`
(six), `filters.py` renamed for the view stage (the import), and the
graph as the carrier through the pipeline in place of the statement
list (`handle_filters`, `remove_unused_hidables`, `generate_dot`). A
task allowed to edit the tests takes them together.

### 41. Code structure, families B to H (from #143)

The analysis of #143 (`discussions/code-structure.md`, § 4 to § 6)
proposed eight families of structural improvements to the application
code, each with a mock-up green on the four checks. #143 was reframed
to the graph and the derivation of the view (family I) and took D1
with it; the rest waits here: C (the parser's result type and its
names by scope), D2 to D4 (typed selection, `Literal` subsets,
explicit copies), E (`styles.py`, `dsl/stars.py`), F (Graphviz
raises, the CLI exits; one debug mechanism), G (the naming sweep) and
H (21 small smells). § 5 of the discussion gives the order; the taste
rows are in the devlog of #143 as first drafted (git history). Related:
TODO 40 for what the tests pin.

### 42. Distinctive types for the identifiers (from #143)

`Item.name`, `Connection.src` and `.dst`, `Frame.items`,
`Filter.names`, `Merge.names` and `.replacer` are `str`; so are
`Style.style` and `Attrib.alias`. A distinctive type based on `str`
(a `NewType`, or a subclass) says they are identifiers and lets mypy
tell a name from a label. Born at the parser and carried through
every stage, so it touches all modules and the unit tests' literal
constructions (mypy checks `tests/`): a task of its own, first among
the deferred typing rows of TODO 41 (family D). To decide: `NewType`
or subclass; the names (`ItemName`, `StyleName`, `AttribAlias`);
whether the `Literal` subsets of `Keyword` (D2) ride along. Asked by
the user at the review of #143's mock-up, 2026-09-28.
