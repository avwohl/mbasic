"""
Keyboard binding definitions for MBASIC UI.

This module centralizes all keyboard shortcuts used across the application.
Each keybinding is defined in three forms:
1. key_name: The urwid key name (e.g., 'ctrl a')
2. char_code: The ASCII control character code (e.g., '\x01')
3. display_name: The user-facing name (e.g., 'Ctrl+A')

This ensures consistency across the UI, tests, and documentation.
"""

# =============================================================================
# Global Commands
# =============================================================================

# Help system
HELP_KEY = 'ctrl a'
HELP_CHAR = '\x01'
HELP_DISPLAY = 'Ctrl+A'

# Menu system
MENU_KEY = 'ctrl u'
MENU_CHAR = '\x15'
MENU_DISPLAY = 'Ctrl+U'

# Quit
QUIT_KEY = 'ctrl q'
QUIT_CHAR = '\x11'
QUIT_DISPLAY = 'Ctrl+Q'

# Alternative quit (Ctrl+C)
QUIT_ALT_KEY = 'ctrl c'
QUIT_ALT_CHAR = '\x03'
QUIT_ALT_DISPLAY = 'Ctrl+C'

# Variables watch window
VARIABLES_KEY = 'ctrl w'
VARIABLES_CHAR = '\x17'
VARIABLES_DISPLAY = 'Ctrl+W'

# Execution stack window
STACK_KEY = 'ctrl k'
STACK_CHAR = '\x0b'
STACK_DISPLAY = 'Ctrl+K'

# =============================================================================
# Program Management
# =============================================================================

# Run program
RUN_KEY = 'ctrl r'
RUN_CHAR = '\x12'
RUN_DISPLAY = 'Ctrl+R'

# List program
LIST_KEY = 'ctrl l'
LIST_CHAR = '\x0c'
LIST_DISPLAY = 'Ctrl+L'

# New program
NEW_KEY = 'ctrl n'
NEW_CHAR = '\x0e'
NEW_DISPLAY = 'Ctrl+N'

# Save program
SAVE_KEY = 'ctrl s'
SAVE_CHAR = '\x13'
SAVE_DISPLAY = 'Ctrl+S'

# Open/Load program
OPEN_KEY = 'ctrl o'
OPEN_CHAR = '\x0f'
OPEN_DISPLAY = 'Ctrl+O'

# =============================================================================
# Editing Commands
# =============================================================================

# Toggle breakpoint
BREAKPOINT_KEY = 'ctrl b'
BREAKPOINT_CHAR = '\x02'
BREAKPOINT_DISPLAY = 'Ctrl+B'

# Delete current line
DELETE_LINE_KEY = 'ctrl d'
DELETE_LINE_CHAR = '\x04'
DELETE_LINE_DISPLAY = 'Ctrl+D'

# Renumber lines
RENUMBER_KEY = 'ctrl e'
RENUMBER_CHAR = '\x05'
RENUMBER_DISPLAY = 'Ctrl+E'

# =============================================================================
# Debugger Commands
# =============================================================================

# Continue execution (Go)
CONTINUE_KEY = 'ctrl g'
CONTINUE_CHAR = '\x07'
CONTINUE_DISPLAY = 'Ctrl+G'

# Step (execute one line)
STEP_KEY = 'ctrl t'
STEP_CHAR = '\x14'
STEP_DISPLAY = 'Ctrl+T'

# Stop execution (eXit)
STOP_KEY = 'ctrl x'
STOP_CHAR = '\x18'
STOP_DISPLAY = 'Ctrl+X'

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
        (RENUMBER_DISPLAY, 'Renumber all lines (RENUM)'),
    ],
    'Debugger (when program running)': [
        (CONTINUE_DISPLAY, 'Continue execution (Go)'),
        (STEP_DISPLAY, 'Step - execute one line (sTep)'),
        (STOP_DISPLAY, 'Stop execution (eXit)'),
        (VARIABLES_DISPLAY, 'Show/hide variables window'),
        (STACK_DISPLAY, 'Show/hide execution stack window'),
    ],
    'Navigation': [
        (TAB_DISPLAY, 'Switch between editor and output'),
    ],
}

# Quick reference for status bar
STATUS_BAR_SHORTCUTS = f"MBASIC 5.21 - Press {HELP_DISPLAY} for help, {MENU_DISPLAY} for menu, {VARIABLES_DISPLAY} for variables, {STACK_DISPLAY} for stack, {QUIT_DISPLAY} to quit"
EDITOR_STATUS = f"Editor - Press {HELP_DISPLAY} for help"
OUTPUT_STATUS = f"Output - Use Up/Down to scroll, {TAB_DISPLAY} to return to editor"

# =============================================================================
# Character Code Reference (for testing and documentation)
# =============================================================================

# All control character codes for reference
CONTROL_CHARS = {
    'Ctrl+A': '\x01',  # Help
    'Ctrl+B': '\x02',  # Breakpoint
    'Ctrl+C': '\x03',  # Quit (alternative)
    'Ctrl+D': '\x04',  # Delete line
    'Ctrl+E': '\x05',  # Renumber
    'Ctrl+F': '\x06',  # (available)
    'Ctrl+G': '\x07',  # Continue/Go
    'Ctrl+H': '\x08',  # Backspace (not available)
    'Ctrl+I': '\x09',  # Tab (not available)
    'Ctrl+J': '\x0a',  # Newline/LF (not available)
    'Ctrl+K': '\x0b',  # Stack window
    'Ctrl+L': '\x0c',  # List
    'Ctrl+M': '\x0d',  # Return/Enter (not available)
    'Ctrl+N': '\x0e',  # New
    'Ctrl+O': '\x0f',  # Open
    'Ctrl+P': '\x10',  # (available)
    'Ctrl+Q': '\x11',  # Quit
    'Ctrl+R': '\x12',  # Run
    'Ctrl+S': '\x13',  # Save
    'Ctrl+T': '\x14',  # Step
    'Ctrl+U': '\x15',  # Menu
    'Ctrl+V': '\x16',  # (available)
    'Ctrl+W': '\x17',  # Variables window
    'Ctrl+X': '\x18',  # Stop
    'Ctrl+Y': '\x19',  # (available)
    'Ctrl+Z': '\x1a',  # (available)
}
