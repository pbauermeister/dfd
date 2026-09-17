#!/usr/bin/env python3
"""Check that the CI workflow tests exactly the given Python versions.

The supported versions are listed in the Makefile (PYTHONS, used by
test-matrix) and in the CI workflow's job matrix. The Makefile passes
its list to this script, which fails on a discrepancy without resolving
it. Run from the repository root.

Usage:
    uv run ./tools/check-python-versions.py 3.11 3.12 3.13
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
CI_WORKFLOW = ROOT_DIR / ".github" / "workflows" / "ci.yml"
CI_JOB = "test"


def read_ci_versions() -> list[str]:
    """Return the Python versions of the CI job matrix."""
    workflow = yaml.safe_load(CI_WORKFLOW.read_text())
    try:
        versions = workflow["jobs"][CI_JOB]["strategy"]["matrix"][
            "python-version"
        ]
    except (KeyError, TypeError):
        sys.exit(
            f"ERROR: no python-version matrix in job '{CI_JOB}' of {CI_WORKFLOW}"
        )

    # An unquoted 3.10 would be read as the float 3.1: insist on strings.
    if not all(isinstance(v, str) for v in versions):
        sys.exit(
            f"ERROR: python-version entries must be quoted in {CI_WORKFLOW}"
        )
    return versions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that CI tests exactly the given Python versions."
    )
    parser.add_argument("versions", nargs="+", help="expected versions")
    args = parser.parse_args()

    ci_versions = read_ci_versions()
    if ci_versions != args.versions:
        sys.exit(
            "ERROR: Python version lists differ: "
            f"expected {args.versions} vs {CI_WORKFLOW.name} {ci_versions}"
        )
    print(f"Python versions consistent: {' '.join(args.versions)}")


if __name__ == "__main__":
    main()
