"""
MBASIC-2025 Interactive Command Mode
Modern implementation of MBASIC 5.21 interactive REPL

Implements the interactive REPL with:
- Line entry and editing
- Direct commands: AUTO, EDIT, HELP (special-cased before parser, see execute_command())
- Immediate mode statements: Most commands (RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES,
  SYSTEM, DELETE, RENUM, CONT, CHAIN, etc.) are parsed as BASIC statements and executed via execute_immediate()
- AUTO command for automatic line numbering with customizable start/step
- EDIT command for character-by-character line editing (insert/delete/copy mode)
- Immediate mode execution (PRINT, LET, etc. without line numbers)

Note: Line number detection happens first in process_line(), then non-numbered lines go to
execute_command() where AUTO/EDIT/HELP are handled before attempting to parse as BASIC statements.
"""

import sys
import re
import os
import traceback
from pathlib import Path
from src.lexer import tokenize
from src.parser import Parser
from src.runtime import Runtime
from src.interpreter import Interpreter, ChainException
import src.ast_nodes as ast_nodes
from src.input_sanitizer import sanitize_and_clear_parity
from src.debug_logger import debug_log_error, is_debug_mode
from src.ui.keybinding_loader import KeybindingLoader

# Try to import readline for better line editing
# This enhances input() with:
# - Backspace/Delete working properly
# - Arrow keys for navigation
# - Command history (up/down arrows)
# - Ctrl+E (end of line)
# - Other Emacs keybindings (Ctrl+K, Ctrl+U, etc.)
# Note: Ctrl+A is rebound for EDIT mode to insert ASCII 0x01 (see _setup_readline)
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


def print_error(e, runtime=None):
    """Print error with optional traceback in MBASIC_DEBUG mode"""
    from src.parser import ParseError

    # For ParseError (user input mistakes), just print simple message
    # Don't log verbose debug info since these are expected user errors, not bugs
    if isinstance(e, ParseError):
        print(f"?{e}")
        return

    # For runtime errors, gather context for debug logging
    context = {}
    if runtime:
        if runtime.pc and runtime.pc.line_num:
            context['current_line'] = runtime.pc.line_num
        if hasattr(runtime, 'line_text_map') and runtime.pc and runtime.pc.line_num:
            line_num = runtime.pc.line_num
            if line_num in runtime.line_text_map:
                context['source_line'] = runtime.line_text_map[line_num]

    # Log error (outputs to stderr in debug mode)
    error_msg = debug_log_error(
        "Runtime error",
        exception=e,
        context=context
    )

    # Normal mode - print error with line number if available
    if runtime and runtime.pc and runtime.pc.line_num:
        line_num = runtime.pc.line_num
        print(f"?{type(e).__name__} in {line_num}: {e}")
        # Also print the source code line if available
        if hasattr(runtime, 'line_text_map') and line_num in runtime.line_text_map:
            print(f"  {runtime.line_text_map[line_num]}")
    else:
        print(f"?{type(e).__name__}: {e}")

    # In debug mode, print a hint about stderr
    if is_debug_mode():
        print("(Full traceback sent to stderr - check console)")


def _format_key_for_display(key_string):
    """
    Convert keybinding format to ^X notation for CLI display.

    Args:
        key_string: Key in format like "Ctrl+A" or "SYSTEM"

    Returns:
        Display string like "^A" or "SYSTEM"
    """
    if key_string.startswith("Ctrl+"):
        # Convert "Ctrl+A" to "^A"
        letter = key_string[5:]
        return f"^{letter}"
    return key_string


class InteractiveMode:
    """MBASIC 5.21 interactive command mode"""

    def __init__(self, io_handler=None, file_io=None):
        # Initialize DEF type map (like Parser does)
        # Import TypeInfo here to avoid circular dependency
        from src.parser import TypeInfo
        self.def_type_map = {}
        # Default type is SINGLE for all letters (use lowercase)
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.def_type_map[letter] = TypeInfo.SINGLE

        # Program manager for line/AST storage
        from editing import ProgramManager
        self.program = ProgramManager(self.def_type_map)

        # For backward compatibility, provide direct access to lines/line_asts
        # (These are now properties that return references to program manager's dictionaries)
        self.current_file = None  # Maintained for compatibility

        self.runtime = None  # Persistent runtime for immediate mode
        self.interpreter = None  # Persistent interpreter
        self.program_runtime = None  # Runtime for RUN (preserved for CONT)
        self.program_interpreter = None  # Interpreter for RUN (preserved for CONT)
        self.ctrl_c_count = 0  # Track consecutive Ctrl+C presses

        # I/O handler (defaults to console if not provided)
        if io_handler is None:
            from src.iohandler.console import ConsoleIOHandler
            io_handler = ConsoleIOHandler(debug_enabled=False)
        self.io = io_handler

        # File I/O module (defaults to real filesystem if not provided)
        if file_io is None:
            from src.file_io import RealFileIO
            file_io = RealFileIO()
        self.file_io = file_io

        # Load CLI keybindings for displaying keyboard shortcuts
        self.keybindings = KeybindingLoader('cli')
        # Cache formatted key displays
        edit_key = self.keybindings.get_primary('editor', 'edit') or 'Ctrl+A'
        stop_key = self.keybindings.get_primary('editor', 'stop') or 'Ctrl+C'
        self.edit_key_display = _format_key_for_display(edit_key)
        self.stop_key_display = _format_key_for_display(stop_key)

    # Properties for backward compatibility
    @property
    def lines(self):
        """Access program lines (backward compatibility)."""
        return self.program.lines

    @property
    def line_asts(self):
        """Access program ASTs (backward compatibility)."""
        return self.program.line_asts

    def parse_single_line(self, line_text, basic_line_num=None):
        """Parse a single line into a LineNode AST.

        Args:
            line_text: The text of the line to parse
            basic_line_num: Optional BASIC line number for error reporting

        Returns: LineNode or None if parse fails
        """
        line_node, error = self.program.parse_single_line(line_text, basic_line_num)

        if error:
            # Print error message
            print(error)
            if basic_line_num is not None:
                print(f"  {line_text}")

        return line_node

    def clear_execution_state(self):
        """Clear GOSUB/RETURN and FOR/NEXT stacks when program is edited.

        This prevents crashes when line edits invalidate saved return addresses
        and loop contexts. Called when lines are added, deleted, or renumbered.

        Note: We do NOT clear/reset the PC here. The PC is preserved so that
        CONT can detect if the program was edited. The cmd_cont() method uses
        pc.is_valid() to check if the PC position still exists after editing.
        If PC is still valid, CONT resumes; if not, shows "?Can't continue"
        matching MBASIC 5.21 behavior.
        """
        if self.program_runtime:
            self.program_runtime.gosub_stack.clear()
            self.program_runtime.for_loops.clear()

    def _setup_readline(self):
        """Configure readline for better line editing"""
        import readline
        import atexit

        # Set up history file
        history_file = os.path.expanduser('~/.mbasic_history')
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass  # No history file yet

        # Save history on exit
        atexit.register(readline.write_history_file, history_file)

        # Set history length
        readline.set_history_length(1000)

        # Setup tab completion for BASIC keywords
        readline.set_completer(self._completer)
        readline.parse_and_bind('tab: complete')

        # Use emacs-style keybindings (default, but be explicit)
        readline.parse_and_bind('set editing-mode emacs')

        # Bind Ctrl+A to insert the character (ASCII 0x01) into the input line,
        # overriding the default Ctrl+A (beginning-of-line) behavior.
        # When the user presses Ctrl+A, readline's 'self-insert' action inserts the
        # 0x01 character into the input buffer (the input line becomes just "^A").
        # When the user then presses Enter, the input is returned to the application.
        # The start() method detects this character in the returned input and enters edit mode.
        readline.parse_and_bind('Control-a: self-insert')

    def _completer(self, text, state):
        """Tab completion for BASIC keywords and commands"""
        # BASIC keywords and common commands
        keywords = [
            'PRINT', 'INPUT', 'LET', 'IF', 'THEN', 'ELSE', 'FOR', 'TO', 'STEP', 'NEXT',
            'GOTO', 'GOSUB', 'RETURN', 'END', 'STOP', 'CONT', 'RUN', 'LIST', 'NEW',
            'LOAD', 'SAVE', 'DELETE', 'RENUM', 'AUTO', 'EDIT', 'WHILE', 'WEND',
            'DIM', 'READ', 'DATA', 'RESTORE', 'ON', 'REM', 'DEF', 'FN',
            'AND', 'OR', 'NOT', 'MOD',
            'DEFINT', 'DEFSNG', 'DEFDBL', 'DEFSTR',
            'MERGE', 'FILES', 'SYSTEM', 'LPRINT'
        ]

        # Get matches
        text_upper = text.upper()
        matches = [kw for kw in keywords if kw.startswith(text_upper)]

        # Return the match at position 'state'
        if state < len(matches):
            # Return in lowercase to match user's input case preference
            if text.islower():
                return matches[state].lower()
            elif text.isupper():
                return matches[state]
            else:
                # Mixed case - return uppercase
                return matches[state]
        return None

    def start(self):
        """Start interactive mode"""
        # Setup readline if available
        if READLINE_AVAILABLE:
            self._setup_readline()

        print("MBASIC-2025 - Modern MBASIC 5.21 Interpreter")
        if not READLINE_AVAILABLE:
            print("(Note: readline not available - line editing limited)")
        else:
            print(f"(Tip: Press {self.edit_key_display} to edit last line, or {self.edit_key_display} followed by line number)")
        print("Ready")

        while True:
            try:
                # Read input
                line = input()

                # Sanitize input: clear parity bits and filter control characters
                # (except Ctrl+A which is used for edit mode)
                if line and line[0] != '\x01':
                    line, _ = sanitize_and_clear_parity(line)

                # Reset Ctrl+C counter on successful input
                self.ctrl_c_count = 0

                # Check for Ctrl+A (edit mode) - character code 0x01
                if line and line[0] == '\x01':
                    # Ctrl+A pressed - enter edit mode
                    # If rest of line has a number, edit that line
                    # Otherwise edit the last line
                    rest = line[1:].strip()
                    if rest and rest.isdigit():
                        line_num = int(rest)
                    else:
                        # Edit last line entered
                        if self.lines:
                            line_num = max(self.lines.keys())
                        else:
                            print("?No lines to edit")
                            continue

                    self.cmd_edit(str(line_num))
                    continue

                # Process line
                if not line.strip():
                    continue

                self.process_line(line)

            except EOFError:
                # Ctrl+D to exit
                print()
                break
            except KeyboardInterrupt:
                # Ctrl+C - track consecutive presses
                print()
                self.ctrl_c_count += 1

                if self.ctrl_c_count >= 3:
                    # Three Ctrl+C in a row - quit
                    print("Exiting...")
                    break
                elif self.ctrl_c_count == 2:
                    # Two Ctrl+C in a row - show hint
                    print(f"Press {self.stop_key_display} again to exit, or type SYSTEM to return to OS")
                else:
                    # First Ctrl+C - just show "Break"
                    print("Break")
                continue
            except Exception as e:
                print_error(e)
                # Reset Ctrl+C counter on other exceptions
                self.ctrl_c_count = 0

    def process_line(self, line):
        """Process a line of input (numbered line or direct command)"""
        line = line.strip()

        # Check if it's a numbered line
        match = re.match(r'^(\d+)\s*(.*)', line)
        if match:
            line_num = int(match.group(1))
            rest = match.group(2)

            if not rest:
                # Delete line
                if line_num in self.lines:
                    del self.lines[line_num]
                    del self.line_asts[line_num]
                    # Clear execution state since line edits invalidate GOSUB/FOR stacks
                    self.clear_execution_state()
                    # Update runtime's statement_table if program is running
                    if self.program_runtime:
                        self.program_runtime.statement_table.delete_line(line_num)
            else:
                # Add/replace line - store both text and parsed AST
                self.lines[line_num] = line
                line_ast = self.parse_single_line(line)
                if line_ast:
                    self.line_asts[line_num] = line_ast
                    # Clear execution state since line edits invalidate GOSUB/FOR stacks
                    self.clear_execution_state()
                    # Update runtime's statement_table if program is running
                    if self.program_runtime:
                        self.program_runtime.statement_table.replace_line(line_num, line_ast)
        else:
            # Direct command
            self.execute_command(line)

    def execute_command(self, cmd):
        """Execute a direct command or immediate mode statement"""
        cmd_stripped = cmd.strip()

        # Parse command and arguments (preserve case for arguments)
        parts = cmd_stripped.split(None, 1)
        command = parts[0].upper() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        # Special commands that require direct handling
        # AUTO, EDIT, and HELP cannot be parsed as BASIC statements (no corresponding AST nodes),
        # so they're handled directly here before attempting to parse.
        # Everything else goes through the parser as immediate mode statements.
        if command == "AUTO":
            self.cmd_auto(args)
        elif command == "EDIT":
            self.cmd_edit(args)
        elif command == "HELP":
            self.cmd_help(args)
        elif command == "":
            pass  # Empty command
        else:
            # Everything else (including LIST, DELETE, RENUM, FILES, RUN, LOAD, SAVE, MERGE, SYSTEM, NEW, PRINT, etc.)
            # goes through the real parser as immediate mode statements
            try:
                self.execute_immediate(cmd)
            except Exception as e:
                # Use the runtime from immediate mode or program runtime
                runtime = self.program_runtime if self.program_runtime else self.runtime
                print_error(e, runtime)

    def cmd_run(self, start_line=None):
        """RUN - Execute the program

        Args:
            start_line: Optional line number to start execution at (for RUN line_number)
        """
        if not self.lines:
            print("?No program")
            return

        try:
            # Execute using line ASTs directly (new style)
            # Runtime will reference self.line_asts which is mutable
            # Pass line text map for better error messages
            from resource_limits import create_unlimited_limits
            runtime = Runtime(self.line_asts, self.lines)
            interpreter = Interpreter(runtime, self.io, limits=create_unlimited_limits(), file_io=self.file_io)
            # Pass reference to interactive mode so statements like LIST can access the line editor
            interpreter.interactive_mode = self

            # Save runtime for CONT
            self.program_runtime = runtime
            self.program_interpreter = interpreter

            # If start_line is specified, we need to handle it specially
            # because interpreter.run() calls start() which calls setup() which resets PC
            if start_line is not None:
                from src.pc import PC
                # Verify the line exists
                if start_line not in self.line_asts:
                    print(f"?Undefined line {start_line}")
                    return

                # Clear variables (RUN line_number clears variables per MBASIC spec)
                runtime.clear_variables()

                # Start the interpreter (which calls setup() and resets PC to first line)
                state = interpreter.start()
                if state.error_info:
                    raise RuntimeError(state.error_info.error_message)

                # NOW set PC to the target line (after setup has built the statement table)
                runtime.pc = PC.from_line(start_line)

                # Run the tick loop manually (same as interpreter.run())
                while runtime.pc.is_running() and not state.error_info:
                    state = interpreter.tick(mode='run', max_statements=10000)

                    # Handle input synchronously for CLI
                    if state.input_prompt:
                        try:
                            value = input()
                            state = interpreter.provide_input(value)
                        except KeyboardInterrupt:
                            self.io.output("")
                            self.io.output(f"Break in {state.current_line or '?'}")
                            return
                        except EOFError:
                            self.io.output("")
                            return
            else:
                # Normal RUN without line number - just call interpreter.run()
                interpreter.run()

        except Exception as e:
            print_error(e, runtime)

    def cmd_cont(self):
        """CONT - Continue execution after STOP or Break

        State management:
        - Uses immutable PC approach: checks if pc.is_running() is False (stopped)
        - Validates PC position with pc.is_valid(program) before resuming
        - Creates new running PC with pc.resume()
        - Resumes tick-based execution loop
        - Handles input prompts and errors during execution

        BUG FIX: Now properly detects if the program has been edited (lines added, deleted,
        or renumbered) by using pc.is_valid() to check if the PC position still exists in
        the program. Shows "?Can't continue" after editing, matching MBASIC 5.21 behavior.
        """
        # Check if we have a stopped program
        if not self.program_runtime or self.program_runtime.pc.is_running():
            print("?Can't continue")
            return

        # Check if PC position is still valid (program may have been edited)
        if not self.program_runtime.pc.is_valid(self.program_runtime.statement_table):
            print("?Can't continue")
            return

        try:
            # Resume execution by creating new running PC at same position
            self.program_runtime.pc = self.program_runtime.pc.resume()

            # Resume execution using tick-based loop (same as run())
            state = self.program_interpreter.state
            while self.program_runtime.pc.is_running() and not state.error_info:
                state = self.program_interpreter.tick(mode='run', max_statements=10000)

                # Handle input synchronously for CLI
                if state.input_prompt:
                    try:
                        value = input()
                        state = self.program_interpreter.provide_input(value)
                    except KeyboardInterrupt:
                        self.io.output("")
                        self.io.output(f"Break in {state.current_line or '?'}")
                        return
                    except EOFError:
                        self.io.output("")
                        return

            # Handle final errors
            if state.error_info:
                raise RuntimeError(state.error_info.error_message)

        except Exception as e:
            print_error(e, self.program_runtime)

    def cmd_list(self, args):
        """LIST [start][-][end] - List program lines"""
        if not self.lines:
            return

        # Parse range
        start = None
        end = None

        if args:
            # Handle various formats: LIST 100, LIST 100-200, LIST -200, LIST 100-
            if '-' in args:
                parts = args.split('-', 1)
                if parts[0]:
                    start = int(parts[0])
                if parts[1]:
                    end = int(parts[1])
            else:
                # Single line or start
                start = int(args)
                end = start

        # Get sorted line numbers
        line_numbers = sorted(self.lines.keys())

        # Filter by range
        for line_num in line_numbers:
            if start is not None and line_num < start:
                continue
            if end is not None and line_num > end:
                continue

            print(self.lines[line_num])

    def cmd_new(self):
        """NEW - Clear program"""
        self.program.clear()
        self.current_file = None
        # Clear execution stacks (GOSUB/FOR/STOP state) when program is cleared
        # Note: program_runtime object persists, only its stacks are cleared
        self.clear_execution_state()
        print("Ready")

    def cmd_save(self, filename):
        """SAVE "filename" - Save program to file"""
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'

            self.program.save_to_file(filename)
            self.current_file = filename
            print(f"Saved to {filename}")

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_load(self, filename):
        """LOAD "filename" - Load program from file"""
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'

            success, errors = self.program.load_from_file(filename)

            if errors:
                # Print parse errors
                for line_num, error in errors:
                    print(error)

            if success:
                self.current_file = filename
                print(f"Loaded from {filename}")
                print("Ready")
            else:
                print("?No lines loaded")

        except FileNotFoundError:
            print(f"?File not found: {filename}")
        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_merge(self, filename):
        """MERGE "filename" - Merge program from file into current program

        MERGE adds or replaces lines from a file without clearing existing lines.
        - Lines with matching line numbers are replaced
        - New line numbers are added
        - Existing lines not in the file are kept
        - If merge is successful AND program_runtime exists, updates runtime's statement_table
          (for CONT support). Runtime update only happens after successful merge.
        """
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Use ProgramManager's merge_from_file
            success, errors, lines_added, lines_replaced = self.program.merge_from_file(filename)

            # Show parse errors if any
            if errors:
                for line_num, error in errors:
                    # Error message from merge_from_file:
                    # Format: "Syntax error in {line_num}: {message}" (no "?" prefix)
                    # Add "?" prefix for MBASIC error style
                    print(f"?{error}")

            if success:
                # Update runtime if it exists (for CONT support)
                if self.program_runtime:
                    for line_num in self.program.line_asts:
                        line_ast = self.program.line_asts[line_num]
                        self.program_runtime.statement_table.replace_line(line_num, line_ast)

                print(f"Merged from {filename}")
                print(f"{lines_added} line(s) added, {lines_replaced} line(s) replaced")
                print("Ready")
            else:
                print("?No lines merged")

        except FileNotFoundError:
            print(f"?File not found: {filename}")
        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def cmd_chain(self, filename, start_line=None, merge=False, all_flag=False, delete_range=None):
        """CHAIN [MERGE] filename$ [, [line_number] [, ALL] [, DELETE range]]

        Chain to another program, optionally:
        - MERGE: Merge as overlay instead of replacing
        - start_line: Begin execution at specified line
        - all_flag: Pass all variables to chained program (ALL option)
        - delete_range: Delete line range after merge (DELETE option)

        Raises ChainException when called during program execution to signal the interpreter's
        run() loop to restart with the new program. This avoids recursive run() calls.
        When called from command line (not during execution), runs the program directly.
        """
        if not filename:
            print("?Syntax error")
            return

        # Remove quotes if present
        filename = filename.strip().strip('"').strip("'")

        if not filename:
            print("?Syntax error")
            return

        try:
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'

            with open(filename, 'r') as f:
                program_text = f.read()

            # Save variables based on CHAIN options:
            # - ALL: passes all variables to the chained program
            # - MERGE: merges program lines (overlays code) - NOTE: Currently also passes all vars
            # - Neither: passes only COMMON variables (resolves type suffixes if needed)
            #
            # KNOWN LIMITATION: In MBASIC 5.21, MERGE and ALL are orthogonal options:
            # - MERGE (without ALL) should only merge lines, keeping existing variables
            # - ALL should pass all variables, replacing the program entirely
            # Current implementation: Both MERGE and ALL result in passing all variables.
            # TODO (Future): Separate line merging (MERGE) from variable passing (ALL).
            # For now, MERGE provides program overlay but also passes all variables.
            saved_variables = None
            if self.program_runtime:
                if all_flag or merge:
                    # Save all variables
                    saved_variables = self.program_runtime.get_all_variables()
                elif self.program_runtime.common_vars:
                    # Save only COMMON variables (in order declared)
                    saved_variables = {}
                    for var_name in self.program_runtime.common_vars:
                        # Resolve type suffix and save first matching variable
                        found = False
                        for suffix in ['%', '$', '!', '#', '']:
                            full_name = var_name + suffix
                            if self.program_runtime.variable_exists(full_name):
                                saved_variables[full_name] = self.program_runtime.get_variable_raw(full_name)
                                found = True
                                break
                        # Skip uninitialized variables

            # Load or merge program
            if merge:
                # MERGE mode - keep existing lines
                for line in program_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Sanitize input: clear parity bits and filter control characters
                    line, _ = sanitize_and_clear_parity(line)

                    match = re.match(r'^(\d+)\s', line)
                    if match:
                        line_num = int(match.group(1))
                        self.lines[line_num] = line
                        line_ast = self.parse_single_line(line)
                        if line_ast:
                            self.line_asts[line_num] = line_ast
            else:
                # Normal mode - clear and load
                self.lines.clear()
                self.line_asts.clear()

                for line in program_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Sanitize input: clear parity bits and filter control characters
                    line, _ = sanitize_and_clear_parity(line)

                    match = re.match(r'^(\d+)\s', line)
                    if match:
                        line_num = int(match.group(1))
                        self.lines[line_num] = line
                        line_ast = self.parse_single_line(line)
                        if line_ast:
                            self.line_asts[line_num] = line_ast

            # Handle DELETE range if specified
            if delete_range and merge:
                # delete_range is a tuple of (start_expr, end_expr)
                # We need to evaluate them if they're expressions
                start_expr, end_expr = delete_range
                # For now, assume they're NumberNodes - full implementation would evaluate
                if hasattr(start_expr, 'value'):
                    start_line_del = int(start_expr.value)
                else:
                    start_line_del = int(start_expr)

                if hasattr(end_expr, 'value'):
                    end_line_del = int(end_expr.value)
                else:
                    end_line_del = int(end_expr)

                # Delete lines in range
                lines_to_delete = [ln for ln in self.lines.keys()
                                   if start_line_del <= ln <= end_line_del]
                for ln in lines_to_delete:
                    del self.lines[ln]
                    if ln in self.line_asts:
                        del self.line_asts[ln]

            # CHAIN: Reuse existing runtime/interpreter to preserve UI references
            # Clear execution state (GOSUB stack, FOR loops, etc.) but keep variables based on options
            if self.program_runtime and self.program_interpreter:
                # Reuse existing objects
                runtime = self.program_runtime
                interpreter = self.program_interpreter

                # Reset runtime with new program (clears stacks, DATA, files, etc.)
                runtime.reset_for_run(self.line_asts, self.lines)

                # Restore variables if saved (after reset which cleared them)
                if saved_variables:
                    runtime.update_variables(saved_variables)

                # Preserve COMMON variable list
                if runtime.common_vars:
                    # Keep the existing common_vars list
                    pass

                # Set starting line if specified
                if start_line:
                    runtime.next_line = start_line

                # Raise ChainException to signal run() loop to restart with new program
                # This avoids recursive run() calls
                raise ChainException()
            else:
                # First time running (from command line, not during execution) - create new objects
                from resource_limits import create_unlimited_limits
                runtime = Runtime(self.line_asts, self.lines)
                interpreter = Interpreter(runtime, self.io, limits=create_unlimited_limits(), file_io=self.file_io)
                interpreter.interactive_mode = self

                # Restore variables if saved
                if saved_variables:
                    runtime.update_variables(saved_variables)

                # Preserve COMMON variable list from previous runtime
                if self.program_runtime and self.program_runtime.common_vars:
                    runtime.common_vars = list(self.program_runtime.common_vars)

                # Save runtime for CONT
                self.program_runtime = runtime
                self.program_interpreter = interpreter

                # Set starting line if specified
                if start_line:
                    runtime.next_line = start_line

                # Run the program (only for first-time from command line)
                interpreter.run()

        except FileNotFoundError:
            print(f"?File not found: {filename}")
        except ChainException:
            # Re-raise ChainException so it can be caught by interpreter.run() loop
            raise
        except Exception as e:
            print_error(e, self.program_runtime if hasattr(self, 'program_runtime') else None)

    def cmd_delete(self, args):
        """DELETE - Delete line or range of lines.

        Delegates to ui_helpers.delete_lines_from_program() which handles:
        - Parsing the delete range syntax
        - Removing lines from program manager
        - Updating runtime statement table if program is loaded
        - Returns list of deleted line numbers (not used by this command)

        Error handling: ValueError is caught and displayed with "?" prefix,
        all other exceptions are converted to "?Syntax error".

        Syntax:
            DELETE 40       - Delete single line 40
            DELETE 40-100   - Delete lines 40 through 100 (inclusive)
            DELETE -40      - Delete all lines up to and including 40
            DELETE 40-      - Delete from line 40 to end of program

        Raises:
            ValueError: Invalid syntax or line range
        """
        from src.ui.ui_helpers import delete_lines_from_program

        try:
            # delete_lines_from_program returns list of deleted line numbers (not used here)
            delete_lines_from_program(self, args, self.program_runtime)
        except ValueError as e:
            print(f"?{e}")
        except Exception as e:
            print(f"?Syntax error")

    def cmd_renum(self, args):
        """RENUM [new_start][,[old_start][,increment]] - Renumber program lines and update references

        Delegates to renum_program() from ui_helpers.
        The renum_program() implementation uses an AST-based approach (see ui_helpers.py):
        1. Parse program to AST
        2. Build line number mapping (old -> new)
        3. Walk AST and update all line number references (via _renum_statement callback)
        4. Serialize AST back to source

        ERL handling: ERL expressions with ANY binary operators (ERL+100, ERL*2, ERL=100)
        have all right-hand numbers renumbered, even for arithmetic operations.
        This is intentionally broader than the MBASIC manual (which only specifies comparison
        operators like ERL=100) to avoid missing valid line references. Rationale: We cannot
        distinguish ERL=100 (comparison, renumber) from ERL+100 (arithmetic, don't renumber)
        without semantic analysis, so we conservatively renumber both. Known limitation: arithmetic
        like "IF ERL+100 THEN..." will incorrectly renumber 100 if it's an old line number.
        This is rare in practice. See _renum_erl_comparison() for implementation details.

        Args format: "new_start,old_start,increment"
        Examples:
            RENUM           -> 10,0,10 (renumber all from line 10)
            RENUM 100       -> 100,0,10 (renumber all from line 100)
            RENUM 100,50    -> 100,50,10 (renumber from line 50 onwards)
            RENUM 100,50,20 -> 100,50,20 (full control)
        """
        from src.ui.ui_helpers import renum_program

        try:
            # Use consolidated RENUM implementation
            old_lines, line_map = renum_program(
                self.program,
                args,
                self._renum_statement,
                self.program_runtime
            )
            # Clear execution state since renumbering invalidates GOSUB/FOR stacks
            # (line numbers in stacks are now incorrect)
            self.clear_execution_state()
            print("Renumbered")

        except ValueError as e:
            print(f"?{e}")
        except Exception as e:
            print(f"?Error during renumber: {e}")


    def _renum_statement(self, stmt, line_map):
        """Recursively update line number references in a statement

        Args:
            stmt: Statement node to update
            line_map: dict mapping old line numbers to new line numbers
        """
        import src.ast_nodes as ast_nodes

        stmt_type = type(stmt).__name__

        # GOTO statement
        if stmt_type == 'GotoStatementNode':
            if stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # GOSUB statement
        elif stmt_type == 'GosubStatementNode':
            if stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # ON...GOTO/GOSUB statement
        elif stmt_type == 'OnGotoStatementNode' or stmt_type == 'OnGosubStatementNode':
            stmt.target_lines = [
                line_map.get(line, line) for line in stmt.target_lines
            ]

        # IF statement with line number jumps
        elif stmt_type == 'IfStatementNode':
            if stmt.then_line_number is not None and stmt.then_line_number in line_map:
                stmt.then_line_number = line_map[stmt.then_line_number]
            if stmt.else_line_number is not None and stmt.else_line_number in line_map:
                stmt.else_line_number = line_map[stmt.else_line_number]

            # Check for "IF ERL = line_number" pattern
            # According to manual: if ERL is on left side of =, right side is a line number
            if stmt.condition:
                self._renum_erl_comparison(stmt.condition, line_map)

            # Also update statements within THEN/ELSE blocks
            if stmt.then_statements:
                for then_stmt in stmt.then_statements:
                    self._renum_statement(then_stmt, line_map)
            if stmt.else_statements:
                for else_stmt in stmt.else_statements:
                    self._renum_statement(else_stmt, line_map)

        # RESTORE statement
        elif stmt_type == 'RestoreStatementNode':
            if stmt.line_number_expr and hasattr(stmt.line_number_expr, 'value'):
                # It's a literal number
                if stmt.line_number_expr.value in line_map:
                    stmt.line_number_expr.value = line_map[stmt.line_number_expr.value]

        # RUN statement
        elif stmt_type == 'RunStatementNode':
            if hasattr(stmt, 'line_number') and stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

        # ON ERROR GOTO statement
        elif stmt_type == 'OnErrorStatementNode':
            if stmt.line_number is not None and stmt.line_number in line_map:
                stmt.line_number = line_map[stmt.line_number]

    def _renum_erl_comparison(self, expr, line_map):
        """Handle binary operations with ERL on left side

        MBASIC 5.21 Manual Specification:
        When ERL appears on the left side of a comparison operator (=, <>, <, >, <=, >=),
        the right-hand number is treated as a line number reference and should be renumbered.
        Note: Only ERL on LEFT side is checked (ERL = 100, not 100 = ERL).

        INTENTIONAL DEVIATION FROM MANUAL:
        This implementation renumbers for ANY binary operator with ERL on left, including
        arithmetic operators (ERL + 100, ERL * 2, etc.), not just comparison operators.
        This is a deliberate design choice to avoid missing valid line number references.

        Rationale: We cannot reliably distinguish comparison operators (ERL=100) from
        arithmetic operators (ERL+100) without complex semantic analysis. To ensure we never
        miss renumbering a valid line reference in a comparison, we conservatively renumber
        ALL binary operations with ERL on the left side.

        Known limitation: Arithmetic like "IF ERL+100 THEN..." will incorrectly renumber
        the 100 if it happens to be an old line number. This is rare in practice.

        Implementation: Checks if expression is BinaryOpNode with ERL (VariableNode) on left
        and NumberNode on right. Operator type is intentionally NOT checked - all operators
        are treated the same to implement the conservative renumbering strategy described above.

        Args:
            expr: Expression node to check
            line_map: dict mapping old line numbers to new line numbers
        """
        # Check if this is a binary operation
        if type(expr).__name__ != 'BinaryOpNode':
            return

        # Check if left side is ERL (a VariableNode with name 'ERL')
        left = expr.left
        if type(left).__name__ == 'VariableNode' and left.name == 'ERL':
            # Right side should be renumbered if it's a literal number
            right = expr.right
            if type(right).__name__ == 'NumberNode':
                # Check if this number is a line number in our program
                if right.value in line_map:
                    right.value = line_map[right.value]

    def _serialize_line(self, line_node):
        """Serialize a LineNode back to source text, preserving indentation

        Args:
            line_node: LineNode to serialize

        Returns:
            str: Source text for the line
        """
        from src.ui.ui_helpers import serialize_line
        return serialize_line(line_node)

    def _serialize_statement(self, stmt):
        """Serialize a statement node back to source text

        Args:
            stmt: Statement node to serialize

        Returns:
            str: Source text for the statement
        """
        from src.ui.ui_helpers import serialize_statement
        return serialize_statement(stmt)

    def _serialize_variable(self, var):
        """Serialize a variable reference"""
        from src.ui.ui_helpers import serialize_variable
        return serialize_variable(var)

    def _token_to_operator(self, token_type):
        """Convert a TokenType operator to its string representation"""
        from src.ui.ui_helpers import token_to_operator
        return token_to_operator(token_type)

    def _serialize_expression(self, expr):
        """Serialize an expression node to source text"""
        from src.ui.ui_helpers import serialize_expression
        return serialize_expression(expr)

    def cmd_edit(self, args):
        """EDIT line_number - Character-by-character line editor

        EDIT 100 - Edit line 100 using edit subcommands

        Edit mode subcommands (all implemented):
        - Space: Move cursor right, printing character
        - D: Delete character at cursor
        - C: Change character at cursor
        - I<text>$: Insert text ($ = Escape)
        - X: Extend line (go to end and insert)
        - H: Delete to end and insert
        - L: List rest of line, return to start
        - E: End and save (don't print rest)
        - Q: Quit without saving
        - A: Abort and restart
        - <CR>: End and save

        Not yet implemented: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K).

        INTENTIONAL MBASIC-COMPATIBLE BEHAVIOR: When digits are entered, they silently do nothing
        (no output, no cursor movement, no error). This matches MBASIC 5.21 behavior where digits
        are reserved for count prefixes (e.g., "3D" = delete 3 chars). Implementation: digits fall
        through the command checks without matching any elif branch. Future enhancement will add
        explicit digit parsing to accumulate count prefixes for commands like [n]D, [n]C, [n]S.
        """
        if not args or not args.strip():
            print("?Syntax error - specify line number")
            return

        try:
            line_num = int(args.strip())
        except ValueError:
            print("?Syntax error - invalid line number")
            return

        # Check if line exists
        if line_num not in self.lines:
            print(f"?Undefined line number: {line_num}")
            return

        # Get the current line text (without line number prefix)
        current_line = self.lines[line_num]
        import re
        match = re.match(r'^\d+\s*', current_line)
        if match:
            original_text = current_line[match.end():]
        else:
            original_text = current_line

        # Edit state
        text = original_text
        cursor = 0
        new_text = ""

        # Display line number prompt
        print(f"{line_num}", end='', flush=True)

        try:
            while True:
                # Read one character at a time
                ch = self._read_char()

                if ch is None:  # EOF
                    print()
                    return

                # Handle edit commands
                if ch == '\r' or ch == '\n':
                    # CR: Save changes and exit
                    # Print rest of line
                    print(text[cursor:])
                    new_text += text[cursor:]
                    break

                elif ch == ' ':
                    # Space: Move cursor right and print character
                    if cursor < len(text):
                        print(text[cursor], end='', flush=True)
                        new_text += text[cursor]
                        cursor += 1

                elif ch.upper() == 'D':
                    # Delete: Delete character at cursor
                    if cursor < len(text):
                        print(f"\\{text[cursor]}\\", end='', flush=True)
                        cursor += 1

                elif ch.upper() == 'I':
                    # Insert: Insert text at cursor
                    insert_text = self._read_until_escape()
                    print(insert_text, end='', flush=True)
                    new_text += insert_text

                elif ch.upper() == 'X':
                    # Extend: Go to end and insert
                    new_text += text[cursor:]
                    cursor = len(text)
                    insert_text = self._read_until_escape()
                    print(insert_text, end='', flush=True)
                    new_text += insert_text

                elif ch.upper() == 'H':
                    # H: Delete to end and insert
                    cursor = len(text)
                    insert_text = self._read_until_escape()
                    print(insert_text, end='', flush=True)
                    new_text += insert_text

                elif ch.upper() == 'E':
                    # E: End without printing rest
                    print()
                    break

                elif ch.upper() == 'Q':
                    # Q: Quit without saving
                    print()
                    return

                elif ch.upper() == 'L':
                    # L: List rest and go to start
                    print(text[cursor:])
                    cursor = 0
                    new_text = ""
                    print(f"{line_num}", end='', flush=True)

                elif ch.upper() == 'A':
                    # A: Abort and restart
                    print()
                    text = original_text
                    cursor = 0
                    new_text = ""
                    print(f"{line_num}", end='', flush=True)

                elif ch.upper() == 'C':
                    # C: Change next character
                    if cursor < len(text):
                        replacement = self._read_char()
                        if replacement:
                            print(replacement, end='', flush=True)
                            new_text += replacement
                            cursor += 1

            # Update the line with new text
            full_line = str(line_num) + " " + new_text
            self.lines[line_num] = full_line

            # Parse and update AST
            line_ast = self.parse_single_line(full_line)
            if line_ast:
                self.line_asts[line_num] = line_ast
                # Update runtime's statement_table if program is running
                if self.program_runtime:
                    self.program_runtime.statement_table.replace_line(line_num, line_ast)
                # Clear execution state since line edits invalidate GOSUB/FOR stacks
                # (must be called after statement_table update)
                self.clear_execution_state()

        except KeyboardInterrupt:
            # Ctrl+C cancels edit
            print()
            return

    def _read_char(self):
        """Read a single character from stdin"""
        import sys
        import tty
        import termios

        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                return ch if ch else None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (AttributeError, OSError, ImportError):
            # Fallback for non-TTY/piped input or terminal errors
            # (AttributeError: fd not available, OSError/termios.error: raw mode failed,
            #  ImportError: termios not available on Windows)
            ch = sys.stdin.read(1)
            return ch if ch else None

    def _read_until_escape(self):
        """Read characters until Escape ($) is pressed"""
        result = ""
        while True:
            ch = self._read_char()
            if ch is None or ch == '\x1b' or ch == '$':  # ESC or $
                break
            elif ch == '\x7f' or ch == '\x08':  # DEL or Backspace
                if result:
                    result = result[:-1]
                    print('\b \b', end='', flush=True)
            else:
                result += ch
        return result

    def cmd_auto(self, args):
        """AUTO [start][,increment] - Automatic line numbering mode

        AUTO - Use default start/increment from settings
        AUTO 100 - Start at 100, use default increment
        AUTO 100,5 - Start at 100, increment by 5
        AUTO ,5 - Use default start, increment by 5
        """
        # Load defaults from settings
        from src.settings import get
        start = get('auto_number_start')
        increment = get('auto_number_step')

        if args:
            parts = args.split(',')
            # Handle "AUTO start" or "AUTO start,increment"
            if parts[0].strip():
                try:
                    start = int(parts[0].strip())
                except ValueError:
                    print("?Syntax error")
                    return
            # Handle "AUTO ,increment" or "AUTO start,increment"
            if len(parts) > 1 and parts[1].strip():
                try:
                    increment = int(parts[1].strip())
                except ValueError:
                    print("?Syntax error")
                    return

        # Enter AUTO mode
        current_line = start

        try:
            while True:
                # Check if line already exists
                if current_line in self.lines:
                    # Show asterisk for existing line
                    prompt = f"*{current_line} "
                else:
                    # Show line number for new line
                    prompt = f"{current_line} "

                # Read input
                try:
                    line_text = input(prompt)
                except EOFError:
                    # Ctrl+D exits AUTO mode
                    print()
                    break

                # Sanitize input: clear parity bits and filter control characters
                # (second return value is bool indicating if parity bits were found; not needed here)
                line_text, _ = sanitize_and_clear_parity(line_text)

                # Check if line is empty (just pressing Enter)
                if not line_text or not line_text.strip():
                    # Empty line exits AUTO mode
                    break

                # Add the line with its number
                full_line = str(current_line) + " " + line_text.strip()
                self.lines[current_line] = full_line

                # Parse and store AST
                line_ast = self.parse_single_line(full_line)
                if line_ast:
                    self.line_asts[current_line] = line_ast
                    # Update runtime's statement_table if program is running
                    if self.program_runtime:
                        self.program_runtime.statement_table.replace_line(current_line, line_ast)

                # Move to next line number
                current_line += increment

        except KeyboardInterrupt:
            # Ctrl+C exits AUTO mode
            print()
            return

    def cmd_help(self, args=""):
        """HELP - Show help information about commands"""
        print()
        print("MBASIC-2025 Commands:")
        print()
        print("Program Management:")
        print("  NEW                - Clear program")
        print("  RUN [line]         - Run program")
        print("  LOAD \"file\"        - Load program")
        print("  SAVE \"file\"        - Save program")
        print("  MERGE \"file\"       - Merge program")
        print("  LIST [range]       - List program lines")
        print("  DELETE range       - Delete lines")
        print("  RENUM [params]     - Renumber lines")
        print("  AUTO [start][,inc] - Auto line numbering")
        print("  EDIT line          - Edit line")
        print()
        print("Debugging:")
        print("  BREAK line         - Set breakpoint at line")
        print("  STEP               - Execute one statement")
        print("  CONT               - Continue execution")
        print("  STACK              - Show execution stack")
        print()
        print("Settings:")
        print("  SHOW SETTINGS [\"pattern\"] - View settings")
        print("  SET \"setting\" value       - Change setting")
        print()
        print("File System:")
        print("  FILES [\"pattern\"]  - List files")
        print("  SYSTEM             - Exit")
        print()

    def cmd_system(self):
        """SYSTEM - Exit to operating system"""
        print("Goodbye")
        self.file_io.system_exit()

    def cmd_files(self, filespec):
        """FILES [filespec] - Display directory listing

        FILES - List all files in current directory
        FILES "*.BAS" - List files matching pattern

        Note: Drive letter syntax (e.g., "A:*.*") from CP/M and DOS is not supported.
        This is a modern implementation running on Unix-like and Windows systems where
        CP/M-style drive letter prefixes don't apply. Use standard path patterns instead
        (e.g., "*.BAS", "../dir/*.BAS"). Drive letter mapping is not currently planned.
        """
        from src.ui.ui_helpers import list_files

        try:
            files = list_files(filespec)

            if not files:
                pattern = filespec if filespec else "*"
                print(f"No files matching: {pattern}")
                return

            # Display files (MBASIC shows them in columns)
            # Simple format: one per line with size
            for filename, size, is_dir in files:
                if is_dir:
                    print(f"{filename:<20}      <DIR>")
                elif size is not None:
                    print(f"{filename:<20} {size:>8} bytes")
                else:
                    print(f"{filename:<20}        ? bytes")

            # Show count
            print(f"\n{len(files)} File(s)")

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def execute_immediate(self, statement):
        """Execute a statement in immediate mode (no line number)

        Runtime selection:
        - If program_runtime exists (from RUN), use it so immediate mode can
          examine/modify program variables. Works for stopped programs (via STOP/Break)
          AND finished programs (program_runtime persists until NEW/LOAD/next RUN).
        - Otherwise use persistent immediate mode runtime for variable isolation
        """
        # Build a minimal program with line 0
        program_text = "0 " + statement

        # Initialize runtime to None in case parsing fails
        runtime = None

        try:
            tokens = list(tokenize(program_text))
            parser = Parser(tokens, self.def_type_map)
            ast = parser.parse()

            # Choose which runtime to use:
            # - If program has been run (especially if stopped), use program runtime
            # - Otherwise use immediate mode runtime
            if self.program_runtime is not None:
                # Use program runtime so we can access program variables
                runtime = self.program_runtime
                interpreter = self.program_interpreter
            else:
                # Initialize immediate mode runtime if needed
                if self.runtime is None:
                    from resource_limits import create_unlimited_limits
                    # Pass empty line_text_map since immediate mode uses temporary line 0.
                    # Design note: Could pass {0: statement} to improve error reporting, but immediate
                    # mode errors typically reference the statement the user just typed (visible on screen),
                    # so line_text_map provides minimal benefit. Future enhancement if needed.
                    self.runtime = Runtime(ast, {})
                    self.runtime.setup()
                    self.interpreter = Interpreter(self.runtime, self.io, limits=create_unlimited_limits())
                    # Pass reference to interactive mode for commands like LOAD/SAVE
                    self.interpreter.interactive_mode = self
                runtime = self.runtime
                interpreter = self.interpreter

            # Execute just the statement at line 0
            if ast.lines and len(ast.lines) > 0:
                line_node = ast.lines[0]
                # Save old PC to preserve stopped program position for CONT.
                # Note: GOTO/GOSUB in immediate mode work but PC restoration affects CONT behavior:
                # They execute and jump during execute_statement(), but we restore the
                # original PC afterward to preserve CONT functionality. This means:
                # - The jump happens and target code runs during execute_statement()
                # - The final PC change is then reverted, preserving the stopped position
                # - CONT will resume at the original stopped location, not the GOTO target
                # This implementation allows GOTO/GOSUB to function while preserving CONT state.
                # However, the transient jump behavior may be unexpected - use this feature cautiously.
                old_pc = runtime.pc

                # Execute each statement on line 0
                for stmt in line_node.statements:
                    interpreter.execute_statement(stmt)

                # Restore previous PC to maintain stopped program position
                # This reverts any GOTO/GOSUB PC changes from above execution
                runtime.pc = old_pc

        except Exception as e:
            # Use helper function for consistent error reporting
            print_error(e, runtime)

    def get_program_text(self):
        """Get program as text"""
        lines = []
        for line_num in sorted(self.lines.keys()):
            lines.append(self.lines[line_num])
        return '\n'.join(lines) + '\n'
