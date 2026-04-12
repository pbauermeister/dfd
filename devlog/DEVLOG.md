# General Devlog

Analysis outcomes and informal notes that are not yet tracked by a dedicated
`NNN-short-description.md` file. Owned by Claude; entries are append-only.

---

## 1. 2026-02-12 00:26 — Top-level README first-glance analysis [DONE]

**Prompt:** Analyze how the top-level README.md reads at first glance for new users (e.g. on GitHub). List critical show-stopper improvements, then list improvements to make it top-tier.

Promoted to issue #57 and tracked in
[`devlog/057-readme-overhaul.md`](057-readme-overhaul.md).

## 2. 2026-04-12 — Evaluate GitHub Releases strategy [PENDING]

**Prompt:** Given versions are published to PyPI, GitHub Releases are no longer
actively generated and the releases page shows stale entries.

Options to evaluate: (a) automate GH releases via GitHub Actions on version
tag push, (b) delete stale releases and add a note pointing to PyPI, or
(c) leave as-is. Consider project size and maintenance overhead.

## 3. 2026-04-12 — Add CI/build status badge to README [PENDING]

**Prompt:** If GitHub Actions CI is configured, add a build status badge to the
README badge row. Comparable projects (Mermaid, D2, PlantUML) all show one.
Signals project health to new visitors.
