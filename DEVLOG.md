## 2026-02-12 00:26 — Top-level README first-glance analysis [PENDING]

**Prompt:** Analyze how the top-level README.md reads at first glance for new users (e.g. on GitHub). List critical show-stopper improvements, then list improvements to make it top-tier.

### How it reads at first glance

A new visitor landing on the GitHub page sees:

1. **Title "DFD"** — followed by a one-liner that clearly states what it does (command-line tool, text to diagram, multiple formats). This is good.
2. **Scope section** — Immediately dives into SA/SD methodology and Edward Yourdon. This is domain-accurate but alienating: most developers don't know what SA/SD is. The Rosetta Lander reference is impressive but niche. A newcomer's first reaction is likely "is this tool for me?" rather than "I want to try this."
3. **Summary section** — Shows a code snippet and a rendered SVG image. This is the "aha moment" but it comes after the academic Scope section. The example is simple and effective, though the DFD source syntax in the code fence looks unfamiliar without any prior explanation.
4. **Syntax and examples** — A single link to the doc/ subfolder. The user must leave the README to learn anything about the syntax.
5. **Dependencies / Installing / Usage** — Practical sections, but the Usage section pastes CLI help output that is outdated (see below).

Overall impression: the README is **functional but not inviting**. It serves existing users who already know what DFDs are, but does little to attract or onboard new users.

### Critical improvements (current show-stoppers)

1. **CLI help output is stale.** The README (lines 76–107) is missing options that the actual CLI has:
   - `--percent-zoom` / `-p` — present but with truncated description
   - `--background-color` / `-b` — present but with truncated description
   - `--version` / `-V` — completely absent
   - `--debug` wording differs ("emits" in README vs "emit" in actual CLI)
   Users copying commands from the README will get inconsistent behavior.

2. **"UML sequence input file" in CLI help.** The positional argument `INPUT_FILE` is described as "UML sequence input file" — this is a DFD tool, not a UML sequence diagram tool. This is confusing and looks like a copy-paste error from another project. (Note: this is in the source code itself, not just the README.)

3. **Example image URL points to `master` branch** (`https://raw.githubusercontent.com/pbauermeister/dfd/master/example.svg`) but the default remote branch is `origin/main`. If the `master` branch no longer exists on GitHub, the image is broken and the README shows nothing visual — which is fatal for a diagramming tool.

4. **The code fence uses `data-flow-diagram example.svg` as the language tag.** On GitHub, this renders as a plain code block with an unrecognized language. The `example.svg` portion looks like a stray artifact to someone unfamiliar with the `--markdown` snippet feature. There is no explanation of what this code block notation means.

### Improvements to make the README top-tier

1. **Lead with a hero image.** Show a visually compelling, moderately complex diagram (like the `complete-example.svg` from doc/) at the very top, before any text. A diagramming tool should sell itself visually.

2. **Add badges.** PyPI version, license, Python version — standard open-source signals that build trust at a glance.

3. **Rewrite the opening as an elevator pitch.** Replace the academic Scope section with a brief, accessible "Why?" paragraph: *"Describe system architectures as text, get diagrams as SVG/PNG/PDF. Version-controlled, diffable, no GUI needed."* Keep the SA/SD/Yourdon reference as a secondary note.

4. **Add a quick-start section** (install + first diagram in 3 steps):
   ```
   pip install data-flow-diagram
   echo 'entity User\nprocess App\nUser --> App  request' | data-flow-diagram -o my-first.svg
   # open my-first.svg
   ```
   This gives users immediate hands-on success.

5. **Show input → output side by side.** Display the DFD source text next to its rendered SVG so the mapping is visually obvious.

6. **Add a feature highlights list** for quick scanning: multiple output formats, markdown embedding, includes/reuse, dependency checking, attribute styling, SA/RT real-time support, frames/grouping.

7. **Fix the example code block.** Either use a plain ``` fence (and explain the syntax separately), or add a brief note explaining the `data-flow-diagram OUTFILE` fence convention.

8. **Make the documentation link more prominent.** Instead of a one-liner "See the documentation page", provide a brief TOC of what the documentation covers (items, connections, frames, styling, includes, dependencies).

9. **Add a "Diagrams as Code" tagline or section.** This is the primary value proposition for developers — text-based diagrams that live in git alongside code. This concept should be front and center.

10. **Regenerate the Usage section from the actual CLI** or, better, remove the pasted help block and instead document the most common invocations as practical examples (single file, markdown mode, format selection, piping from stdin).

## 2026-02-14 — Refactor DSL keyword constants into StrEnum [DONE]

**Prompt:** Refactor the string constants (STYLE..WITHOUT) in model.py into a string-backed enum, with intermediate steps to replace hardcoded strings and add connection-variant constants.

Three incremental steps were applied:

1. **Replace hardcoded string literals** (parser.py): 6 dispatch-table keys (`"flow.r"`, etc.) and 10 keyword strings in `apply_syntactic_sugars()` were replaced with references to model constants. The stale FIXME about a circular dependency was removed. The `"!~"` character check was replaced with `(model.ONLY, model.WITHOUT)`.

2. **Add connection-variant constants** (model.py): introduced `_REVERSED`/`_RELAXED` building blocks and 10 new constants (`FLOW_REVERSED`, `FLOW_RELAXED`, `FLOW_REVERSED_RELAXED`, `CFLOW_*`, `BFLOW_RELAXED`, `UFLOW_RELAXED`, `SIGNAL_*`, `CONSTRAINT_REVERSED`). Updated parser.py dispatch table and `apply_syntactic_sugars()` — the latter was refactored with a `resolve(keyword, relaxed_keyword)` helper to eliminate repetitive `q`/`parts`/`fmt` boilerplate.

3. **Consolidate into `class Keyword(StrEnum)`** (model.py): all 27 keyword constants (17 base + 10 variants) gathered into a single enum. Consumer files (parser.py, dfd.py, dependency_checker.py) updated to use `Keyword.MEMBER` access. `StrEnum` membership means values remain usable as plain strings for parsing, comparison, hashing, and serialization.

Files changed: `model.py`, `parser.py`, `dfd.py`, `dependency_checker.py`. Output verified identical (smoke test).

## 2026-02-17 — Debrief: Non-regression test framework (#023) [DONE]

**Prompt:** Rate our collaborative work on the NR test framework task.

### User feedback

Good interactive analysis and design teamwork. Claude handled the tedious
bulk work (26 test cases, 33 golden files, script logic, renaming cycles)
that would not have been done with patience by hand. Under user guidance,
we also improved the documentation process (task-specific devlog and
CLAUDE.md conventions). This took involvement but would likely have been
postponed indefinitely without AI help. Very pleased by the outcomes.

### Claude feedback

**What went well:**
- The iterative rhythm worked: user sets direction, Claude proposes a
  plan, user spots gaps (missing sections E.3, F.1; preview not showing
  .md SVGs; flat SVG naming; doc-order numbering), Claude executes the
  fix quickly. Each correction round was one exchange, not a prolonged
  back-and-forth.
- Devlog discipline paid off. Having a written design before coding meant
  no wasted implementation — the sed temp-copy approach, the subdirectory
  convention, and the snippet-name stability argument were all validated
  on paper first.
- The tedium-to-value ratio was high: creating 26 fixtures, verifying
  path substitutions, and renaming with cycle-breaking are exactly the
  kind of error-prone mechanical work where AI assistance shines.

**What could have gone better:**
- I initially skipped sections E.3 and F.1 from the doc — the user had
  to point this out. A more systematic checklist (enumerate all doc
  sections, tick off coverage) would have caught this in the planning
  phase.
- The `.md` preview was initially omitted ("not needed"), then needed
  a follow-up fix, then a second fix for flat naming. Thinking through
  the full developer workflow upfront would have avoided two extra rounds.

### Comparative rating

| Dimension               | Rating   | Notes                                      |
| ----------------------- | -------- | ------------------------------------------ |
| Human–AI interaction    | Strong   | Short feedback loops, clear delegation of design (human) vs execution (AI). Above average compared to typical AI-assisted coding where prompts are one-shot. |
| Task difficulty          | Moderate | No algorithmic complexity, but many moving parts (path conventions, sed safety, snippet-name invariants, cycle-breaking renames). |
| Tediousness             | High     | 26 fixtures, 33 golden files, 6 scripts, content-aware renames — ideal AI territory. |
| Outcome quality          | High     | Full doc coverage, regression detection verified, clean devlog, reusable conventions in CLAUDE.md. |

### How to make future teamwork stronger

1. **Checklist-driven coverage.** Before implementing test suites or
   feature sets, have Claude enumerate all source items (doc sections,
   API endpoints, CLI flags) and present a coverage matrix for user
   sign-off. This prevents the "you missed section E.3" pattern.
2. **Workflow walkthrough.** Before finalizing scripts, mentally
   simulate the full developer workflow (create → preview → inspect →
   approve → commit → test → clean) and verify each step produces
   usable output. This catches UX gaps like the missing preview.
3. **Terminology early.** Agreeing on terms (fixtures, golden files)
   at the start avoids documentation inconsistency and rework later.
