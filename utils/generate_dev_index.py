#!/usr/bin/env python3
"""Generate index.md for docs/dev/ with all markdown files listed."""

import os
from pathlib import Path
from datetime import datetime

def generate_dev_index():
    """Generate index.md for docs/dev/ directory."""
    dev_dir = Path(__file__).parent.parent / "docs" / "dev"
    index_file = dev_dir / "index.md"

    # Get all markdown files except index.md and README.md
    md_files = sorted([f for f in dev_dir.glob("*.md") if f.name not in ["index.md", "README.md"]])

    # Get all markdown files in subdirectories
    subdir_files = {}
    for subdir in sorted(dev_dir.iterdir()):
        if subdir.is_dir():
            files = sorted(subdir.glob("*.md"))
            if files:
                subdir_files[subdir.name] = files

    # Generate index content
    content = f"""# Developer Documentation

This section contains implementation notes, design decisions, and development history for the MBASIC project.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
**Total Documents:** {len(md_files) + sum(len(files) for files in subdir_files.values())}

## What's Here

This directory contains documentation for developers working on MBASIC:

- **Implementation Notes** - How features were implemented
- **Design Decisions** - Why things work the way they do
- **Testing Documentation** - Test coverage and methodologies
- **Work in Progress** - Current development tasks
- **Bug Fixes** - Historical fixes and their explanations

## Organization

Documents are organized chronologically as they were created during development. Use the search function or browse by topic below.

## For Contributors

If you're contributing to MBASIC:
1. Read `.claude/CLAUDE.md` for coding guidelines
2. Check `WORK_IN_PROGRESS.md` for current tasks
3. Review relevant implementation docs before making changes
4. Add new docs here when implementing significant features

## Browse by Category

"""

    # Organize files by category based on filename patterns
    categories = {
        "UI Implementation": [],
        "Language Features": [],
        "Testing & Quality": [],
        "Help System": [],
        "File I/O": [],
        "Debugging & Errors": [],
        "Settings & Configuration": [],
        "Refactoring & Cleanup": [],
        "Installation & Packaging": [],
        "Work in Progress": [],
        "Other": []
    }

    for f in md_files:
        name = f.stem
        title = name.replace('_', ' ').title()
        link = f"[{title}]({f.name})"

        # Categorize
        if any(x in name.upper() for x in ['UI', 'TK', 'CURSES', 'WEB', 'VISUAL', 'EDITOR']):
            categories["UI Implementation"].append(link)
        elif any(x in name.upper() for x in ['TEST', 'COVERAGE', 'INVENTORY']):
            categories["Testing & Quality"].append(link)
        elif any(x in name.upper() for x in ['HELP', 'DOCUMENTATION']):
            categories["Help System"].append(link)
        elif any(x in name.upper() for x in ['FILE', 'IO', 'FILESYSTEM']):
            categories["File I/O"].append(link)
        elif any(x in name.upper() for x in ['DEBUG', 'ERROR', 'FIX', 'BUG']):
            categories["Debugging & Errors"].append(link)
        elif any(x in name.upper() for x in ['SETTING', 'CONFIG', 'OPTION']):
            categories["Settings & Configuration"].append(link)
        elif any(x in name.upper() for x in ['REFACTOR', 'CLEANUP', 'CONSOLIDAT']):
            categories["Refactoring & Cleanup"].append(link)
        elif any(x in name.upper() for x in ['INSTALL', 'PACKAGE', 'PYPI', 'PUBLISH', 'DISTRIBUT']):
            categories["Installation & Packaging"].append(link)
        elif any(x in name.upper() for x in ['WORK_IN_PROGRESS', 'TODO', 'WIP']):
            categories["Work in Progress"].append(link)
        elif any(x in name.upper() for x in ['DEF', 'CALL', 'INPUT', 'PRINT', 'DATA', 'RANDOMIZE', 'RUN', 'SYSTEM', 'MID', 'ELSE', 'LOOP', 'GOSUB']):
            categories["Language Features"].append(link)
        else:
            categories["Other"].append(link)

    # Write categories with content
    for category, links in categories.items():
        if links:
            content += f"### {category}\n\n"
            for link in sorted(links):
                content += f"- {link}\n"
            content += "\n"

    # Add subdirectories
    if subdir_files:
        content += "## Subdirectories\n\n"
        for subdir_name, files in subdir_files.items():
            content += f"### {subdir_name}/\n\n"
            for f in files:
                title = f.stem.replace('_', ' ').title()
                link = f"[{title}]({subdir_name}/{f.name})"
                content += f"- {link}\n"
            content += "\n"

    content += """## See Also

- [MBASIC Help](../help/mbasic/index.md) - User-facing documentation
- Search function (top of page) - Find docs by keyword
"""

    # Write the index file
    index_file.write_text(content)
    print(f"✓ Generated {index_file} with {len(md_files)} files")

if __name__ == "__main__":
    generate_dev_index()
