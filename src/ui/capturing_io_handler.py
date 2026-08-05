"""Capturing IO Handler for output buffering.

This module provides a simple IO handler that captures output to a buffer,
used by various UI backends for executing commands and capturing their output.
"""

from src.iohandler.console import ConsoleKeyboardMixin


class CapturingIOHandler(ConsoleKeyboardMixin):
    """IO handler that captures output to a buffer.

    Keyboard reads come from ConsoleKeyboardMixin, which reads the process's
    own terminal. That is what INKEY$ and INPUT$ did before they were routed
    through the I/O handler, so the curses UI behaves as it did - but it is a
    placeholder: this handler belongs to a urwid UI that owns the terminal,
    and it should be reading urwid's keys, not competing for the same fd.
    """

    def __init__(self, keyboard=None):
        """
        Args:
            keyboard: optional object with input_char()/input_chars(), used
                for INKEY$ and INPUT$ instead of the process's terminal. The
                curses UI passes a UrwidKeyboard so a program gets the keys
                urwid collected rather than racing urwid for the same fd.
        """
        self.output_buffer = []
        self.debug_enabled = False
        self.keyboard = keyboard

    def input_char(self, blocking=True):
        if self.keyboard is not None:
            return self.keyboard.input_char(blocking=blocking)
        return super().input_char(blocking=blocking)

    def input_chars(self, count, interrupted=None):
        if self.keyboard is not None:
            return self.keyboard.input_chars(count, interrupted=interrupted)
        return super().input_chars(count, interrupted=interrupted)

    def output(self, text, end='\n'):
        if end == '\n':
            self.output_buffer.append(str(text))
        else:
            if self.output_buffer:
                self.output_buffer[-1] += str(text) + end
            else:
                self.output_buffer.append(str(text) + end)

    def get_and_clear_output(self):
        output = self.output_buffer[:]
        self.output_buffer.clear()
        return output

    def set_debug(self, enabled):
        self.debug_enabled = enabled

    def input(self, prompt=''):
        return ""

    def input_line(self, prompt=''):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.output(f"Error: {message}")

    def debug(self, message):
        if self.debug_enabled:
            self.output(f"Debug: {message}")
