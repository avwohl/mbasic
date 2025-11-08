"""CodeMirror 5 Editor Component for NiceGUI.

This module provides a Python wrapper around a CodeMirror 5 editor component,
which uses simple script tags instead of ES6 modules (avoiding the module
loading conflicts of CodeMirror 6).

Features:
- Find highlighting (yellow background)
- Breakpoint markers (red line background)
- Current statement highlighting (green background)
- Line numbers
- Text editing
"""

from pathlib import Path
from typing import Callable, Optional
from nicegui import ui


class CodeMirror5Editor(ui.element, component='codemirror5_editor.js'):
    """CodeMirror 5 based code editor component.

    This component uses CodeMirror 5 (legacy version) which doesn't require
    ES6 module loading, making it compatible with NiceGUI's module system.

    Args:
        value: Initial text content
        on_change: Callback function when content changes
        readonly: Whether editor is read-only
    """

    def __init__(self,
                 value: str = '',
                 on_change: Optional[Callable] = None,
                 readonly: bool = False) -> None:
        """Initialize the CodeMirror 5 editor.

        Args:
            value: Initial editor content
            on_change: Optional callback for content changes
            readonly: Whether the editor is read-only
        """
        super().__init__()
        self._value = value
        self._readonly = readonly
        self._props['value'] = value
        self._props['readonly'] = readonly

        # Internal handler to keep _value in sync with user edits
        def _internal_change_handler(e):
            self._value = e.args  # CodeMirror sends new value in e.args attribute
            if on_change:
                on_change(e)

        if on_change:
            self.on('change', _internal_change_handler)
        else:
            self.on('change', lambda e: setattr(self, '_value', e.args))

    @property
    def value(self) -> str:
        """Get current editor content.

        Always returns a string, even if internal value is dict or None.
        """
        if isinstance(self._value, dict):
            # Sometimes event args are dict - return empty string
            return ''
        return self._value or ''

    @value.setter
    def value(self, text: str) -> None:
        """Set editor content."""
        self._value = text
        self._props['value'] = text
        self.run_method('setValue', text)

    def add_find_highlight(self, line: int, start_col: int, end_col: int) -> None:
        """Add yellow highlight to search result.

        Args:
            line: 0-based line number
            start_col: Starting column (0-based)
            end_col: Ending column (0-based)
        """
        self.run_method('addFindHighlight', line, start_col, end_col)

    def clear_find_highlights(self) -> None:
        """Clear all find highlights."""
        self.run_method('clearFindHighlights')

    def add_breakpoint(self, line_num: int, char_start: Optional[int] = None, char_end: Optional[int] = None) -> None:
        """Add breakpoint marker (red background) to BASIC line number.

        Args:
            line_num: BASIC line number (e.g., 10, 20, 30)
            char_start: Optional character start position for statement-level breakpoint
            char_end: Optional character end position for statement-level breakpoint
        """
        if char_start is not None and char_end is not None:
            self.run_method('addBreakpoint', line_num, char_start, char_end)
        else:
            self.run_method('addBreakpoint', line_num)

    def remove_breakpoint(self, line_num: int) -> None:
        """Remove breakpoint marker from BASIC line number.

        Args:
            line_num: BASIC line number
        """
        self.run_method('removeBreakpoint', line_num)

    def clear_breakpoints(self) -> None:
        """Clear all breakpoint markers."""
        self.run_method('clearBreakpoints')

    def set_current_statement(self, line_num: Optional[int], char_start: Optional[int] = None, char_end: Optional[int] = None) -> None:
        """Highlight current executing statement (green background).

        Args:
            line_num: BASIC line number, or None to clear highlighting
            char_start: Optional character start position for statement-level highlighting
            char_end: Optional character end position for statement-level highlighting
        """
        if char_start is not None and char_end is not None:
            self.run_method('setCurrentStatement', line_num, char_start, char_end)
        else:
            self.run_method('setCurrentStatement', line_num)

    def scroll_to_line(self, line: int) -> None:
        """Scroll editor to show specific line.

        Args:
            line: 0-based line number
        """
        self.run_method('scrollToLine', line)

    def get_cursor_position(self) -> dict:
        """Get current cursor position.

        Note: This is a placeholder implementation that always returns line 0, column 0.
        Full implementation would require async JavaScript communication support.

        Returns:
            Dict with 'line' and 'column' keys (placeholder: always {'line': 0, 'column': 0})
        """
        # This would need async support, for now return placeholder
        return {'line': 0, 'column': 0}

    def set_readonly(self, readonly: bool) -> None:
        """Set readonly state.

        Args:
            readonly: Whether editor should be read-only
        """
        self._readonly = readonly
        self._props['readonly'] = readonly
        self.run_method('setReadonly', readonly)
