#!/usr/bin/env python3
"""Regenerate the auto-updatable sections of README.md and doc/*.md.

Each section is demarcated by HTML comment markers:

    <!-- AUTO:section-name -->
    ...generated content...
    <!-- /AUTO:section-name -->

Everything between the markers is replaced, then the touched files are
reformatted with prettier so that editor auto-formatting (VSCode +
prettier) produces no further diff. Hand-edited content outside the
markers is never touched.

Environment: VENV (default .venv) locates prettier, installed there by
`make require`.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "tools"
VENV = Path(os.environ.get("VENV", ROOT_DIR / ".venv"))
README = ROOT_DIR / "README.md"
DOC_README = ROOT_DIR / "doc" / "README.md"
DOC_SYNTAX = ROOT_DIR / "doc" / "SYNTAX.md"
PRETTIER = VENV / "node_modules" / ".bin" / "prettier"

# argparse wraps the help text to the terminal width; pin it
HELP_COLUMNS = "80"


# ── section generators ───────────────────────────────────────────────


def generate_cli_help() -> str:
    """CLI help of the dev wrapper, as a fenced code block."""
    result = subprocess.run(
        [sys.executable, ROOT_DIR / "data-flow-diagram", "--help"],
        env={**os.environ, "COLUMNS": HELP_COLUMNS},
        check=True,
        capture_output=True,
        text=True,
    )
    return f"````\n{result.stdout}````"


def generate_doc_toc() -> str:
    """Linked list of the level-2 headings of doc/README.md."""
    lines = []
    for line in DOC_README.read_text().splitlines():
        if not line.startswith("## "):
            continue
        title = line[len("## ") :].rstrip()
        # build a GitHub-compatible anchor
        anchor = re.sub(r"[^a-z0-9 _-]", "", title.lower()).replace(" ", "-")
        lines.append(f"- [{title}](doc/README.md#{anchor})")
    return "\n".join(lines)


def generate_style_table(table: str) -> str:
    """Style options table (readme|syntax), from doc-print-style-table.py."""
    result = subprocess.run(
        [sys.executable, TOOLS_DIR / "doc-print-style-table.py", table],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.rstrip("\n")


# ── generic marker replacement ───────────────────────────────────────


def replace_section(path: Path, section_name: str, new_content: str) -> None:
    """Replace the content between the markers of a section, in place."""
    open_marker = f"<!-- AUTO:{section_name} -->"
    close_marker = f"<!-- /AUTO:{section_name} -->"

    lines = path.read_text().splitlines()
    if open_marker not in lines:
        print(
            f"warning: marker {open_marker} not found in {path} — skipping",
            file=sys.stderr,
        )
        return
    start = lines.index(open_marker)
    end = lines.index(close_marker, start)

    # replace everything between the markers: blank line, content, blank line
    replacement = [open_marker, "", *new_content.splitlines(), "", close_marker]
    lines[start : end + 1] = replacement
    path.write_text("\n".join(lines) + "\n")
    print(f"  - {path.relative_to(ROOT_DIR)}: {section_name} done")


# ── prettier ─────────────────────────────────────────────────────────


def reformat(paths: list[Path]) -> None:
    """Run prettier on the files, or warn when it is not installed."""
    if not os.access(PRETTIER, os.X_OK):
        print(
            f"warning: {PRETTIER} not found (run 'make require')"
            " — skipping reformat",
            file=sys.stderr,
        )
        return
    subprocess.run(
        [PRETTIER, "--log-level", "warn", "--write", *paths], check=True
    )
    print("  - prettier: done")


# ── main ─────────────────────────────────────────────────────────────


def main() -> None:
    print("Updating auto-generated sections...")

    replace_section(README, "cli-help", generate_cli_help())
    replace_section(README, "doc-toc", generate_doc_toc())
    replace_section(DOC_README, "style-table", generate_style_table("readme"))
    replace_section(DOC_SYNTAX, "style-table", generate_style_table("syntax"))

    reformat([README, DOC_README, DOC_SYNTAX])

    print("Done.")


if __name__ == "__main__":
    main()
