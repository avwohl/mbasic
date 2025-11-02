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


def _ctrl_key_to_urwid(key_string):
    """
    Convert keybinding string to urwid format.

    Examples:
        "Ctrl+H" -> "ctrl h"
        "Ctrl+Q" -> "ctrl q"
        "/" -> "/"
    """
    if key_string.startswith('Ctrl+'):
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

# Help system - Note: Ctrl+? is actually Ctrl+Shift+/ which terminals send as '?'
# We use '?' key which works universally without conflicting with backspace (Ctrl+H)
HELP_KEY = '?'
HELP_CHAR = '?'
HELP_DISPLAY = '?'

# Menu system (not in JSON, hardcoded)
MENU_KEY = 'ctrl u'
MENU_CHAR = '\x15'
MENU_DISPLAY = 'Ctrl+U'

# Quit
_quit_key = _get_key('editor', 'quit') or 'Ctrl+Q'
QUIT_KEY = _ctrl_key_to_urwid(_quit_key)
QUIT_CHAR = _ctrl_key_to_char(_quit_key)
QUIT_DISPLAY = _quit_key

# Alternative quit (Ctrl+C)
_quit_alt_key = _get_key('editor', 'continue') or 'Ctrl+C'
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_key)
QUIT_ALT_CHAR = _ctrl_key_to_char(_quit_alt_key)
QUIT_ALT_DISPLAY = _quit_alt_key

# Variables watch window (not in JSON, hardcoded)
VARIABLES_KEY = 'ctrl w'
VARIABLES_CHAR = '\x17'
VARIABLES_DISPLAY = 'Ctrl+W'

# Execution stack window (not in JSON, hardcoded)
STACK_KEY = 'ctrl k'
STACK_CHAR = '\x0b'
STACK_DISPLAY = 'Ctrl+K'

# =============================================================================
# Program Management (loaded from JSON)
# =============================================================================

# Run program
_run_key = _get_key('editor', 'run') or 'Ctrl+R'
RUN_KEY = _ctrl_key_to_urwid(_run_key)
RUN_CHAR = _ctrl_key_to_char(_run_key)
RUN_DISPLAY = _run_key

# List program
_list_key = _get_key('editor', 'load') or 'Ctrl+L'
LIST_KEY = _ctrl_key_to_urwid(_list_key)
LIST_CHAR = _ctrl_key_to_char(_list_key)
LIST_DISPLAY = _list_key

# New program
_new_key = _get_key('editor', 'new') or 'Ctrl+N'
NEW_KEY = _ctrl_key_to_urwid(_new_key)
NEW_CHAR = _ctrl_key_to_char(_new_key)
NEW_DISPLAY = _new_key

# Save program
_save_key = _get_key('editor', 'save') or 'Ctrl+S'
SAVE_KEY = _ctrl_key_to_urwid(_save_key)
SAVE_CHAR = _ctrl_key_to_char(_save_key)
SAVE_DISPLAY = _save_key

# Open/Load program (same as load/list)
OPEN_KEY = LIST_KEY
OPEN_CHAR = LIST_CHAR
OPEN_DISPLAY = LIST_DISPLAY

# =============================================================================
# Editing Commands (loaded from JSON where available)
# =============================================================================

# Toggle breakpoint
_breakpoint_key = _get_key('editor', 'toggle_breakpoint') or 'Ctrl+B'
BREAKPOINT_KEY = _ctrl_key_to_urwid(_breakpoint_key)
BREAKPOINT_CHAR = _ctrl_key_to_char(_breakpoint_key)
BREAKPOINT_DISPLAY = _breakpoint_key

# Clear all breakpoints (hardcoded)
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

# Smart Insert Line (not in JSON, hardcoded)
INSERT_LINE_KEY = 'ctrl i'
INSERT_LINE_CHAR = '\x09'  # Same as tab, but urwid distinguishes 'ctrl i' from 'tab'
INSERT_LINE_DISPLAY = 'Ctrl+I'

# =============================================================================
# Debugger Commands (loaded from JSON where available)
# =============================================================================

# Continue execution (Go)
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
        (MENU_DISPLAY, 'Show menu'),
        (HELP_DISPLAY, 'This help'),
        (SETTINGS_DISPLAY, 'Settings'),
        (VARIABLES_DISPLAY, 'Toggle variables watch window'),
        (STACK_DISPLAY, 'Toggle execution stack window'),
    ],
    'Program Management': [
        (RUN_DISPLAY, 'Run program'),
        (LIST_DISPLAY, 'List program'),
        (NEW_DISPLAY, 'New program'),
        (SAVE_DISPLAY, 'Save program'),
        (OPEN_DISPLAY, 'Open/Load program'),
    ],
    'Editing': [
        (BREAKPOINT_DISPLAY, 'Toggle breakpoint on current line'),
        (DELETE_LINE_DISPLAY, 'Delete current line'),
        (INSERT_LINE_DISPLAY, 'Smart insert line between current and next'),
        (RENUMBER_DISPLAY, 'Renumber all lines (RENUM)'),
    ],
    'Debugger (when program running)': [
        (CONTINUE_DISPLAY, 'Continue execution (Go)'),
        (LIST_DISPLAY, 'Step Line - execute all statements on current line'),
        (STEP_DISPLAY, 'Step Statement - execute one statement at a time'),
        (STOP_DISPLAY, 'Stop execution (eXit)'),
        (VARIABLES_DISPLAY, 'Show/hide variables window'),
        (STACK_DISPLAY, 'Show/hide execution stack window'),
    ],
    'Variables Window (when visible)': [
        ('s', 'Cycle sort mode (Name → Accessed → Written → Read → Type → Value)'),
        ('d', 'Toggle sort direction (ascending ↑ / descending ↓)'),
    ],
    'Navigation': [
        (TAB_DISPLAY, 'Switch between editor and output'),
    ],
}

# Quick reference for status bar
STATUS_BAR_SHORTCUTS = f"MBASIC - ? help, {MENU_DISPLAY} menu, {VARIABLES_DISPLAY} vars, {STACK_DISPLAY} stack, {QUIT_DISPLAY} quit"
EDITOR_STATUS = f"Editor - ? help, {MENU_DISPLAY} menu"
OUTPUT_STATUS = f"Output - Up/Down scroll, {TAB_DISPLAY} editor"

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
