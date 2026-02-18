# 023 — Add a Non-Regression Tests Framework

**Date:** 2026-02-18
**Status:** IN-SPECS

## 1. Requirement

Consider the existing unit tests framework embryo.

Analyze how it could be improved to achieve the same results, but be more Pythonic and use conventions (naming, packages) that are commonly used.

1. Refine this specification
2. Analyze current siuation
3. Propose and plan changes
4. Implement and test changes

### 1.1. Scope

As usual for unit tests, call the internal features by inner access to the Python code.

You may minimally instrument or add features dedicated to testing in the code, if it can avoid mocking.

Running all tests shall be fast enough to not hamper the install-publish process, or possibly, in the future, be included in the process of merging pull requests.

The existing tests check both successes and failures. They shall also become a test for edge cases. They should not test basic nominal cases, which are covered by the non-regression tests.

### 1.2. Developer workflow

Unit tests shall be called like now, as a Makefile target, that can be called separately, or in combination with other targets.

### 1.3. Terminology

- **Fixtures**: mainly DFD snippets
- **Golden data**: TBD
- <enhance list as needed>

### 1.4. Naming conventions

- <enhance list as needed>

## 2. Design

## 3. Implementation decisions

## 4. Implementation summary

## 5. Implementation summary
