# 040 — Star-endpoint connections silently dropped by handle_filters

**Date:** 2026-02-19

**Status:** PENDING

**Issue:** https://github.com/pbauermeister/dfd/issues/40

## Requirement

Connections with anonymous star endpoints (`*`) are parsed correctly but
silently dropped during filter handling. `ENDPOINT_STAR` (`"*"`) is never
a declared item name, so it is never in `kept_names`, and all
star-endpoint connections are unconditionally filtered out — even when no
`only`/`without` filter is present.

### Reproduction

```
process P1
process P2
flow * P1 external input
flow P2 * external output
```

Expected: two star items with labels connected to P1 and P2.
Actual: both connections are silently dropped.

### Acceptance criteria

- Star-endpoint connections are preserved when no filter removes them.
- Star-endpoint connections are correctly handled by only/without filters.
- Existing NR fixtures `002-connections.dfd` and `008-complete-example.dfd`
  produce corrected golden files that include star connections.
- `make black && make lint && make test` passes.

## Design

*(To be filled during Phase 3 — Specification refinement.)*
