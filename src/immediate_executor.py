"""
Immediate Mode Execution Helper

Provides immediate statement execution for visual UIs.
Allows execution of BASIC statements without line numbers in the context
of the current runtime state.
"""

from src.lexer import tokenize
from src.parser import Parser
from src.runtime import Runtime
from src.interpreter import Interpreter
import traceback
import os


class ImmediateExecutor:
    """
    Executes immediate mode statements in the context of a running program.

    This class allows visual UIs to provide an "Ok" prompt experience where
    users can execute BASIC statements without line numbers, accessing and
    modifying the current program state. It also handles numbered line editing
    for program modification.

    Features:
    - Execute immediate statements (PRINT, LET, etc.) without line numbers
    - Numbered line editing: add/modify/delete program lines (e.g., "100 PRINT X")
    - Access and modify current program state (variables, arrays)

    Safe execution: For tick-based execution (visual UIs), only execute immediate
    mode when:
    - PC is not running (program stopped) - Any reason: idle, paused, at breakpoint, done
    - OR state.error_info is not None (program encountered error)
    - OR state.input_prompt is not None (waiting for INPUT)

    DO NOT execute immediate mode while PC is running (program actively executing).

    Unsafe condition:
    - state.interpreter.runtime.pc.is_running() is True - Program is executing a statement

    Usage:
        executor = ImmediateExecutor(runtime, interpreter, io_handler)

        # Check if safe to execute
        if executor.can_execute_immediate():
            success, output = executor.execute("PRINT X")
            success, output = executor.execute("X = 100")
            success, output = executor.execute("100 PRINT X")  # Add line 100
            success, output = executor.execute("100")  # Delete line 100
    """

    def __init__(self, runtime=None, interpreter=None, io_handler=None):
        """
        Initialize immediate executor.

        Args:
            runtime: Runtime instance (typically available in TK UI, may be None)
            interpreter: Interpreter instance (typically available in TK UI, may be None)
            io_handler: IOHandler instance for capturing output
        """
        self.runtime = runtime
        self.interpreter = interpreter
        self.io = io_handler
        self.def_type_map = {}

        # Initialize default type map
        from src.parser import TypeInfo
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.def_type_map[letter] = TypeInfo.SINGLE

    def can_execute_immediate(self):
        """
        Check if immediate mode execution is safe.

        For tick-based interpreters, we check the interpreter's boolean state flags
        (halted, error_info, input_prompt) as documented in the class docstring.

        Returns:
            bool: True if safe to execute immediate mode, False otherwise
        """
        # If no interpreter, we'll create a temporary one - always safe
        if self.interpreter is None:
            return True

        # Check interpreter state flags
        if hasattr(self.interpreter, 'state') and self.interpreter.state:
            state = self.interpreter.state
            # Safe to execute immediate commands when:
            # - Program is halted (paused/done/breakpoint)
            # - OR there's an error
            # - OR waiting for input (allows inspection while paused for INPUT)
            # NOT safe when program is actively running
            return (not self.runtime.pc.is_running() or
                    state.error_info is not None or
                    state.input_prompt is not None)

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
        Execute an immediate mode statement or handle numbered line editing.

        IMPORTANT: For tick-based interpreters, this should only be called when
        can_execute_immediate() returns True. Calling while the program is actively
        running (halted=False) may corrupt the interpreter state.

        Args:
            statement: BASIC statement, which can be:
                - Immediate statement without line number (e.g., "PRINT X", "X=5")
                - Numbered line for program editing (e.g., "100 PRINT", "200")

        Returns:
            tuple: (success: bool, output: str)
                - success: True if execution succeeded, False if error
                - output: Output text or error message

        Numbered Line Editing:
            When a numbered line is entered (e.g., "100 PRINT X"), this method
            adds or updates that line in the program via UI integration:
            - Requires interpreter.interactive_mode to reference the UI object
            - UI.program must have add_line() and delete_line() methods
            - Empty line content (e.g., "100") deletes that line
            - Returns error tuple if UI integration is missing or incomplete

        Examples:
            >>> executor.execute("PRINT 2 + 2")
            (True, " 4\\n")

            >>> executor.execute("X = 100")
            (True, "")

            >>> executor.execute("? X")
            (True, " 100\\n")

            >>> executor.execute("100 PRINT X")
            (True, "")  # Adds line 100 to program

            >>> executor.execute("100")
            (True, "")  # Deletes line 100 from program

            >>> executor.execute("SYNTAX ERROR")
            (False, "Syntax error\\n")
        """
        # Check if safe to execute (for tick-based interpreters)
        if not self.can_execute_immediate():
            return (False, "Cannot execute immediate mode while program is running\n")

        # Special case: empty statement
        statement = statement.strip()
        if not statement:
            return (True, "")

        # Special case: HELP command
        if statement.upper() in ('HELP', 'HELP()', '?HELP'):
            return self._show_help()

        # Special case: Numbered line - this is a program edit, not immediate execution
        # In real MBASIC, typing a numbered line in immediate mode adds/edits that line
        #
        # This feature requires the following UI integration:
        # - interpreter.interactive_mode must reference the UI object (checked with hasattr)
        # - UI.program must have add_line() and delete_line() methods (validated, returns error tuple if missing)
        # - UI._refresh_editor() method to update the display (optional, checked with hasattr)
        # - UI._highlight_current_statement() for restoring execution highlighting (optional, checked with hasattr)
        # If interactive_mode doesn't exist or is falsy, returns (False, error_message) tuple.
        # If interactive_mode exists but required program methods are missing, returns (False, error_message) tuple.
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
                # Validate required UI integration
                if not hasattr(ui, 'program') or not ui.program:
                    return (False, "Cannot edit program lines: UI program manager not available\n")
                if line_content and not hasattr(ui.program, 'add_line'):
                    return (False, "Cannot edit program lines: add_line method not available\n")
                if not line_content and not hasattr(ui.program, 'delete_line'):
                    return (False, "Cannot edit program lines: delete_line method not available\n")

                if hasattr(ui, 'program') and ui.program:
                    if line_content:
                        # Add/update line - add_line(line_number, complete_line_text) takes two parameters
                        complete_line = f"{line_num} {line_content}"
                        success, error = ui.program.add_line(line_num, complete_line)
                        if not success:
                            return (False, f"Syntax error: {error}\n")
                    else:
                        # Delete line (numbered line with no content)
                        ui.program.delete_line(line_num)

                    # Refresh the editor display
                    if hasattr(ui, '_refresh_editor'):
                        ui._refresh_editor()

                    # Restore yellow highlight if there's a current execution position
                    if hasattr(ui.interpreter, 'state') and ui.interpreter.state:
                        state = ui.interpreter.state
                        # Check if halted (paused/breakpoint) or has error
                        if not ui.runtime.pc.is_running() or state.error_info:
                            # Get current PC directly from runtime
                            if hasattr(ui, '_highlight_current_statement') and hasattr(ui, 'runtime'):
                                pc = ui.runtime.pc
                                if not pc.halted():
                                    # Look up the statement at current PC
                                    stmt = ui.runtime.statement_table.get(pc)
                                    if stmt:
                                        char_start = getattr(stmt, 'char_start', 0)
                                        char_end = getattr(stmt, 'char_end', 0)
                                        ui._highlight_current_statement(pc.line_num, char_start, char_end)

                    return (True, "")

            return (False, "Cannot edit program lines in this mode\n")

        # Build a minimal program with line 0
        program_text = "0 " + statement

        try:
            # Parse the statement
            tokens = list(tokenize(program_text))
            parser = Parser(tokens, self.def_type_map)
            ast = parser.parse()

            # Check runtime and interpreter availability (defensive check)
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

                # Execute each statement on line 0
                for stmt in line_node.statements:
                    interpreter.execute_statement(stmt)

                # Design: We intentionally do NOT save/restore the PC before/after execution.
                # This allows statements like RUN to properly change execution position.
                # Rationale: If we saved/restored PC, RUN (which changes PC to line 0 to start
                # from the beginning) would be undone after immediate mode returns, breaking RUN.
                # Tradeoff: Control flow statements (GOTO, GOSUB) can also modify PC but are
                # not recommended in immediate mode as they may produce unexpected results
                # (see help text). This design prioritizes RUN functionality over preventing
                # potentially confusing GOTO/GOSUB behavior. Normal statements (PRINT, LET)
                # don't modify PC and work as expected.

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

  • INPUT statement will fail at runtime in immediate mode (use direct assignment instead)
  • Multi-statement lines (: separator) are fully supported
  • GOTO, GOSUB, and control flow statements are not recommended
    (they will execute but may produce unexpected results)
  • DEF FN works, but FN calls may fail without proper program context
  • Cannot execute while program is actively running (paused/input/breakpoint OK)

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
        """INPUT statement not supported in immediate mode - fails at runtime.

        User-facing behavior: INPUT statement will fail at runtime in immediate mode.
        NOT at parse time - INPUT statements parse successfully but execution fails
        when the interpreter calls this input() method during statement execution."""
        raise RuntimeError("INPUT not allowed in immediate mode")

    def write(self, text):
        """Write text without newline."""
        self.output_buffer.append(text)

    def output(self, text, end='\n'):
        """IOHandler-compatible output method."""
        self.output_buffer.append(str(text) + end)
