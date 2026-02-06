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
