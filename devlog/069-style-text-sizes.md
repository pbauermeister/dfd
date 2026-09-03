# 069 — Style Statements for Text Sizes

Date: 2026-09-03

Status: ONGOING

## Requirement

Add three new `style` statements to control text sizes in the generated
diagram, complementing the existing `*-text-width` wrapping options:

- `style item-text-size N` — item label text size (default 10)
- `style connection-text-size N` — connection label text size (default 10)
- `style graph-title-size N` — graph title text size (default 9)

Constraints and decisions:

- Defaults match the previously hardcoded `fontsize` values in the DOT
  templates, so existing diagrams render identically (non-breaking).
- Non-integer values raise a `DfdException` with source context, like the
  existing width options.
- Documentation (`doc/README.md`, `doc/SYNTAX.md`) and `CHANGES.md` updated.
- Version bumps to **1.17.0** — MINOR, per user decision: new non-breaking
  features warrant a MINOR bump (not just PATCH).
- The implementation was hand-written by the user; the agent handles review
  fixes, NR fixtures, and workflow.

## Design

The hand-written implementation (already done, committed as-is on this
branch):

- `config.py`: `DEFAULT_ITEM_TEXT_SIZE`, `DEFAULT_CONNECTION_TEXT_SIZE`,
  `DEFAULT_GRAPH_TITLE_SIZE` constants.
- `model.py`: three new `StyleOption` members and `GraphOptions` fields.
- `dfd.py`: three new `match` cases in `handle_options`; new `get_style_int()`
  helper deduplicating the int-parsing try/except (also adopted by the
  existing width options; fixes a stray `"` in the old error message).
- `rendering/templates.py`: `DOT_FONT_EDGE` / `DOT_FONT_NODE` /
  `DOT_FONT_GRAPH` hardcoded `fontsize` values become format placeholders.
- `rendering/dot.py`: passes the three sizes when formatting templates.
- Docs: new rows in the style tables of `doc/README.md` and `doc/SYNTAX.md`.

Review findings to fix on the branch:

1. **`DOT_GRAPH_NOTITLE` placeholder leak**: it is appended in
   `dot.py` without `.format()`, so with `style no-graph-title` the DOT
   output contains the literal `fontsize={graph_title_size}`. Fix: format it
   with `graph_title_size` at the point of use.
2. **Unused import**: `from typing import Any` in `dfd.py`.

### Implementation steps

1. Commit the user's hand-written implementation as-is.
2. Fix review findings (1) and (2) above.
3. Create NR fixtures:
   - `075-style-text-sizes.dfd` + `.dot`: all three sizes set to
     non-default values, default (titled) graph — exercises
     `DOT_GRAPH_TITLE`, `DOT_FONT_EDGE`, `DOT_FONT_NODE`.
   - `076-style-text-sizes-no-title.dfd` + `.dot`: sizes set with
     `style no-graph-title` — exercises the `DOT_GRAPH_NOTITLE` path
     (regression guard for finding 1).
   - Error path (non-integer value) is already covered by
     `066-err-bad-style-int`.
   - `make nr-review` → inspect → `make nr-regenerate` → commit fixtures and
     golden files together.
4. Mutation smoke-test: mutate the size plumbing (e.g. ignore
   `item_text_size`), confirm the new fixtures fail, revert.
5. `make black`, `make lint`, `make test`; update PR body; mark PR ready.
