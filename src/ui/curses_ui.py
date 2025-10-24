"""Curses UI backend for MBASIC interpreter.

This module provides a text-based visual UI using Python's curses library.
Curses provides a full-screen terminal interface with multiple windows,
making it suitable for a classic BASIC IDE experience.
"""

from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter
from iohandler.curses_io import CursesIOHandler
from .help_browser import HelpBrowser
import os


class CursesBackend(UIBackend):
    """Curses-based text UI backend.

    Provides a full-screen terminal UI with:
    - Split screen: editor on top, output on bottom
    - Status line showing current mode and commands
    - Function key commands (F2=Run, F3=List, F5=Save, F9=Load, Q=Quit)
    - Visual line editing
    - Scrollable editor and output windows

    Usage:
        from iohandler.curses_io import CursesIOHandler
        from editing import ProgramManager
        from ui.curses_ui import CursesBackend

        io = CursesIOHandler()
        program = ProgramManager(def_type_map)
        backend = CursesBackend(io, program)
        backend.start()  # Runs curses UI until user exits
    """

    def __init__(self, io_handler, program_manager):
        """Initialize curses backend.

        Args:
            io_handler: IOHandler for I/O operations (will be replaced with CursesIOHandler)
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # Runtime and interpreter for program execution
        self.runtime = None
        self.interpreter = None

        # Curses state
        self.stdscr = None
        self.editor_win = None
        self.output_win = None
        self.status_win = None
        self.curses_io = None

        # Editor state
        self.editor_lines = {}  # line_num -> text for editing
        self.current_line_num = 10  # Default starting line number
        self.current_line_text = ""
        self.cursor_x = 0
        self.editor_scroll_offset = 0
        self.status_message = "Ready"

        # Help system
        self.help_browser = None

    def start(self) -> None:
        """Start the curses UI.

        Initializes curses, creates windows, and runs the main event loop.
        """
        import curses
        try:
            curses.wrapper(self._curses_main)
        except KeyboardInterrupt:
            pass  # Clean exit on Ctrl+C

    def _curses_main(self, stdscr):
        """Main curses loop (called by curses.wrapper).

        Args:
            stdscr: Main curses screen window
        """
        import curses

        self.stdscr = stdscr

        # Initialize colors if available
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Status line
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Editor
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Output
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Errors

        # Set up curses mode
        curses.curs_set(1)  # Show cursor
        self.stdscr.keypad(True)  # Enable function keys

        # Create windows
        self._create_windows()

        # Create CursesIOHandler for program execution
        self.curses_io = CursesIOHandler(output_win=self.output_win, debug_enabled=False)

        # Initialize help browser
        help_root = os.path.join(os.path.dirname(__file__), '../../docs/help')
        self.help_browser = HelpBrowser(self.stdscr, help_root)

        # Load program into editor
        self._load_program_to_editor()

        # Draw initial UI
        self._refresh_all()

        # Main event loop
        while True:
            key = self.stdscr.getch()

            if key == ord('q') or key == ord('Q'):
                # Quit
                break
            # ESC: Clear error message and return to Ready
            elif key == 27:  # ESC
                self.status_message = "Ready"
            # Help: Ctrl+H (note: conflicts with backspace on some terminals, also handled below)
            elif key == ord('?'):  # ? key for help
                self._show_help()
            # Run: Ctrl+R
            elif key == 18:  # Ctrl+R
                self._run_program()
            # List: Ctrl+L
            elif key == 12:  # Ctrl+L
                self._list_program()
            # Save: Ctrl+S
            elif key == 19:  # Ctrl+S
                self._save_program()
            # Load: Ctrl+O
            elif key == 15:  # Ctrl+O
                self._load_program()
            # New: Ctrl+N
            elif key == 14:  # Ctrl+N
                self.cmd_new()
            # Navigation
            elif key == curses.KEY_UP:
                self._move_line_up()
            elif key == curses.KEY_DOWN:
                self._move_line_down()
            elif key == curses.KEY_LEFT:
                self._move_cursor_left()
            elif key == curses.KEY_RIGHT:
                self._move_cursor_right()
            elif key == curses.KEY_HOME or key == 1:  # Home or Ctrl+A
                self.cursor_x = 0
            elif key == curses.KEY_END or key == 5:  # End or Ctrl+E
                self.cursor_x = len(self.current_line_text)
            # Line editing
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                self._handle_enter()
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                self._handle_backspace()
            elif key == curses.KEY_DC:  # Delete key
                self._handle_delete()
            elif key >= 32 and key < 127:
                # Printable character
                self._insert_char(chr(key))

            self._refresh_all()

    def _create_windows(self):
        """Create curses windows for UI layout."""
        import curses

        height, width = self.stdscr.getmaxyx()

        # Status line at bottom (1 line)
        self.status_win = curses.newwin(1, width, height - 1, 0)

        # Editor window (top 2/3)
        editor_height = (height - 1) * 2 // 3
        self.editor_win = curses.newwin(editor_height, width, 0, 0)

        # Output window (bottom 1/3, minus status line)
        output_height = (height - 1) - editor_height
        self.output_win = curses.newwin(output_height, width, editor_height, 0)

        # Enable scrolling for output window
        self.output_win.scrollok(True)

    def _load_program_to_editor(self):
        """Load program from ProgramManager into editor."""
        self.editor_lines = {}
        for line_num, line_text in self.program.get_lines():
            self.editor_lines[line_num] = line_text

        # Set current line to first line or default
        if self.editor_lines:
            self.current_line_num = min(self.editor_lines.keys())
            self.current_line_text = self.editor_lines[self.current_line_num]
        else:
            self.current_line_num = 10
            self.current_line_text = f"{self.current_line_num} "

        self.cursor_x = len(self.current_line_text)

    def _save_editor_to_program(self):
        """Save current line to editor_lines and sync to ProgramManager."""
        # Save current line to editor
        if self.current_line_text.strip():
            self.editor_lines[self.current_line_num] = self.current_line_text

        # Sync all editor lines to ProgramManager
        self.program.clear()
        for line_num in sorted(self.editor_lines.keys()):
            line_text = self.editor_lines[line_num]
            success, error = self.program.add_line(line_num, line_text)
            if not error:
                self.status_message = f"Parse error at line {line_num}: {error}"

    def _refresh_all(self):
        """Refresh all windows."""
        self._draw_status()
        self._draw_output()
        self._draw_editor()  # Draw editor last to keep cursor there

        # Refresh in order, editor last so cursor stays there
        self.status_win.refresh()
        self.output_win.refresh()
        self.stdscr.refresh()
        self.editor_win.refresh()  # Refresh editor last to position cursor

    def _draw_status(self):
        """Draw status line."""
        import curses

        self.status_win.clear()

        if curses.has_colors():
            self.status_win.bkgd(' ', curses.color_pair(1))

        # If there's an error or long message, show ESC hint
        if "error" in self.status_message.lower() or len(self.status_message) > 40:
            status_text = f" MBASIC | {self.status_message} | [ESC to clear]"
        else:
            status_text = f" MBASIC | {self.status_message} | ?=Help ^R=Run ^L=List ^S=Save ^O=Load ^N=New Q=Quit"

        height, width = self.status_win.getmaxyx()
        self.status_win.addstr(0, 0, status_text[:width-1])

    def _draw_editor(self):
        """Draw editor window showing program lines."""
        import curses

        self.editor_win.clear()

        if curses.has_colors():
            self.editor_win.bkgd(' ', curses.color_pair(2))

        height, width = self.editor_win.getmaxyx()

        # Get sorted line numbers
        line_numbers = sorted(self.editor_lines.keys())

        # Find current line position
        if self.current_line_num in line_numbers:
            current_idx = line_numbers.index(self.current_line_num)
        else:
            current_idx = len(line_numbers)

        # Calculate visible range
        if current_idx < self.editor_scroll_offset:
            self.editor_scroll_offset = current_idx
        elif current_idx >= self.editor_scroll_offset + height - 1:
            self.editor_scroll_offset = current_idx - height + 2

        # Draw lines and find cursor position
        row = 0
        cursor_row = 0
        for i in range(self.editor_scroll_offset, len(line_numbers)):
            if row >= height - 1:
                break
            line_num = line_numbers[i]

            # Check if this is the current line being edited
            if line_num == self.current_line_num:
                # Draw current line text (being edited)
                self.editor_win.addstr(row, 0, self.current_line_text[:width-1])
                cursor_row = row
            else:
                # Draw saved line
                line_text = self.editor_lines[line_num]
                self.editor_win.addstr(row, 0, line_text[:width-1])
            row += 1

        # If current line is not in editor_lines yet, draw it at the end
        if self.current_line_num not in self.editor_lines:
            if current_idx >= self.editor_scroll_offset:
                edit_row = current_idx - self.editor_scroll_offset
                if edit_row < height:
                    self.editor_win.addstr(edit_row, 0, self.current_line_text[:width-1])
                    cursor_row = edit_row

        # Always position cursor at current editing position
        cursor_col = min(self.cursor_x, width - 1)
        self.editor_win.move(cursor_row, cursor_col)

    def _draw_output(self):
        """Draw output window."""
        import curses

        if curses.has_colors():
            self.output_win.bkgd(' ', curses.color_pair(3))

        # Output is drawn by CursesIOHandler during program execution

    def _run_program(self):
        """Run the current program."""
        try:
            # Save current line and sync to ProgramManager
            self._save_editor_to_program()

            # Clear output window
            self.output_win.clear()
            self.output_win.refresh()

            # Get program AST
            program_ast = self.program.get_program_ast()

            # Create runtime and interpreter with CursesIOHandler
            self.runtime = Runtime(self.program.line_asts, self.program.lines)
            self.interpreter = Interpreter(self.runtime, self.curses_io)

            # Run the program
            self.status_message = "Running..."
            self._draw_status()
            self.status_win.refresh()

            self.interpreter.run()

            self.status_message = "Program finished"

        except Exception as e:
            self.status_message = f"Error: {e}"
            self.curses_io.error(f"Runtime error: {e}")

    def _list_program(self):
        """List program to output window."""
        self.output_win.clear()
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self.curses_io.output(line_text)
        self.status_message = "Program listed"

    def _save_program(self):
        """Save program to file."""
        import curses

        # Prompt for filename
        self.status_message = "Save as: "
        self._draw_status()
        self.status_win.refresh()

        # Get filename
        curses.echo()
        curses.curs_set(1)
        self.status_win.addstr(0, len(self.status_message), "")
        filename_bytes = self.status_win.getstr(0, len(self.status_message), 40)
        filename = filename_bytes.decode('utf-8', errors='replace').strip()
        curses.noecho()

        if filename:
            try:
                self._save_editor_to_program()
                self.program.save_to_file(filename)
                self.status_message = f"Saved to {filename}"
            except Exception as e:
                self.status_message = f"Save error: {e}"
        else:
            self.status_message = "Save cancelled"

    def _load_program(self):
        """Load program from file."""
        import curses

        # Prompt for filename
        self.status_message = "Load file: "
        self._draw_status()
        self.status_win.refresh()

        # Get filename
        curses.echo()
        curses.curs_set(1)
        self.status_win.addstr(0, len(self.status_message), "")
        filename_bytes = self.status_win.getstr(0, len(self.status_message), 40)
        filename = filename_bytes.decode('utf-8', errors='replace').strip()
        curses.noecho()

        if filename:
            try:
                success, errors = self.program.load_from_file(filename)
                if errors:
                    self.output_win.clear()
                    for line_num, error in errors:
                        self.curses_io.error(f"Line {line_num}: {error}")
                if success:
                    self._load_program_to_editor()
                    self.status_message = f"Loaded {filename}"
                else:
                    self.status_message = "Load failed"
            except Exception as e:
                self.status_message = f"Load error: {e}"
        else:
            self.status_message = "Load cancelled"

    def _move_line_up(self):
        """Move to previous line in editor."""
        line_numbers = sorted(self.editor_lines.keys())
        if self.current_line_num in line_numbers:
            idx = line_numbers.index(self.current_line_num)
            if idx > 0:
                # Save current line
                self.editor_lines[self.current_line_num] = self.current_line_text
                # Move to previous line
                self.current_line_num = line_numbers[idx - 1]
                self.current_line_text = self.editor_lines[self.current_line_num]
                self.cursor_x = min(self.cursor_x, len(self.current_line_text))

    def _move_line_down(self):
        """Move to next line in editor."""
        line_numbers = sorted(self.editor_lines.keys())
        if self.current_line_num in line_numbers:
            idx = line_numbers.index(self.current_line_num)
            if idx < len(line_numbers) - 1:
                # Save current line
                self.editor_lines[self.current_line_num] = self.current_line_text
                # Move to next line
                self.current_line_num = line_numbers[idx + 1]
                self.current_line_text = self.editor_lines[self.current_line_num]
                self.cursor_x = min(self.cursor_x, len(self.current_line_text))

    def _move_cursor_left(self):
        """Move cursor left one character."""
        if self.cursor_x > 0:
            self.cursor_x -= 1

    def _move_cursor_right(self):
        """Move cursor right one character."""
        if self.cursor_x < len(self.current_line_text):
            self.cursor_x += 1

    def _handle_enter(self):
        """Handle Enter key - save line and move to next."""
        # Parse line number from current line
        import re
        match = re.match(r'^(\d+)\s', self.current_line_text)
        if match:
            line_num = int(match.group(1))
            # Save to editor lines
            self.editor_lines[line_num] = self.current_line_text
            # Parse and add to program
            success, error = self.program.add_line(line_num, self.current_line_text)
            if not success and error:
                self.status_message = f"Parse error: {error}"
            else:
                self.status_message = f"Line {line_num} added"
                # Move to next line (increment by 10)
                self.current_line_num = line_num + 10
                self.current_line_text = f"{self.current_line_num} "
                self.cursor_x = len(self.current_line_text)
        else:
            self.status_message = "Line must start with number"

    def _handle_backspace(self):
        """Handle backspace key."""
        if self.cursor_x > 0:
            self.current_line_text = (
                self.current_line_text[:self.cursor_x-1] +
                self.current_line_text[self.cursor_x:]
            )
            self.cursor_x -= 1

    def _handle_delete(self):
        """Handle delete key."""
        if self.cursor_x < len(self.current_line_text):
            self.current_line_text = (
                self.current_line_text[:self.cursor_x] +
                self.current_line_text[self.cursor_x+1:]
            )

    def _insert_char(self, char):
        """Insert character at cursor position."""
        self.current_line_text = (
            self.current_line_text[:self.cursor_x] +
            char +
            self.current_line_text[self.cursor_x:]
        )
        self.cursor_x += 1

    # UIBackend interface methods

    def cmd_run(self) -> None:
        """Execute RUN command - run the program."""
        self._run_program()

    def cmd_list(self, args: str = "") -> None:
        """Execute LIST command - list program lines."""
        self._list_program()

    def cmd_new(self) -> None:
        """Execute NEW command - clear program."""
        self.program.clear()
        self.editor_lines = {}
        self.current_line_num = 10
        self.current_line_text = f"{self.current_line_num} "
        self.cursor_x = len(self.current_line_text)
        self.status_message = "Program cleared"

    def cmd_save(self, filename: str) -> None:
        """Execute SAVE command - save to file."""
        try:
            self._save_editor_to_program()
            self.program.save_to_file(filename)
            self.status_message = f"Saved to {filename}"
        except Exception as e:
            self.status_message = f"Save error: {e}"

    def _show_help(self) -> None:
        """Show the help browser."""
        if self.help_browser:
            # Show help starting at curses UI index
            self.help_browser.show_help("ui/curses/index.md")
            # After help exits, redraw everything
            self._create_windows()
            self._refresh_all()

    def cmd_load(self, filename: str) -> None:
        """Execute LOAD command - load from file."""
        try:
            success, errors = self.program.load_from_file(filename)
            if errors:
                for line_num, error in errors:
                    self.curses_io.error(f"Line {line_num}: {error}")
            if success:
                self._load_program_to_editor()
                self.status_message = f"Loaded {filename}"
        except Exception as e:
            self.status_message = f"Load error: {e}"

    def cmd_delete(self, args: str) -> None:
        """Execute DELETE command - delete line range."""
        # Parse args and delete lines
        # TODO: Implement line range parsing
        pass

    def cmd_renum(self, args: str) -> None:
        """Execute RENUM command - renumber lines."""
        # TODO: Implement
        pass

    def cmd_cont(self) -> None:
        """Execute CONT command - continue after STOP."""
        # TODO: Implement
        pass
