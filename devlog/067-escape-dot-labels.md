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
- `DOT_GRAPH_TITLE` in `rendering/templates.py` interpolates `{title}` into
  `label="..."` unescaped.
- Items rendered with HTML-like labels (`label=<...>`) have *different*
  escaping rules: `&`, `<`, `>` need HTML-entity escaping there.
- Generated `/* N: source line */` comments would break if a source line
  contains `*/` (cosmetic/robustness, same family).
- Item *names* containing `"` also produce invalid DOT (names are emitted
  as `"{name}"` in node declarations, edge endpoints, and frame member
  lists). Same crash class; fixed with the same helper, applied
  consistently so declaration and references still match.

Decision on backslashes (agreed during specification): labels form a small
escape language. Recognized escapes are `\n` (line break, documented),
`\l` / `\r` (reserved for #59 alignment support), and `\\` (literal
backslash). Any other backslash is **stray and rejected with an error** at
check time — e.g. `C:\hello` fails, `C:\\hello` renders `C:\hello`. This
keeps rendering predictable and lets future escapes be added without
silently changing the meaning of existing diagrams.

## Design

| Context                    | Sites                                                | Handling             |
| -------------------------- | ---------------------------------------------------- | -------------------- |
| DSL labels and names       | item names + texts, connection texts, frame texts    | checker error on     |
|                            |                                                      | stray `\`            |
| Double-quoted DOT strings  | item labels (process, control, entity, none/star),   | `"` → `\"`; escapes  |
|                            | item names, edge endpoints + labels, frame labels +  | (`\n` `\l` `\r` `\\`)|
|                            | member refs, graph title                             | forwarded to dot     |
| HTML-like labels           | store + channel `{text}` (and `{name}` is quoted)    | `html.escape`; then  |
|                            |                                                      | `\\` → `\`,          |
|                            |                                                      | `\n` → `<br/>`       |
| DOT `/* */` comments       | `append()` source echo                               | break `*/`           |

Implementation steps:

1. Create NR fixture inputs: `072-label-quotes.dfd` (quotes in labels of all
   plain-label item types, in an item name, in a connection label, in a frame
   label; `\\` and `\n` cases), `073-label-html.dfd` (store and channel
   labels containing `<`, `>`, `&`, `\\`), and `074-err-stray-backslash.dfd`
   (error fixture).
2. Implement: `_check_backslashes()` in `dsl/checker.py` (stray-backslash
   error with source context); `escape` handling in `rendering/dot.py`
   (`_escape_dot_string()` for quotes at all double-quoted emission sites,
   escape translation in `_item_to_html_dict`, `*/` sanitization in
   `append()`). Graph title covered by the same helper, plus unit tests
   (title not reachable from a fixture file).
3. `make nr-regenerate`, inspect outputs, commit fixtures + goldens with the
   fix.
4. `make black`, `make lint`, `make test`; mutation smoke-test each escaping
   / validation path.
5. Bump to 1.16.9, update `CHANGES.md` and `doc/README.md`; update PR body,
   mark ready.

## Outcome

- Checker: stray backslashes in names/labels rejected with
  `Stray backslash in "..."; use \\ for a literal backslash, \n for a line
  break` (error-fixture `074-err-stray-backslash`).
- Renderer: `"` → `\"` at every double-quoted emission site (item names +
  labels, edge endpoints + labels, frame labels + member refs, graph
  title); recognized escapes forwarded to Graphviz. HTML-like labels
  (store/channel): HTML-entity escaping, then `\\` → `\` and
  `\n` → `<br/>` translated left-to-right. `*/` broken in source-echo
  comments.
- `doc/README.md` documents the backslash rule next to the `\n` feature.
- New NR fixtures 072/073/074 and 3 new unit tests (title quoting, escape
  forwarding, stray-backslash error) + 1 checker robustness case. Existing
  77 goldens byte-identical — the changes are a no-op on valid input.
- Mutation smoke-tests: disabling quote escaping fails 072; disabling HTML
  escaping fails 073; disabling the checker rule fails 074 + 2 unit tests.
  All reverted.
- Incidental discovery: a trailing `\` in a DSL line is consumed by the
  scanner as line continuation, so it can never reach a rendered label.
