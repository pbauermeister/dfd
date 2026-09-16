# 075 — Replace Black with ruff format and add ruff check

Date: 2026-09-16

Status: ONGOING

## Requirement

From TODO.md item 1 (GitHub issue #75).

Replace `black` with `ruff format` and add `ruff check`, consolidating
formatting and linting into one tool. mypy stays for type checking.

Scope:

- Add `ruff` to `make require`; drop the system Black dependency
  (Black is currently not installed by `make require` at all).
- `make black` → `make format` (`ruff format`, line length 80, quote
  style preserve), keep a `black` alias target for muscle memory.
- `make lint` runs `ruff check` then mypy; `ruff format --check` added
  so CI (`tox -e py` → `make test`/`make lint`) fails on unformatted
  code.
- Configure ruff in `pyproject.toml`: default rules + ANN401, FBT,
  PLR0917 with `max-positional-args = 3`. PLR0917 replaces the PLR0913
  named in TODO.md and `doc/CONVENTIONS.md`: PLR0913 counts keyword-only
  parameters too, which contradicts the "four or more → keyword-only"
  rule.
- Apply the resulting reformat (11 hunks, 9 files) and fix the current
  violations: 28 default-set hits (18 auto-fixable), 4 FBT boolean
  positional parameters, 1 PLR0917 hit in `tools/`.
- Update `doc/CONVENTIONS.md` tooling paragraph, `CLAUDE.md` Formatting
  section (`make black` → `make format`), TODO.md item 1 → DONE.
- Version bump: PATCH (tooling).

Baseline measured with ruff 0.16.8 on main at 7fe82f9:

| Check                                   | Hits                    |
| --------------------------------------- | ----------------------- |
| `ruff format` vs current Black output   | 11 hunks in 9 files     |
| ruff default rule set                   | 28, 18 auto-fixable     |
| ANN401                                  | 0                       |
| PLR0913 max-args=3 (as written in TODO) | 19, all false positives |
| PLR0917 max-positional-args=3           | 1 (a `tools/` script)   |
| FBT                                     | 4 signatures            |

## Design

No NR fixtures: no behavior change; the existing NR fixtures guard the
lint-driven code edits.

Steps:

1. Tooling config. `[tool.ruff]` in `pyproject.toml`: line length 80,
   quote style preserve, extra rules ANN401, FBT, PLR0917 with
   `max-positional-args = 3`. Makefile: `format` target, `black` kept
   as alias, `ruff` added to `make require`, `all` uses `format`.
   `tools/lint.sh` runs `ruff check` and `ruff format --check` before
   mypy. `tox.ini` deps gain `ruff`.
2. Mechanical pass: `ruff format`, `ruff check --fix` (safe fixes).
   Hand-fix the merged string in `dsl/scanner.py` where ruff emits
   escaped double quotes.
3. Judgment fixes: FBT (four signatures, boolean made keyword-only,
   including single-parameter `set_debug`), PLR0917 (`renumber_title`
   keyword-only), SIM115 in `cli.py` (`noqa`, handle flows out on
   purpose), PLW1510 (`check=False` explicit), plus one-liners (SIM102,
   SIM118, UP031, C403, C408, RUF059, F541, F401).
4. Docs and version: `doc/CONVENTIONS.md` tooling paragraph (PLR0917),
   `CLAUDE.md` Formatting section (`make format`), TODO.md item 1 DONE,
   CHANGES.md 1.17.3.
5. Verify (`make format`, `make lint`, `make test`), self-review against
   Type safety, mark PR ready.
