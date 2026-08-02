"""UI backends for MBASIC interpreter.

This module provides abstract interfaces and implementations for different
UI types (CLI, GUI, web, mobile, etc.).
"""

from .base import UIBackend
from .cli import CLIBackend
from .visual import VisualBackend

# Try to import tkinter-based GUI (optional dependency)
try:
    from .tk_ui import TkBackend
    _has_tk = True
except (ImportError, OSError):
    # Tkinter UI not available (may need: apt install python3-tk).
    # OSError covers a missing/unreadable keybindings JSON, which must not
    # prevent the dependency-free CLI backend from being importable.
    _has_tk = False
    TkBackend = None

# Try to import urwid-based curses UI (optional dependency)
try:
    from .curses_ui import CursesBackend
    _has_curses = True
except (ImportError, OSError):
    # Curses UI not available (requires urwid: pip install urwid).
    # OSError covers a missing/unreadable keybindings JSON (see above).
    _has_curses = False
    CursesBackend = None

__all__ = ['UIBackend', 'CLIBackend', 'VisualBackend', 'CursesBackend', 'TkBackend']
