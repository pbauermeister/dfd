# DFD DSL Syntax Reference (Developer)

This document is the single reference for the DFD domain-specific language
syntax, written for developers working on the codebase. It bridges the
user-facing documentation (`doc/README.md`) and the implementation.

> **Sync note:** This document is manually maintained. When the DSL changes,
> update this file first, then propagate to `doc/README.md` and the code.

## Overview

A DFD source is a sequence of **statements**, one per line. Blank lines and
lines starting with `#` (comments) are ignored. Line continuation is supported
via trailing `\` (stitched by the scanner before parsing).

Parsing is keyword-dispatched: the first token of each line selects a parser
from a dispatch table (`parser._PARSERS`). Before dispatch, syntactic sugars
(arrow notation) are rewritten to keyword form.

## 1. Items

```
ITEM_TYPE NAME[?] [LABEL]
```

| Token       | Values                                                      |
| ----------- | ----------------------------------------------------------- |
| `ITEM_TYPE` | `process`, `entity`, `store`, `channel`, `control`, `none`  |
| `NAME`      | Identifier, no whitespace. Trailing `?` makes item hidable. |
| `LABEL`     | Optional free text. Defaults to `NAME` if omitted.          |

The label may start with `[ATTRS]` (Graphviz attributes in brackets),
which are stripped and stored separately.

### Hidable items

A `?` suffix on `NAME` (e.g. `process P?`) marks the item as **hidable**: it
will not be rendered unless at least one connection references it.

### External items (dependencies)

```
ITEM_TYPE GRAPH:NAME [LABEL]
```

`GRAPH` is a snippet reference (`#snippet-name`) or file path
(`path/file.ext`). The colon triggers dependency parsing. An empty `NAME`
(i.e. `GRAPH:`) refers to the whole graph and requires `ITEM_TYPE` = `none`.

## 2. Connections

### Keyword form

```
CONN_TYPE SRC DST [LABEL]
```

| Token       | Values                                                             |
| ----------- | ------------------------------------------------------------------ |
| `CONN_TYPE` | `flow`, `cflow`, `bflow`, `uflow`, `signal`, `constraint`         |
| `SRC`/`DST` | Item name, or `*` for an anonymous endpoint (generates a `none`).  |
| `LABEL`     | Optional free text. May start with `[ATTRS]`.                      |

### Variants

Keyword variants encode direction and constraint behaviour:

| Suffix | Meaning                              | Example          |
| ------ | ------------------------------------ | ---------------- |
| `.r`   | Reversed (swap src/dst in rendering) | `flow.r`         |
| `?`    | Relaxed (no layout constraint)       | `flow?`          |
| `.r?`  | Both reversed and relaxed            | `flow.r?`        |

Not all combinations exist for all types. See `model.Keyword` for the
full enumeration.

### Arrow sugar (syntactic sugar)

```
SRC ARROW DST [LABEL]
```

Arrows are rewritten to keyword form before parsing:

| Arrow pattern | Keyword equivalent | Notes                    |
| ------------- | ------------------ | ------------------------ |
| `-->`         | `flow`             | Shaft of any length      |
| `<--`         | `flow.r`           | Reversed                 |
| `->>`         | `cflow`            | Continuous flow           |
| `<<-`         | `cflow.r`          | Reversed                 |
| `<->`         | `bflow`            | Bidirectional            |
| `---`         | `uflow`            | Undirected               |
| `::>`         | `signal`           | Signal                   |
| `<::`         | `signal.r`         | Reversed signal          |
| `>>`          | `constraint`       | Layout constraint        |
| `<<`          | `constraint.r`     | Reversed constraint      |

Appending `?` to any arrow (e.g. `-->?`) produces the relaxed variant.
The shaft (`-`, `:`) can be of arbitrary length.

## 3. Frames

```
frame ITEM_NAME [ITEM_NAME...] [= [ATTRS] LABEL]
```

Groups items visually. The `=` separates the item list from the optional
label. Without `=`, the frame has no label. Each item may belong to at most
one frame.

## 4. Styles

```
style OPTION [VALUE]
```

| Option                  | Value    | Effect                             |
| ----------------------- | -------- | ---------------------------------- |
| `horizontal`            | -        | Left-to-right layout (default)     |
| `vertical`              | -        | Top-to-bottom layout               |
| `context`               | -        | Context diagram mode               |
| `rotated`               | -        | Rotate diagram 90 degrees          |
| `unrotated`             | -        | Cancel rotation                    |
| `item-text-width`       | integer  | Item label wrap width (default 20) |
| `connection-text-width` | integer  | Connection label wrap width (14)   |
| `background-color`      | color    | Graphviz color spec                |
| `no-graph-title`        | -        | Suppress auto-generated title      |

Styles apply globally. Last declaration wins if redefined.

## 5. Attribute aliases

```
attrib ALIAS GRAPHVIZ_ATTRS
```

Defines a reusable name for Graphviz attributes. Used in `[ALIAS]` within
item or connection labels. Multiple aliases can be combined: `[A B]`.

## 6. Including

```
#include PATH_OR_SNIPPET
```

Handled by the scanner before parsing.

- `#include filename` includes a file.
- `#include #snippet-name` includes a markdown snippet by name.
- Recursive inclusion is detected and raises an error.

## 7. Filters

Filters manipulate a **kept-names set** to produce diagram subsets.

### 7.1. Only filter (`!`)

```
! [NEIGHBOUR_SPEC] ITEM_NAME [ITEM_NAME...]
```

Additive: the first `!` initialises the kept set to empty, then adds the
listed names (and optionally their neighbours).

### 7.2. Without filter (`~`)

```
~ [NEIGHBOUR_SPEC] [=REPLACEMENT] ITEM_NAME [ITEM_NAME...]
```

Subtractive: the first `~` initialises the kept set to all names, then
removes the listed names (and optionally their neighbours).

The `=REPLACEMENT` syntax rewires connections from removed items to the
replacement item instead of discarding them.

### 7.3. Neighbour specification

```
DIRECTION[FLAGS]SPAN
```

| Part        | Values                                           |
| ----------- | ------------------------------------------------ |
| `DIRECTION` | `>` downstream, `<` upstream, `<>` both, `[` left, `]` right |
| `FLAGS`     | `x` = neighbours only (suppress anchors), `f` = suppress frames |
| `SPAN`      | `*` = unlimited, or integer distance              |

Examples: `>*` (all downstream), `<>2` (two levels in both directions),
`<>xf2` (two levels, neighbours only, suppress frames).

### 7.4. Filter semantics

Filters are processed **sequentially** in source order:

1. Each `!` adds names to the kept set.
2. Each `~` removes names from the kept set.
3. Names referenced by a filter must be valid (exist and be currently
   available); otherwise an error is raised.
4. After all filters are processed, statements are filtered: items not in
   the kept set are dropped, connections with missing endpoints are dropped,
   and frames are trimmed or dropped.
5. Connections with replaced endpoints are rewritten; duplicates from
   replacement are deduplicated.

### 7.5. Syntactic sugar

The `!` or `~` character may be written without a separating space before
arguments (e.g. `!A B` is equivalent to `! A B`).
