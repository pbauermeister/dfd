# 043 — Streamline error handling

**Date:** 2026-02-19

**Status:** PENDING

**Issue:** https://github.com/pbauermeister/dfd/issues/43

## Requirement

Replace the repetitive `prefix = mk_err_prefix_from(src)` +
`raise DfdException(f"{prefix}...")` two-step pattern with a single-call
mechanism. This is task D from the refactoring strategy (#34).

There are ~12 `mk_err_prefix_from` calls and ~30 `raise DfdException`
sites across the codebase. The verbose pattern is error-prone (easy to
forget the prefix) and adds visual noise.

## Design

*(To be filled after approach is chosen and confirmed.)*
