# 138 — Study the dependency updates

Date: 2026-09-26
Status: ONGOING
Issue: #138 · PR: #141 · Branch: `doc/138-dependency-updates`
Task nature: analysis
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 28 (raised at the review of #114, reframed as a study on
2026-09-26, removed by the filing commit of the batch). Second of the
batch 30, 28, 36 of 2026-09-26, off `main`, reviewed second. The
reframing: understand the situation and the consequences before any
configuration; the goal is stable and secure versions, not the latest,
and to learn of a CVE when it is published.

### 1.2 Goal

`discussions/dependency-updates.md` answers the aspects of the item
with measured facts and dated sources: the inventory and blast radius
of every dependency, the security state and the CVE path, the
detection options with their cost, timing against the release state,
the pinning policy per kind, the tests worth adding. Decisions are
listed for the review, none taken.

### 1.3 Design decisions

| #   | Decision                                                                                                           | Basis                          | Alternatives considered               |
| --- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------ | ------------------------------------- |
| 1   | A discussion file, no `dependabot.yml`, no repository setting changed                                              | the reframing (rule)           | Ship option A's settings as a default |
| 2   | Every claim on a tool from its documentation read on the day, dated in the text; every number from a command named | batch assessment (rule)        | Recollection                          |
| 3   | The lock audited with both `uv audit` and `pip-audit` (PyPI and OSV), so that one finding is confirmed twice       | measure, don't estimate (rule) | One tool                              |
| 4   | Options A to D presented with their cost and marked as combinable; the agent's reading stays out of the file       | the reframing (taste)          | A recommendation row                  |

### 1.4 Acceptance criteria

1. Every dependency of the pipeline in the inventory table with its
   consumer and where a break shows.
2. The security state measured (settings, audit) and the CVE path
   described from the docs.
3. Each detection option with a cost line; the pinning policy per kind.
4. Sources dated; `make lint` (prettier) passes.

Approved: 2026-09-26 (the go for the batch)

## 2. Findings

Measured on 2026-09-26 (the discussion holds the tables):

- Six direct dev packages, 51 locked; six actions; one hook. Two
  outdated at depth 1 (`python-semantic-release`, `ruff`), seven
  moves under `uv lock --upgrade --dry-run`.
- Dependency graph on, Dependabot alerts off, security updates off.
- One vulnerability in the lock: click 8.1.8, PYSEC-2026-2132, fixed
  in 8.3.3, under `python-semantic-release`. A targeted bump needs the
  version named (`--upgrade-package click==8.3.3`); the bare form
  reports no change.
- Dependabot covers `github-actions`, `uv` and `pre-commit`
  (version updates; security updates not for `pre-commit`); it has
  `cooldown`, `groups`, `ignore` by semver level. Renovate covers
  the same through `pep621` with `uv.lock`. `uv audit` (OSV,
  preview) reads the lock directly.
- `astral-sh/setup-uv` publishes immutable releases and has no moving
  tag past `v7`; `actions/checkout` moves `v7`.
- Commands: `uv tree --outdated --depth 1`, `uv lock --upgrade
--dry-run`, `uv audit`, `uv export --no-hashes --all-groups` then
  `uv tool run pip-audit -r req.txt --disable-pip --no-deps
[--vulnerability-service osv]`, `gh api repos/<r>/releases/latest`,
  `gh api repos/pbauermeister/dfd --jq .security_and_analysis`,
  `gh api repos/pbauermeister/dfd/dependency-graph/sbom`.

Account: `75396b3` the discussion; this devlog.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- Criteria 1 to 4 met. The agent's reading, for the review and not
  in the file: option A (alerts and security updates) plus `uv audit`
  in CI is the smallest step that closes the CVE gap; B adds the
  monthly drift PRs, which this project can absorb grouped and with
  majors ignored.

### 3.2 Discussion

| #   | Point                                                                      | Decision |
| --- | -------------------------------------------------------------------------- | -------- |
| 1   | The click bump: apply now as a `chore(deps)` PR, or with the option chosen | review   |

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                      | Agent    | User |
| --- | ---------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: analysis nature in fast form, Findings in place of Execution                     | well     |      |
| 2   | The audit found a real CVE on the first run; the study's value was measured before it was written          | well     |      |
| 3   | The summary fetches of the docs missed rows twice (uv ecosystem on one page); a second source settled each | surprise |      |

Process: 1 round before the go (the batch assessment); 0 loops.

Closed: pending

### 4.2 Rule trace

| Source                                                      | Rule                                | Verb (applied / created) |
| ----------------------------------------------------------- | ----------------------------------- | ------------------------ |
| `engineering/PROCESS.md` Established tool vs bespoke script | Measure, don't estimate             | applied                  |
| `engineering/PROCESS.md` discussions/ files                 | Executive summary and outcomes last | applied                  |
