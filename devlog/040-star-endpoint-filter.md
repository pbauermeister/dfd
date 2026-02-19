# 040 — Star-endpoint connections silently dropped by handle_filters

**Date:** 2026-02-19

**Status:** ONGOING

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
* --> P1 external input
P2 --> * external output
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

### Stars must be proper items for filters to work correctly

All star endpoints share the sentinel value `"*"` during parsing. This
causes two problems:

1. **Filter exemption is too broad.** Simply exempting `ENDPOINT_STAR`
   from the kept-names check (initial fix) means `! P1` would keep
   a star connection to P1 even though the filter specifies no
   neighbors — the star should NOT be kept.

2. **Neighborhood conflation.** During neighbor expansion, all `*`
   endpoints are treated as the same name. If P1 and P2 each have
   a star connection, expanding neighbors from P1 could falsely
   discover P2 through the shared `"*"` value.

### Root cause

Star endpoints are resolved too late — during DOT generation
(`Generator.generate_star()`), after filtering has already run. For
filters to handle stars correctly, each star must have a unique name
and exist as a real item before the filter engine runs.

### Correct filter behavior for stars

- Stars cannot be filter anchors (they have no user-visible name).
- Stars participate in neighborhood traversal: `!>1 P1` with
  `P1 --> * label` keeps the star (it is at distance 1 downstream).
- `! P1` (no neighbor spec) does NOT keep the star connection.
- Stars cannot be in frames (not declared by the user).

## Design

### Resolve stars early in the pipeline

Add a new step in `dfd.py:build()` after `checker.check()` and before
`handle_filters()`:

1. Scan all connections for `ENDPOINT_STAR` endpoints.
2. For each occurrence, generate a unique name using `STAR_ITEM_FMT`
   (`__star_0__`, `__star_1__`, etc.).
3. Replace `conn.src` or `conn.dst` with the unique name.
4. Create a `model.Item(type=NONE, name=unique_name, text=conn.text)`
   with edge font attrs, and clear `conn.text`.
5. Insert the new item into the statements list.
6. Add the star item to `items_by_name`.

After this step, no `ENDPOINT_STAR` sentinel remains in any connection.
Stars are regular `none` items that the filter engine handles normally.

### Simplifications enabled

- **`_apply_filters`**: revert the `ENDPOINT_STAR` exemption — stars
  are now regular items in `kept_names`.
- **`_get_item()`**: remove `ENDPOINT_STAR` special case.
- **`generate_star()`**: remove entirely — stars are rendered via
  `generate_item()` as regular `none` items.
- **`generate_connection()`**: remove star branches (`if not src_item`
  / `if not dst_item`).
- **`checker.py`**: remove `ENDPOINT_STAR` special case (resolution
  happens after checking).

### NR impact

- `002-connections.dot`, `003-connections-sugar.dot`,
  `008-complete-example.dot` — golden files will change (star
  connections appear, star numbering may differ).
- Filter NR fixtures with star connections in their shared
  `028-filter-master.part` may also produce updated goldens.

### Implementation steps

1. Add `resolve_star_endpoints()` in `dfd.py`, wire it into the
   pipeline after `checker.check()`.
2. Revert the `ENDPOINT_STAR` exemption in `_apply_filters`.
3. Simplify rendering: remove `generate_star()`, `_get_item()` special
   case, and star branches in `generate_connection()`.
4. Regenerate NR goldens, inspect the diff.
5. Run `make black && make lint && make test`.
6. Mutation smoke-test.
