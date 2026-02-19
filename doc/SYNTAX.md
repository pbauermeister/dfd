# DFD DSL Syntax Reference (Developer)

This document is the single reference for the DFD domain-specific language
syntax, written for developers working on the codebase. It bridges the
user-facing documentation (`doc/README.md`) and the implementation.

> **Sync note:** This document is manually maintained. When the DSL changes,
> update this file first, then propagate to `doc/README.md` and the code.

## Glossary

The terms below are authoritative. Use them in code identifiers, comments,
documentation, and commit messages.

### Core concepts

| Term           | Definition                                                        |
| -------------- | ----------------------------------------------------------------- |
| **statement**  | A single logical line of DFD source (after preprocessing).        |
| **item**       | A node in the diagram. Never use "node" in prose — that is a Graphviz term. |
| **connection** | A directed or undirected link between two items.                  |
| **endpoint**   | The source or destination item of a connection (`SRC` / `DST`).   |
| **frame**      | A visual grouping (subgraph) of items.                            |
| **name**       | The unique identifier of an item (no whitespace).                 |
| **label**      | The display text of an item or connection. Defaults to the name.  |

### Item types

| Term        | Definition                                                         |
| ----------- | ------------------------------------------------------------------ |
| **process** | A functional unit that processes inputs and generates outputs.      |
| **entity**  | An external actor, outside the scope of the model.                 |
| **store**   | Holds data.                                                        |
| **channel** | Alters the course of flows (data or timing). APIs are channels.    |
| **control** | Receives and emits signals exclusively (SA/RT).                    |
| **none**    | A generic point, e.g. repeated from an upper level.                |

### Connection types

| Term           | Definition                                         |
| -------------- | -------------------------------------------------- |
| **flow**       | Directed data flow.                                |
| **cflow**      | Continuous (streaming) flow.                       |
| **bflow**      | Bidirectional flow.                                |
| **uflow**      | Undirected flow (no arrowheads).                   |
| **signal**     | Directed signal (SA/RT events).                    |
| **constraint** | Invisible layout constraint (not a data flow).     |

### Modifiers

| Term                  | Definition                                                              |
| --------------------- | ----------------------------------------------------------------------- |
| **reversed** (`.r`)   | Connection whose rendering direction is swapped.                        |
| **relaxed** (`?`)     | Connection that does not impose a layout constraint.                    |
| **hidable** (`?`)     | Item hidden from the diagram unless at least one connection references it. |
| **external item**     | Item referencing another graph via the dependency syntax (`GRAPH:NAME`). |
| **inline attributes** | Graphviz attributes in brackets prefixing a label (`[ATTRS]`).          |
| **attribute alias**   | A reusable name for a set of Graphviz attributes (`attrib`).            |

### Including

| Term         | Definition                                                    |
| ------------ | ------------------------------------------------------------- |
| **include**  | Directive (`#include`) to insert content from another source. |
| **snippet**  | A DFD code block embedded in a markdown file.                 |
| **includee** | The source being included.                                    |
| **includer** | The source performing the inclusion.                          |

### Dependencies

| Term           | Definition                                                          |
| -------------- | ------------------------------------------------------------------- |
| **dependency** | A reference from one graph to an item (or the whole graph) of another graph. |

### Filters

| Term                       | Definition                                                                |
| -------------------------- | ------------------------------------------------------------------------- |
| **filter**                 | A statement (`!` or `~`) that manipulates the kept set.                   |
| **Only filter** (`!`)      | Additive: adds items to the kept set.                                     |
| **Without filter** (`~`)   | Subtractive: removes items from the kept set.                             |
| **kept set**               | The set of item names retained after all filters have been processed.     |
| **anchor**                 | An item explicitly listed in a filter (as opposed to its neighbors). Called "listed items" in `doc/README.md`. |
| **neighbor**              | An item reachable from an anchor by traversing connections.               |
| **upstream**               | Toward the source of a flow.                                              |
| **downstream**             | Toward the destination of a flow.                                         |
| **left** / **right**       | Layout-based direction (as rendered by Graphviz), orthogonal to the flow. |
| **direction**              | Upstream, downstream, left, or right.                                     |
| **span**                   | How many levels of neighbors to traverse (`*` = unlimited, or integer).  |
| **"x" flag**               | Suppress anchors: select only neighbors, not the listed items themselves. |
| **"f" flag**               | Suppress frames: remove frames involving the selected items.              |
| **replacement**            | An item that takes over connections from removed items (`=NAME` in Without). |

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
| `SRC`/`DST` | Item name (endpoint), or `*` for an anonymous endpoint (generates a `none`). |
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

Filters manipulate the **kept set** to produce diagram subsets.

### 7.1. Only filter (`!`)

```
! [NEIGHBOUR_SPEC] ITEM_NAME [ITEM_NAME...]
```

Additive: the first `!` initialises the kept set to empty, then adds the
anchors (and optionally their neighbors).

### 7.2. Without filter (`~`)

```
~ [NEIGHBOUR_SPEC] [=REPLACEMENT] ITEM_NAME [ITEM_NAME...]
```

Subtractive: the first `~` initialises the kept set to all names, then
removes the anchors (and optionally their neighbors).

The `=REPLACEMENT` syntax rewires connections from removed items to the
replacement item instead of discarding them.

### 7.3. Neighbour specification

```
DIRECTION[FLAGS]SPAN
```

| Part        | Values                                           |
| ----------- | ------------------------------------------------ |
| `DIRECTION` | `>` downstream, `<` upstream, `<>` both, `[` left, `]` right |
| `FLAGS`     | `x` = suppress anchors (neighbors only), `f` = suppress frames |
| `SPAN`      | `*` = unlimited, or integer distance              |

Examples: `>*` (all downstream), `<>2` (two levels in both directions),
`<>xf2` (two levels, neighbors only, suppress frames).

### 7.4. Filter semantics

Filters are processed **sequentially** in source order:

1. Each `!` adds anchors (and their neighbors) to the kept set.
2. Each `~` removes anchors (and their neighbors) from the kept set.
3. Anchors referenced by a filter must exist and be currently available in
   the kept set; otherwise an error is raised.
4. After all filters are processed, statements are filtered: items not in
   the kept set are dropped, connections with missing endpoints are dropped,
   and frames are trimmed or dropped.
5. Connections whose endpoints have a replacement are rewritten; duplicates
   from replacement are deduplicated.

### 7.5. Syntactic sugar

The `!` or `~` character may be written without a separating space before
arguments (e.g. `!A B` is equivalent to `! A B`).
