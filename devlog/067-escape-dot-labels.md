# 067 — Escape labels in generated DOT output

Date: 2026-08-05

Status: DONE

## Requirement

From issue [#67](https://github.com/pbauermeister/dfd/issues/67):

Any item or connection whose label contains a double quote produces invalid
DOT and crashes rendering:

```
entity E name with "quotes"
```

generates

```
"E" [shape=rectangle label="name with "quotes"" ]
```

and `dot` fails with a syntax error.

Confirmed scope:

- **Node labels** — all item types that use plain `label="..."` attributes.
- **Edge labels** — `P --> S data "x"` produces `[label="data "x""]`, same
  crash.

Likely also affected (to verify during the task):

- `DOT_GRAPH_TITLE` in `rendering/templates.py` interpolates `{title}` into
  `label="..."` unescaped.
- Items rendered with HTML-like labels (`label=<...>`) have *different*
  escaping rules: `&`, `<`, `>` need HTML-entity escaping there.
- Generated `/* N: source line */` comments would break if a source line
  contains `*/` (cosmetic/robustness, same family).

Expected: label values must be escaped for the DOT context they are emitted
into (`\"` inside double-quoted attribute values; HTML entities inside
HTML-like labels), so that any user-provided text renders instead of
crashing.

Additional finding during design: item *names* containing `"` also produce
invalid DOT (names are emitted as `"{name}"` in node declarations, edge
endpoints, and frame member lists). Same crash class; included in the fix
with the same helper, applied consistently so declaration and references
still match.

## Design

Emission sites in `rendering/dot.py` / `rendering/templates.py`:

| Context                    | Sites                                                | Escaping           |
| -------------------------- | ---------------------------------------------------- | ------------------ |
| Double-quoted DOT strings  | item labels (process, control, entity, none/star),   | `"` → `\"`,        |
|                            | item names, edge endpoints + labels, frame labels +  | stray `\` → `\\`   |
|                            | member refs, graph title                             |                    |
| HTML-like labels           | store + channel `{text}` (and `{name}` is quoted)    | `html.escape`      |
| DOT `/* */` comments       | `append()` source echo                               | break `*/`         |

Backslash rule (refined on user request): a *stray* backslash — one not
starting a recognized Graphviz label escape (`\n`, `\l`, `\r`, `\\`) — is
escaped to `\\` so it renders literally and cannot eat the closing quote
(e.g. a label ending in `\`). Recognized escapes are deliberately forwarded
to Graphviz: `\n` is the DSL's documented line-break, `\l`/`\r` are reserved
for TODO #59 alignment support.

Implementation steps:

1. Create NR fixture inputs: `072-label-quotes.dfd` (quotes in labels of all
   plain-label item types, in an item name, in a connection label, in a frame
   label) and `073-label-html.dfd` (store and channel labels containing `<`,
   `>`, `&`).
2. Implement escaping in `rendering/dot.py`: `escape_dot_string()` helper
   applied at all double-quoted emission sites; `html.escape()` in
   `_item_to_html_dict` (before the `\n` → `<br/>` substitution); sanitize
   `*/` in `append()` comments. Graph title covered by the same helper, plus
   a unit test (title with quote) since the title is not reachable from a
   fixture file.
3. `make nr-regenerate`, inspect SVGs, commit fixtures + goldens with the fix.
4. `make black`, `make lint`, `make test`; mutation smoke-test: disable the
   escaping, confirm 072/073 fail, revert.
5. Bump to 1.16.9, update `CHANGES.md`; update PR body, mark ready.

## Outcome

- `_escape_dot_string()` in `rendering/dot.py` escapes `"` and stray `\` at
  every double-quoted emission site (item names + labels, edge endpoints +
  labels, frame labels + member refs, graph title); `html.escape()` covers
  the store/channel HTML-like labels; `*/` is broken in source-echo comments.
- New NR fixtures `072-label-quotes` (incl. quoted item name, backslash
  cases, `\"` combination) and `073-label-html`; two new unit tests cover
  the graph title and backslash rules. Existing 77 goldens byte-identical —
  escaping is a no-op on all previous fixtures.
- Mutation smoke-test: disabling `_escape_dot_string` fails 072 + 2 unit
  tests; disabling `html.escape` fails 073. Both reverted.
- Incidental discovery: a trailing `\` in a DSL line is consumed by the
  scanner as line continuation, so it can never reach a rendered label.
