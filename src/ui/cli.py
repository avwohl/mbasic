"""CLI backend for MBASIC interpreter.

This module provides the command-line interface (REPL) backend.
Wraps the existing InteractiveMode class to provide UIBackend interface.
"""

from .base import UIBackend


class CLIBackend(UIBackend):
    """Command-line interface backend.

    Provides traditional REPL (Read-Eval-Print Loop) interface
    with commands like LIST, RUN, SAVE, LOAD, etc.

    Implementation: Wraps the existing InteractiveMode class to reuse
    its command parsing and execution logic.

    Usage:
        from src.iohandler.console import ConsoleIOHandler
        from editing import ProgramManager
        from src.ui.cli import CLIBackend

        io = ConsoleIOHandler()
        program = ProgramManager(def_type_map)
        backend = CLIBackend(io, program)
        backend.start()
    """

    def __init__(self, io_handler, program_manager):
        """Initialize CLI backend.

        Args:
            io_handler: IOHandler instance (typically ConsoleIOHandler)
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Import InteractiveMode here to avoid circular dependency
        from interactive import InteractiveMode

        # Create InteractiveMode and inject our io_handler and program_manager
        self.interactive = InteractiveMode(io_handler)

        # Replace interactive's program manager with ours (for external control)
        # This allows programmatic loading before start()
        self.interactive.program = program_manager

        # Add debugging capabilities
        from .cli_debug import add_debug_commands
        self.debugger = add_debug_commands(self.interactive)

    def start(self) -> None:
        """Start the CLI REPL loop.

        Runs the interactive mode until user exits.
        """
        self.interactive.start()

    # Delegate command methods to InteractiveMode
    # These allow programmatic control (e.g., for testing or embedding)

    def cmd_run(self) -> None:
        """Execute RUN command."""
        self.interactive.cmd_run()

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command."""
        self.interactive.cmd_list(args)

    def cmd_new(self) -> None:
        """Execute NEW command."""
        self.interactive.cmd_new()

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command."""
        self.interactive.cmd_save(filename)

    def cmd_load(self, filename: str) -> None:
        """Execute LOAD command."""
        self.interactive.cmd_load(filename)

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command."""
        self.interactive.cmd_delete(args)

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command."""
        self.interactive.cmd_renum(args)

    def cmd_cont(self) -> None:
        """Execute CONT command."""
        self.interactive.cmd_cont()

    def execute_immediate(self, statement: str) -> None:
        """Execute immediate mode statement."""
        self.interactive.execute_statement(statement)


def get_additional_keybindings():
    """Return additional keybindings for CLI that aren't in the JSON file.

    These are readline keybindings that are handled by Python's readline module,
    not by the keybinding system. They're documented here for completeness.

    NOTE: These keybindings are intentionally NOT in cli_keybindings.json because:
    1. They're provided by readline, not the MBASIC keybinding system
    2. They're only available when readline is installed (platform-dependent)
    3. Users can't customize them through MBASIC settings
    4. They follow standard readline/Emacs conventions (Ctrl+E, Ctrl+K, etc.)

    This separation keeps cli_keybindings.json focused on MBASIC-specific keybindings
    that users can customize, while this function documents readline's built-in keybindings
    for reference in help systems.

    Returns:
        dict: Additional keybindings in the same format as cli_keybindings.json
    """
    try:
        import readline
        readline_available = True
    except ImportError:
        readline_available = False

    if not readline_available:
        # If readline isn't available, return empty dict
        return {}

    # Standard readline/Emacs keybindings available when readline is loaded
    # Note: Ctrl+A is overridden by MBASIC to trigger edit mode
    return {
        "line_editing": {
            "move_end_of_line": {
                "keys": ["Ctrl+E"],
                "primary": "Ctrl+E",
                "description": "Move cursor to end of line"
            },
            "delete_to_end": {
                "keys": ["Ctrl+K"],
                "primary": "Ctrl+K",
                "description": "Delete from cursor to end of line"
            },
            "delete_line": {
                "keys": ["Ctrl+U"],
                "primary": "Ctrl+U",
                "description": "Delete entire line"
            },
            "delete_word": {
                "keys": ["Ctrl+W"],
                "primary": "Ctrl+W",
                "description": "Delete word before cursor"
            },
            "transpose_chars": {
                "keys": ["Ctrl+T"],
                "primary": "Ctrl+T",
                "description": "Transpose (swap) two characters"
            },
            "history_prev": {
                "keys": ["Up Arrow", "Ctrl+P"],
                "primary": "Up Arrow",
                "description": "Previous command in history"
            },
            "history_next": {
                "keys": ["Down Arrow", "Ctrl+N"],
                "primary": "Down Arrow",
                "description": "Next command in history"
            },
            "move_forward_char": {
                "keys": ["Right Arrow", "Ctrl+F"],
                "primary": "Right Arrow",
                "description": "Move cursor forward one character"
            },
            "move_backward_char": {
                "keys": ["Left Arrow", "Ctrl+B"],
                "primary": "Left Arrow",
                "description": "Move cursor backward one character"
            },
            "delete_char": {
                "keys": ["Ctrl+D"],
                "primary": "Ctrl+D",
                "description": "Delete character under cursor"
            },
            "backward_delete_char": {
                "keys": ["Backspace", "Ctrl+H"],
                "primary": "Backspace",
                "description": "Delete character before cursor"
            },
            "tab_complete": {
                "keys": ["Tab"],
                "primary": "Tab",
                "description": "Auto-complete BASIC keywords"
            }
        }
    }
