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
| 038    | `038-filter-only-left-numeric.dfd`   | `![2` — left (layout) direction, numeric span     |
| 039    | `039-filter-only-right-unlimited.dfd`| `!]*` — right (layout) direction, unlimited span  |
| 040    | `040-filter-without-upstream.dfd`    | `~<*` — remove upstream neighbours, unlimited     |
| 041    | `041-filter-without-downstream.dfd`  | `~>*` — remove downstream neighbours, unlimited   |
| 042    | `042-filter-without-both-numeric.dfd`| `~<>2` — remove both directions, numeric span     |
| 043    | `043-filter-without-x-flag.dfd`      | `~<>x2` — neighbours only, suppress anchors       |
| 044    | `044-filter-without-xf-flags.dfd`    | `~<>xf2` — suppress anchors and frames            |
| 045    | `045-filter-without-left.dfd`        | `~[*` — left (layout) direction, unlimited        |
| 046    | `046-filter-without-left-numeric.dfd`| `~[2` — left (layout) direction, numeric span     |
| 047    | `047-filter-without-right-unlimited.dfd`| `~]*` — right (layout) direction, unlimited    |
| 048    | `048-filter-without-right-numeric.dfd`| `~]1` — right (layout) direction, span 1          |

### Unit tests for error cases

Cross-reference of all `raise model.DfdException` sites against test
coverage. Sites marked **existing** are already tested; **new** will
be added; **defensive** are unreachable through normal DSL input;
**deferred** require complex setup or belong to a separate subsystem.

#### parser.py (16 raise sites)

| Line | Function           | Error                                 | Coverage             |
| ---- | ------------------ | ------------------------------------- | -------------------- |
| 34   | check()            | Duplicate item name                   | Existing             |
| 53   | check()            | Connection to undefined item          | Existing             |
| 61   | check()            | Connection to control w/ non-signal   | New: check           |
| 68   | check()            | Both endpoints are `*`                | Existing             |
| 83   | check()            | Frame is empty                        | New: check           |
| 86   | check()            | Frame includes undefined item         | New: check           |
| 91   | check()            | Item in multiple frames               | New: check           |
| 127  | parse()            | Unrecognized keyword                  | Existing             |
| 134  | parse()            | Re-raise with prefix                  | (wrapper)            |
| 168  | _split_args()      | Wrong arg count                       | New: parse           |
| 170  | _split_args()      | Wrong arg count (optional)            | New: parse           |
| 215  | _parse_filter()    | Filter: no arguments                  | New: parse           |
| 239  | _parse_filter()    | Replacer on Only filter               | New: parse           |
| 271  | _parse_filter()    | Unrecognized flag                     | New: parse           |
| 280  | _parse_filter()    | Bad span                              | Dead code            |
| 294  | _parse_filter()    | No names after spec                   | New: parse           |

#### dfd.py (9 raise sites)

| Line | Function              | Error                              | Coverage             |
| ---- | --------------------- | ---------------------------------- | -------------------- |
| 135  | generate_item()       | Unsupported item type              | Defensive            |
| 155  | _attrib_to_dict()     | Invalid attribute format           | Deferred             |
| 186  | _expand_attribs()     | Alias not found                    | Defensive            |
| 275  | generate_connection() | Unsupported connection type        | Defensive            |
| 417  | handle_options()      | item-text-width not int            | New: dfd             |
| 422  | handle_options()      | connection-text-width not int      | (same pattern as 417)|
| 428  | handle_options()      | Unsupported style                  | New: dfd             |
| 518  | handle_filters()      | Filter name unknown                | New: dfd             |
| 522  | handle_filters()      | Name no longer available           | New: dfd             |

#### scanner.py (4 raise sites)

| Line | Function  | Error                              | Coverage             |
| ---- | --------- | ---------------------------------- | -------------------- |
| 79   | include() | Recursive include                  | New: scanner         |
| 87   | include() | Snippet from non-markdown source   | New: scanner         |
| 95   | include() | Snippet not found                  | New: scanner         |
| 104  | include() | File not found                     | New: scanner         |

#### markdown.py / dependency_checker.py (2 raise sites)

| Line | Function                  | Error                       | Coverage             |
| ---- | ------------------------- | --------------------------- | -------------------- |
| 77   | check_snippets_unicity()  | Duplicate snippet names     | Deferred             |
| 76   | dependency_checker.check()| Accumulated dep. errors     | Deferred             |

#### Summary

| Category | Count |
| -------- | ----- |
| Existing | 5     |
| New      | 19    |
| Deferred | 3     |
| Dead     | 1     |
| Wrapper  | 1     |
| Defense  | 3     |

New tests by file:

- `test_parser.py`: +4 check errors, +6 parse errors
- `test_scanner.py` (new): 4 include errors
- `test_dfd.py` (new): 2 filter errors + 1 filter-replacer + 2 style errors
