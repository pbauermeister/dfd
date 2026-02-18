# 031 — Fix style options

**Date:** 2026-02-18
**Status:** ONGOING

---

## Requirement

Fix GitHib bug #31.

The two styles `background-color` and `no-graph-title` options shall be able to be specified from the command line (as now) and also as `style` in the DFD source.

If both are specified, the command line one shall take precedence.

Moreover, `background-color` had no effect (it was not implemented).

## Design

1. Extend the enum `StyleOption` to accept the two new options from DFD source.

2. Between the parsing and generation steps, merge the provenance of the option values, which can come from commandline or DFD source.

## Implementation

- Removed the commandline option `--percent-zoom`, which is not implemented.

- Updated the main README.md to have an up-to-date output of the help.

- Update the doc/README.md to list all `style ...` options (alpha sorted).

- In the doc, added a DFD example with `background-color` and `no-graph-title`.

- Merge the `background-color` and `no-graph-title` options coming from DFD or commandline, with precedence of commandline.

- Remove no longer used models `ExportedStyle` and `SharedOptions` (which were not a good design) and related code.

## Testing

TODO: add at least one NR case, that can be copied from the doc (img/bg-color-no-title)
