# Dependency updates: detection, blast radius, timing, security

Date: 2026-09-26
Status: PENDING
Origin: #138 (devlog `devlog/138-dependency-updates.md`), branch
`doc/138-dependency-updates`.

**Prompt:** How should the project learn of outdated or vulnerable
dependencies, judge the blast radius of each update, and decide when to
apply it, given that the package has no runtime dependency and the aim
is stable and secure versions rather than the latest?

## 1. The situation

The package ships with no runtime dependency (`dependencies = []` in
`pyproject.toml`). Every dependency serves the pipeline: six direct
dev packages (45 transitive, 51 in `uv.lock`), six GitHub Actions and
one pre-commit hook. Graphviz, Python and uv itself are system
dependencies that no bot sees. An update can break a check, a render
in CI or a release; it can never reach a user.

State on 2026-09-26, measured with `uv tree --outdated --depth 1`,
`uv lock --upgrade --dry-run`, `gh api repos/<r>/releases/latest` and
the repository's security settings:

| Dependency                                     | Pinned     | Latest         | Used by                                                     | A break shows in                |
| ---------------------------------------------- | ---------- | -------------- | ----------------------------------------------------------- | ------------------------------- |
| `python-semantic-release`                      | 10.6.2     | 10.7.0         | `make release`, the merge gate, `print-release-plan`        | the gate on every PR; a release |
| `ruff`                                         | 0.16.8     | 0.16.9         | `make format`, `make lint`, the commit hook                 | lint on every commit, noisily   |
| `mypy`                                         | 2.3.1      | 2.3.1          | `make lint`                                                 | lint on every commit, noisily   |
| `pytest`                                       | 9.1.1      | 9.1.1          | `make test`, the push hook                                  | the suite                       |
| `pre-commit`                                   | 4.6.2      | 4.6.2          | the git hooks                                               | a hook that stops running       |
| `pyyaml`                                       | 6.0.3      | 6.0.3          | two tools (`conventional-commits`, `check-python-versions`) | lint                            |
| `actions/checkout`                             | `v7`       | v7.0.1         | every workflow                                              | every workflow                  |
| `astral-sh/setup-uv`                           | `v10.2.0`  | v10.2.0        | CI, gate, release                                           | every workflow                  |
| `actions/upload-artifact`, `download-artifact` | `v7`, `v8` | v7.0.1, v8.0.1 | `release.yml`                                               | a release only                  |
| `amannn/action-semantic-pull-request`          | `v6.1.1`   | v6.1.1         | `pr-title.yml`                                              | the title check on every PR     |
| `compilerla/conventional-pre-commit`           | `v4.4.0`   | v4.4.0         | the commit-msg hook                                         | every commit                    |

Transitive drift on the same day: `uv lock --upgrade --dry-run` moves
seven packages (click, filelock, nodeenv, platformdirs,
python-semantic-release, ruff, virtualenv).

Blast radius reads off the "used by" column. The release tooling is
the widest: `python-semantic-release` decides the version bump in the
merge gate on every PR and drives `make release`; the release workflow
is the only place where `upload-artifact` and `download-artifact` run.
A break there shows at release time, or in the dry run from a branch
(TODO item 12). `ruff` and `mypy` are the noisiest: a minor of either
adds rules or narrows an inference, and the cost is a formatting or
typing sweep across the tree rather than a failure of the product.
`pytest`, `pyyaml` and `pre-commit` are the narrowest, with one
consumer each. The two version limits in the dev group,
`python-semantic-release <11` and `pre-commit <5`, already say where
a major is expected to hurt.

What the tests cover: the suite (154 tests, `make test`) and `make
lint` run on every push and every commit through the hooks and on
every push in CI, so a bump that breaks a checker, the parser or the
NR fixtures fails within the bump's own PR. Nothing exercises the
release path short of a release or the dry run; nothing exercises the
hooks themselves (a bump of `pre-commit` or of the conventional hook
shows only at the next commit on a developer's machine).

## 2. Security today

The dependency graph is on (the SBOM endpoint lists 60 packages), but
Dependabot alerts and Dependabot security updates are off, and no
audit runs anywhere. So today a CVE against a dependency reaches the
project by chance.

Measured on the lock of 2026-09-26, `uv audit` and `pip-audit` (PyPI
advisory database and OSV) agree on one finding: `click 8.1.8`,
PYSEC-2026-2132, fixed in 8.3.3. `click` is a dependency of
`python-semantic-release` and `click-option-group`; it runs in the
merge gate and in `make release`, on our own inputs, so the exposure
is nil, but it is the release path and it went unnoticed for as long
as the advisory has existed. The targeted bump works:
`uv lock --upgrade-package click==8.3.3` moves click (and
`python-semantic-release` to 10.7.0); the bare
`--upgrade-package click` reports no change, a uv behavior to keep
in mind when a fix has to be named.

The tools, as their documentation reads on 2026-09-26:

- **Dependabot alerts** are the notice: GitHub matches the dependency
  graph against its advisory database and opens an alert per
  vulnerable package. They need only the graph, which is on. They
  cost nothing in PRs.
- **Dependabot security updates** are the response: a PR per alert
  that has a patched version, grouped per ecosystem on request. They
  need the alerts, take an optional `dependabot.yml`, and are distinct
  from version updates ("all dependencies defined in lock files with
  vulnerable dependencies are updated by security updates", version
  updates target the manifest). `pre-commit` gets version updates
  only, no security updates.
- **`uv audit`** (preview, June 2026, OSV) reads `uv.lock` and reports
  the same finding in a second; `pip-audit` reads an exported
  requirements file (`uv export`, then `--no-deps`). Either fits a CI
  step or a `make audit` target, and both stay silent until a finding
  appears. uv's malware check at sync (`UV_MALWARE_CHECK=1`) is a
  separate, opt-in gate against known malicious packages.

The response to a CVE is a bump on its own, outside any cadence, with
the severity read against what the dependency does here: a tool that
runs locally and in CI on the project's own files, as click does, is
not an exposure, and the bump can wait for the next batch; a
dependency that touches the release artifacts or a token (the
publishing step, the upload action) is bumped the day the alert
arrives. Stable over latest holds in both cases: a security patch is
taken at once, a major waits for a reason.

## 3. Detection, the options

| Option                                             | What it does                                                                                                                         | Cost                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| A. Alerts and security updates, no version updates | GitHub opens an alert and a PR when a CVE has a fix; nothing else moves                                                              | two repository settings; a PR a few times a year; drift accumulates as today                             |
| B. A plus Dependabot version updates               | `dependabot.yml` for `github-actions`, `uv` and `pre-commit`, grouped, on a schedule                                                 | one file of about 30 lines; one to three PRs per period; each PR a review and a merge                    |
| C. Renovate (Mend app)                             | Same coverage (`github-actions`, `pep621` with `uv.lock`, `pre-commit`), a dependency dashboard issue, automerge rules               | an app install and a JSON config; the richest tuning, the most to learn; a third party with write access |
| D. By hand at release time, plus an audit in CI    | `uv lock --upgrade`, `pre-commit autoupdate`, action tags read from the release pages, before `make release`; `uv audit` in `ci.yml` | a checklist step in `engineering/RELEASING.md`; no bot; the audit is the only CVE notice                 |

The four are not exclusive: D's audit step complements A or B, and D's
checklist is what B automates. Dependabot's options that matter here:
`schedule.interval` (`monthly` is enough for a project that releases
on demand), `groups` (one PR per ecosystem), `cooldown` (a new
version is not proposed before N days, 3 by default, the "stable over
latest" knob), `ignore` with `version-update:semver-major` (a major
arrives only when asked), `commit-message.prefix` (`chore(deps)`),
`open-pull-requests-limit`. Dependabot PRs run the CI (a push event)
and the two required checks with a read-only token and no secrets,
which is all these workflows need.

## 4. Timing and the release state

A bump is `chore(deps):`, none-level, so the merge gate never blocks
it and it never forces a release; it also never appears in
`CHANGES.md`. Two consequences. A bump can sit on `main` for weeks and
a broken release tool shows only at the next release, which is the
argument for the dry run from a branch after a bump of
`python-semantic-release` or of the release workflow's actions, and
for no other bump. And the gate itself runs the bumped
`python-semantic-release` on every later PR, which is a free check of
its version computation.

Cadence, then: monthly for version updates, or at each release for
the by-hand option; at once for a security patch of the release path;
never for a major without a reading of its release notes, which is
the one part of the work that stays by hand under every option.

## 5. Supply chain and the pinning policy

Three kinds, three policies:

- **Actions.** GitHub's hardening guide: "pinning an action to a
  full-length commit SHA is currently the only way to use an action as
  an immutable release"; a tag "can be moved or deleted if a bad actor
  gains access to the repository storing the action". Immutable
  releases (generally available since October 2025) lock a release's
  tag and assets; `astral-sh/setup-uv` publishes them, which is why
  it has no moving major tag past `v7` and is pinned exact here.
  `actions/checkout` still moves `v7`. Dependabot bumps SHA pins and
  keeps the `# vX.Y.Z` comment current, but with a moving major tag
  it proposes only majors. The policy candidates: exact tag everywhere
  (readable, trusts the publisher, immutable where the publisher opted
  in) or SHA everywhere with the version in a comment (the guide's
  answer, unreadable without the comment, needs the bot to stay
  current). Never a branch.
- **Dev group.** `uv.lock` is the only pin; `pyproject.toml` keeps
  the ranges (`>=`, `<` a known-bad major). The bot edits the lock,
  the ranges stay by hand.
- **Hooks.** `rev:` in `.pre-commit-config.yaml` is an exact tag;
  Dependabot's `pre-commit` ecosystem or `pre-commit autoupdate` moves
  it.

Two rules hold under any option: a bot PR is never auto-merged (the
PR is the attack path, whoever opens it), and a major is merged after
its release notes are read.

## 6. Tests on our side

A bump of a tool that the suite already runs needs no new test: the
suite and lint are the test. Three gaps are worth a test or a check,
independent of the bot question:

1. The release path: a `make release` dry run from a branch after a
   bump of `python-semantic-release` or of `release.yml`'s actions
   (TODO item 12 already lists the dry run).
2. The hooks: `tests/test_nr_scripts.py` is the model for a test that
   runs `pre-commit run --all-files` in a temporary clone; cheap, but
   the hooks fail loudly on the developer's machine anyway.
3. An audit step: `uv audit` in `ci.yml` or as `make audit`, which
   turns a CVE notice into a red check rather than an e-mail.

## Executive summary

No runtime dependency: an update can break the pipeline, never a
user. Today nothing reports a CVE (alerts off, no audit), and the lock
of 2026-09-26 carries one, click 8.1.8 in the release path, harmless
here but unnoticed. Detection is one of: alerts and security updates
alone (A), plus Dependabot version updates monthly and grouped (B),
Renovate (C), or by hand at release time with an audit in CI (D); an
audit step fits under all four. The widest blast radius is the
release tooling, checked by the dry run from a branch; ruff and mypy
are noise, not risk. Policies per kind: exact tag or SHA for actions,
the lock for the dev group, `rev:` for hooks; never auto-merge, read
the notes of a major.

## Outcomes and measures

To decide at the review of #138, none taken here:

- The option (A to D) and, for B, the file's cadence, groups, cooldown
  and major policy.
- Whether `uv audit` enters CI or the Makefile.
- The pinning policy for actions: exact tag or SHA with comment.
- The click bump, as the first application of whatever is chosen.
