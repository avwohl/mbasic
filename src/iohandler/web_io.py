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

    def print(self, text="", end="\n"):
        """
        Output text to the web UI log.

        Args:
            text: Text to print
            end: Line ending (default newline)
        """
        output = str(text) + end
        # Remove trailing newline for log display
        if output.endswith("\n"):
            output = output[:-1]

        if output:  # Only push non-empty lines
            self.output_log.push(output)
        elif end == "\n":  # Empty line with newline
            self.output_log.push("")

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

    def get_char(self):
        """
        Get single character input (for INKEY$).

        Note: Not yet implemented for web UI.
        Returns empty string.
        """
        return ""

    def clear_screen(self):
        """Clear the output log."""
        self.output_log.clear()

    def set_cursor_position(self, row, col):
        """
        Set cursor position.

        Note: Not applicable for log-based output.
        """
        pass

    def get_screen_size(self):
        """
        Get terminal size.

        Returns:
            Tuple of (rows, cols) - returns reasonable defaults for web
        """
        return (24, 80)
