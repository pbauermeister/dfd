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

## Analysis

### The bug exists even without any filters

`handle_filters()` is called unconditionally in the pipeline
(`dfd.py:30`). When the DFD source contains no `!`/`~` filter
statements, the following happens:

1. `_collect_kept_names` returns `kept_names = None` (no filter
   encountered).
2. `handle_filters` line 345: `kept_names = all_names` — fallback to
   the set of all declared item names.
3. `_apply_filters` runs with that `kept_names`.
4. `_apply_filters` line 272:
   `conn.src not in kept_names or conn.dst not in kept_names` —
   `ENDPOINT_STAR` (`"*"`) is never a declared item, so **every
   star-endpoint connection is dropped unconditionally**.

So `002-connections.dfd` and `008-complete-example.dfd` — which have
zero filters — have been silently losing their star connections all
along. The golden files were approved with the bug present.

### Neighborhood expansion cannot reach stars either

Even if a filter's neighborhood expansion were to "reach" a star
endpoint by traversing connections, the star wouldn't be in `all_names`
to begin with, so it could never enter `kept_names` that way. But this
is moot — the connections are already gone before neighborhood
expansion has any effect.

### Root cause

The kept-names check in `_apply_filters` treats `ENDPOINT_STAR` like a
regular item name, but it is a sentinel value that is never declared as
an item. Star endpoints are resolved later during DOT generation
(`Generator.generate_star()`), not during filtering.

## Design

### Fix

In `_apply_filters` (line 272), exempt `ENDPOINT_STAR` from the
kept-names check. A star endpoint should never be filtered out — it is
not a declared item but a sentinel resolved during rendering:

```python
# skip if either endpoint was filtered out (star endpoints are always kept)
if (
    conn.src not in kept_names and conn.src != model.ENDPOINT_STAR
) or (
    conn.dst not in kept_names and conn.dst != model.ENDPOINT_STAR
):
```

### NR impact

- `002-connections.dot`, `003-connections-sugar.dot`,
  `008-complete-example.dot` — golden files will change (star
  connections will now correctly appear).
- Filter NR fixtures that use star connections in their source may also
  produce updated goldens — need to inspect after regeneration.

### Implementation steps

1. Fix the filter check in `_apply_filters`.
2. Regenerate NR goldens, inspect the diff.
3. Run full test suite (`make black && make lint && make test`).
4. Mutation smoke-test (revert the fix, confirm NR fails on affected
   fixtures, re-apply).
