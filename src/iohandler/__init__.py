"""I/O abstraction layer for MBASIC interpreter.

This module provides abstract interfaces for I/O operations,
allowing the interpreter to work with different I/O backends
(console, GUI, curses, embedded, etc.).

Note: This module was originally named 'io' but was renamed to 'iohandler'
to avoid conflicts with Python's built-in 'io' module.
"""

from .base import IOHandler
from .console import ConsoleIOHandler
from .curses_io import CursesIOHandler

__all__ = ['IOHandler', 'ConsoleIOHandler', 'CursesIOHandler']
