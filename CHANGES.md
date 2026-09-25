<!-- semantic-release -->

## v1.18.1 (2026-09-25)

### Bug Fixes

- A bare replacer sign in a filter is an error, not a hang
  ([`d9b2e49`](https://github.com/pbauermeister/dfd/commit/d9b2e49e8844000a7325c12c3fb832d1dbb6b703))

- One neighbor specification per filter, a second one is an error
  ([`e26ba92`](https://github.com/pbauermeister/dfd/commit/e26ba92e30b103967c2f938af5afeca27b1d14c1))

### Build System

- Make install stamps the version with the branch and revision
  ([`1ddeff4`](https://github.com/pbauermeister/dfd/commit/1ddeff4f44c359b2fdb9cd6d45f8ce00530b4aea))

### Chores

- Bookkeeping commits must not bump the version
  ([`aebbe98`](https://github.com/pbauermeister/dfd/commit/aebbe98c37a80865ba028f0c152504ebbf2cb958))

- Devlog 125, a task stopped at its review, and its try-it pictures
  ([`b03e03d`](https://github.com/pbauermeister/dfd/commit/b03e03dbcd9ecdd1587f3712b1033efac64745ce))

- Rename the Shipped stop to Ready ([#110](https://github.com/pbauermeister/dfd/pull/110),
  [`8f59beb`](https://github.com/pbauermeister/dfd/commit/8f59bebfe941cb2681c3d104c99ec5e99895367d))

- TODO 31, codify the batch of chained fast-track tasks
  ([`e6fc61b`](https://github.com/pbauermeister/dfd/commit/e6fc61bbf666689ccf9db799cb34ce9f035951dd))

- TODO 31, fit by kind as one way among others
  ([`1ffb80f`](https://github.com/pbauermeister/dfd/commit/1ffb80f42ae55a0fda0b78c2e4188605d33e20e2))

- TODO 31, the assessment also judges the fit and the order of the batch
  ([`6611e05`](https://github.com/pbauermeister/dfd/commit/6611e052b4deca77d9086ba272c0a946ab799cfc))

### Continuous Integration

- Clear the GitHub Actions deprecation annotations
  ([`3a48eef`](https://github.com/pbauermeister/dfd/commit/3a48eef4f251b98798435646f228c87dac02bf10))

- Skip CI on pushes confined to bookkeeping paths
  ([`4152d66`](https://github.com/pbauermeister/dfd/commit/4152d662605e975e99abf99bf46239d4ec05e717))

- The merge gate blocks a bumping title on a bookkeeping-only PR
  ([`3df8c0c`](https://github.com/pbauermeister/dfd/commit/3df8c0c97366c7990c46f81887fd7f11a71fce2b))


## v1.18.0 (2026-09-24)

### Features

- Strict only filter "!!" keeps only the path flows
  ([#105](https://github.com/pbauermeister/dfd/pull/105),
  [`d90cf84`](https://github.com/pbauermeister/dfd/commit/d90cf84e5b5a0f6a905e7aa820fcc96e61fc11fc))


## v1.17.10 (2026-09-24)

### Documentation

- TODO.md as numbered headings with a counter, done items removed
  ([`80e97b3`](https://github.com/pbauermeister/dfd/commit/80e97b39031d912e2b89921033382809fdcb33f1))


## v1.17.9 (2026-09-24)

### Bug Fixes

- Drop rewired flows whose other end was removed by a filter
  ([#103](https://github.com/pbauermeister/dfd/pull/103),
  [`4c7db69`](https://github.com/pbauermeister/dfd/commit/4c7db6993329d8eea8be2441e2253d73bea2495d))

- Keep and rewire flows between two replaced groups
  ([#101](https://github.com/pbauermeister/dfd/pull/101),
  [`db2b973`](https://github.com/pbauermeister/dfd/commit/db2b973b25621f6852d05570b40b428f96815d1e))

### Documentation

- Devlog templates per task kind, set-based design gate
  ([#93](https://github.com/pbauermeister/dfd/pull/93),
  [`6677d4b`](https://github.com/pbauermeister/dfd/commit/6677d4b814b56612348e0ceb45ec4813f6f670b7))

- Discussions on vibe coding and set-based design; TODO item 14
  ([`4859335`](https://github.com/pbauermeister/dfd/commit/4859335636406e0d0ba4d00ccbe6f2da6da409fe))

- Offload CLAUDE.md into a root file plus on-demand documents
  ([#99](https://github.com/pbauermeister/dfd/pull/99),
  [`31b4254`](https://github.com/pbauermeister/dfd/commit/31b425482a5416dd2643545f0a7d56e866480fa4))

- Stop 0 in the devlog template, frame confirmed before the mock-up
  ([#97](https://github.com/pbauermeister/dfd/pull/97),
  [`e3dc2ac`](https://github.com/pbauermeister/dfd/commit/e3dc2acbb3e2e03eb15e68837e8d8fa39606da55))

- TODO item 12, exercise the release and merge-gate paths of #88
  ([`481e7b7`](https://github.com/pbauermeister/dfd/commit/481e7b729574a82c0563a9234579dac0ebc50fc4))

### Refactoring

- Name tool scripts by level and split recipes/ from tools/
  ([#91](https://github.com/pbauermeister/dfd/pull/91),
  [`bde62e5`](https://github.com/pbauermeister/dfd/commit/bde62e55838142eb7d9b212726592e204c40a9ed))

- Tracing prelude without aliases (DEBUG trap) ([#95](https://github.com/pbauermeister/dfd/pull/95),
  [`0f465d9`](https://github.com/pbauermeister/dfd/commit/0f465d9d742ae5365c66c2d0fde3e8c8ef7f3106))


## v1.17.8 (2026-09-19)

### Build System

- Adopt conventional commits and python-semantic-release
  ([#89](https://github.com/pbauermeister/dfd/pull/89),
  [`0b4050b`](https://github.com/pbauermeister/dfd/commit/0b4050bdeef387a62346fda57a895d891f99df16))

### Documentation

- CLAUDE.md, one pushed commit per design step
  ([`edbcf5a`](https://github.com/pbauermeister/dfd/commit/edbcf5aa66c8ffc474fa0e38393a82f33dea2f6d))

- TODO item 11, script levels and the tools/runbooks split from #88
  ([`9d4accc`](https://github.com/pbauermeister/dfd/commit/9d4accc4c4b3ae631c79d3484350903de38def25))


## Version 1.17.7:

- Fix #84: `--version`, `--help` and `-f dot` work without Graphviz.
  The missing-`dot` error (exit status 2) is reported when a rendered
  format is requested, not before argument parsing. The smoke-test jobs
  of `release.yml` and `ci.yml` no longer install Graphviz.
- Refactor #85: `tools/update-docs.sh` rewritten as
  `tools/update-docs.py` (same sections, markers and prettier pass;
  the CLI help is generated at a pinned width of 80 columns). No
  behavior change.

## Version 1.17.6:

- Doc: `doc/CONVENTIONS.md` gains a "Tooling scripts" section (Python
  vs bash for scripts in `tools/` and `tests/`).
- Tooling #80: release from GitHub Actions. `make release` dispatches
  `release.yml` on `main`, which runs CI, builds once, rehearses on
  TestPyPI, publishes to PyPI with trusted publishing (no tokens) and
  creates the GitHub release and tag from the same files. Procedure and
  recovery in `doc/RELEASING.md`; `make publish-to-pypi` then
  `make publish-to-gh` remain as a local fallback. No behavior change.

## Version 1.17.5:

- Refactor #79: migrate the project tooling to uv. Package metadata
  moves to a PEP 621 `[project]` table (`setup.py` only supplies the
  version parsed from `CHANGES.md`; wheels and sdists now ship the
  license). `uv sync`/`uv run` replace venv handling in the Makefile
  and scripts, `uv build`/`uv publish` replace `setup.py` commands and
  twine, `make install` becomes a user-wide `uv tool install` (with a
  matching `make uninstall`), and a uv-driven Python matrix replaces
  tox (CI on `setup-uv`). README install instructions use
  `uv tool install`. No behavior change.

## Version 1.17.4:

- Test #77: release rehearsal on TestPyPI. `tools/smoke-test-install.sh`
  installs the package into a fresh venv and checks `--version` and a
  `-f dot` render against an NR golden file; `make smoke-test-wheel`
  runs it on the built wheel (also in CI). `make publish-to-testpypi`
  uploads to TestPyPI and smoke-tests the install from there;
  `make publish-to-pypi` runs that rehearsal before the real upload.
  No behavior change.

## Version 1.17.3:

- Refactor #75: replace Black with `ruff format` and add `ruff check`
  (default rules plus ANN401, FBT and PLR0917, enforcing the type-safety
  conventions). `make black` becomes `make format` (alias kept);
  `make lint` runs ruff before mypy. No behavior change.

## Version 1.17.2:

- Refactor #73: codify the type-safety conventions (new "Type safety"
  section in `doc/CONVENTIONS.md`) and align the code: `kw_only`
  dataclasses, keyword-only signatures from four parameters, booleans
  passed by keyword, dataclasses instead of tuples and `Any` dicts for
  internal records, parser dispatch table keyed by `Keyword`. No behavior
  change.

## Version 1.17.1:

- Refactor #71: `style` options are now declared in one place (the
  `GraphOptions` field declarations in `model.py`; default values stay in
  `config.py`), from which the keyword registry, the parsing, and the style
  tables of `doc/README.md` and `doc/SYNTAX.md` are derived. `make readme` regenerates the tables and
  reformats the docs with prettier; a pytest guards against drift. No
  behavior change.

## Version 1.17.0:

- Add style statements:
  - `style item-text-size N`
  - `style connection-text-size N`
  - `style graph-title-size N`

## Version 1.16.9:

- Fix #67: labels containing double quotes produced invalid DOT and crashed
  rendering. All values are now escaped for their DOT emission context:
  quotes in double-quoted strings (item names and labels, connection labels,
  frame labels, graph title); HTML entities in store/channel HTML-like
  labels.
- Labels form a small escape language: `\n` inserts a line break
  (documented), `\\` a literal backslash; `\l`/`\r` are reserved (#59). Any
  other backslash is now rejected with a clear error instead of producing
  undefined DOT behavior.

## Version 1.16.8:

- Fix #65: pip-installed package crashed on startup in a clean venv
  (`ModuleNotFoundError: No module named 'typing_extensions'`). `Literal`
  is now imported from stdlib `typing`; the `typing_extensions`
  dependency is gone.

## Version 1.16.7.post2:

- Bump to post2, to re-publish on PyPi.

## Version 1.16.7:

- Fix #40: star-endpoint connections (`*`) were silently dropped by filters.
  Stars are now resolved into unique items before filtering, so they
  participate correctly in neighborhood expansion and only/without filters.

## Version 1.16.6.post2:

- Break up large functions and extract `dsl/checker.py` (#47).

## Version 1.16.6.post1:

- Move CLI logic from `__init__.py` into dedicated `cli.py` module (#41).
- Fix stale "UML sequence input file" help string to "DFD input file".

## Version 1.16.5:

- Fix #31: allow `background-color` and `no-graph-title` to be specified as
  `style` options in the DFD source, with command-line precedence.
- Implement the `background-color` option (was previously a no-op).
- Remove the unimplemented `--percent-zoom` command-line option.

## Version 1.16.4:

- Fix #29: restore `make lint` by adding missing type annotations to all test
  files; document `make lint` requirement and branch prefix convention in
  `CLAUDE.md`.

## Version 1.16.3:

- Add non-regression test framework (`--format dot` support, golden-file comparison).
- Add and improve unit and integration tests.
- Fix: replace deprecated `pkg_resources` with `importlib.metadata` (stdlib),
  resolving `ModuleNotFoundError` in CI environments.
- Doc: document filtering (`only`/`without`) and layout constraints (`A > B`).
- Doc: normalize section titles in `doc/README.md`.

## Version 1.16.2.post2:

- Refactoring of style options.

## Version 1.16.2.post1:

- Refactoring of keywords.

## Version 1.16.2:

- `A > B` adds a layout constraint, but not a real connection.

## Version 1.16.1.post1:

- Fix: When using attribs alias for stores or channel, unquote attribs

## Version 1.16.0.post1:

- Fix: With --no-graph-title, frame titles have wrong font.

## Version 1.15.3:

- The filters can mandate to remove impacted frames.

## Version 1.15.2:

- The "without" filter can act as a replacer.

## Version 1.15.1:

- Both "only" and "without" filters accept up/down propagation.

- They also can be told to filter only neighbors, by e.g. "~+>3 NODE"
  meaning: "remove 3 downstream neighbors, but not the NODE itself".

- Filters summary:

  ```
  # Only-filter
  # -----------

  ! NODE...          # keep NODE(s)

  # With filters:
  !FILTER... NODE...

  # Filter:
  DIRECTION[ONLY]NUM

  # DIRECTION:
  #   >       downstream neighbors
  #   <       upstream neighbors
  #   <>      all directions
  #   [       left neighbors
  #   ]       right neighbors
  #
  # ONLY (optional):
  #   x       take neighbors but not nodes themselves
  #
  # NUM:
  #   DECIMAL number of neighbors
  #   *       all neighbors in given direction
  #

  # Without-filter
  # --------------

  ~ NODE...          # remove NODE(s)

  # Etc. similarly as for the only-filter.
  ```

- They also can be told to filter only neighbors, by e.g. "~+>3 NODE"
  meaning: "remove 3 downstream neighbors, but not the NODE itself".

- TODO: update doc.

## Version 1.15.0:

- The "only" filter now accepts up/down propagation of inclusion.

## Version 1.14.4:

- Fix bug affecting frames and only/without filters.

## Version 1.14.3:

- Slight factoring

## Version 1.14.2:

- Supports the "without" prefix: `~ NODE`.
- TODO: update doc.

## Version 1.14.1:

- Supports the "only" prefix: `! NODE`.
- TODO: update doc.

## Version 1.13.1:

- Supports style rotated (and unrotated).

## Version 1.12.1.post3:

- CHANGES.md is read by setup.py to deduce the version.

## Version 1.12.0:

- Support style (and hence attrib) on Stores and Channels.

## Version 1.11.1.post2:

Bug fixes:

- Apply attribs on frames.
- Attribs are matched by whole names, so e.g. DATA and DATABASE will work.

Improvements:

- 'make install' to install locally.

## Version 1.11.0:

- Keyword "attrib" to define styles.

## Version 1.10.1:

- When item text is numbered, add newline after the number.

## Version 1.9.1:

- Add troubleshooting in README.md.

## Version 1.9.0:

- Allow line continuation with a trailing backslash

## Version 1.8.0:

- Add frames

## Version 1.7.1:

- Support continuous back- and relaxed- flows.

## Version 1.7.0:

- Add continuous flow (cflow or -->>).
- Add control (may only connect to signals).

## Version 1.6.0:

- Dependencies:
  - items with name #SNIPPET:[NAME] or FILE:[NAME] refer to another graph,
  - referred item is rendered "ghosted",
  - dependencies are checked (unless --no-check-dependencies is passed).
- Add graph title (unless --no-graph-title is passed).
- Error in snippets of MD files: display line number relative to MD file (not snippet).

## Version 1.5.0:

- Wrap labels by `style item-text-width N` (default N=20).
- and `style connection-text-width N` (default N=14).

## Version 1.4.1:

- Processes have very light grey backgrounds.
- Add the 'none' item type.
- Connections with reversed direction affect the items placements.
- A '?' postfix to a connection, removes the edge constraint.
- Fix formatting of '\n' for Store and Channel (which are HTML nodes).
- Colorize error messages.
- Add drawable attributes as [ATTRS...] prefix before labels.

## Version 1.3.x:

- Style vertical: is supported.
- Style context: for context (top-level) diagrams.
- Add undirected flow (uflow aka '--').

## Version 1.2.3

- Snippet reference and ungenerated snippet were marked with '<'; now
  use '#' instead.
- Detect include (infinite) recursions and print error.
- Can print its own version.

## Version 1.1.1

- Fix bug with left/bidir arrows.

## Version 1.1.0

- Upon error, print error stack trace.
- Items: label can be ommitted.
- Connections: syntactic sugars with arrows.

## Version 1.0.0

- Initial release.
