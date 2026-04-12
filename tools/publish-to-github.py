#!/usr/bin/env python3
"""Publish a GitHub Release for the current version.

Reads the version and changelog from CHANGES.md, tags the repo,
and creates a GitHub Release with dist artifacts attached.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command, printing it first."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, cwd=ROOT_DIR)


def run_output(cmd: list[str]) -> str:
    """Run a command and return its stdout, stripped."""
    return subprocess.run(
        cmd, check=True, capture_output=True, text=True, cwd=ROOT_DIR
    ).stdout.strip()


def extract_version() -> str:
    """Extract the latest version from CHANGES.md."""
    changes = (ROOT_DIR / "CHANGES.md").read_text()
    m = re.search(r"^## Version\s+(\S+?):", changes, re.MULTILINE)
    if not m:
        sys.exit("ERROR: could not extract version from CHANGES.md")
    return m.group(1)


def extract_changelog(version: str) -> str:
    """Extract the changelog entry for a given version."""
    changes = (ROOT_DIR / "CHANGES.md").read_text()
    # find the section for this version
    pattern = rf"^## Version\s+{re.escape(version)}:\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, changes, re.MULTILINE | re.DOTALL)
    if not m:
        return f"Release {version}"
    return m.group(1).strip()


def check_branch():
    """Ensure we are on the main branch with a clean working tree."""
    branch = run_output(["git", "branch", "--show-current"])
    if branch != "main":
        sys.exit(
            f"ERROR: current branch is '{branch}', expected 'main'.\n"
            "Use --no-check to skip this check (e.g. for backfilling)."
        )

    status = run_output(["git", "status", "--porcelain"])
    if status:
        sys.exit(
            "ERROR: working tree is not clean.\n"
            "Commit or stash changes before publishing."
        )


def build():
    """Build sdist and wheel."""
    print("\n--- Building dist artifacts ---")
    run(["python3", "setup.py", "sdist", "bdist_wheel"])


def find_dist_files() -> list[str]:
    """Find dist artifacts to attach to the release."""
    dist_dir = ROOT_DIR / "dist"
    if not dist_dir.exists():
        sys.exit("ERROR: dist/ directory not found.")
    files = sorted(str(p) for p in dist_dir.iterdir() if p.is_file())
    if not files:
        sys.exit("ERROR: no files found in dist/.")
    return files


def tag_version(version: str):
    """Create or update the version tag."""
    tag = f"v{version}"
    print(f"\n--- Tagging {tag} ---")
    run(["git", "tag", "-f", tag])
    run(["git", "push", "origin", tag, "--force"])


def create_release(version: str, changelog: str, dist_files: list[str]):
    """Create or recreate the GitHub Release."""
    tag = f"v{version}"
    print(f"\n--- Creating GitHub Release {tag} ---")

    # delete existing release if present
    result = run(
        ["gh", "release", "view", tag], check=False
    )
    if result.returncode == 0:
        print(f"  Release {tag} exists, deleting...")
        run(["gh", "release", "delete", tag, "-y"])

    # create release with assets
    cmd = [
        "gh", "release", "create", tag,
        "--title", f"v{version}",
        "--notes", changelog,
    ] + dist_files
    run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Publish a GitHub Release for the current version."
    )
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="skip branch and clean-tree checks (for backfilling)",
    )
    args = parser.parse_args()

    # extract version and changelog
    version = extract_version()
    changelog = extract_changelog(version)
    print(f"Version: {version}")
    print(f"Changelog:\n{changelog}\n")

    # safety checks
    if not args.no_check:
        check_branch()
    else:
        print("(branch check skipped)")

    # build
    build()

    # find dist files
    dist_files = find_dist_files()
    print(f"Dist files: {', '.join(Path(f).name for f in dist_files)}")

    # tag and release
    tag_version(version)
    create_release(version, changelog, dist_files)

    print(f"\n=== Done: GitHub Release v{version} published ===")


if __name__ == "__main__":
    main()
