"""Capturing IO Handler for output buffering.

This module provides a simple IO handler that captures output to a buffer,
used by various UI backends for executing commands and capturing their output.
"""


class CapturingIOHandler:
    """IO handler that captures output to a buffer."""

    def __init__(self):
        self.output_buffer = []
        self.debug_enabled = False

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

    def input_char(self, blocking=True):
        return ""

    def clear_screen(self):
        pass

    def error(self, message):
        self.output(f"Error: {message}")

    def debug(self, message):
        if self.debug_enabled:
            self.output(f"Debug: {message}")
