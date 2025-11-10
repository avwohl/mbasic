"""
Keyboard binding definitions for MBASIC Curses UI.

This module loads keybindings from curses_keybindings.json and provides them
in the format expected by the Curses UI (urwid key names, character codes, display names).

This ensures consistency between the JSON config, the UI behavior, and the documentation.

File location: curses_keybindings.json is located in the src/ui/ directory (same directory as this module).
If you need to modify keybindings, edit that JSON file rather than changing constants here.
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


# Lookup tables for key conversions
_KEY_TO_CHAR_TABLE = {
    'tab': '\t',
    'enter': '\n',
    'backspace': '\x08',
    'esc': '\x1b',
}

_KEY_TO_DISPLAY_TABLE = {
    'enter': 'Enter',
    'esc': 'ESC',
    'tab': 'Tab',
    'backspace': 'Backspace',
    'up': 'Up',
    'down': 'Down',
    'left': 'Left',
    'right': 'Right',
}


def key_to_char(urwid_key):
    """
    Convert urwid key name to character code.

    This is the single source of truth for key character codes.
    We NEVER want separate constants that could get out of sync.

    Examples:
        'ctrl a' -> '\x01'
        'ctrl r' -> '\x12'
        'tab' -> '\t'
        'enter' -> '\n'
        's' -> 's'

    Returns:
        Character code string, or empty string if no single character
    """
    # Check lookup table first
    if urwid_key in _KEY_TO_CHAR_TABLE:
        return _KEY_TO_CHAR_TABLE[urwid_key]

    # Handle ctrl combinations
    if urwid_key.startswith('ctrl '):
        letter = urwid_key[5:].upper()
        # Ctrl+A = 1, Ctrl+B = 2, etc.
        code = ord(letter) - ord('A') + 1
        return chr(code)

    # Single character key
    if len(urwid_key) == 1:
        return urwid_key

    # Multi-key combinations like 'shift ctrl b' don't have single char
    return ''


def key_to_display(urwid_key):
    """
    Convert urwid key name to user-friendly display string.

    This is the single source of truth for how keys are displayed to users.
    We NEVER want to lie about what key does what, so display strings are
    automatically computed from the actual key binding.

    Examples:
        'ctrl a' -> '^A'
        'ctrl r' -> '^R'
        'shift ctrl b' -> '^Shift+B'
        'enter' -> 'Enter'
        'esc' -> 'ESC'
        'tab' -> 'Tab'
        's' -> 's'
        'backspace' -> 'Backspace'
    """
    # Check lookup table first
    if urwid_key in _KEY_TO_DISPLAY_TABLE:
        return _KEY_TO_DISPLAY_TABLE[urwid_key]

    # Handle ctrl combinations
    if urwid_key.startswith('ctrl shift '):
        letter = urwid_key[11:].upper()
        return f'^Shift+{letter}'
    elif urwid_key.startswith('shift ctrl '):
        letter = urwid_key[11:].upper()
        return f'^Shift+{letter}'
    elif urwid_key.startswith('ctrl '):
        letter = urwid_key[5:].upper()
        return f'^{letter}'

    # Single character keys display as-is
    return urwid_key


def _get_key(section, action):
    """Get keybinding from config."""
    if section in _config and action in _config[section]:
        return _config[section][action]['primary']
    return None


# =============================================================================
# Global Commands (loaded from JSON)
# =============================================================================

# Help system
HELP_KEY = 'ctrl f'

# Menu system (not in JSON, hardcoded)
MENU_KEY = 'ctrl u'

# Quit - No dedicated keybinding in QUIT_KEY (most Ctrl keys intercepted by terminal or already assigned)
# Primary method: Use menu (Ctrl+U -> File -> Quit)
# Alternative method: Ctrl+C (interrupt signal) - handled by QUIT_ALT_KEY below
QUIT_KEY = None  # No standard keybinding (use menu or Ctrl+C instead)

# Alternative quit keybinding (loaded from JSON config)
# Note: QUIT_ALT_KEY is loaded from the JSON config (defaults to 'ctrl c')
# and provides an additional way to quit the program via keyboard.
_quit_alt_from_json = _get_key('editor', 'quit')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

# Variables window
_variables_from_json = _get_key('editor', 'variables')
VARIABLES_KEY = _ctrl_key_to_urwid(_variables_from_json) if _variables_from_json else 'ctrl w'

# Execution stack window (menu only - no dedicated key)
STACK_KEY = ''  # No keyboard shortcut

# =============================================================================
# Program Management (loaded from JSON)
# =============================================================================

# Run program
_run_from_json = _get_key('editor', 'run')
RUN_KEY = _ctrl_key_to_urwid(_run_from_json) if _run_from_json else 'ctrl r'

# Step Line - execute all statements on current line (debugger command)
_step_line_from_json = _get_key('editor', 'step_line')
STEP_LINE_KEY = _ctrl_key_to_urwid(_step_line_from_json) if _step_line_from_json else 'ctrl k'

# Open/Load program
_open_from_json = _get_key('editor', 'open')
OPEN_KEY = _ctrl_key_to_urwid(_open_from_json) if _open_from_json else 'ctrl o'

# New program
_new_from_json = _get_key('editor', 'new')
NEW_KEY = _ctrl_key_to_urwid(_new_from_json) if _new_from_json else 'ctrl n'

# Save program
_save_from_json = _get_key('editor', 'save')
SAVE_KEY = _ctrl_key_to_urwid(_save_from_json) if _save_from_json else 'ctrl v'

# =============================================================================
# Editing Commands (loaded from JSON where available)
# =============================================================================

# Toggle breakpoint
_breakpoint_from_json = _get_key('editor', 'toggle_breakpoint')
BREAKPOINT_KEY = _ctrl_key_to_urwid(_breakpoint_from_json) if _breakpoint_from_json else 'ctrl b'

# Clear all breakpoints
_clear_breakpoints_from_json = _get_key('editor', 'clear_all_breakpoints')
CLEAR_BREAKPOINTS_KEY = _ctrl_key_to_urwid(_clear_breakpoints_from_json) if _clear_breakpoints_from_json else 'ctrl shift b'

# Delete current line
_delete_line_from_json = _get_key('editor', 'delete_line')
DELETE_LINE_KEY = _ctrl_key_to_urwid(_delete_line_from_json) if _delete_line_from_json else 'ctrl d'

# Renumber lines
_renumber_from_json = _get_key('editor', 'renumber')
RENUMBER_KEY = _ctrl_key_to_urwid(_renumber_from_json) if _renumber_from_json else 'ctrl e'

# Smart Insert Line
_insert_line_from_json = _get_key('editor', 'insert_line')
INSERT_LINE_KEY = _ctrl_key_to_urwid(_insert_line_from_json) if _insert_line_from_json else 'ctrl y'

# =============================================================================
# Debugger Commands (loaded from JSON where available)
# =============================================================================

# Go to line (also used for Continue execution in debugger context)
# Note: This key serves dual purpose - "Go to line" in editor mode and
# "Continue execution (Go)" in debugger mode. The JSON key is 'goto_line'
# to reflect its primary function, but CONTINUE_KEY name reflects debugger usage.
_continue_from_json = _get_key('editor', 'goto_line')
CONTINUE_KEY = _ctrl_key_to_urwid(_continue_from_json) if _continue_from_json else 'ctrl g'

# Step Statement - execute one statement at a time (debugger command)
_step_from_json = _get_key('editor', 'step')
STEP_KEY = _ctrl_key_to_urwid(_step_from_json) if _step_from_json else 'ctrl t'

# Stop execution
_stop_from_json = _get_key('editor', 'stop')
STOP_KEY = _ctrl_key_to_urwid(_stop_from_json) if _stop_from_json else 'ctrl x'

# Settings
_settings_from_json = _get_key('editor', 'settings')
SETTINGS_KEY = _ctrl_key_to_urwid(_settings_from_json) if _settings_from_json else 'ctrl p'

# Maximize output
_maximize_output_from_json = _get_key('editor', 'maximize_output')
MAXIMIZE_OUTPUT_KEY = _ctrl_key_to_urwid(_maximize_output_from_json) if _maximize_output_from_json else 'ctrl shift m'

# =============================================================================
# Navigation
# =============================================================================

TAB_KEY = 'tab'

# =============================================================================
# Generic UI Keys (standard across all dialogs and widgets)
# =============================================================================

ENTER_KEY = 'enter'
ESC_KEY = 'esc'
BACKSPACE_KEY = 'backspace'
DOWN_KEY = 'down'
UP_KEY = 'up'
LEFT_KEY = 'left'
RIGHT_KEY = 'right'

# =============================================================================
# Variables Window Keys
# =============================================================================

VARS_SORT_MODE_KEY = 's'
VARS_SORT_DIR_KEY = 'd'
VARS_EDIT_KEY = 'e'
VARS_FILTER_KEY = 'f'
VARS_CLEAR_KEY = 'c'

# =============================================================================
# Dialog Keys
# =============================================================================

DIALOG_YES_KEY = 'y'
DIALOG_NO_KEY = 'n'

# =============================================================================
# Settings Window Keys
# =============================================================================

SETTINGS_APPLY_KEY = 'ctrl a'
SETTINGS_RESET_KEY = 'ctrl r'

# =============================================================================
# Keybinding Documentation
# =============================================================================

# All keybindings organized by category for help display
# Note: This dictionary contains keybindings shown in the help system.
# Some defined constants are not included here:
# - CLEAR_BREAKPOINTS_KEY (Shift+Ctrl+B) - Available in menu under Edit > Clear All Breakpoints
# - STOP_KEY (Ctrl+X) - Shown in debugger context in the Debugger category
# - MAXIMIZE_OUTPUT_KEY (Shift+Ctrl+M) - Menu-only feature, not documented as keyboard shortcut
# - STACK_KEY (empty string) - No keyboard shortcut assigned, menu-only
# - Dialog-specific keys (DIALOG_YES_KEY, DIALOG_NO_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY) - Shown in dialog prompts
# - Context-specific keys (VARS_SORT_MODE_KEY, VARS_SORT_DIR_KEY, etc.) - Shown in Variables Window category
KEYBINDINGS_BY_CATEGORY = {
    'Global Commands': [
        (key_to_display(QUIT_ALT_KEY), 'Quit'),
        (key_to_display(MENU_KEY), 'Activate menu bar (arrows navigate, Enter selects)'),
        (key_to_display(HELP_KEY), 'This help'),
        (key_to_display(SETTINGS_KEY), 'Settings'),
        (key_to_display(VARIABLES_KEY), 'Toggle variables window'),
    ],
    'Program Management': [
        (key_to_display(RUN_KEY), 'Run program'),
        (key_to_display(NEW_KEY), 'New program'),
        (key_to_display(OPEN_KEY), 'Open/Load program'),
        (key_to_display(SAVE_KEY), 'Save program'),
    ],
    'Editing': [
        (key_to_display(BREAKPOINT_KEY), 'Toggle breakpoint on current line'),
        (key_to_display(DELETE_LINE_KEY), 'Delete current line'),
        (key_to_display(INSERT_LINE_KEY), 'Insert line'),
        (key_to_display(RENUMBER_KEY), 'Renumber all lines (RENUM)'),
    ],
    'Debugger (when program running)': [
        (key_to_display(CONTINUE_KEY), 'Continue execution (Go)'),
        (key_to_display(STEP_LINE_KEY), 'Step Line - execute all statements on current line'),
        (key_to_display(STEP_KEY), 'Step Statement - execute one statement at a time'),
        (key_to_display(STOP_KEY), 'Stop execution (eXit)'),
        (key_to_display(VARIABLES_KEY), 'Show/hide variables window'),
    ],
    'Variables Window (when visible)': [
        (key_to_display(VARS_SORT_MODE_KEY), 'Cycle sort mode (Name → Accessed → Written → Read → Type → Value)'),
        (key_to_display(VARS_SORT_DIR_KEY), 'Toggle sort direction (ascending ↑ / descending ↓)'),
    ],
    'Navigation': [
        (key_to_display(TAB_KEY), 'Switch between editor and output'),
        (key_to_display(ESC_KEY), 'Cancel dialogs and input prompts'),
    ],
}

# Quick reference for status bar
STATUS_BAR_SHORTCUTS = f"MBASIC - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu  {key_to_display(VARIABLES_KEY)} vars  {key_to_display(STEP_LINE_KEY)} step line  {key_to_display(TAB_KEY)} cycle  ↑↓ scroll"
EDITOR_STATUS = f"Editor - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu  {key_to_display(TAB_KEY)} cycle"
OUTPUT_STATUS = f"Output - {key_to_display(UP_KEY)}/{key_to_display(DOWN_KEY)} scroll  {key_to_display(TAB_KEY)} cycle  {key_to_display(MENU_KEY)} menu"


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

# All control character codes - generated programmatically from Ctrl+A to Ctrl+Z
# Ctrl+A = 1, Ctrl+B = 2, ..., Ctrl+Z = 26
CONTROL_CHARS = {
    f'Ctrl+{chr(ord("A") + i)}': chr(i + 1)
    for i in range(26)
}
