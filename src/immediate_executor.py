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

    Usage:
        executor = ImmediateExecutor(runtime, interpreter, io_handler)
        success, output = executor.execute("PRINT X")
        success, output = executor.execute("X = 100")
    """

    def __init__(self, runtime=None, interpreter=None, io_handler=None):
        """
        Initialize immediate executor.

        Args:
            runtime: Runtime instance (program runtime if available, or None)
            interpreter: Interpreter instance (program interpreter if available, or None)
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

        Args:
            statement: BASIC statement without line number (e.g., "PRINT X", "X=5")

        Returns:
            tuple: (success: bool, output: str)
                - success: True if execution succeeded, False if error
                - output: Output text or error message

        Examples:
            >>> executor.execute("PRINT 2 + 2")
            (True, " 4\\n")

            >>> executor.execute("X = 100")
            (True, "")

            >>> executor.execute("? X")
            (True, " 100\\n")

            >>> executor.execute("SYNTAX ERROR")
            (False, "Syntax error\\n")
        """
        # Special case: empty statement
        statement = statement.strip()
        if not statement:
            return (True, "")

        # Build a minimal program with line 0
        program_text = "0 " + statement

        try:
            # Parse the statement
            tokens = list(tokenize(program_text))
            parser = Parser(tokens, self.def_type_map)
            ast = parser.parse()

            # Choose runtime: use program runtime if available, otherwise create temporary
            if self.runtime is not None and self.interpreter is not None:
                runtime = self.runtime
                interpreter = self.interpreter
                using_program_runtime = True
            else:
                # Create temporary runtime/interpreter for this execution
                runtime = Runtime(ast)
                runtime.setup()
                interpreter = Interpreter(runtime, self.io)
                using_program_runtime = False

            # Capture output
            if self.io:
                self.io.clear_output()

            # Execute the statement at line 0
            if ast.lines and len(ast.lines) > 0:
                line_node = ast.lines[0]

                # Save current execution position if using program runtime
                if using_program_runtime:
                    old_line = runtime.current_line
                    old_index = runtime.current_stmt_index

                # Update runtime's current line
                runtime.current_line = line_node
                runtime.current_stmt_index = 0

                # Execute each statement on line 0
                for stmt in line_node.statements:
                    interpreter.execute_statement(stmt)

                # Restore previous position if using program runtime
                if using_program_runtime:
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
