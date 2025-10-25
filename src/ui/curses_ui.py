"""Curses UI backend using urwid.

This module provides a full-screen terminal UI for MBASIC using the urwid library.
It provides an editor, output window, and menu system.
"""

import urwid
from .base import UIBackend
from runtime import Runtime
from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


class TopLeftBox(urwid.WidgetWrap):
    """Custom box widget that only draws top and left borders.

    Unlike LineBox, this doesn't reserve space for bottom/right borders,
    allowing content to use the full available space.
    """

    def __init__(self, original_widget, title=''):
        """Create a box with only top and left borders.

        Args:
            original_widget: The widget to wrap
            title: Title to display in top border
        """
        self.title = title
        self.original_widget = original_widget

        # Create the top border line with title
        if title:
            # Title in the top border: "┌─ Title ────────"
            title_text = urwid.Text(f'┌─ {title} ', wrap='clip')
            fill_text = urwid.Text('─' * 200, wrap='clip')
            top_border = urwid.Columns([
                ('pack', title_text),
                fill_text
            ], dividechars=0)
        else:
            top_border = urwid.Text('┌' + '─' * 200, wrap='clip')

        # Use SolidFill with │ for the left border (fills all vertical space)
        left_border = urwid.SolidFill('│')

        content_with_border = urwid.Columns([
            ('fixed', 1, left_border),
            original_widget
        ], dividechars=0)

        # Stack top border and content
        pile = urwid.Pile([
            ('pack', top_border),
            content_with_border
        ])

        super().__init__(pile)


class EditorWidget(urwid.Edit):
    """Multi-line editor widget for BASIC programs."""

    def __init__(self):
        super().__init__(multiline=True, align='left', wrap='clip')
        self.set_caption("")

    def keypress(self, size, key):
        """Handle key presses in the editor."""
        # Let parent handle most keys
        return super().keypress(size, key)


class CursesBackend(UIBackend):
    """Urwid-based curses UI backend.

    Provides a full-screen terminal interface with:
    - Multi-line editor for program entry
    - Output window for program results
    - Menu system for commands
    - Keyboard shortcuts
    """

    def __init__(self, io_handler, program_manager):
        """Initialize the curses UI backend.

        Args:
            io_handler: IOHandler instance for I/O operations
            program_manager: ProgramManager instance
        """
        super().__init__(io_handler, program_manager)

        # UI state
        self.app = None
        self.loop = None
        self.editor = None
        self.output = None
        self.status_bar = None

        # Editor state
        self.editor_lines = {}  # line_num -> text for editing
        self.current_line_num = 10  # Default starting line number

        # Execution state
        self.runtime = None
        self.interpreter = None
        self.running = False
        self.paused_at_breakpoint = False
        self.output_buffer = []

    def start(self):
        """Start the urwid-based curses UI."""
        # Create the UI layout
        self._create_ui()

        # Run the main loop
        self.loop.run()

    def _create_ui(self):
        """Create the urwid UI layout."""
        # Create widgets
        self.editor = EditorWidget()
        self.output = urwid.Text("")
        self.status_bar = urwid.Text("MBASIC 5.21 - Press Ctrl+H for help, Ctrl+Q to quit")

        # Create editor frame with top/left border only (no bottom/right space reserved)
        editor_frame = TopLeftBox(
            urwid.Filler(self.editor, valign='top'),
            title="Editor"
        )

        # Create output frame with top/left border only (no bottom/right space reserved)
        output_frame = TopLeftBox(
            urwid.Filler(self.output, valign='top'),
            title="Output"
        )

        # Create layout - editor on top (70%), output on bottom (30%)
        pile = urwid.Pile([
            ('weight', 7, editor_frame),
            ('weight', 3, output_frame),
            ('pack', self.status_bar)
        ])

        # Create main widget with keybindings
        main_widget = urwid.AttrMap(pile, 'body')

        # Set up the main loop
        self.loop = urwid.MainLoop(
            main_widget,
            palette=self._get_palette(),
            unhandled_input=self._handle_input
        )

    def _get_palette(self):
        """Get the color palette for the UI."""
        return [
            ('body', 'white', 'black'),
            ('header', 'white,bold', 'dark blue'),
            ('footer', 'white', 'dark blue'),
            ('focus', 'black', 'yellow'),
            ('error', 'light red', 'black'),
        ]

    def _handle_input(self, key):
        """Handle global keyboard shortcuts."""
        if key == 'ctrl q':
            # Quit
            raise urwid.ExitMainLoop()

        elif key == 'ctrl h':
            # Show help
            self._show_help()

        elif key == 'ctrl r':
            # Run program
            self._run_program()

        elif key == 'ctrl l':
            # List program
            self._list_program()

        elif key == 'ctrl n':
            # New program
            self._new_program()

        elif key == 'ctrl s':
            # Save program
            self._save_program()

        elif key == 'ctrl o':
            # Open/Load program
            self._load_program()

    def _show_help(self):
        """Show help dialog."""
        help_text = """
MBASIC 5.21 - Keyboard Shortcuts

Ctrl+Q  - Quit
Ctrl+H  - This help
Ctrl+R  - Run program
Ctrl+L  - List program
Ctrl+N  - New program
Ctrl+S  - Save program
Ctrl+O  - Open/Load program

Editor:
- Type line numbers followed by BASIC code
- Press Enter to add/modify lines
- Empty line number deletes that line

Examples:
  10 PRINT "Hello, World!"
  20 END
"""
        # Create help dialog
        text = urwid.Text(help_text.strip())
        fill = urwid.Filler(text, valign='top')
        box = urwid.LineBox(fill, title="Help - Press any key to close")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 80),
            valign='middle',
            height=('relative', 80)
        )

        # Show overlay and wait for key
        self.loop.widget = overlay

        # Set up a one-time keypress handler to close the dialog
        def close_help(key):
            self.loop.widget = main_widget
            self.loop.unhandled_input = self._handle_input

        # Store original widget
        main_widget = self.loop.widget.base_widget
        self.loop.unhandled_input = close_help

    def _run_program(self):
        """Run the current program using tick-based interpreter."""
        try:
            # Parse editor content into program
            self._parse_editor_content()

            if not self.editor_lines:
                self.output_buffer.append("No program to run")
                self._update_output()
                return

            # Update status
            self.status_bar.set_text("Running program...")
            # Screen will update automatically when loop is running

            # Load program lines into program manager
            self.program.clear()
            for line_num in sorted(self.editor_lines.keys()):
                line_text = f"{line_num} {self.editor_lines[line_num]}"
                success, error = self.program.add_line(line_num, line_text)
                if not success:
                    self.output_buffer.append(f"Error at line {line_num}: {error}")
                    self._update_output()
                    self.status_bar.set_text("Parse error - Press Ctrl+H for help")
                    return

            # Create a capturing IO handler that just buffers output
            class CapturingIOHandler:
                """IO handler that captures output to a buffer.

                Output is collected during tick execution and then
                picked up by the UI after the tick returns.
                """
                def __init__(self):
                    self.output_buffer = []
                    self.debug_enabled = False

                def output(self, text, end='\n'):
                    """Capture output to buffer."""
                    if end == '\n':
                        self.output_buffer.append(str(text))
                    else:
                        # For same-line output, append to last line or create new
                        if self.output_buffer:
                            self.output_buffer[-1] += str(text) + end
                        else:
                            self.output_buffer.append(str(text) + end)

                def get_and_clear_output(self):
                    """Get buffered output and clear the buffer."""
                    output = self.output_buffer[:]
                    self.output_buffer.clear()
                    return output

                def set_debug(self, enabled):
                    self.debug_enabled = enabled

                # Stub methods required by IOHandler interface
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

            # Create runtime and interpreter
            io_handler = CapturingIOHandler()
            runtime = Runtime(self.program.line_asts, self.program.lines)
            self.interpreter = Interpreter(runtime, io_handler)
            self.runtime = runtime
            self.io_handler = io_handler  # Keep reference to get output later

            # Start execution
            state = self.interpreter.start()

            if state.status == 'error':
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                self.output_buffer.append(f"Error: {error_msg}")
                self._update_output()
                self.status_bar.set_text("Error - Press Ctrl+H for help")
                return

            # Set up tick-based execution using urwid's alarm
            self._execute_tick()

        except Exception as e:
            import traceback
            self.output_buffer.append(f"Runtime error: {e}")
            self.output_buffer.append(traceback.format_exc())
            self._update_output()
            self.status_bar.set_text("Error - Press Ctrl+H for help")

    def _execute_tick(self):
        """Execute one tick of the interpreter and schedule next tick."""
        try:
            # Execute one tick
            state = self.interpreter.tick(mode='run', max_statements=100)

            # Collect any output produced during the tick
            new_output = self.io_handler.get_and_clear_output()
            if new_output:
                self.output_buffer.extend(new_output)
                self._update_output()

            # Handle state transitions
            if state.status == 'running':
                # Schedule next tick
                self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

            elif state.status == 'waiting_for_input':
                # Prompt user for input
                prompt = state.input_prompt or "? "
                self._get_input_for_interpreter(prompt)

            elif state.status == 'done':
                # Program completed - show final output if any
                final_output = self.io_handler.get_and_clear_output()
                if final_output:
                    self.output_buffer.extend(final_output)
                self.output_buffer.append("Ok")
                self._update_output()
                self.status_bar.set_text("Ready - Press Ctrl+H for help")

            elif state.status == 'error':
                # Error occurred - show any output before error
                error_output = self.io_handler.get_and_clear_output()
                if error_output:
                    self.output_buffer.extend(error_output)
                error_msg = state.error_info.error_message if state.error_info else "Unknown error"
                line_num = state.error_info.error_line if state.error_info else "?"
                self.output_buffer.append(f"Error in {line_num}: {error_msg}")
                self._update_output()
                self.status_bar.set_text("Error - Press Ctrl+H for help")

            elif state.status == 'paused' or state.status == 'at_breakpoint':
                # Paused execution
                self.output_buffer.append(f"Paused at line {state.current_line}")
                self._update_output()
                self.status_bar.set_text("Paused - Press Ctrl+C to continue")

        except Exception as e:
            import traceback
            self.output_buffer.append(f"Runtime error: {e}")
            self.output_buffer.append(traceback.format_exc())
            self._update_output()
            self.status_bar.set_text("Error - Press Ctrl+H for help")

    def _get_input_for_interpreter(self, prompt):
        """Show input dialog and provide input to interpreter."""
        # Get input from user
        result = self._get_input_dialog(prompt)

        # Provide input to interpreter
        self.interpreter.provide_input(result)

        # Continue execution
        self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

    def _list_program(self):
        """List the current program."""
        # Parse editor content
        self._parse_editor_content()

        # Get program listing
        lines = []
        for line_num in sorted(self.editor_lines.keys()):
            lines.append(f"{line_num} {self.editor_lines[line_num]}")

        if lines:
            self.output_buffer.append("Program listing:")
            self.output_buffer.extend(lines)
        else:
            self.output_buffer.append("No program loaded")

        self._update_output()

    def _new_program(self):
        """Clear the current program."""
        self.editor_lines = {}
        self.editor.set_edit_text("")
        self.output_buffer.append("Program cleared")
        self._update_output()
        self.status_bar.set_text("Ready - Press Ctrl+H for help")

    def _parse_editor_content(self):
        """Parse the editor content into line-numbered statements."""
        content = self.editor.get_edit_text()

        # Clear existing lines
        self.editor_lines = {}

        # Parse each line
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Try to extract line number
            parts = line.split(None, 1)
            if parts and parts[0].isdigit():
                line_num = int(parts[0])
                code = parts[1] if len(parts) > 1 else ""
                self.editor_lines[line_num] = code

    def _update_output(self):
        """Update the output window with buffered content."""
        # Show last 20 lines
        visible_lines = self.output_buffer[-20:]
        self.output.set_text('\n'.join(visible_lines))

    def _update_output_with_lines(self, lines):
        """Update output window with specific lines."""
        visible_lines = lines[-20:]
        self.output.set_text('\n'.join(visible_lines))

    def _get_input_dialog(self, prompt):
        """Show input dialog and get user response."""
        # Create input widget
        edit = urwid.Edit(caption=prompt)

        # Create dialog
        fill = urwid.Filler(edit, valign='top')
        box = urwid.LineBox(fill, title="Input Required - Press Enter to submit")
        overlay = urwid.Overlay(
            urwid.AttrMap(box, 'body'),
            self.loop.widget,
            align='center',
            width=('relative', 60),
            valign='middle',
            height=5
        )

        # Store original widget
        original_widget = self.loop.widget
        self.loop.widget = overlay

        # Variable to store result
        result = {'value': ''}
        done = {'flag': False}

        def handle_input(key):
            if key == 'enter':
                result['value'] = edit.get_edit_text()
                done['flag'] = True
                self.loop.widget = original_widget
            elif key == 'esc':
                result['value'] = ''
                done['flag'] = True
                self.loop.widget = original_widget
            else:
                # Let edit widget handle it
                return key

        # Temporarily override input handler
        old_handler = self.loop.unhandled_input
        self.loop.unhandled_input = handle_input

        # Run loop until we get input
        while not done['flag']:
            self.loop.draw_screen()
            keys = self.loop.screen.get_input()
            for key in keys:
                self.loop.process_input(keys)
            if done['flag']:
                break

        # Restore handler
        self.loop.unhandled_input = old_handler

        return result['value']

    def _get_editor_text(self):
        """Get formatted editor text from line-numbered program."""
        lines = []
        for line_num in sorted(self.editor_lines.keys()):
            lines.append(f"{line_num} {self.editor_lines[line_num]}")
        return '\n'.join(lines)

    def _load_program_file(self, filename):
        """Load a program from a file."""
        try:
            self.program.load_from_file(filename)

            # Convert program to editor lines
            self.editor_lines = {}
            for line_num, line_obj in sorted(self.program.lines.items()):
                # Get the original text for the line
                self.editor_lines[line_num] = line_obj.original_text

            # Update editor display
            self.editor.set_edit_text(self._get_editor_text())

            self.output_buffer.append(f"Loaded {filename}")
            self._update_output()

        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    def _save_program(self):
        """Save program to file."""
        # Get filename from user
        filename = self._get_input_dialog("Save as: ")

        if not filename:
            self.output_buffer.append("Save cancelled")
            self._update_output()
            return

        try:
            # Parse editor content first
            self._parse_editor_content()

            # Create program content
            lines = []
            for line_num in sorted(self.editor_lines.keys()):
                lines.append(f"{line_num} {self.editor_lines[line_num]}")

            # Write to file
            with open(filename, 'w') as f:
                f.write('\n'.join(lines))
                f.write('\n')

            self.output_buffer.append(f"Saved to {filename}")
            self._update_output()

        except Exception as e:
            self.output_buffer.append(f"Error saving file: {e}")
            self._update_output()

    def _load_program(self):
        """Load program from file."""
        # Get filename from user
        filename = self._get_input_dialog("Load file: ")

        if not filename:
            self.output_buffer.append("Load cancelled")
            self._update_output()
            return

        try:
            self._load_program_file(filename)
        except Exception as e:
            self.output_buffer.append(f"Error loading file: {e}")
            self._update_output()

    # Command implementations (inherited from UIBackend)

    def cmd_run(self):
        """Execute RUN command."""
        self._run_program()

    def cmd_list(self, args=""):
        """Execute LIST command."""
        self._list_program()

    def cmd_new(self):
        """Execute NEW command."""
        self._new_program()

    def cmd_load(self, filename):
        """Execute LOAD command."""
        self._load_program_file(filename)
