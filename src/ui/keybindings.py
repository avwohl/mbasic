"""
Keyboard binding definitions for MBASIC Curses UI.

This module loads keybindings from curses_keybindings.json and provides them
in the format expected by the Curses UI (urwid key names, character codes, display names).

This ensures consistency between the JSON config, the UI behavior, and the documentation.
"""

import json
from pathlib import Path

# Load keybindings from JSON
_config_path = Path(__file__).parent / 'curses_keybindings.json'
with open(_config_path, 'r') as f:
    _config = json.load(f)


def _validate_keybindings():
    """Validate keybindings at module load time.

    Rules:
    1. Control keys must be Ctrl+A through Ctrl+Z (or Shift+Ctrl+A through Shift+Ctrl+Z)
    2. No duplicate key assignments
    """
    seen_keys = {}  # key -> (context, action, description)
    valid_ctrl_keys = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    for context, bindings in _config.items():
        for action, config in bindings.items():
            for key in config.get('keys', []):
                # Validate control keys
                if key.startswith('Ctrl+'):
                    letter = key[5:]
                    if len(letter) != 1 or letter.upper() not in valid_ctrl_keys:
                        raise ValueError(f"Invalid control key '{key}' in {context}.{action}: "
                                       f"Control keys must be Ctrl+A through Ctrl+Z")

                elif key.startswith('Shift+Ctrl+'):
                    letter = key[11:]
                    if len(letter) != 1 or letter.upper() not in valid_ctrl_keys:
                        raise ValueError(f"Invalid control key '{key}' in {context}.{action}: "
                                       f"Control keys must be Shift+Ctrl+A through Shift+Ctrl+Z")

                # Check for duplicates (within same context)
                if key in seen_keys and seen_keys[key][0] == context:
                    prev_action, prev_desc = seen_keys[key][1], seen_keys[key][2]
                    curr_desc = config.get('description', action)
                    raise ValueError(f"Duplicate keybinding '{key}' in {context}:\n"
                                   f"  1) {prev_action}: {prev_desc}\n"
                                   f"  2) {action}: {curr_desc}\n"
                                   f"Each key can only have one function per context.")

                seen_keys[key] = (context, action, config.get('description', action))


# Validate at module load time
_validate_keybindings()


def _ctrl_key_to_urwid(key_string):
    """
    Convert keybinding string to urwid format.

    Examples:
        "Ctrl+H" -> "ctrl h"
        "Ctrl+Q" -> "ctrl q"
        "Shift+Ctrl+L" -> "shift ctrl l"
        "/" -> "/"
    """
    if key_string.startswith('Shift+Ctrl+'):
        letter = key_string[11:].lower()
        return f'shift ctrl {letter}'
    elif key_string.startswith('Ctrl+'):
        letter = key_string[5:].lower()
        return f'ctrl {letter}'
    return key_string.lower()


def _ctrl_key_to_char(key_string):
    """
    Convert keybinding string to control character code.

    Examples:
        "Ctrl+H" -> '\x08'
        "Ctrl+A" -> '\x01'
    """
    if key_string.startswith('Ctrl+'):
        letter = key_string[5:].upper()
        # Ctrl+A = 1, Ctrl+B = 2, etc.
        code = ord(letter) - ord('A') + 1
        return chr(code)
    return key_string


def _get_key(section, action):
    """Get keybinding from config."""
    if section in _config and action in _config[section]:
        return _config[section][action]['primary']
    return None


# =============================================================================
# Global Commands (loaded from JSON)
# =============================================================================

# Help system - use Ctrl+F (mnemonic: F for Find help)
HELP_KEY = 'ctrl f'
HELP_CHAR = '\x06'
HELP_DISPLAY = '^F'

# Menu system (not in JSON, hardcoded)
# Ctrl+U activates the interactive menu bar at the top
# Use arrow keys to navigate, Enter to select, ESC to close
# Note: MENU_DISPLAY uses Ctrl+X notation for internal consistency with other DISPLAY constants.
# The STATUS_BAR_SHORTCUTS below uses ^X notation for compact display in the status bar.
MENU_KEY = 'ctrl u'
MENU_CHAR = '\x15'
MENU_DISPLAY = 'Ctrl+U'

# Keymap window - accessible via menu only (no dedicated key to avoid conflicts with typing)

# Quit - use Ctrl+X (Ctrl+Q/Ctrl+S unavailable due to terminal flow control XON/XOFF)
_quit_key = _get_key('editor', 'quit') or 'Ctrl+X'
QUIT_KEY = _ctrl_key_to_urwid(_quit_key)
QUIT_CHAR = _ctrl_key_to_char(_quit_key)
QUIT_DISPLAY = _quit_key

# Alternative quit (Ctrl+C)
_quit_alt_key = _get_key('editor', 'continue') or 'Ctrl+C'
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_key)
QUIT_ALT_CHAR = _ctrl_key_to_char(_quit_alt_key)
QUIT_ALT_DISPLAY = _quit_alt_key

# Variables watch window
_variables_key = _get_key('editor', 'variables') or 'Ctrl+W'
VARIABLES_KEY = _ctrl_key_to_urwid(_variables_key)
VARIABLES_CHAR = _ctrl_key_to_char(_variables_key)
VARIABLES_DISPLAY = _variables_key

# Execution stack window (menu only - no dedicated key)
# Note: No keyboard shortcut is assigned to avoid conflicts with editor typing.
# The stack window is accessed via the menu system (Ctrl+U -> Debug -> Execution Stack).
STACK_KEY = ''  # No keyboard shortcut
STACK_CHAR = ''
STACK_DISPLAY = 'Menu only'

# =============================================================================
# Program Management (loaded from JSON)
# =============================================================================

# Run program
_run_key = _get_key('editor', 'run') or 'Ctrl+R'
RUN_KEY = _ctrl_key_to_urwid(_run_key)
RUN_CHAR = _ctrl_key_to_char(_run_key)
RUN_DISPLAY = _run_key

# Step Line - execute all statements on current line (debugger command)
# Note: These constants are named LIST_KEY/LIST_CHAR/LIST_DISPLAY for historical reasons
# (originally associated with BASIC's LIST command). They now implement step_line debugger
# functionality, which executes all statements on the current line before pausing again.
# The constants are retained with their original names for backward compatibility with
# existing UI code that references them, but they implement 'step_line' action from the
# JSON configuration, not LIST functionality.
_list_key = _get_key('editor', 'step_line') or 'Ctrl+K'
LIST_KEY = _ctrl_key_to_urwid(_list_key)
LIST_CHAR = _ctrl_key_to_char(_list_key)
LIST_DISPLAY = _list_key

# Open/Load program (Ctrl+O)
_open_key = _get_key('editor', 'open') or 'Ctrl+O'
OPEN_KEY = _ctrl_key_to_urwid(_open_key)
OPEN_CHAR = _ctrl_key_to_char(_open_key)
OPEN_DISPLAY = _open_key

# New program
_new_key = _get_key('editor', 'new') or 'Ctrl+N'
NEW_KEY = _ctrl_key_to_urwid(_new_key)
NEW_CHAR = _ctrl_key_to_char(_new_key)
NEW_DISPLAY = _new_key

# Save program (Ctrl+S unavailable - terminal flow control)
# Use Ctrl+V instead (V for saVe)
_save_key = _get_key('editor', 'save') or 'Ctrl+V'
SAVE_KEY = _ctrl_key_to_urwid(_save_key)
SAVE_CHAR = _ctrl_key_to_char(_save_key)
SAVE_DISPLAY = _save_key

# =============================================================================
# Editing Commands (loaded from JSON where available)
# =============================================================================

# Toggle breakpoint
_breakpoint_key = _get_key('editor', 'toggle_breakpoint') or 'Ctrl+B'
BREAKPOINT_KEY = _ctrl_key_to_urwid(_breakpoint_key)
BREAKPOINT_CHAR = _ctrl_key_to_char(_breakpoint_key)
BREAKPOINT_DISPLAY = _breakpoint_key

# Clear all breakpoints (hardcoded)
# Note: urwid format is 'ctrl shift b', display format is 'Ctrl+Shift+B'
CLEAR_BREAKPOINTS_KEY = 'ctrl shift b'
CLEAR_BREAKPOINTS_DISPLAY = 'Ctrl+Shift+B'

# Delete current line (not in JSON, hardcoded)
DELETE_LINE_KEY = 'ctrl d'
DELETE_LINE_CHAR = '\x04'
DELETE_LINE_DISPLAY = 'Ctrl+D'

# Renumber lines (not in JSON, hardcoded)
RENUMBER_KEY = 'ctrl e'
RENUMBER_CHAR = '\x05'
RENUMBER_DISPLAY = 'Ctrl+E'

# Smart Insert Line (Ctrl+I unavailable - identical to Tab)
# Use Ctrl+J instead (J for inJect/insert)
INSERT_LINE_KEY = 'ctrl j'
INSERT_LINE_CHAR = '\x0a'
INSERT_LINE_DISPLAY = 'Ctrl+J'

# =============================================================================
# Debugger Commands (loaded from JSON where available)
# =============================================================================

# Continue execution (Go) / Go to line
# Note: This key (typically Ctrl+G) is context-sensitive in the UI:
#   - In debugger mode: Continue execution until next breakpoint or end
#   - In editor mode: Go to line number (not yet implemented)
# This module only defines the key constant. The actual context-sensitive behavior is
# implemented in src/ui/curses_ui.py by checking the current program state.
# Loaded from 'goto_line' action in JSON since both uses share the same key.
_continue_key = _get_key('editor', 'goto_line') or 'Ctrl+G'
CONTINUE_KEY = _ctrl_key_to_urwid(_continue_key)
CONTINUE_CHAR = _ctrl_key_to_char(_continue_key)
CONTINUE_DISPLAY = _continue_key

# Step (execute one line)
_step_key = _get_key('editor', 'step') or 'Ctrl+T'
STEP_KEY = _ctrl_key_to_urwid(_step_key)
STEP_CHAR = _ctrl_key_to_char(_step_key)
STEP_DISPLAY = _step_key

# Stop execution (eXit) (not in JSON, hardcoded)
STOP_KEY = 'ctrl x'
STOP_CHAR = '\x18'
STOP_DISPLAY = 'Ctrl+X'

# Clear Output (not in JSON, hardcoded)
CLEAR_OUTPUT_KEY = 'ctrl y'
CLEAR_OUTPUT_CHAR = '\x19'
CLEAR_OUTPUT_DISPLAY = 'Ctrl+Y'

# Note: Ctrl+L is context-sensitive in curses UI:
# - When debugging: Step Line (execute all statements on current line)
# - When editing: List program (same as LIST_KEY)

# Settings
SETTINGS_KEY = 'ctrl p'
SETTINGS_CHAR = '\x10'  # Ctrl+P
SETTINGS_DISPLAY = 'Ctrl+P'

# Maximize output (for games/full-screen programs)
# Note: Changed from Ctrl+O to Ctrl+Shift+M to avoid conflict with Open (Ctrl+O)
MAXIMIZE_OUTPUT_KEY = 'ctrl shift m'
MAXIMIZE_OUTPUT_CHAR = ''  # No single char for Shift+Ctrl+M
MAXIMIZE_OUTPUT_DISPLAY = 'Ctrl+Shift+M'

# =============================================================================
# Navigation
# =============================================================================

# Tab key (switch between editor and output)
TAB_KEY = 'tab'
TAB_CHAR = '\t'
TAB_DISPLAY = 'Tab'

# =============================================================================
# Keybinding Documentation
# =============================================================================

# All keybindings organized by category for help display
KEYBINDINGS_BY_CATEGORY = {
    'Global Commands': [
        (QUIT_DISPLAY, 'Quit'),
        (QUIT_ALT_DISPLAY, 'Quit (alternative)'),
        (MENU_DISPLAY, 'Activate menu bar (arrows navigate, Enter selects)'),
        (HELP_DISPLAY, 'This help'),
        (SETTINGS_DISPLAY, 'Settings'),
        (VARIABLES_DISPLAY, 'Toggle variables watch window'),
        (STACK_DISPLAY, 'Show/hide execution stack window (menu only)'),
    ],
    'Program Management': [
        (RUN_DISPLAY, 'Run program'),
        (NEW_DISPLAY, 'New program'),
        (OPEN_DISPLAY, 'Open/Load program'),
        (SAVE_DISPLAY, 'Save program'),
        ('Shift+Ctrl+V', 'Save As'),
        ('Shift+Ctrl+O', 'Recent files'),
    ],
    'Editing': [
        (BREAKPOINT_DISPLAY, 'Toggle breakpoint on current line'),
        (CLEAR_BREAKPOINTS_DISPLAY, 'Clear all breakpoints'),
        (DELETE_LINE_DISPLAY, 'Delete current line'),
        (INSERT_LINE_DISPLAY, 'Insert line'),
        (RENUMBER_DISPLAY, 'Renumber all lines (RENUM)'),
    ],
    'Debugger (when program running)': [
        (CONTINUE_DISPLAY, 'Continue execution (Go)'),
        (LIST_DISPLAY, 'Step Line - execute all statements on current line'),
        (STEP_DISPLAY, 'Step Statement - execute one statement at a time'),
        (STOP_DISPLAY, 'Stop execution (eXit)'),
        (VARIABLES_DISPLAY, 'Show/hide variables window'),
        (STACK_DISPLAY, 'Show/hide execution stack window (menu only)'),
    ],
    'Variables Window (when visible)': [
        ('s', 'Cycle sort mode (Name → Accessed → Written → Read → Type → Value)'),
        ('d', 'Toggle sort direction (ascending ↑ / descending ↓)'),
    ],
    'Navigation': [
        (TAB_DISPLAY, 'Switch between editor and output'),
        ('ESC', 'Cancel dialogs and input prompts'),
    ],
}

# Quick reference for status bar - use compact ^X notation instead of Ctrl+X
# Note: ^K is "step line" (execute all statements on current line)
#       Stack window is menu-only (Ctrl+U -> Debug -> Execution Stack)
STATUS_BAR_SHORTCUTS = "MBASIC - ^F help  ^U menu  ^W vars  ^K step line  Tab cycle  ^X quit"
EDITOR_STATUS = "Editor - ^F help  ^U menu  Tab cycle"
OUTPUT_STATUS = "Output - Up/Down scroll  Tab cycle  ^U menu"


def dump_keymap():
    """Print the keymap in a formatted table for documentation.

    This is used by `mbasic --dump-keymap` to generate documentation.
    """
    print("# MBASIC Curses UI Keyboard Shortcuts\n")

    for category, bindings in KEYBINDINGS_BY_CATEGORY.items():
        print(f"## {category}\n")
        print("| Key | Action |")
        print("|-----|--------|")

        for key, description in bindings:
            # Escape pipe characters in descriptions
            description = description.replace('|', '\\|')
            print(f"| `{key}` | {description} |")

        print()  # Blank line between categories

# =============================================================================
# Character Code Reference (for testing and documentation)
# =============================================================================

# All control character codes for reference
CONTROL_CHARS = {
    'Ctrl+A': '\x01',
    'Ctrl+B': '\x02',
    'Ctrl+C': '\x03',
    'Ctrl+D': '\x04',
    'Ctrl+E': '\x05',
    'Ctrl+F': '\x06',
    'Ctrl+G': '\x07',
    'Ctrl+H': '\x08',
    'Ctrl+I': '\x09',  # Tab
    'Ctrl+J': '\x0a',  # Newline/LF
    'Ctrl+K': '\x0b',
    'Ctrl+L': '\x0c',
    'Ctrl+M': '\x0d',  # Return/Enter
    'Ctrl+N': '\x0e',
    'Ctrl+O': '\x0f',
    'Ctrl+P': '\x10',
    'Ctrl+Q': '\x11',
    'Ctrl+R': '\x12',
    'Ctrl+S': '\x13',
    'Ctrl+T': '\x14',
    'Ctrl+U': '\x15',
    'Ctrl+V': '\x16',
    'Ctrl+W': '\x17',
    'Ctrl+X': '\x18',
    'Ctrl+Y': '\x19',
    'Ctrl+Z': '\x1a',
}
