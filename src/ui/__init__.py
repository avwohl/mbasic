"""UI backends for MBASIC interpreter.

This module provides abstract interfaces and implementations for different
UI types (CLI, GUI, web, mobile, etc.).
"""

from .base import UIBackend
from .cli import CLIBackend
from .visual import VisualBackend
from .tk_ui import TkBackend

# Try to import urwid-based curses UI (optional dependency)
try:
    from .curses_ui import CursesBackend
    _has_curses = True
except ImportError:
    # Curses UI not available (requires urwid: pip install urwid)
    _has_curses = False
    CursesBackend = None

__all__ = ['UIBackend', 'CLIBackend', 'VisualBackend', 'CursesBackend', 'TkBackend']
