#!/usr/bin/env python3
"""
Fix Ctrl+ references in docs/help to use keybinding macros.

This script processes help documentation files and replaces hardcoded
Ctrl+ references with {{kbd:action:ui}} macros.
"""

import re
import sys
from pathlib import Path

# Mapping of Ctrl+ combinations to action names for each UI
KEYBINDING_MAPS = {
    'tk': {
        'Ctrl+N': 'file_new',
        'Ctrl+O': 'file_open',
        'Ctrl+S': 'file_save',
        'Ctrl+Shift+S': 'file_save_as',
        'Ctrl+R': 'run_program',
        'Ctrl+B': 'toggle_breakpoint',
        'Ctrl+W': 'toggle_variables',
        'Ctrl+K': 'toggle_stack',
        'Ctrl+E': 'renumber',
        'Ctrl+H': 'replace',
        'Ctrl+F': 'find',
        'Ctrl+I': 'smart_insert',
        'Ctrl+X': 'cut',
        'Ctrl+C': 'copy',
        'Ctrl+V': 'paste',
        'Ctrl+Q': 'file_quit',
        'Ctrl+?': 'help_topics',
    },
    'curses': {
        'Ctrl+N': 'new',
        'Ctrl+O': 'open',
        'Ctrl+V': 'save',  # Curses uses Ctrl+V for save
        'Ctrl+S': 'save',  # If mentioned, map to save
        'Ctrl+R': 'run',
        'Ctrl+B': 'toggle_breakpoint',
        'Ctrl+T': 'step',
        'Ctrl+C': 'continue',
        'Ctrl+X': 'stop',
        'Ctrl+Q': 'quit',
        'Ctrl+H': 'help',
        'Ctrl+G': 'goto_line',
        'Ctrl+P': 'parse',
        'Ctrl+K': 'step_line',
        'Ctrl+W': None,  # Not available in Curses
        'Ctrl+D': None,  # Delete, not in keybindings
        'Ctrl+A': None,  # Home key alternative
        'Ctrl+E': None,  # End key alternative
        'Ctrl+M': None,  # Maximize window
        'Ctrl+Arrow': None,  # Window movement
    },
    'web': {
        'Ctrl+R': 'run',
        'Ctrl+S': 'save',
        'Ctrl+N': 'new',
        'Ctrl+O': 'open',
        'Ctrl+V': None,  # Browser paste, not our keybinding
        'Ctrl+A': None,  # Browser select all
        'Ctrl+C': None,  # Browser copy
        'Ctrl+G': 'continue',
        'Ctrl+T': 'step',
        'Ctrl+K': None,  # Step line, check if in keybindings
        'Ctrl+Q': 'stop',
        'Ctrl+F': 'find',
        'Ctrl+H': 'replace',
        'F9': 'toggle_breakpoint',
        'F10': 'step',
        'F5': 'continue',
        'F1': 'help',
        'Ctrl+Alt+V': 'toggle_variables',
    },
    'cli': {
        'Ctrl+C': 'stop',
    },
}


def fix_file(filepath: Path, ui: str) -> int:
    """
    Fix Ctrl+ references in a file.

    Args:
        filepath: Path to file
        ui: UI name ('tk', 'curses', 'web', 'cli', or None for common)

    Returns:
        Number of replacements made
    """
    content = filepath.read_text()
    original = content
    replacements = 0

    if ui and ui in KEYBINDING_MAPS:
        mapping = KEYBINDING_MAPS[ui]

        # Sort by length (longest first) to avoid partial matches
        patterns = sorted(mapping.keys(), key=len, reverse=True)

        for ctrl_combo in patterns:
            action = mapping[ctrl_combo]

            # Skip if no mapping (None means keep as-is or handle manually)
            if action is None:
                continue

            # Create macro
            macro = f"{{{{kbd:{action}:{ui}}}}}"

            # Replace in text
            # Match Ctrl+X but not in existing macros or code blocks
            pattern = re.escape(ctrl_combo)

            # Count matches for reporting
            matches = len(re.findall(pattern, content))
            if matches > 0:
                content = re.sub(pattern, macro, content)
                replacements += matches

    # Write back if changed
    if content != original:
        filepath.write_text(content)
        return replacements

    return 0


def main():
    """Process all help files."""
    help_dir = Path(__file__).parent.parent / 'docs' / 'help'

    total_replacements = 0
    files_changed = 0

    # Process UI-specific files in docs/help/ui/{ui}/
    for ui in ['tk', 'curses', 'web', 'cli']:
        ui_dir = help_dir / 'ui' / ui
        if ui_dir.exists():
            for md_file in ui_dir.rglob('*.md'):
                replacements = fix_file(md_file, ui)
                if replacements > 0:
                    print(f"✓ {md_file.relative_to(help_dir)}: {replacements} replacements")
                    total_replacements += replacements
                    files_changed += 1

    # Process common files that are UI-specific (docs/help/common/ui/{ui}/)
    common_ui_dir = help_dir / 'common' / 'ui'
    if common_ui_dir.exists():
        for ui in ['tk', 'curses', 'web', 'cli']:
            ui_subdir = common_ui_dir / ui
            if ui_subdir.exists():
                for md_file in ui_subdir.rglob('*.md'):
                    replacements = fix_file(md_file, ui)
                    if replacements > 0:
                        print(f"✓ {md_file.relative_to(help_dir)}: {replacements} replacements")
                        total_replacements += replacements
                        files_changed += 1

    print()
    print(f"Total: {total_replacements} replacements in {files_changed} files")
    print()
    print("Note: True common files and unmapped shortcuts need manual review")


if __name__ == '__main__':
    main()
