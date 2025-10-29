"""CLI backend for MBASIC interpreter.

This module provides the command-line interface (REPL) backend.
Currently wraps InteractiveMode for backward compatibility.
"""

from .base import UIBackend


class CLIBackend(UIBackend):
    """Command-line interface backend.

    Provides traditional REPL (Read-Eval-Print Loop) interface
    with commands like LIST, RUN, SAVE, LOAD, etc.

    Currently wraps the existing InteractiveMode for backward
    compatibility. In the future, this could be refactored to
    use UIBackend interface more directly.

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
