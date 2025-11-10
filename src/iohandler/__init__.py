"""I/O abstraction layer for MBASIC interpreter.

This module provides abstract interfaces for I/O operations,
allowing the interpreter to work with different I/O backends
(console, GUI, curses, embedded, etc.).

Module naming: This package is named 'iohandler' rather than 'io' to avoid
conflicts with Python's built-in 'io' module, which is used elsewhere in the
codebase (e.g., in src/filesystem/sandboxed_fs.py and test files) for standard
I/O operations like io.StringIO and io.BytesIO.

GUIIOHandler is a stub implementation with no external dependencies - it uses
only Python standard library. WebIOHandler has dependencies on nicegui.
They are not exported here to keep this module focused on core I/O handlers:
  - from src.iohandler.gui import GUIIOHandler (stub for custom GUI implementations)
  - from src.iohandler.web_io import WebIOHandler (requires nicegui)
"""

from .base import IOHandler
from .console import ConsoleIOHandler
from .curses_io import CursesIOHandler

__all__ = ['IOHandler', 'ConsoleIOHandler', 'CursesIOHandler']
