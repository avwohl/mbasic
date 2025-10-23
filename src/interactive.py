"""
MBASIC 5.21 Interactive Command Mode

Implements the interactive REPL with:
- Line entry and editing
- Direct commands (RUN, LIST, SAVE, LOAD, NEW, etc.)
- Immediate mode execution
"""

import sys
import re
import os
import traceback
from pathlib import Path
from lexer import tokenize
from parser import Parser
from runtime import Runtime
from interpreter import Interpreter
import ast_nodes

# Try to import readline for better line editing
# This enhances input() with:
# - Backspace/Delete working properly
# - Arrow keys for navigation
# - Command history (up/down arrows)
# - Ctrl+A (start of line), Ctrl+E (end of line)
# - Emacs keybindings (Ctrl+K, Ctrl+U, etc.)
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


def print_error(e, runtime=None):
    """Print error with optional traceback in DEBUG mode"""
    if os.environ.get('DEBUG'):
        # Print full traceback in debug mode
        print(f"?{type(e).__name__}: {e}")
        traceback.print_exc()
    else:
        # Normal mode - just print error with line number if available
        if runtime and runtime.current_line:
            print(f"?{type(e).__name__} in {runtime.current_line.line_number}: {e}")
        else:
            print(f"?{type(e).__name__}: {e}")


class InteractiveMode:
    """MBASIC 5.21 interactive command mode"""

    def __init__(self):
        self.lines = {}  # line_number -> line_text (for SAVE/LIST)
        self.line_asts = {}  # line_number -> LineNode (parsed AST)
        self.current_file = None
        self.runtime = None  # Persistent runtime for immediate mode
        self.interpreter = None  # Persistent interpreter
        self.program_runtime = None  # Runtime for RUN (preserved for CONT)
        self.program_interpreter = None  # Interpreter for RUN (preserved for CONT)
        self.ctrl_c_count = 0  # Track consecutive Ctrl+C presses

        # Initialize DEF type map (like Parser does)
        # Import TypeInfo here to avoid circular dependency
        from parser import TypeInfo
        self.def_type_map = {}
        # Default type is SINGLE for all letters (use lowercase)
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.def_type_map[letter] = TypeInfo.SINGLE

    def parse_single_line(self, line_text):
        """Parse a single line into a LineNode AST.

        Returns: LineNode or None if parse fails
        """
        try:
            tokens = list(tokenize(line_text))
            parser = Parser(tokens, self.def_type_map)
            line_node = parser.parse_line()
            return line_node
        except Exception as e:
            print(f"?Syntax error: {e}")
            return None

    def clear_execution_state(self):
        """Clear GOSUB/RETURN and FOR/NEXT stacks when program is edited.

        This prevents crashes when line edits invalidate saved return addresses
        and loop contexts. Called when lines are added, deleted, or renumbered.
        """
        if self.program_runtime:
            self.program_runtime.gosub_stack.clear()
            self.program_runtime.for_loops.clear()
            # Also clear STOP state since line edits invalidate the stop position
            self.program_runtime.stopped = False
            self.program_runtime.stop_line = None
            self.program_runtime.stop_stmt_index = None

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

        # Bind Ctrl+A to insert itself (so we can detect it in input)
        # This overrides the default Ctrl+A (beginning-of-line) for MBASIC compatibility
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

        print("MBASIC 5.21 Interpreter")
        if not READLINE_AVAILABLE:
            print("(Note: readline not available - line editing limited)")
        else:
            print("(Tip: Press Ctrl+A to edit last line, or Ctrl+A followed by line number)")
        print("Ready")

        while True:
            try:
                # Read input
                line = input()

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
                    print("Press Ctrl+C again to exit, or type SYSTEM to return to OS")
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
                    # Update runtime's line_table if program is running
                    if self.program_runtime and line_num in self.program_runtime.line_table:
                        del self.program_runtime.line_table[line_num]
                        if line_num in self.program_runtime.line_order:
                            self.program_runtime.line_order.remove(line_num)
            else:
                # Add/replace line - store both text and parsed AST
                self.lines[line_num] = line
                line_ast = self.parse_single_line(line)
                if line_ast:
                    self.line_asts[line_num] = line_ast
                    # Update runtime's line_table if program is running
                    if self.program_runtime:
                        self.program_runtime.line_table[line_num] = line_ast
                        if line_num not in self.program_runtime.line_order:
                            # Insert in sorted position
                            import bisect
                            bisect.insort(self.program_runtime.line_order, line_num)
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

        # Meta-commands (editor commands that manipulate program source)
        # Only AUTO and EDIT are true meta-commands that can't be parsed
        # Everything else (LIST, DELETE, RENUM, FILES, LOAD, SAVE, etc.) goes through parser
        if command == "AUTO":
            self.cmd_auto(args)
        elif command == "EDIT":
            self.cmd_edit(args)
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

    def cmd_run(self):
        """RUN - Execute the program"""
        if not self.lines:
            print("?No program")
            return

        try:
            # Execute using line ASTs directly (new style)
            # Runtime will reference self.line_asts which is mutable
            runtime = Runtime(self.line_asts)
            interpreter = Interpreter(runtime)
            # Pass reference to interactive mode so statements like LIST can access the line editor
            interpreter.interactive_mode = self

            # Save runtime for CONT
            self.program_runtime = runtime
            self.program_interpreter = interpreter

            interpreter.run()

        except Exception as e:
            print_error(e, runtime)

    def cmd_cont(self):
        """CONT - Continue execution after STOP or Break"""
        if not self.program_runtime or not self.program_runtime.stopped:
            print("?Can't continue")
            return

        try:
            # Clear stopped flag
            self.program_runtime.stopped = False

            # Restore execution position
            self.program_runtime.current_line = self.program_runtime.stop_line
            self.program_runtime.current_stmt_index = self.program_runtime.stop_stmt_index
            self.program_runtime.halted = False

            # Resume execution - we need to continue from where we stopped,
            # not restart from the beginning. We'll use run_from_current()
            # which doesn't call setup() and continues from current position.
            self.program_interpreter.run_from_current()

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
        self.lines.clear()
        self.line_asts.clear()
        self.current_file = None
        # Clear execution state when program is cleared
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

            program_text = self.get_program_text()

            with open(filename, 'w') as f:
                f.write(program_text)

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

            with open(filename, 'r') as f:
                program_text = f.read()

            # Clear current program
            self.lines.clear()
            self.line_asts.clear()

            # Parse and load lines
            for line in program_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'^(\d+)\s', line)
                if match:
                    line_num = int(match.group(1))
                    self.lines[line_num] = line
                    # Parse line into AST
                    line_ast = self.parse_single_line(line)
                    if line_ast:
                        self.line_asts[line_num] = line_ast

            self.current_file = filename
            print(f"Loaded from {filename}")
            print("Ready")

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

            # Don't clear current program - that's the difference from LOAD
            # Parse and merge lines
            lines_added = 0
            lines_replaced = 0

            for line in program_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'^(\d+)\s', line)
                if match:
                    line_num = int(match.group(1))
                    if line_num in self.lines:
                        lines_replaced += 1
                    else:
                        lines_added += 1
                    self.lines[line_num] = line
                    # Parse line into AST
                    line_ast = self.parse_single_line(line)
                    if line_ast:
                        self.line_asts[line_num] = line_ast
                        # Update runtime's line_table if program is running
                        if self.program_runtime:
                            self.program_runtime.line_table[line_num] = line_ast
                            if line_num not in self.program_runtime.line_order:
                                import bisect
                                bisect.insort(self.program_runtime.line_order, line_num)

            print(f"Merged from {filename}")
            print(f"{lines_added} line(s) added, {lines_replaced} line(s) replaced")
            print("Ready")

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
            # - MERGE: always preserves all variables (it's an overlay)
            # - ALL: passes all variables to new program
            # - Neither: only pass COMMON variables
            saved_variables = None
            if self.program_runtime:
                if all_flag or merge:
                    # Save all variables
                    saved_variables = self.program_runtime.get_all_variables()
                elif self.program_runtime.common_vars:
                    # Save only COMMON variables (in order)
                    # Note: common_vars stores base names (e.g., "i"), but actual variables
                    # may have type suffixes (e.g., "i%", "i$") based on DEF statements
                    saved_variables = {}
                    for var_name in self.program_runtime.common_vars:
                        # Try to find the variable with type suffix
                        # Check all possible type suffixes: %, $, !, #
                        found = False
                        for suffix in ['%', '$', '!', '#', '']:
                            full_name = var_name + suffix
                            if self.program_runtime.variable_exists(full_name):
                                saved_variables[full_name] = self.program_runtime.get_variable_raw(full_name)
                                found = True
                                break
                        # If not found with any suffix, the variable might not have been initialized
                        # That's okay - we just skip it

            # Load or merge program
            if merge:
                # MERGE mode - keep existing lines
                for line in program_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

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

            # Run the program
            runtime = Runtime(self.line_asts)
            interpreter = Interpreter(runtime)
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

            # Run the program
            interpreter.run()

        except FileNotFoundError:
            print(f"?File not found: {filename}")
        except Exception as e:
            print_error(e, self.program_runtime if hasattr(self, 'program_runtime') else None)

    def cmd_delete(self, args):
        """DELETE start-end - Delete range of lines"""
        if not args or '-' not in args:
            print("?Syntax error")
            return

        try:
            parts = args.split('-', 1)
            start = int(parts[0]) if parts[0] else min(self.lines.keys())
            end = int(parts[1]) if parts[1] else max(self.lines.keys())

            # Delete lines in range
            to_delete = [n for n in self.lines.keys() if start <= n <= end]
            for line_num in to_delete:
                del self.lines[line_num]
                if line_num in self.line_asts:
                    del self.line_asts[line_num]
                # Update runtime's line_table if program is running
                if self.program_runtime and line_num in self.program_runtime.line_table:
                    del self.program_runtime.line_table[line_num]
                    if line_num in self.program_runtime.line_order:
                        self.program_runtime.line_order.remove(line_num)

        except Exception as e:
            print(f"?Syntax error")

    def cmd_renum(self, args):
        """RENUM [new_start][,increment] - Renumber program lines and update references

        Uses AST-based approach:
        1. Parse program to AST
        2. Build line number mapping (old -> new)
        3. Walk AST and update all line number references
        4. Serialize AST back to source
        """
        new_start = 10
        increment = 10

        if args:
            parts = args.split(',')
            if parts[0]:
                new_start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                increment = int(parts[1])

        try:
            # Build mapping from old line numbers to new line numbers
            old_lines = sorted(self.line_asts.keys())
            line_map = {}

            new_num = new_start
            for old_num in old_lines:
                line_map[old_num] = new_num
                new_num += increment

            # Walk each line AST and update line number references
            for line_node in self.line_asts.values():
                # Update line number references in statements
                for stmt in line_node.statements:
                    self._renum_statement(stmt, line_map)
                # Update the line's own number
                old_line_num = line_node.line_number
                line_node.line_number = line_map[old_line_num]

            # Rebuild line_asts dict with new line numbers
            new_line_asts = {}
            new_lines = {}
            for old_num in old_lines:
                new_num = line_map[old_num]
                line_node = self.line_asts[old_num]
                new_line_asts[new_num] = line_node
                new_lines[new_num] = self._serialize_line(line_node)

            self.line_asts = new_line_asts
            self.lines = new_lines

            # Update runtime's line_table if program is running
            if self.program_runtime:
                self.program_runtime.line_table = self.line_asts
                self.program_runtime.line_order = sorted(self.line_asts.keys())

            print("Renumbered")

        except Exception as e:
            print(f"?Error during renumber: {e}")


    def _renum_statement(self, stmt, line_map):
        """Recursively update line number references in a statement

        Args:
            stmt: Statement node to update
            line_map: dict mapping old line numbers to new line numbers
        """
        import ast_nodes

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
        """Handle ERL = line_number patterns in expressions

        According to MBASIC manual: if ERL appears on the left side of =,
        the number on the right side is treated as a line number reference.

        Also handles: ERL <> line, ERL < line, ERL > line, etc.

        Args:
            expr: Expression node to check
            line_map: dict mapping old line numbers to new line numbers
        """
        # Check if this is a binary operation (comparison)
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
        # Start with line number
        line_num_str = str(line_node.line_number)
        parts = [line_num_str]

        # Preserve indentation from original source
        # The column indicates where the first statement started in the original source
        # We maintain the same column position (absolute indentation) when possible
        if line_node.statements:
            first_stmt = line_node.statements[0]
            if hasattr(first_stmt, 'column') and first_stmt.column > 0:
                # The original statement was at this column (1-indexed)
                # We want to put the statement at the same column position
                current_pos = len(line_num_str) + 1  # +1 for 1-indexed
                desired_col = first_stmt.column

                # Add spacing to reach the desired column
                # But ensure at least 1 space after line number
                spaces_needed = max(1, desired_col - current_pos)
                parts.append(' ' * spaces_needed)
            else:
                parts.append(' ')

            # Serialize each statement
            for i, stmt in enumerate(line_node.statements):
                stmt_text = self._serialize_statement(stmt)
                if i == 0:
                    parts.append(stmt_text)
                else:
                    parts.append(' : ' + stmt_text)

        return ''.join(parts)

    def _serialize_statement(self, stmt):
        """Serialize a statement node back to source text

        Args:
            stmt: Statement node to serialize

        Returns:
            str: Source text for the statement
        """
        import ast_nodes

        stmt_type = type(stmt).__name__

        # This is a simplified serializer - only handles common cases
        # For a complete implementation, we'd need to handle all statement types

        if stmt_type == 'PrintStatementNode':
            parts = ['print']
            for i, expr in enumerate(stmt.expressions):
                if i > 0 and i <= len(stmt.separators):
                    # Add separator from previous expression
                    sep = stmt.separators[i-1] if i-1 < len(stmt.separators) else ''
                    if sep:
                        parts.append(sep)
                parts.append(' ' if not parts[-1].endswith(' ') else '')
                parts.append(self._serialize_expression(expr))
            return ''.join(parts)

        elif stmt_type == 'GotoStatementNode':
            return f"goto {stmt.line_number}"

        elif stmt_type == 'GosubStatementNode':
            return f"gosub {stmt.line_number}"

        elif stmt_type == 'LetStatementNode':
            var_text = self._serialize_variable(stmt.variable)
            expr_text = self._serialize_expression(stmt.expression)
            return f"{var_text} = {expr_text}"

        elif stmt_type == 'EndStatementNode':
            return "end"

        elif stmt_type == 'ReturnStatementNode':
            return "return"

        elif stmt_type == 'StopStatementNode':
            return "stop"

        elif stmt_type == 'RemarkStatementNode':
            # Preserve comments using REM
            return f"rem {stmt.text}"

        elif stmt_type == 'IfStatementNode':
            parts = ['if ', self._serialize_expression(stmt.condition)]
            if stmt.then_line_number is not None:
                parts.append(f' then {stmt.then_line_number}')
            elif stmt.then_statements:
                parts.append(' then ')
                parts.append(' : '.join(self._serialize_statement(s) for s in stmt.then_statements))
            if stmt.else_line_number is not None:
                parts.append(f' else {stmt.else_line_number}')
            elif stmt.else_statements:
                parts.append(' else ')
                parts.append(' : '.join(self._serialize_statement(s) for s in stmt.else_statements))
            return ''.join(parts)

        elif stmt_type == 'ForStatementNode':
            var = self._serialize_variable(stmt.variable)
            start = self._serialize_expression(stmt.start_expr)
            end = self._serialize_expression(stmt.end_expr)
            parts = [f"for {var} = {start} to {end}"]
            if stmt.step_expr:
                step = self._serialize_expression(stmt.step_expr)
                parts.append(f" step {step}")
            return ''.join(parts)

        elif stmt_type == 'NextStatementNode':
            if stmt.variables:
                vars_text = ', '.join(self._serialize_variable(v) for v in stmt.variables)
                return f"next {vars_text}"
            return "next"

        elif stmt_type == 'OnGotoStatementNode':
            expr = self._serialize_expression(stmt.expression)
            lines = ','.join(str(line) for line in stmt.target_lines)
            return f"on {expr} goto {lines}"

        elif stmt_type == 'OnGosubStatementNode':
            expr = self._serialize_expression(stmt.expression)
            lines = ','.join(str(line) for line in stmt.target_lines)
            return f"on {expr} gosub {lines}"

        elif stmt_type == 'OnErrorStatementNode':
            if stmt.line_number is not None:
                return f"on error goto {stmt.line_number}"
            else:
                return "on error goto 0"

        elif stmt_type == 'ErrorStatementNode':
            error_code = self._serialize_expression(stmt.error_code)
            return f"error {error_code}"

        # For other statement types, use a generic approach
        # This is a fallback - ideally all statement types should be handled explicitly
        else:
            # Try to reconstruct from the original source if possible
            # For now, return a placeholder
            return f"rem {stmt_type}"

    def _serialize_variable(self, var):
        """Serialize a variable reference"""
        text = var.name
        if var.type_suffix:
            text += var.type_suffix
        if var.subscripts:
            subs = ','.join(self._serialize_expression(sub) for sub in var.subscripts)
            text += f"({subs})"
        return text

    def _token_to_operator(self, token_type):
        """Convert a TokenType operator to its string representation"""
        from tokens import TokenType

        operator_map = {
            TokenType.PLUS: '+',
            TokenType.MINUS: '-',
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.POWER: '^',
            TokenType.EQUAL: '=',
            TokenType.NOT_EQUAL: '<>',
            TokenType.LESS_THAN: '<',
            TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER_THAN: '>',
            TokenType.GREATER_EQUAL: '>=',
            TokenType.AND: 'and',
            TokenType.OR: 'or',
            TokenType.NOT: 'not',
            TokenType.MOD: 'mod',
            TokenType.BACKSLASH: '\\',
        }

        return operator_map.get(token_type, str(token_type))

    def _serialize_expression(self, expr):
        """Serialize an expression node to source text"""
        import ast_nodes

        expr_type = type(expr).__name__

        if expr_type == 'NumberNode':
            return str(expr.value)

        elif expr_type == 'StringNode':
            return f'"{expr.value}"'

        elif expr_type == 'VariableNode':
            return self._serialize_variable(expr)

        elif expr_type == 'BinaryOpNode':
            left = self._serialize_expression(expr.left)
            right = self._serialize_expression(expr.right)
            # Convert TokenType operator to string
            op_str = self._token_to_operator(expr.operator)
            return f"{left} {op_str} {right}"

        elif expr_type == 'UnaryOpNode':
            operand = self._serialize_expression(expr.operand)
            return f"{expr.operator}{operand}"

        elif expr_type == 'FunctionCallNode':
            # ERR and ERL are special - they're not functions and don't use ()
            if expr.name in ('ERR', 'ERL') and len(expr.arguments) == 0:
                return expr.name
            args = ','.join(self._serialize_expression(arg) for arg in expr.arguments)
            return f"{expr.name}({args})"

        else:
            return "?"

    def cmd_edit(self, args):
        """EDIT line_number - Character-by-character line editor

        EDIT 100 - Edit line 100 using edit subcommands

        Edit mode subcommands:
        - Space: Move cursor right, printing characters
        - [n]D: Delete n characters
        - I<text>$: Insert text ($ = Escape)
        - X: Extend line (go to end and insert)
        - H: Delete to end and insert
        - [n]S<ch>: Search for nth occurrence of ch
        - [n]K<ch>: Kill (delete) up to nth occurrence of ch
        - [n]C: Change next n characters
        - L: List rest of line, go to start
        - E: End and save (don't print rest)
        - Q: Quit without saving
        - A: Abort and restart
        - <CR>: End and save
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
                # Update runtime's line_table if program is running
                if self.program_runtime:
                    self.program_runtime.line_table[line_num] = line_ast

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
        except:
            # Fallback for non-TTY (piped input)
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

        AUTO - Start at 10, increment by 10
        AUTO 100 - Start at 100, increment by 10
        AUTO 100,5 - Start at 100, increment by 5
        AUTO ,5 - Start at 10, increment by 5
        """
        start = 10
        increment = 10

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
                    # Update runtime's line_table if program is running
                    if self.program_runtime:
                        self.program_runtime.line_table[current_line] = line_ast
                        if current_line not in self.program_runtime.line_order:
                            import bisect
                            bisect.insort(self.program_runtime.line_order, current_line)

                # Move to next line number
                current_line += increment

        except KeyboardInterrupt:
            # Ctrl+C exits AUTO mode
            print()
            return

    def cmd_system(self):
        """SYSTEM - Exit to operating system"""
        print("Goodbye")
        sys.exit(0)

    def cmd_files(self, filespec):
        """FILES [filespec] - Display directory listing

        FILES - List all .bas files in current directory
        FILES "*.BAS" - List files matching pattern
        FILES "A:*.*" - List files on drive A (not supported, lists current dir)
        """
        import glob
        import os

        # Default pattern if no argument
        if not filespec:
            pattern = "*.bas"
        else:
            # Remove quotes if present
            pattern = filespec.strip().strip('"').strip("'")

            # If pattern is empty after stripping, use default
            if not pattern:
                pattern = "*.bas"

        # In MBASIC, FILES shows disk directory. We'll list matching files in current directory
        # Get matching files
        try:
            files = sorted(glob.glob(pattern))

            if not files:
                print(f"No files matching: {pattern}")
                return

            # Display files (MBASIC shows them in columns)
            # Simple format: one per line with size
            for filename in files:
                try:
                    size = os.path.getsize(filename)
                    # MBASIC shows file sizes in bytes or blocks
                    # We'll show bytes
                    print(f"{filename:<20} {size:>8} bytes")
                except OSError:
                    print(f"{filename:<20}        ? bytes")

            # Show count
            print(f"\n{len(files)} File(s)")

        except Exception as e:
            print(f"?{type(e).__name__}: {e}")

    def execute_immediate(self, statement):
        """Execute a statement in immediate mode (no line number)

        Uses persistent runtime so variables persist between statements.
        If a program has been run (or stopped), use the program runtime
        so immediate mode can examine/modify program variables.
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
                    self.runtime = Runtime(ast)
                    self.runtime.setup()
                    self.interpreter = Interpreter(self.runtime)
                    # Pass reference to interactive mode for commands like LOAD/SAVE
                    self.interpreter.interactive_mode = self
                runtime = self.runtime
                interpreter = self.interpreter

            # Execute just the statement at line 0
            if ast.lines and len(ast.lines) > 0:
                line_node = ast.lines[0]
                # Update runtime's current line
                old_line = runtime.current_line
                old_index = runtime.current_stmt_index
                runtime.current_line = line_node
                runtime.current_stmt_index = 0

                # Execute each statement on line 0
                for stmt in line_node.statements:
                    interpreter.execute_statement(stmt)

                # Restore previous line/index (important for stopped programs)
                runtime.current_line = old_line
                runtime.current_stmt_index = old_index

        except Exception as e:
            # Use helper function for consistent error reporting
            print_error(e, runtime)

    def get_program_text(self):
        """Get program as text"""
        lines = []
        for line_num in sorted(self.lines.keys()):
            lines.append(self.lines[line_num])
        return '\n'.join(lines) + '\n'
