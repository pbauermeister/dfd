# 052 — Align identifiers to glossary

**Date:** 2026-02-19

**Status:** PENDING

**Issue:** https://github.com/pbauermeister/dfd/issues/52

## Requirement

Systematic audit and rename of identifiers (classes, methods, variables,
constants) to match the official terminology in `doc/SYNTAX.md`, making code
and documentation speak the same language.

This is the final task in the refactoring strategy (#34, section J).

### Scope

- Audit all identifiers against the glossary in `doc/SYNTAX.md`.
- Rename local variables where they use informal terms.
- Evaluate identifiers that clash with Python builtins/keywords (`filter`,
  `type`, `input`) and rename where appropriate.
- Update comments and docstrings to match any renamed identifiers.
- Every module will be touched — this is mechanical but pervasive.

### Acceptance criteria

- All identifiers use glossary terms from `doc/SYNTAX.md`.
- `make black && make lint && make test` passes.
- No functional changes — purely renaming.

## Design

*(To be filled during Phase 3 — Specification refinement.)*
