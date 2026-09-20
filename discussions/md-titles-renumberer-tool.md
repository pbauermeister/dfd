# Markdown titles renumberer as a standalone tool

Date: 2026-09-20
Status: PENDING
Origin: #90 (devlog `devlog/090-script-levels.md`), branch
`refactor/90-script-levels`.

**Prompt:** Extract `tools/doc-renumber-md-titles.py` into its own
GitHub repository and PyPI package, a command-line tool usable from
several projects. This file is the brief for that repository: what
the script does today, what it lacks, what exists elsewhere, and what
the new tool must be. It is copied into the new repository as its
founding devlog once the repository exists.

## 1. What the script does today

`tools/doc-renumber-md-titles.py`, 160 lines, Python 3.11+, stdlib
only (`argparse`, `re`, `dataclasses`). Called as
`tools/doc-renumber-md-titles.py doc/README.md` by `make-doc.sh`.

- Reads a Markdown file, renumbers its ATX titles (`#`, `##`, ...),
  writes back in place; `-o FILE` writes elsewhere, `-o -` to stdout.
- Numbering is `1.`, `1.1.`, `1.1.1.`: indices joined by `.`, a
  trailing dot, a space, then the title text. Each level restarts at 1
  under a new parent; a skipped level (`##` directly to `####`) gets
  the indices of the levels present (`1.1.`), no zero.
- Existing numbering is stripped before renumbering: any prefix of
  dot-terminated alphanumeric groups (`2.3. `, `A. `, `B.2. `).
- The document title: when the lowest heading level occurs exactly
  once, that title is the document title and numbering starts at the
  next level present. Otherwise numbering starts at the lowest level.
  Detected, not configured.
- A title ending in `{-}` is left unnumbered (pandoc convention),
  without consuming an index.
- Lines inside fences opened and closed by a line starting with
  ` ``` ` are copied unchanged (DFD code blocks hold `#` comments).
- Output is the text stripped of leading and trailing blank lines,
  plus one final newline.

## 2. Known gaps

Found by a mutation file during #90 (fences, a skipped level, a `{-}`
title) and by reading the code:

- Tilde fences (`~~~`) are not recognized: a `##` line inside one is
  numbered.
- Fence detection toggles on every line starting with three backticks,
  so a four-backtick fence containing three-backtick lines gets
  desynchronized. The top-level `README.md` of dfd uses four-backtick
  fences for the CLI help; it is not renumbered today.
- Indented code blocks, HTML comments and setext titles are not
  handled.
- The start level is detected, never configured; there is no end
  level.
- No check mode: nothing for CI or a pre-commit hook to report
  "numbering is stale" without rewriting.
- No tests.
- Title matching requires a space after the hashes; `#hashtag` lines
  are left alone, which is correct.

## 3. Existing tools, measured (2026-09-20)

Trials on a copy of dfd's `doc/README.md` (already numbered: the ideal
result is an empty diff) and on the mutation file.

| Candidate                                 | Config          | On `doc/README.md` | On the mutation file                             |
| ----------------------------------------- | --------------- | ------------------ | ------------------------------------------------ |
| `markdown-heading-numbering` 0.1.1 (PyPI) | 1 dep + 1 call  | 0 diff lines       | numbers `##` inside code fences and `{-}` titles |
| remark + `remark-numbered-headings` 0.1.0 | 3 deps + 1 call | 656 diff lines     | format `1-1. `, keeps the old number             |
| pandoc 3.1.3 gfm round trip + Lua filter  | filter to write | 735 diff lines     | not tried: drops fence info strings and tabs     |
| `dumber` 4.1.1 (Rust, 3 stars)            | rustc ≥ 1.97    | not tried          | toolchain newer than the installed 1.75          |
| `AutonumberMarkdown` (C#, 4 stars)        | .NET            | not tried          | last push 2018                                   |
| `md-numbering` (bash gist, 0 stars)       | copy            | not tried          | a bespoke script by someone else                 |

The only near miss, `markdown-heading-numbering` (2 stars, 7 commits,
MIT, one dependency on click, 318 lines): its source has no fence
handling at all; it passes on `doc/README.md` only because the DFD
comments in the fences are single `#` lines, below its
`--start-from-level 2`. It offers what the dfd script lacks: start and
end levels, a `.pre-commit-hooks.yaml`, PyPI packaging.

Conclusion: the niche is open. No published tool is both fence-aware
and configurable.

## 4. Requirements for the new tool

- **Behavior:** section 1 as the baseline, section 2 closed: tilde and
  longer fences per CommonMark (a fence closes only on the same
  character, at least as long), indented code blocks, HTML comments;
  `--start-level N` and `--end-level N` with the single-title
  detection as the default; `--check` exits 1 and names the stale
  titles; `{-}` kept.
- **Interface:** `argparse`; positional files (several); `-o` and `-`
  as today; verb-first name per dfd's `doc/CONVENTIONS.md` "Tooling
  scripts" (the family here is the package, so the command is the
  verb: e.g. `renumber-md-titles`). PyPI names found free on
  2026-09-20: `mdnum`, `md-number-headings`, `heading-numbering`,
  `markdown-number-headings`.
- **Dependencies:** none at runtime. Python 3.11+.
- **Tests:** pytest; the mutation file of #90 as the first fixture,
  dfd's `doc/README.md` as a golden (renumbering it is a no-op), a
  CommonMark fence case per rule above; a `--check` case.
- **Distribution:** PyPI wheel; `.pre-commit-hooks.yaml`; `uv tool
install` works.
- **Repository scaffolding, reused from dfd:** `pyproject.toml` layout
  with uv, ruff and mypy strict config, conventional commits with the
  commit-msg hook, `tools/conventional-commits.py`, the merge gate and
  `release.yml` with python-semantic-release, `make` as the task layer
  (`doc/CONVENTIONS.md` "Tooling scripts", `doc/RELEASING.md`). The
  new repository is the second consumer of the #88 tooling: what has
  to be copied by hand is the measure of what a template repository
  would save.

## 5. Consumers and integration

- dfd: replace `tools/doc-renumber-md-titles.py` by the package in
  the `dev` dependency group and one line in `recipes/doc.sh`;
  extend `make doc` to the top-level `README.md` once four-backtick
  fences are handled. TODO item 13 of dfd tracks this.
- Other projects of the maintainer: to be listed when the tool exists.

## 6. Sequence

1. `gh repo create pbauermeister/<name> --public --clone` from a
   session started in the new clone; copy this file as
   `devlog/001-founding-brief.md`; set this file's status to DONE with
   the link.
2. Scaffold from dfd per section 4, then port the script and the
   tests, then close the gaps of section 2, then publish.
3. Integrate in dfd (section 5).
