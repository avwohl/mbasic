"""CodeMirror 6 editor component for NiceGUI.

This module provides a custom NiceGUI component wrapping CodeMirror 6,
enabling rich text editing with decorations, markers, and syntax highlighting.

Features:
- Find highlighting (yellow background)
- Breakpoint markers (red gutter markers)
- Current statement highlighting (green/blue background for step debugging)
- Line numbers
- Proper text editing with undo/redo
"""

from nicegui import ui
from typing import Callable, Optional


class CodeMirrorEditor(ui.element, component='codemirror_editor.js'):
    """CodeMirror 6 editor component.

    This component provides a rich code editor with support for:
    - Text decorations (find highlighting, current statement)
    - Line gutter markers (breakpoints)
    - Programmatic scroll control
    - Event callbacks

    Example:
        editor = CodeMirrorEditor(
            value="10 PRINT 'Hello'\n20 END",
            on_change=lambda e: print(f"Content: {e.sender.value}")
        )

        # Highlight find results
        editor.add_find_highlight(line=0, start_col=3, end_col=8)

        # Add breakpoint marker
        editor.add_breakpoint(line_num=10)

        # Highlight current executing statement
        editor.set_current_statement(line_num=10)
    """

    def __init__(self,
                 value: str = '',
                 on_change: Optional[Callable] = None,
                 readonly: bool = False) -> None:
        """Initialize CodeMirror editor.

        Args:
            value: Initial text content
            on_change: Callback when text changes (receives event with .sender.value)
            readonly: Whether editor is read-only
        """
        super().__init__()
        self._value = value
        self._readonly = readonly
        self._props['value'] = value
        self._props['readonly'] = readonly

        # Internal handler to keep _value in sync with user edits
        def _internal_change_handler(e):
            self._value = e.args  # CodeMirror sends new value as args
            if on_change:
                on_change(e)

        if on_change:
            self.on('change', _internal_change_handler)
        else:
            self.on('change', lambda e: setattr(self, '_value', e.args))

    @property
    def value(self) -> str:
        """Get current editor content."""
        return self._value

    @value.setter
    def value(self, text: str) -> None:
        """Set editor content."""
        self._value = text
        self._props['value'] = text
        self.run_method('setValue', text)

    def get_value(self) -> str:
        """Get current editor content (async)."""
        return self.run_method('getValue')

    def set_value(self, text: str) -> None:
        """Set editor content."""
        self.value = text

    def add_find_highlight(self, line: int, start_col: int, end_col: int) -> None:
        """Add yellow highlight for find results.

        Args:
            line: 0-based line number
            start_col: Start column (0-based)
            end_col: End column (exclusive)
        """
        self.run_method('addFindHighlight', line, start_col, end_col)

    def clear_find_highlights(self) -> None:
        """Remove all find highlights."""
        self.run_method('clearFindHighlights')

    def add_breakpoint(self, line_num: int) -> None:
        """Add breakpoint marker to line gutter.

        Args:
            line_num: BASIC line number (e.g., 100, 200)
        """
        self.run_method('addBreakpoint', line_num)

    def remove_breakpoint(self, line_num: int) -> None:
        """Remove breakpoint marker from line gutter.

        Args:
            line_num: BASIC line number
        """
        self.run_method('removeBreakpoint', line_num)

    def clear_breakpoints(self) -> None:
        """Remove all breakpoint markers."""
        self.run_method('clearBreakpoints')

    def set_current_statement(self, line_num: Optional[int]) -> None:
        """Highlight current executing statement during step debugging.

        Args:
            line_num: BASIC line number, or None to clear highlight
        """
        self.run_method('setCurrentStatement', line_num)

    def scroll_to_line(self, line: int) -> None:
        """Scroll to and center the specified line.

        Args:
            line: 0-based line number
        """
        self.run_method('scrollToLine', line)

    def get_cursor_position(self) -> dict:
        """Get current cursor position.

        Returns:
            Dict with 'line' and 'column' (both 0-based)
        """
        return self.run_method('getCursorPosition')

    def set_readonly(self, readonly: bool) -> None:
        """Set editor read-only state.

        Args:
            readonly: True to make read-only, False to allow editing
        """
        self._readonly = readonly
        self._props['readonly'] = readonly
        self.run_method('setReadonly', readonly)
