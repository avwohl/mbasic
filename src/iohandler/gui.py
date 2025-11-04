"""GUI-based I/O handler stub for visual UIs.

This module provides a stub/example implementation of IOHandler for GUI
applications. Visual UI developers should subclass GUIIOHandler and
implement the methods for their specific UI framework (Kivy, BeeWare, etc.).
"""

from .base import IOHandler


class GUIIOHandler(IOHandler):
    """GUI-based I/O handler stub.

    This is a minimal stub implementation showing how to create a custom
    I/O handler for GUI applications. Visual UI developers should:

    1. Subclass this class (or IOHandler directly)
    2. Implement each method to interact with their UI widgets
    3. Pass the custom handler to InterpreterEngine

    Example:
        class MyGUIHandler(GUIIOHandler):
            def __init__(self, output_widget, input_callback):
                self.output_widget = output_widget
                self.input_callback = input_callback

            def output(self, text, end='\\n'):
                self.output_widget.append(text + end)

            def input(self, prompt=''):
                return self.input_callback(prompt)
            ...
    """

    def __init__(self):
        """Initialize GUI I/O handler stub."""
        self._output_buffer = []
        self._input_queue = []

    def output(self, text: str, end: str = '\n') -> None:
        """Output text to GUI.

        Stub implementation: appends to internal buffer.
        Override this to write to your GUI's text widget.
        """
        self._output_buffer.append(text + end)

    def input(self, prompt: str = '') -> str:
        """Input text from GUI.

        Stub implementation: returns from internal queue.
        Override this to show an input dialog and return user's text.
        """
        if prompt:
            self.output(prompt, end='')
        if self._input_queue:
            return self._input_queue.pop(0)
        return ""

    def input_line(self, prompt: str = '') -> str:
        """Input a complete line from GUI.

        Stub implementation: same as input().
        Override for GUI line input dialog.
        """
        return self.input(prompt)

    def input_char(self, blocking: bool = True) -> str:
        """Input single character from GUI.

        Stub implementation: returns first char from queue.
        Override to capture single keypress in GUI.
        """
        if self._input_queue:
            text = self._input_queue.pop(0)
            return text[0] if text else ""
        return ""

    def clear_screen(self) -> None:
        """Clear the GUI output area.

        Stub implementation: clears buffer.
        Override to clear your GUI's text widget.
        """
        self._output_buffer.clear()

    def error(self, message: str) -> None:
        """Output error message in GUI.

        Stub implementation: appends to buffer with prefix.
        Override to show error in red or in error dialog.
        """
        self._output_buffer.append(f"Error: {message}\n")

    def debug(self, message: str) -> None:
        """Output debug message in GUI.

        Stub implementation: appends to buffer.
        Override to show debug info in separate panel or log.
        """
        self._output_buffer.append(f"DEBUG: {message}\n")

    def locate(self, row: int, col: int) -> None:
        """Move cursor to specific position in GUI.

        Stub implementation: does nothing.
        Override if your GUI supports cursor positioning.
        """
        pass

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position in GUI.

        Stub implementation: returns (1, 1).
        Override if your GUI tracks cursor position.
        """
        return (1, 1)

    # Helper methods for stub testing
    def get_output(self) -> str:
        """Get all accumulated output (for testing).

        Returns:
            All output as a single string
        """
        return ''.join(self._output_buffer)

    def clear_output(self) -> None:
        """Clear output buffer (for testing)."""
        self._output_buffer.clear()

    def queue_input(self, text: str) -> None:
        """Queue input text for next input() call (for testing).

        Args:
            text: Text to return on next input() call
        """
        self._input_queue.append(text)
