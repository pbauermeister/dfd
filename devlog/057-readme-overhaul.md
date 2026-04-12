# 057 — Overhaul Top-level README for New Users

**Date:** 2026-04-12
**Status:** PENDING

## Requirement

Overhaul the top-level `README.md` to fix stale content and make it inviting
for new users discovering the project on GitHub.

### Critical fixes

1. **CLI help output is stale** — `INPUT_FILE` still described as "UML sequence
   input file", `--background-color` and `--no-graph-title` carry removed
   deprecation notices. Replace with actual `data-flow-diagram --help` output.
2. **URLs point to `master` branch** — Image URL and doc link reference `master`
   but the default branch is `main`. Fix both.
3. **Code fence language tag** — `` ```data-flow-diagram example.svg `` is
   unexplained and renders as unrecognized language on GitHub. Fix or explain.

### Improvements

4. Lead with a hero image (e.g. `complete-example.svg` from `doc/`).
5. Add badges (PyPI version, license, Python version).
6. Rewrite opening as an elevator pitch — move SA/SD reference to a secondary
   note.
7. Add a quick-start section (install + first diagram in 3 steps).
8. Show input → output side by side.
9. Add a feature highlights list.
10. Make the documentation link more prominent with a mini-TOC.
11. Add a "Diagrams as Code" positioning.

## Design

_To be agreed upon before implementation._

## Analysis

### Original analysis (2026-02-12)

The analysis below was originally recorded in `devlog/DEVLOG.md` entry 1. It
has been updated to reflect the current state of the project (2026-04-12).

#### How it reads at first glance

A new visitor landing on the GitHub page sees:

1. **Title "DFD"** — followed by a one-liner that clearly states what it does
   (command-line tool, text to diagram, multiple formats). This is good.
2. **Scope section** — Immediately dives into SA/SD methodology and Edward
   Yourdon. This is domain-accurate but alienating: most developers don't know
   what SA/SD is. The Rosetta Lander reference is impressive but niche. A
   newcomer's first reaction is likely "is this tool for me?" rather than "I
   want to try this."
3. **Summary section** — Shows a code snippet and a rendered SVG image. This is
   the "aha moment" but it comes after the academic Scope section. The example
   is simple and effective, though the DFD source syntax in the code fence looks
   unfamiliar without any prior explanation.
4. **Syntax and examples** — A single link to the `doc/` subfolder. The user
   must leave the README to learn anything about the syntax.
5. **Dependencies / Installing / Usage** — Practical sections, but the Usage
   section pastes CLI help output that is stale (see below).

Overall impression: the README is **functional but not inviting**. It serves
existing users who already know what DFDs are, but does little to attract or
onboard new users.

#### Critical improvements (current show-stoppers)

1. **CLI help output is stale.** The README differs from actual
   `data-flow-diagram --help` output:
   - `INPUT_FILE` described as "UML sequence input file" — the source code was
     fixed (now says "DFD input file") but the README was never updated.
   - `--background-color` carries "(not yet available)" prefix and a
     "deprecated:" suffix that no longer exist in the actual CLI.
   - `--no-graph-title` carries a "deprecated:" suffix that no longer exists in
     the actual CLI.

2. **URLs point to `master` branch.** The image URL
   (`raw.githubusercontent.com/.../master/example.svg`) and the doc link
   (`github.com/.../tree/master/doc/README.md`) both reference `master`, but the
   default branch is `main`. If `master` is ever removed, the image breaks and
   the doc link 404s.

3. **Code fence language tag.** `` ```data-flow-diagram example.svg `` renders
   as an unrecognized language on GitHub. The `example.svg` portion looks like a
   stray artifact to someone unfamiliar with the `--markdown` snippet feature.
   There is no explanation of what this code block notation means.

#### Improvements to make the README top-tier

1. **Lead with a hero image.** Show a visually compelling, moderately complex
   diagram (like the `complete-example.svg` from `doc/`) at the very top, before
   any text. A diagramming tool should sell itself visually.

2. **Add badges.** PyPI version, license, Python version — standard open-source
   signals that build trust at a glance.

3. **Rewrite the opening as an elevator pitch.** Replace the academic Scope
   section with a brief, accessible "Why?" paragraph: _"Describe system
   architectures as text, get diagrams as SVG/PNG/PDF. Version-controlled,
   diffable, no GUI needed."_ Keep the SA/SD/Yourdon reference as a secondary
   note.

4. **Add a quick-start section** (install + first diagram in 3 steps):
   ```
   pip install data-flow-diagram
   echo 'entity User\nprocess App\nUser --> App  request' | data-flow-diagram -o my-first.svg
   # open my-first.svg
   ```

5. **Show input → output side by side.** Display the DFD source text next to its
   rendered SVG so the mapping is visually obvious.

6. **Add a feature highlights list** for quick scanning: multiple output formats,
   markdown embedding, includes/reuse, dependency checking, attribute styling,
   SA/RT real-time support, frames/grouping.

7. **Fix the example code block.** Either use a plain `` ``` `` fence (and
   explain the syntax separately), or add a brief note explaining the
   `` data-flow-diagram OUTFILE `` fence convention.

8. **Make the documentation link more prominent.** Instead of a one-liner "See
   the documentation page", provide a brief TOC of what the documentation covers
   (items, connections, frames, styling, includes, dependencies).

9. **Add a "Diagrams as Code" tagline or section.** This is the primary value
   proposition for developers — text-based diagrams that live in git alongside
   code. This concept should be front and center.

10. **Regenerate the Usage section from the actual CLI** or, better, remove the
    pasted help block and instead document the most common invocations as
    practical examples (single file, markdown mode, format selection, piping from
    stdin).
