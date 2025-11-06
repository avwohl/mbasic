#!/usr/bin/env python3
"""
Web-specific I/O handler for MBASIC interpreter.

Bridges MBASIC I/O (PRINT, INPUT) to NiceGUI web components.
"""

from .base import IOHandler
from nicegui import ui
import asyncio


class WebIOHandler(IOHandler):
    """I/O handler that outputs to NiceGUI log and uses dialogs for input."""

    def __init__(self, output_log):
        """
        Initialize web I/O handler.

        Args:
            output_log: NiceGUI ui.log component for output
        """
        self.output_log = output_log
        self._input_result = None
        self._input_ready = None

    def output(self, text="", end="\n"):
        """
        Output text to the web UI log.

        Args:
            text: Text to print
            end: Line ending (default newline)
        """
        output_str = str(text) + end
        # Remove trailing newline for log display
        if output_str.endswith("\n"):
            output_str = output_str[:-1]

        if output_str:  # Only push non-empty lines
            self.output_log.push(output_str)
        elif end == "\n":  # Empty line with newline
            self.output_log.push("")

    # Backward compatibility alias
    # This method was renamed from print() to output() to avoid conflicts with Python's
    # built-in print function. The print() alias is maintained for backward compatibility
    # with older code that may still call io_handler.print().
    def print(self, text="", end="\n"):
        """Deprecated: Use output() instead.

        This is a backward compatibility alias. New code should use output().
        """
        self.output(text, end)

    def input(self, prompt=""):
        """
        Get input from user via dialog.

        Args:
            prompt: Prompt to display

        Returns:
            User input as string
        """
        # Print the prompt
        if prompt:
            self.print(prompt, end="")

        # Create event for synchronization
        self._input_ready = asyncio.Event()
        self._input_result = None

        # Show input dialog
        with ui.dialog() as dialog, ui.card():
            ui.label(prompt if prompt else 'Input:').classes('text-h6 mb-2')

            input_field = ui.input(
                label='Enter value',
                on_change=lambda e: None
            ).props('autofocus outlined').classes('w-64')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button(
                    'Cancel',
                    on_click=lambda: self._handle_input_cancel(dialog)
                ).props('flat')

                ui.button(
                    'OK',
                    on_click=lambda: self._handle_input_submit(input_field.value, dialog)
                ).props('color=primary')

            # Handle Enter key in input field
            input_field.on('keydown.enter',
                          lambda: self._handle_input_submit(input_field.value, dialog))

        dialog.open()

        # Wait for input (blocking for interpreter thread)
        # This is called from asyncio.to_thread(), so blocking is OK
        import time
        while self._input_result is None:
            time.sleep(0.1)

        result = self._input_result

        # Echo the input to the log
        self.output_log.push(result)

        return result

    def _handle_input_submit(self, value, dialog):
        """Handle input dialog submission."""
        self._input_result = value if value else ""
        dialog.close()

    def _handle_input_cancel(self, dialog):
        """Handle input dialog cancellation."""
        self._input_result = ""
        dialog.close()

    def input_line(self, prompt=""):
        """
        Get a complete line from user via dialog (LINE INPUT statement).

        Args:
            prompt: Prompt to display

        Returns:
            Complete line entered by user

        Note: Current implementation does NOT preserve leading/trailing spaces
        as documented in base class. HTML input fields strip spaces.
        This is a known limitation - see input_line() documentation in base.py.
        For web UI, input() and input_line() work the same way.
        """
        # For web UI, input() and input_line() work the same way
        return self.input(prompt)

    def input_char(self, blocking=True):
        """
        Get single character input (for INKEY$, INPUT$).

        Args:
            blocking: If True, wait for keypress. If False, return "" if no key ready.

        Returns:
            Single character string, or "" if not available

        Note: Character input not supported in web UI (always returns empty string).
        """
        return ""

    # Backward compatibility alias
    # This method was renamed from get_char() to input_char() for consistency with
    # the IOHandler base class interface. The get_char() alias is maintained for
    # backward compatibility with older code.
    def get_char(self):
        """Deprecated: Use input_char() instead.

        This is a backward compatibility alias. New code should use input_char().
        Note: Always calls input_char(blocking=False) for non-blocking behavior.
        The original get_char() implementation was non-blocking, so this preserves
        that behavior for backward compatibility.
        """
        return self.input_char(blocking=False)

    def clear_screen(self):
        """Clear the output log."""
        self.output_log.clear()

    def error(self, message):
        """
        Output error message to the web UI log.

        Args:
            message: Error message to display
        """
        # Output error with prefix to distinguish from regular output
        self.output(f"Error: {message}")

    def debug(self, message):
        """
        Output debug message to the web UI log (if debugging enabled).

        Args:
            message: Debug message to display

        Note: For web UI, debug messages are output like regular messages.
        In production, this could be filtered or sent to browser console.
        """
        # For now, output debug messages to the log
        # Could be enhanced to use browser console or separate debug log
        self.output(f"Debug: {message}")

    def locate(self, row, col):
        """
        Move cursor to specific position (LOCATE statement).

        Args:
            row: Row number (1-based)
            col: Column number (1-based)

        Note: Not applicable for log-based output (no-op for compatibility).
        """
        pass

    def get_cursor_position(self):
        """
        Get current cursor position.

        Returns:
            Tuple of (row, col) where both are 1-based

        Note: Log-based output doesn't track cursor, returns default (1, 1).
        """
        return (1, 1)

    def get_screen_size(self):
        """
        Get terminal size.

        Returns:
            Tuple of (rows, cols) - returns reasonable defaults for web
        """
        return (24, 80)
