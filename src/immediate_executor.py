"""
Immediate Mode Execution Helper

Provides immediate statement execution for visual UIs.
Allows execution of BASIC statements without line numbers in the context
of the current runtime state.
"""

from lexer import tokenize
from parser import Parser
from runtime import Runtime
from interpreter import Interpreter
import traceback
import os


class ImmediateExecutor:
    """
    Executes immediate mode statements in the context of a running program.

    This class allows visual UIs to provide an "Ok" prompt experience where
    users can execute BASIC statements without line numbers, accessing and
    modifying the current program state.

    IMPORTANT: For tick-based execution (visual UIs), only execute immediate
    mode when the interpreter is in a safe state:
    - 'idle' - No program loaded
    - 'paused' - User hit Ctrl+Q (stop)
    - 'at_breakpoint' - Hit breakpoint
    - 'done' - Program finished
    - 'error' - Program encountered error

    DO NOT execute when status is:
    - 'running' - Program is executing (tick() is running)
    - 'waiting_for_input' - Program is waiting for INPUT (use normal input instead)

    Usage:
        executor = ImmediateExecutor(runtime, interpreter, io_handler)

        # Check if safe to execute
        if executor.can_execute_immediate():
            success, output = executor.execute("PRINT X")
            success, output = executor.execute("X = 100")
    """

    def __init__(self, runtime=None, interpreter=None, io_handler=None):
        """
        Initialize immediate executor.

        Args:
            runtime: Runtime instance (always available in TK UI)
            interpreter: Interpreter instance (always available in TK UI)
            io_handler: IOHandler instance for capturing output
        """
        self.runtime = runtime
        self.interpreter = interpreter
        self.io = io_handler
        self.def_type_map = {}

        # Initialize default type map
        from parser import TypeInfo
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.def_type_map[letter] = TypeInfo.SINGLE

    def can_execute_immediate(self):
        """
        Check if immediate mode execution is safe.

        For tick-based interpreters, we must check the interpreter state.

        Returns:
            bool: True if safe to execute immediate mode, False otherwise
        """
        # If no interpreter, we'll create a temporary one - always safe
        if self.interpreter is None:
            return True

        # Check interpreter state
        if hasattr(self.interpreter, 'state'):
            status = self.interpreter.state.status
            # Safe states: idle, paused, at_breakpoint, done, error
            safe_states = {'idle', 'paused', 'at_breakpoint', 'done', 'error'}
            return status in safe_states

        # No state attribute - assume safe (non-tick-based)
        return True

    def set_context(self, runtime, interpreter):
        """
        Update the execution context.

        Call this when a program starts/stops to update the runtime context
        that immediate mode will use.

        Args:
            runtime: Runtime instance (or None for clean state)
            interpreter: Interpreter instance (or None)
        """
        self.runtime = runtime
        self.interpreter = interpreter

    def execute(self, statement):
        """
        Execute an immediate mode statement.

        IMPORTANT: For tick-based interpreters, this should only be called when
        can_execute_immediate() returns True. Calling during 'running' state
        may corrupt the interpreter state.

        Args:
            statement: BASIC statement without line number (e.g., "PRINT X", "X=5")

        Returns:
            tuple: (success: bool, output: str)
                - success: True if execution succeeded, False if error
                - output: Output text or error message

        Examples:
            >>> if executor.can_execute_immediate():
            ...     success, output = executor.execute("PRINT 2 + 2")
            (True, " 4\\n")

            >>> executor.execute("X = 100")
            (True, "")

            >>> executor.execute("? X")
            (True, " 100\\n")

            >>> executor.execute("SYNTAX ERROR")
            (False, "Syntax error\\n")
        """
        # Check if safe to execute (for tick-based interpreters)
        if not self.can_execute_immediate():
            status = self.interpreter.state.status if hasattr(self.interpreter, 'state') else 'unknown'
            return (False, f"Cannot execute immediate mode while program is {status}\n")

        # Special case: empty statement
        statement = statement.strip()
        if not statement:
            return (True, "")

        # Special case: HELP command
        if statement.upper() in ('HELP', 'HELP()', '?HELP'):
            return self._show_help()

        # Special case: Numbered line - this is a program edit, not immediate execution
        # In real MBASIC, typing a numbered line in immediate mode adds/edits that line
        import re
        line_match = re.match(r'^(\d+)\s*(.*)$', statement)
        if line_match:
            line_num = int(line_match.group(1))
            line_content = line_match.group(2).strip()

            # Add or update the line in the program
            # This should update the UI's program manager
            if hasattr(self.interpreter, 'interactive_mode') and self.interpreter.interactive_mode:
                # Call the UI's method to add/edit a line
                ui = self.interpreter.interactive_mode
                if hasattr(ui, 'program') and ui.program:
                    if line_content:
                        # Add/update line
                        ui.program.add_or_update_line(line_num, line_content)
                    else:
                        # Delete line (numbered line with no content)
                        ui.program.delete_line(line_num)

                    # Refresh the editor display
                    if hasattr(ui, '_refresh_editor'):
                        ui._refresh_editor()

                    return (True, "")

            return (False, "Cannot edit program lines in this mode\n")

        # Build a minimal program with line 0
        program_text = "0 " + statement

        try:
            # Parse the statement
            tokens = list(tokenize(program_text))
            parser = Parser(tokens, self.def_type_map)
            ast = parser.parse()

            # Use the runtime and interpreter (always available in TK UI)
            if self.runtime is None or self.interpreter is None:
                return (False, "Runtime not initialized\n")

            runtime = self.runtime
            interpreter = self.interpreter

            # Capture output
            if self.io:
                self.io.clear_output()

            # Execute the statement at line 0
            if ast.lines and len(ast.lines) > 0:
                line_node = ast.lines[0]

                # Save current execution position
                old_line = runtime.current_line
                old_index = runtime.current_stmt_index

                # Update runtime's current line
                runtime.current_line = line_node
                runtime.current_stmt_index = 0

                # Execute each statement on line 0
                for stmt in line_node.statements:
                    interpreter.execute_statement(stmt)

                # Restore previous position
                runtime.current_line = old_line
                runtime.current_stmt_index = old_index

            # Get captured output
            output = self.io.get_output() if self.io else ""

            return (True, output)

        except Exception as e:
            # Format error message
            error_msg = self._format_error(e, statement)
            return (False, error_msg)

    def _format_error(self, exception, statement):
        """
        Format an error message for user display.

        Args:
            exception: The exception that occurred
            statement: The statement that caused the error

        Returns:
            str: Formatted error message
        """
        # Check if DEBUG mode is enabled
        if os.environ.get('DEBUG'):
            # Return full traceback in debug mode
            return f"?{type(exception).__name__}: {exception}\n{traceback.format_exc()}"
        else:
            # Normal mode - just error type and message
            error_name = type(exception).__name__

            # Common error name simplifications
            if error_name == "RuntimeError":
                # Extract BASIC error names if present
                error_str = str(exception)
                if "Type mismatch" in error_str:
                    return "Type mismatch\n"
                elif "Overflow" in error_str:
                    return "Overflow\n"
                elif "Division by zero" in error_str:
                    return "Division by zero\n"
                elif "Illegal function call" in error_str:
                    return "Illegal function call\n"
                elif "Subscript out of range" in error_str:
                    return "Subscript out of range\n"
                elif "Undefined" in error_str:
                    return f"{error_str}\n"
                else:
                    return f"{error_str}\n"
            elif error_name == "SyntaxError":
                return "Syntax error\n"
            elif error_name == "KeyError":
                # Variable not defined
                return f"Undefined variable\n"
            else:
                return f"?{error_name}: {exception}\n"

    def _show_help(self):
        """
        Show help for immediate mode commands.

        Returns:
            tuple: (True, help_text)
        """
        help_text = """
═══════════════════════════════════════════════════════════════════
                    IMMEDIATE MODE HELP
═══════════════════════════════════════════════════════════════════

Immediate mode allows you to execute BASIC statements directly without
line numbers. You can interact with program variables and test code.

AVAILABLE COMMANDS:
───────────────────────────────────────────────────────────────────

  PRINT <expr>     Print value of expression
  ? <expr>         Shorthand for PRINT
  <var> = <expr>   Assign value to variable
  LET <var>=<expr> Explicit assignment

EXAMPLES:
───────────────────────────────────────────────────────────────────

  PRINT 2 + 2              → Prints: 4
  ? "Hello"                → Prints: Hello
  X = 100                  → Sets X to 100
  PRINT X                  → Prints: 100
  Y$ = "BASIC"             → Sets Y$ to "BASIC"
  ? SQR(16)                → Prints: 4
  ? INT(3.7)               → Prints: 3

ACCESSING PROGRAM VARIABLES:
───────────────────────────────────────────────────────────────────

When a program is loaded or running, you can inspect and modify its
variables in immediate mode:

  PRINT SCORE              → View program variable
  LIVES = 3                → Modify program variable
  ? PLAYER$                → Check string variable

LIMITATIONS:
───────────────────────────────────────────────────────────────────

  • Cannot use multi-statement lines (no : separator)
  • Cannot use GOTO, GOSUB, or control flow statements
  • Cannot define or call functions (DEF FN)
  • Cannot execute during INPUT or program running state

SPECIAL COMMANDS:
───────────────────────────────────────────────────────────────────

  HELP                     Show this help message

═══════════════════════════════════════════════════════════════════

Press Ctrl+H (UI help) for keyboard shortcuts and UI features.

═══════════════════════════════════════════════════════════════════
"""
        return (True, help_text)


class OutputCapturingIOHandler:
    """
    Simple IOHandler that captures output to a string buffer.

    Used by visual UIs to capture immediate mode output.
    """

    def __init__(self):
        self.output_buffer = []

    def clear_output(self):
        """Clear the output buffer."""
        self.output_buffer = []

    def get_output(self):
        """Get accumulated output as string."""
        return ''.join(self.output_buffer)

    def print(self, text):
        """Capture printed text."""
        self.output_buffer.append(str(text))

    def print_line(self, text=""):
        """Capture printed line."""
        self.output_buffer.append(str(text) + "\n")

    def input(self, prompt=""):
        """Input not supported in immediate mode."""
        raise RuntimeError("INPUT not allowed in immediate mode")

    def write(self, text):
        """Write text without newline."""
        self.output_buffer.append(text)

    def output(self, text, end='\n'):
        """IOHandler-compatible output method."""
        self.output_buffer.append(str(text) + end)
