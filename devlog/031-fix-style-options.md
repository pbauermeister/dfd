# 031 — Fix style options

**Date:** 2026-02-18
**Status:** ONGOING

---

## Requirement

Fix GitHub bug #31.

The `background-color` and `no-graph-title` options shall be specifiable both from the command line (as now) and via `style` in the DFD source.

If both are specified, the command-line value takes precedence.

Additionally, `background-color` had no effect (it was not implemented).

## Design

1. Extend the `StyleOption` enum to accept the two new options from DFD source.

2. Between parsing and generation, merge option values coming from the command line and DFD source, with command-line precedence.

## Implementation

- Remove the unimplemented `--percent-zoom` command-line option.

- Update `README.md` with the current help output.

- Update `doc/README.md` to list all `style` options (alphabetically sorted).

- Add a DFD example in the doc demonstrating `background-color` and `no-graph-title`.

- Merge `background-color` and `no-graph-title` values from DFD source and command line, with command-line precedence.

- Remove the now-unused `ExportedStyle` and `SharedOptions` models and related code.

## Testing

TODO: add at least one NR case, that can be copied from the doc (img/bg-color-no-title).
