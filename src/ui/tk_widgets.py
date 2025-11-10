"""Custom Tkinter widgets for MBASIC Tk UI.

This module provides specialized widgets used by the Tk backend,
including line-numbered text editors with status indicators.
"""

try:
    import tkinter as tk
    from tkinter import font as tkfont
except ImportError:
    # Tkinter not available (headless environment)
    tk = None
    tkfont = None


class LineNumberedText(tk.Frame if tk else object):
    """Text widget with status column and automatic blank line removal.

    Layout: [Status (●/?/ )][ Code with line numbers ]

    Status symbols:
    - ● : Breakpoint set on this line
    - ? : Parse error on this line
    - ' ': Normal line (no breakpoint, no error)

    Status priority (when both error and breakpoint):
    - ? takes priority (error shown)
    - After fixing error, ● becomes visible
    - Both set_error() and set_breakpoint() apply the same priority logic:
      error > breakpoint > blank (no special handling for clearing vs setting)

    Automatic blank line removal:
    - When cursor moves away from a blank line, that line is automatically deleted
    - This helps keep BASIC programs clean by removing accidental blank lines
    - Implemented via _on_cursor_move() tracking cursor movement

    Note: BASIC line numbers are part of the text content (not drawn separately in the canvas).
    Line numbers are parsed from the text using _parse_line_number() to map status indicators
    to the correct lines.
    """

    def __init__(self, parent, **kwargs):
        """Initialize line-numbered text widget.

        Args:
            parent: Parent widget
            **kwargs: Arguments passed to Text widget
        """
        if tk is None:
            raise ImportError("tkinter not available")

        tk.Frame.__init__(self, parent)

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create canvas for status symbols only
        # Width: 20 pixels for one status character (●, ?, or space)
        self.canvas = tk.Canvas(
            self,
            width=20,
            bg='#e0e0e0',
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky='ns')

        # Bind click on status column
        self.canvas.bind('<Button-1>', self._on_status_click)

        # Create text widget
        text_kwargs = {
            'wrap': tk.NONE,
            'font': ('Courier', 10),
            'undo': True,
            'maxundo': -1
        }
        text_kwargs.update(kwargs)

        self.text = tk.Text(self, **text_kwargs)
        self.text.grid(row=0, column=1, sticky='nsew')

        # Create vertical scrollbar
        self.vsb = tk.Scrollbar(self, orient='vertical', command=self._on_scrollbar)
        self.vsb.grid(row=0, column=2, sticky='ns')

        # Create horizontal scrollbar
        self.hsb = tk.Scrollbar(self, orient='horizontal', command=self.text.xview)
        self.hsb.grid(row=1, column=1, sticky='ew')

        # Configure text widget scrolling
        self.text.config(
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=self.hsb.set
        )

        # Track line metadata
        # line_number -> {'status': '●'|'?'|' ', 'has_breakpoint': bool, 'has_error': bool}
        self.line_metadata = {}

        # Font metrics for drawing
        self.text_font = tkfont.Font(family='Courier', size=10)
        self.line_height = self.text_font.metrics('linespace')

        # Bind events for redrawing
        self.text.bind('<Configure>', self._on_configure)
        self.text.bind('<<Modified>>', self._on_modified)
        self.text.bind('<KeyRelease>', self._on_text_change)

        # Track current line for blank line removal
        self.current_line = None

        # Bind events for blank line removal
        self.text.bind('<KeyPress>', self._on_cursor_move, add='+')
        self.text.bind('<ButtonPress-1>', self._on_cursor_move, add='+')

        # Initial draw
        self._redraw()

    def _on_scrollbar(self, *args):
        """Handle scrollbar movement."""
        self.text.yview(*args)
        self._redraw()

    def _on_text_scroll(self, *args):
        """Handle text widget scroll."""
        self.vsb.set(*args)
        self._redraw()

    def _on_configure(self, event=None):
        """Handle widget resize."""
        self._redraw()

    def _on_modified(self, event=None):
        """Handle text modification."""
        # Reset modified flag
        self.text.edit_modified(False)
        self._redraw()

    def _on_text_change(self, event=None):
        """Handle key release in text widget."""
        self._redraw()

    def _on_cursor_move(self, event=None):
        """Handle cursor movement - remove blank lines when moving away from them."""
        # Get current cursor position
        cursor_pos = self.text.index(tk.INSERT)
        new_line = int(cursor_pos.split('.')[0])

        # Check if we're moving to a different line
        if self.current_line is not None and self.current_line != new_line:
            # Check if the previous line is blank (only whitespace)
            line_text = self.text.get(f'{self.current_line}.0', f'{self.current_line}.end')
            if line_text.strip() == '':
                # Delete the blank line
                # Schedule deletion after current event processing to avoid interfering
                # with ongoing key/mouse event handling (prevents cursor position issues,
                # undo stack corruption, and widget state conflicts during event processing)
                self.text.after_idle(self._delete_line, self.current_line)

        # Update current line
        self.current_line = new_line

    def _delete_line(self, line_num):
        """Delete a line from the text widget.

        Args:
            line_num: Tkinter text widget line number (1-based sequential index).
                     This is the position in the editor window (row 1, 2, 3, ...).
                     This is NOT a BASIC line number (e.g., 10, 20, 30).
        """
        # Check if line still exists and is still blank
        try:
            line_text = self.text.get(f'{line_num}.0', f'{line_num}.end')
            if line_text.strip() == '':
                # Delete the entire line including newline
                self.text.delete(f'{line_num}.0', f'{line_num + 1}.0')
                self._redraw()
        except tk.TclError:
            # Line no longer exists, ignore
            pass

    def _redraw(self):
        """Redraw status column (●=breakpoint, ?=error).

        Note: BASIC line numbers are part of the text content (not drawn separately
        in the canvas). See _parse_line_number() for the regex-based extraction logic
        that validates line number format (requires whitespace or end-of-string after
        the number).
        """
        self.canvas.delete('all')

        # Get visible line range
        first_visible = self.text.index('@0,0')
        last_visible = self.text.index(f'@0,{self.text.winfo_height()}')

        first_line = int(first_visible.split('.')[0])
        last_line = int(last_visible.split('.')[0])

        # Draw each visible line
        for line_num in range(first_line, last_line + 2):
            # Get y coordinate
            dline = self.text.dlineinfo(f'{line_num}.0')
            if dline is None:
                continue

            y = dline[1]

            # Get BASIC line number from text
            line_text = self.text.get(f'{line_num}.0', f'{line_num}.end')
            basic_line_num = self._parse_line_number(line_text)

            # Get status for this BASIC line
            if basic_line_num and basic_line_num in self.line_metadata:
                metadata = self.line_metadata[basic_line_num]
                status = metadata['status']
            else:
                status = ' '

            # Draw status symbol centered in narrow canvas
            self.canvas.create_text(
                10, y,
                anchor='nw',
                text=status,
                font=self.text_font,
                fill='red' if status == '?' else 'blue' if status == '●' else 'gray'
            )

    def _parse_line_number(self, line_text):
        """Extract BASIC line number from line text.

        Args:
            line_text: Text of the line

        Returns:
            Line number (int) or None
        """
        import re
        line_text = line_text.strip()
        if not line_text:
            return None

        # Match line number followed by whitespace OR end of string (both valid).
        # Valid examples:
        #   "10 PRINT" - line number 10 followed by whitespace, then statement
        #   "10" - standalone line number (no statement, just the line number)
        #   "  10  REM" - leading whitespace is ok (stripped above)
        # Invalid examples:
        #   "10REM" - no whitespace between line number and statement
        #   "ABC10" - non-digit prefix
        #   "" - empty after strip
        # Note: MBASIC 5.21 requires whitespace OR end-of-line between line number and statement.
        # A standalone line number like "10" is valid (represents a numbered line with no code).
        match = re.match(r'^(\d+)(?:\s|$)', line_text)
        if match:
            return int(match.group(1))
        return None

    def set_breakpoint(self, line_number, enabled=True):
        """Set or clear breakpoint on a line.

        Args:
            line_number: BASIC line number
            enabled: True to set breakpoint, False to clear
        """
        if line_number not in self.line_metadata:
            self.line_metadata[line_number] = {
                'status': ' ',
                'has_breakpoint': False,
                'has_error': False,
                'error_message': None
            }

        metadata = self.line_metadata[line_number]
        metadata['has_breakpoint'] = enabled

        # Update status symbol (error takes priority)
        if metadata['has_error']:
            metadata['status'] = '?'
        elif metadata['has_breakpoint']:
            metadata['status'] = '●'
        else:
            metadata['status'] = ' '

        self._redraw()

    def set_error(self, line_number, has_error=True, error_message=None):
        """Set or clear error indicator on a line.

        Args:
            line_number: BASIC line number
            has_error: True to show error, False to clear
            error_message: Optional error message to display
        """
        if line_number not in self.line_metadata:
            self.line_metadata[line_number] = {
                'status': ' ',
                'has_breakpoint': False,
                'has_error': False,
                'error_message': None
            }

        metadata = self.line_metadata[line_number]
        metadata['has_error'] = has_error
        metadata['error_message'] = error_message if has_error else None

        # Update status symbol (error takes priority)
        if metadata['has_error']:
            metadata['status'] = '?'
        elif metadata['has_breakpoint']:
            metadata['status'] = '●'
        else:
            metadata['status'] = ' '

        self._redraw()

    def get_error_message(self, line_number):
        """Get error message for a line.

        Args:
            line_number: BASIC line number

        Returns:
            Error message string or None if no error
        """
        if line_number in self.line_metadata:
            return self.line_metadata[line_number].get('error_message')
        return None

    def _on_status_click(self, event):
        """Handle click on status column (show error details for ?, confirmation message for ●).

        Displays informational messages about line status:
        - For error markers (?): Shows error message in a message box
        - For breakpoint markers (●): Shows confirmation message that breakpoint is set

        Note: This displays information messages only. It does NOT toggle breakpoints -
        that's handled by the UI backend's breakpoint toggle command
        (e.g., TkBackend._toggle_breakpoint(), accessed via ^B in Tk UI or menu).
        """
        import tkinter.messagebox as messagebox

        # Calculate which line was clicked based on Y coordinate
        # Get scroll position
        first_visible = float(self.text.index('@0,0').split('.')[0])

        # Calculate line based on click Y and line height
        clicked_line_offset = int(event.y / self.line_height)
        clicked_editor_line = int(first_visible) + clicked_line_offset

        # Get the text of that editor line to find BASIC line number
        try:
            line_text = self.text.get(f'{clicked_editor_line}.0', f'{clicked_editor_line}.end')
            import re
            # Use same pattern as _parse_line_number() for consistency
            line_text = line_text.strip()
            match = re.match(r'^(\d+)(?:\s|$)', line_text)
            if match:
                line_num = int(match.group(1))
                error_msg = self.get_error_message(line_num)
                if error_msg:
                    messagebox.showerror(
                        f"Error on Line {line_num}",
                        error_msg
                    )
                else:
                    # Has breakpoint, not error
                    metadata = self.line_metadata.get(line_num, {})
                    if metadata.get('has_breakpoint'):
                        messagebox.showinfo(
                            f"Breakpoint on Line {line_num}",
                            f"Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints."
                        )
        except Exception:
            pass  # Click outside valid lines

    def clear_all_errors(self):
        """Clear all error indicators."""
        for metadata in self.line_metadata.values():
            metadata['has_error'] = False
            metadata['error_message'] = None
            # Update status (breakpoint may still be there)
            if metadata['has_breakpoint']:
                metadata['status'] = '●'
            else:
                metadata['status'] = ' '

        self._redraw()

    def get_current_line_number(self):
        """Get BASIC line number at current cursor position.

        Returns:
            Line number (int) or None
        """
        cursor_pos = self.text.index(tk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        line_text = self.text.get(f'{line_num}.0', f'{line_num}.end')
        return self._parse_line_number(line_text)

    # Proxy methods to text widget for compatibility

    def get(self, start, end=None):
        """Get text from widget."""
        return self.text.get(start, end)

    def insert(self, index, text, *args):
        """Insert text into widget."""
        self.text.insert(index, text, *args)
        self._redraw()

    def delete(self, start, end=None):
        """Delete text from widget."""
        self.text.delete(start, end)
        self._redraw()

    def mark_set(self, mark, index):
        """Set a mark."""
        self.text.mark_set(mark, index)

    def mark_gravity(self, mark, gravity):
        """Set mark gravity."""
        self.text.mark_gravity(mark, gravity)

    def see(self, index):
        """Scroll to make index visible."""
        self.text.see(index)

    def index(self, index):
        """Get index."""
        return self.text.index(index)

    def tag_add(self, tag, start, end=None):
        """Add a tag."""
        self.text.tag_add(tag, start, end)

    def tag_remove(self, tag, start, end=None):
        """Remove a tag."""
        self.text.tag_remove(tag, start, end)

    def tag_config(self, tag, **kwargs):
        """Configure a tag."""
        self.text.tag_config(tag, **kwargs)

    def focus_set(self):
        """Set focus to text widget."""
        self.text.focus_set()

    def event_generate(self, event, **kwargs):
        """Generate an event on the text widget."""
        return self.text.event_generate(event, **kwargs)

    def clipboard_clear(self):
        """Clear clipboard."""
        return self.text.clipboard_clear()

    def clipboard_append(self, text):
        """Append to clipboard."""
        return self.text.clipboard_append(text)
