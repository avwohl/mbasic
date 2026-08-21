#!/usr/bin/env python3
"""Locate the BASIC-80 reference manual and extract its text.

The manual is a Microsoft document, so it is not kept in this repository.  It
lives in the retro_docs archive, which collects the vintage manuals that were
duplicated across these projects:

    https://github.com/avwohl/retro_docs/tree/main/mbasic

The help-text generators (extract_statements.py, extract_functions.py) parse it,
so this module finds a local copy and converts it to laid-out text.  Set
MBASIC_BASIC_REF_PDF if your copy lives somewhere the search below misses.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RETRO_DOCS = "https://github.com/avwohl/retro_docs/tree/main/mbasic"
RETRO_DOCS_RAW = "https://raw.githubusercontent.com/avwohl/retro_docs/main/mbasic/basic_ref.pdf"

# Where a local copy might be, in the order we prefer.  A sibling clone of
# retro_docs is the usual case; docs/external/ is where the manual used to live
# before it moved to the archive.
SEARCH_PATHS = (
    REPO_ROOT.parent / "retro_docs" / "mbasic" / "basic_ref.pdf",
    REPO_ROOT / "docs" / "external" / "basic_ref.pdf",
)

# Cached text extraction.  Regenerated whenever the PDF is newer.
LAYOUT_TEXT = Path("/tmp/basic_ref_layout.txt")


def find_basic_ref_pdf() -> Path:
    """Return the path to basic_ref.pdf, or exit explaining how to get it."""
    override = os.environ.get("MBASIC_BASIC_REF_PDF")
    candidates = [Path(override).expanduser()] if override else list(SEARCH_PATHS)

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    searched = "\n".join(f"  {path}" for path in candidates)
    sys.exit(
        f"Cannot find basic_ref.pdf.  Looked in:\n{searched}\n\n"
        f"The manual is not kept in this repository - it lives in {RETRO_DOCS}\n"
        "Either clone the archive next to this one:\n"
        "  git clone git@github.com:avwohl/retro_docs.git ../retro_docs\n"
        "or fetch just the manual and point this script at it:\n"
        f"  curl -Lo /tmp/basic_ref.pdf {RETRO_DOCS_RAW}\n"
        "  MBASIC_BASIC_REF_PDF=/tmp/basic_ref.pdf python3 utils/<script>.py"
    )


def basic_ref_layout_text(pdf: Path | None = None, txt: Path = LAYOUT_TEXT) -> Path:
    """Extract the manual to text with its column layout preserved, and cache it."""
    pdf = pdf or find_basic_ref_pdf()

    if txt.exists() and txt.stat().st_mtime >= pdf.stat().st_mtime:
        return txt

    if shutil.which("pdftotext") is None:
        sys.exit("pdftotext not found - install poppler-utils to read the manual")

    print(f"Extracting text from {pdf}...")
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
    return txt


if __name__ == "__main__":
    print(basic_ref_layout_text())
