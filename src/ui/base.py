"""Abstract base class for UI backends.

This module defines the UIBackend interface that all UI implementations
(CLI, GUI, mobile, web) must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional


class UIBackend(ABC):
    """Abstract interface for UI backends.

    A UI backend combines:
    - IOHandler for input/output
    - ProgramManager for program storage/editing
    - InterpreterEngine for execution
    - UI-specific interaction loop

    Different UIs can implement this interface:
    - CLIBackend: Terminal-based REPL (interactive command mode)
    - CursesBackend: Full-screen terminal UI with visual editor
    - TkBackend: Desktop GUI using Tkinter

    Future/potential backend types (not yet implemented):
    - WebBackend: Browser-based interface

    Note: Non-interactive/batch execution (running programs from command line without UI)
    is intentionally not included as a UIBackend type, as it would contradict the purpose
    of the UIBackend abstraction. Batch execution is better handled outside this framework.

    Usage:
        backend = CLIBackend(io_handler, program_manager)
        backend.start()  # Runs until user exits
    """

    def __init__(self, io_handler, program_manager):
        """Initialize UI backend.

        Args:
            io_handler: IOHandler instance for I/O operations
            program_manager: ProgramManager instance for program storage
        """
        self.io = io_handler
        self.program = program_manager

    @abstractmethod
    def start(self) -> None:
        """Start the UI and run main loop.

        This is the main entry point for the UI. It should:
        1. Initialize any UI components
        2. Run the main interaction loop
        3. Handle user input
        4. Execute commands
        5. Exit cleanly when user quits

        For CLI: This is the REPL (Read-Eval-Print Loop)
        For GUI: This starts the GUI event loop
        For Web: This starts the web server
        """
        pass

    # Optional: Standard commands that backends may implement
    # (CLI implements these, GUI may have different UX)

    def cmd_run(self) -> None:
        """Execute RUN command - run the program."""
        pass

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines.

        Args:
            args: Optional line range (e.g., "10-50", "100-")
        """
        pass

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""
        pass

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command - save to file.

        Args:
            filename: File to save to
        """
        pass

    def cmd_load(self, filename: str) -> None:
        """Execute LOAD command - load from file.

        Args:
            filename: File to load from
        """
        pass

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command - delete line range.

        Args:
            args: Line range (e.g., "10-50", "100")
        """
        pass

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command - renumber lines.

        Args:
            args: Optional new start and increment (e.g., "10,10")
        """
        pass

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP."""
        pass

    def execute_immediate(self, statement: str) -> None:
        """Execute immediate mode statement.

        Args:
            statement: BASIC statement to execute immediately

        Examples:
            PRINT 2+2
            A=5: PRINT A
            FOR I=1 TO 10: PRINT I: NEXT I
        """
        pass
