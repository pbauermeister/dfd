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

| Term           | Definition                                                                 |
| -------------- | -------------------------------------------------------------------------- |
| **statement**  | A single logical line of DFD source (after preprocessing).                 |
| **item**       | A node in the diagram. Never use "node" in prose; that is a Graphviz term. |
| **connection** | A directed or undirected link between two items.                           |
| **endpoint**   | The source or destination item of a connection (`SRC` / `DST`).            |
| **frame**      | A visual grouping (subgraph) of items.                                     |
| **name**       | The unique identifier of an item (no whitespace).                          |
| **label**      | The display text of an item or connection. Defaults to the name.           |

### Item types

| Term        | Definition                                                      |
| ----------- | --------------------------------------------------------------- |
| **process** | A functional unit that processes inputs and generates outputs.  |
| **entity**  | An external actor, outside the scope of the model.              |
| **store**   | Holds data.                                                     |
| **channel** | Alters the course of flows (data or timing). APIs are channels. |
| **control** | Receives and emits signals exclusively (SA/RT).                 |
| **none**    | A generic point, e.g. repeated from an upper level.             |

### Connection types

| Term           | Definition                                     |
| -------------- | ---------------------------------------------- |
| **flow**       | Directed data flow.                            |
| **cflow**      | Continuous (streaming) flow.                   |
| **bflow**      | Bidirectional flow.                            |
| **uflow**      | Undirected flow (no arrowheads).               |
| **signal**     | Directed signal (SA/RT events).                |
| **constraint** | Invisible layout constraint (not a data flow). |

### Modifiers

| Term                  | Definition                                                                 |
| --------------------- | -------------------------------------------------------------------------- |
| **reversed** (`.r`)   | Connection whose rendering direction is swapped.                           |
| **relaxed** (`?`)     | Connection that does not impose a layout constraint.                       |
| **hidable** (`?`)     | Item hidden from the diagram unless at least one connection references it. |
| **external item**     | Item referencing another graph via the dependency syntax (`GRAPH:NAME`).   |
| **inline attributes** | Graphviz attributes in brackets prefixing a label (`[ATTRS]`).             |
| **attribute alias**   | A reusable name for a set of Graphviz attributes (`attrib`).               |

### Including

| Term         | Definition                                                    |
| ------------ | ------------------------------------------------------------- |
| **include**  | Directive (`#include`) to insert content from another source. |
| **snippet**  | A DFD code block embedded in a markdown file.                 |
| **includee** | The source being included.                                    |
| **includer** | The source performing the inclusion.                          |

### Dependencies

| Term           | Definition                                                                   |
| -------------- | ---------------------------------------------------------------------------- |
| **dependency** | A reference from one graph to an item (or the whole graph) of another graph. |

### Filters

| Term                          | Definition                                                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **filter**                    | A statement (`!` or `~`) that manipulates the kept set.                                                        |
| **Only filter** (`!`)         | Additive: adds items to the kept set.                                                                          |
| **strict Only filter** (`!!`) | As `!`, but the items it selects show only their path flows.                                                   |
| **path flow**                 | A flow followed by a filter to reach a neighbor.                                                               |
| **stray flow**                | A flow between kept items that is on no path of a strict filter: hidden by `!!`.                               |
| **Without filter** (`~`)      | Subtractive: removes items from the kept set.                                                                  |
| **kept set**                  | The set of item names retained after all filters have been processed.                                          |
| **anchor**                    | An item explicitly listed in a filter (as opposed to its neighbors). Called "listed items" in `doc/README.md`. |
| **neighbor**                  | An item reachable from an anchor by traversing connections.                                                    |
| **upstream**                  | Toward the source of a flow.                                                                                   |
| **downstream**                | Toward the destination of a flow.                                                                              |
| **left** / **right**          | Layout-based direction (as rendered by Graphviz), orthogonal to the flow.                                      |
| **direction**                 | Upstream, downstream, left, or right.                                                                          |
| **span**                      | How many levels of neighbors to traverse (`*` = unlimited, or integer).                                        |
| **"x" flag**                  | Suppress anchors: select only neighbors, not the listed items themselves.                                      |
| **"f" flag**                  | Suppress frames: remove frames involving the selected items.                                                   |
| **merge**                     | A statement collapsing items into a replacer, which takes over their connections (`merge ITEMS : REPLACER`).   |

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

| Token       | Values                                                                       |
| ----------- | ---------------------------------------------------------------------------- |
| `CONN_TYPE` | `flow`, `cflow`, `bflow`, `uflow`, `signal`, `constraint`                    |
| `SRC`/`DST` | Item name (endpoint), or `*` for an anonymous endpoint (generates a `none`). |
| `LABEL`     | Optional free text. May start with `[ATTRS]`.                                |

### Variants

Keyword variants encode direction and constraint behaviour:

| Suffix | Meaning                              | Example   |
| ------ | ------------------------------------ | --------- |
| `.r`   | Reversed (swap src/dst in rendering) | `flow.r`  |
| `?`    | Relaxed (no layout constraint)       | `flow?`   |
| `.r?`  | Both reversed and relaxed            | `flow.r?` |

Not all combinations exist for all types. See `model.Keyword` for the
full enumeration.

### Arrow sugar (syntactic sugar)

```
SRC ARROW DST [LABEL]
```

Arrows are rewritten to keyword form before parsing:

| Arrow pattern | Keyword equivalent | Notes               |
| ------------- | ------------------ | ------------------- |
| `-->`         | `flow`             | Shaft of any length |
| `<--`         | `flow.r`           | Reversed            |
| `->>`         | `cflow`            | Continuous flow     |
| `<<-`         | `cflow.r`          | Reversed            |
| `<->`         | `bflow`            | Bidirectional       |
| `---`         | `uflow`            | Undirected          |
| `::>`         | `signal`           | Signal              |
| `<::`         | `signal.r`         | Reversed signal     |
| `>>`          | `constraint`       | Layout constraint   |
| `<<`          | `constraint.r`     | Reversed constraint |

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

<!-- AUTO:style-table -->

| Option                  | Value   | Default | Effect                                                                            |
| ----------------------- | ------- | ------- | --------------------------------------------------------------------------------- |
| `horizontal`            | -       | -       | Layouts flows in the horizontal direction (the default).                          |
| `vertical`              | -       | -       | Layouts flows in the vertical direction.                                          |
| `rotated`               | -       | -       | Rotates the diagram by 90°.                                                       |
| `unrotated`             | -       | -       | Reverts the diagram rotation, if any.                                             |
| `context`               | -       | -       | Makes the diagram a context diagram.                                              |
| `item-text-width`       | integer | 20      | Sets the items labels wrapping to use N chars columns.                            |
| `item-text-size`        | integer | 10      | Sets the items label text size.                                                   |
| `connection-text-width` | integer | 14      | Sets the connections labels wrapping to use N chars columns.                      |
| `connection-text-size`  | integer | 10      | Sets the connections label text size.                                             |
| `background-color`      | color   | -       | Sets a graph background color as per https://graphviz.org/docs/attr-types/color/. |
| `no-graph-title`        | -       | -       | Suppress graph title containing the image file path (without extension).          |
| `graph-title-size`      | integer | 9       | Sets the graph title text size.                                                   |

<!-- /AUTO:style-table -->

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

## 7. Filters and merge

Filters manipulate the **kept set** to produce diagram subsets. A merge
collapses items into one. Both serve to derive subgraphs or simplified
graphs from a master graph that carries all the details (see § 6).

### 7.1. Only filter (`!`)

```
! [NEIGHBOUR_SPEC] ITEM_NAME [ITEM_NAME...]
```

Additive: the first `!` initialises the kept set to empty, then adds the
anchors (and optionally their neighbors).

```
!! [NEIGHBOUR_SPEC] ITEM_NAME [ITEM_NAME...]
```

Strict: as `!`, and the items it selects show only their path flows (see
§ 7.5). Strictness applies to the whole filter, whatever the neighbour
specification. There is no `~~`.

### 7.2. Without filter (`~`)

```
~ [NEIGHBOUR_SPEC] ITEM_NAME [ITEM_NAME...]
```

Subtractive: the first `~` initialises the kept set to all names, then
removes the anchors (and optionally their neighbors).

### 7.3. Merge (`merge`)

```
merge ITEM_NAME [ITEM_NAME...] : REPLACER
```

Collapses the items into the replacer, i.e. an item declared elsewhere.
Their connections are rewired to it, and a connection between two merged
items disappears. The items become unavailable, and the replacer takes
their place in the kept set. A merge is not a filter: the kept set is
otherwise untouched, and once a kept set exists, a merge can only name
kept items. Merges are processed in source order with the filters, and
they chain (`merge B C : G` then `merge G D : H`). The merged items must
be in one frame or all unframed, otherwise an error is raised; the
replacer takes their place in that frame. A replacer declared in a frame
that would also inherit one ends up in multiple frames, which is an
error.

### 7.4. Neighbour specification

```
DIRECTION[FLAGS]SPAN
```

| Part        | Values                                                         |
| ----------- | -------------------------------------------------------------- |
| `DIRECTION` | `>` downstream, `<` upstream, `<>` both, `[` left, `]` right   |
| `FLAGS`     | `x` = suppress anchors (neighbors only), `f` = suppress frames |
| `SPAN`      | `*` = unlimited, or integer distance                           |

A filter takes one specification, and `<>` counts as one; a second is an
error. Another neighbourhood is another filter with the same items.

Examples: `>*` (all downstream), `<>2` (two levels in both directions),
`<>xf2` (two levels, neighbors only, suppress frames).

### 7.5. Filter and merge semantics

Filters and merges are processed **sequentially** in source order:

1. Each `!` adds anchors (and their neighbors) to the kept set.
2. Each `~` removes anchors (and their neighbors) from the kept set.
3. Each `merge` rewires the connections of its items to the replacer;
   the filters that follow read the connections as rewired.
4. Anchors referenced by a filter, and the items and replacer of a merge,
   must exist and be available: not removed by a previous `~`, not merged
   away; the items of a merge must be kept once a kept set exists;
   otherwise an error is raised, naming the statement that removed or
   merged the item.
5. After all statements are processed, the diagram is filtered: items not
   in the kept set (and merged items) are dropped, connections with missing
   endpoints are dropped, frames are trimmed or dropped (a replacer takes
   the place of merged items in the one frame that held them all).
6. Connections whose endpoints were merged are rewritten; duplicates from
   merging are deduplicated.
7. Stray flows are dropped. A flow is a stray flow when it touches an item
   selected by a `!!` filter, and neither is a path flow of some `!!` filter
   nor joins two items named together by a `!` filter. Constraints are never
   stray flows. Without any `!!`, nothing is dropped by this step.

### 7.6. Syntactic sugar

The `!`, `!!` or `~` mnemonic may be written without a separating space
before arguments (e.g. `!A B` is equivalent to `! A B`).
