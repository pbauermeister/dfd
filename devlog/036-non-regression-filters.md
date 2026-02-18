# 036 — Add non-regression tests for filters and other gaps

**Date:** 2026-02-18

**Status:** ONGOING

**Issue:** https://github.com/pbauermeister/dfd/issues/36

## Requirement

Anchor current behaviour with non-regression tests before starting
structural refactoring. This is task A from the refactoring strategy
(#34).

Priority areas:

1. Filters (biggest gap) — `!` (only), `~` (without), neighbours,
   direction, flags, distance, replacements.
2. Review existing fixtures for coverage gaps.

## Design

### Filter tests

A shared master diagram (`028-filter-master.part`) provides a
multi-item, multi-connection graph. Individual `.dfd` files include it
and apply different filter combinations.

The master diagram mirrors the "data pipeline" example from
`doc/README.md` section 7, adapted to exercise all filter features.

### Test numbering

| Number | Fixture                              | Aspect                                            |
| ------ | ------------------------------------ | ------------------------------------------------- |
| 028    | `028-filter-master.part` (shared)    | Base diagram for all filter tests                 |
| 028    | `028-filter-only-basic.dfd`          | Basic `!` with multiple items                     |
| 029    | `029-filter-only-upstream.dfd`       | `!<*` — upstream neighbours, unlimited span       |
| 030    | `030-filter-only-downstream.dfd`     | `!>*` — downstream neighbours, unlimited span     |
| 031    | `031-filter-only-both-numeric.dfd`   | `!<>2` — both directions, numeric span            |
| 032    | `032-filter-only-x-flag.dfd`         | `!<>x2` — neighbours only, suppress anchors       |
| 033    | `033-filter-only-xf-flags.dfd`       | `!<>xf2` — suppress anchors and frames            |
| 034    | `034-filter-only-left.dfd`           | `![*` — left (layout) direction                   |
| 035    | `035-filter-only-right.dfd`          | `!]1` — right (layout) direction, span 1          |
| 036    | `036-filter-without-replace.dfd`     | `~=name` — without filter with replacement        |
| 037    | `037-filter-combined.dfd`            | Combined `!` and `~` filters in sequence          |
