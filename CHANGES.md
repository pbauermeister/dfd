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
