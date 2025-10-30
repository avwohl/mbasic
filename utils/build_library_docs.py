#!/usr/bin/env python3
"""
Generate static HTML documentation for the MBASIC library.

This script reads library metadata (games.json, etc.) and generates
markdown documentation pages with download links. The actual .bas files
are copied during the build process to ensure they're always up-to-date.

Usage:
    python3 utils/build_library_docs.py

Output:
    - docs/library/games/index.md (main games page)
    - docs/library/games/*.bas (copied from source)
"""

import json
import shutil
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent

def build_games_library():
    """Build the games library documentation."""

    # Load metadata
    metadata_path = ROOT / "docs/library/games.json"
    with open(metadata_path) as f:
        data = json.load(f)

    # Create output directory
    output_dir = ROOT / "docs/library/games"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy .bas files from source
    print("Copying game files...")
    for game in data["games"]:
        source = ROOT / game["source_path"]
        dest = output_dir / game["filename"]
        if source.exists():
            shutil.copy2(source, dest)
            print(f"  ✓ {game['filename']}")
        else:
            print(f"  ✗ {game['filename']} - source not found: {source}")

    # Generate main index page
    print("\nGenerating index.md...")
    md_lines = [
        "# MBASIC Games Library",
        "",
        data["description"],
        "",
        "## Available Games",
        ""
    ]

    for game in data["games"]:
        md_lines.append(f"### {game['title']}")
        md_lines.append("")
        md_lines.append(game["description"])
        md_lines.append("")

        if "author" in game:
            md_lines.append(f"**Author:** {game['author']}")
        if "year" in game:
            md_lines.append(f"**Year:** {game['year']}")
        if "tags" in game:
            tags = ", ".join(game["tags"])
            md_lines.append(f"**Tags:** {tags}")

        md_lines.append("")
        md_lines.append(f"**[Download {game['filename']}]({game['filename']})**")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Add usage instructions
    md_lines.extend([
        "## How to Use",
        "",
        "1. **Download** the .bas file you want to play",
        "2. **Open MBASIC** in your preferred UI (Web, Tkinter, Curses, or CLI)",
        "3. **Load the file:**",
        "   - **Web/Tkinter UI:** Click File → Open, select the downloaded file",
        "   - **CLI:** Type `LOAD \"filename.bas\"`",
        "4. **Run:** Type `RUN` or press the Run button",
        "",
        "## About These Games",
        "",
        "These games are classic BASIC programs from the CP/M and early PC era (1970s-1980s). ",
        "They demonstrate the creativity and programming skills of early computer enthusiasts ",
        "who created engaging games within the constraints of 1980s hardware.",
        ""
    ])

    # Write index.md
    index_path = output_dir / "index.md"
    with open(index_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"✓ Generated {index_path}")
    print(f"\n✓ Built {len(data['games'])} games")

def main():
    """Main entry point."""
    print("Building MBASIC library documentation...\n")
    build_games_library()
    print("\nDone!")

if __name__ == "__main__":
    main()
