# 067 — Escape labels in generated DOT output

Date: 2026-08-05

Status: PENDING

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

## Design

(To be agreed before implementation.)
