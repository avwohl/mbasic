#!/usr/bin/env python3
"""
Generate static HTML documentation for the MBASIC library.

This script reads library metadata from JSON files and generates
markdown documentation pages with download links. The actual .bas files
are copied during the build process to ensure they're always up-to-date.

Usage:
    python3 utils/build_library_docs.py

Output:
    - docs/library/<category>/index.md (category page)
    - docs/library/<category>/*.bas (copied from source)
"""

import json
import shutil
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent

# Categories to build (in order for library index)
CATEGORIES = [
    ("games", "programs", "Games"),
    ("utilities", "programs", "Utilities"),
    ("demos", "programs", "Demos & Tests"),
    ("education", "programs", "Educational Programs"),
    ("business", "programs", "Business Programs"),
    ("telecommunications", "programs", "Telecommunications"),
    ("electronics", "programs", "Electronics"),
    ("data_management", "programs", "Data Management"),
    ("ham_radio", "programs", "Ham Radio"),
]


def build_category(category_key: str, items_key: str = "programs", category_name: str = None):
    """Build documentation for a single category.

    Args:
        category_key: Directory name and JSON filename (e.g., "games")
        items_key: JSON key for items list (e.g., "programs", "games")
        category_name: Display name (defaults to category_key with title case)
    """
    if category_name is None:
        category_name = category_key.replace("_", " ").title()

    print(f"\n{'='*60}")
    print(f"Building {category_name}")
    print(f"{'='*60}")

    # Load metadata
    metadata_path = ROOT / "docs/library" / f"{category_key}.json"
    if not metadata_path.exists():
        print(f"  ⚠  No metadata file: {metadata_path}")
        return False

    with open(metadata_path) as f:
        data = json.load(f)

    # Create output directory
    output_dir = ROOT / "docs/library" / category_key
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean up old .bas files (remove orphans from previous builds)
    print(f"\nCleaning up old {category_name.lower()} files...")
    for old_file in output_dir.glob("*.bas"):
        old_file.unlink()
        print(f"  ✗ Removed {old_file.name}")

    # Copy .bas files from source
    print(f"\nCopying {category_name.lower()} files...")
    items = data.get(items_key, data.get("games", []))  # Backwards compat with "games" key
    copied_count = 0

    for item in items:
        source = ROOT / item["source_path"]
        dest = output_dir / item["filename"]
        if source.exists():
            shutil.copy2(source, dest)
            print(f"  ✓ {item['filename']}")
            copied_count += 1
        else:
            print(f"  ✗ {item['filename']} - source not found: {source}")

    # Generate category index page
    print(f"\nGenerating {category_key}/index.md...")
    md_lines = [
        f"# {data['title']}",
        "",
        data["description"],
        "",
        f"## Available {category_name}",
        ""
    ]

    for item in items:
        md_lines.append(f"### {item['title']}")
        md_lines.append("")
        md_lines.append(item["description"])
        md_lines.append("")

        if "author" in item:
            md_lines.append(f"**Author:** {item['author']}")
        if "year" in item:
            md_lines.append(f"**Year:** {item['year']}")
        if "tags" in item:
            tags = ", ".join(item["tags"])
            md_lines.append(f"**Tags:** {tags}")

        md_lines.append("")
        md_lines.append(f"**[Download {item['filename']}]({item['filename']})**")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Add usage instructions
    md_lines.extend([
        "## How to Use",
        "",
        "1. **Download** the .bas file you want to use",
        "2. **Open MBASIC** in your preferred UI (Web, Tkinter, Curses, or CLI)",
        "3. **Load the file:**",
        "   - **Web/Tkinter UI:** Click File → Open, select the downloaded file",
        "   - **CLI:** Type `LOAD \"filename.bas\"`",
        "4. **Run:** Type `RUN` or press the Run button",
        "",
        f"## About These {category_name}",
        "",
        f"These programs are from the CP/M and early PC era (1970s-1980s), ",
        "preserved from historical archives including OAK, Simtel, and CP/M CD-ROMs.",
        ""
    ])

    # Write index.md
    index_path = output_dir / "index.md"
    with open(index_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"✓ Generated {index_path}")
    print(f"✓ Built {len(items)} {category_name.lower()} ({copied_count} files copied)")
    return True


def main():
    """Main entry point."""
    print("="*60)
    print("Building MBASIC Library Documentation")
    print("="*60)

    total_categories = 0
    for category_key, items_key, category_name in CATEGORIES:
        if build_category(category_key, items_key, category_name):
            total_categories += 1

    print("\n" + "="*60)
    print(f"✓ Successfully built {total_categories}/{len(CATEGORIES)} categories")
    print("="*60)


if __name__ == "__main__":
    main()
