"""
MBASIC 5.21 Interpreter

Executes BASIC programs from AST.
"""

import sys
import signal
from dataclasses import dataclass, field
from typing import Literal, Optional, Callable, Any, Union
from src.runtime import Runtime
from src.basic_builtins import BuiltinFunctions, TabMarker, SpcMarker, UsingFormatter
from src.tokens import TokenType
from src.pc import PC
import src.ast_nodes as ast_nodes


class BreakException(Exception):
    """Raised when user presses Ctrl+C to break execution"""
    pass


class ChainException(Exception):
    """Raised by CHAIN to signal program change - caught by run() to restart execution"""
    pass


@dataclass
class ErrorInfo:
    """Information about a runtime error"""
    error_code: int
    pc: PC
    error_message: str


@dataclass
class InterpreterState:
    """Complete execution state of the interpreter at any point in time

    Primary execution states (check these to determine current status):

    For UI/callers checking completed state (recommended order):
    - error_info: Non-None if an error occurred (highest priority for display)
    - input_prompt: Non-None if waiting for input (set during statement execution)
    - runtime.pc.is_running(): False if stopped (paused/done/at breakpoint)

    Internal execution order in tick_pc() (for developers understanding control flow):
    1. pause_requested check - pauses if pause() was called
    2. is_running() check - stops if PC is not running
    3. break_requested check - handles Ctrl+C breaks
    4. breakpoints check - pauses at breakpoints
    5. trace output - displays [line] or [line.stmt] if TRON is active
    6. statement execution (with error handling in try/except) - sets input_prompt or error_info
    7. input_prompt check - pauses if waiting for input
    8. PC advancement - moves to next statement or jumps to branch target

    Also tracks: input buffering, debugging flags, performance metrics, and
    provides computed properties for current line/statement position.
    """

    # Input handling (THE CRITICAL STATE - blocks execution)
    input_prompt: Optional[str] = None
    input_variables: list = field(default_factory=list)  # Variables waiting for input
    input_buffer: list = field(default_factory=list)  # Buffered input values
    input_file_number: Optional[int] = None  # If reading from file

    # Debugging (breakpoints are stored in Runtime, not here)
    skip_next_breakpoint_check: bool = False  # Set to True DURING halting at a breakpoint (in tick_pc method),
                                               # within the breakpoint check itself. On next execution, if still True,
                                               # allows stepping past the breakpoint once, then is cleared to False.
                                               # Prevents re-halting on same breakpoint.
    pause_requested: bool = False  # Set by pause() method

    # Error handling
    error_info: Optional[ErrorInfo] = None

    # Performance tracking
    statements_executed: int = 0
    execution_time_ms: float = 0.0

    # First line flag (for CONT support)
    is_first_line: bool = True

    # Reference to interpreter (for computing derived properties)
    _interpreter: Optional['Interpreter'] = field(default=None, repr=False)

    @property
    def current_line(self) -> Optional[int]:
        """Get current line from runtime.pc (computed property, not cached)"""
        if self._interpreter:
            pc = self._interpreter.runtime.pc
            return pc.line_num if pc and pc.is_running() else None
        return None

    @property
    def current_statement_char_start(self) -> int:
        """Get current statement char_start from statement table (computed property)"""
        if self._interpreter:
            pc = self._interpreter.runtime.pc
            if pc and pc.is_running():
                stmt = self._interpreter.runtime.statement_table.get(pc)
                if stmt:
                    return getattr(stmt, 'char_start', 0)
        return 0

    @property
    def current_statement_char_end(self) -> int:
        """Get current statement char_end from statement table (computed property)

        Handles three cases:
        1. Next statement exists: Returns max(char_end, next_char_start - 1) to account
           for string token inaccuracies where char_end may be shorter than expected.
        2. Last statement on line with line_text available: Returns len(line_text) to
           include trailing spaces/comments not captured in char_end.
        3. Last statement without line_text: Returns stmt.char_end as fallback.
        """
        if self._interpreter:
            pc = self._interpreter.runtime.pc
            if pc and pc.is_running():
                stmt = self._interpreter.runtime.statement_table.get(pc)
                if stmt:
                    stmt_char_end = getattr(stmt, 'char_end', 0)

                    # Check if there's a next statement on same line
                    next_pc = PC.running_at(pc.line_num, pc.stmt_offset + 1)
                    next_stmt = self._interpreter.runtime.statement_table.get(next_pc)
                    if next_stmt and next_stmt.char_start > 0:
                        # Use max of char_end and (next_start - 1)
                        # This handles both correct char_end and incorrect string token char_end
                        return max(stmt_char_end, next_stmt.char_start - 1)
                    else:
                        # No next statement - use line length if we have line text, otherwise char_end
                        if pc.line_num in self._interpreter.runtime.line_text_map:
                            line_text = self._interpreter.runtime.line_text_map[pc.line_num]
                            # Return length of line (end of line)
                            return len(line_text)
                        else:
                            return stmt_char_end
        return 0

class Interpreter:
    """Execute MBASIC AST with tick-based execution for UI integration"""

    def __init__(self, runtime, io_handler=None, breakpoint_callback=None, filesystem_provider=None, limits=None, settings_manager=None, file_io=None):
        self.runtime = runtime
        self.builtins = BuiltinFunctions(runtime)

        # I/O handler (defaults to console if not provided)
        if io_handler is None:
            from src.iohandler.console import ConsoleIOHandler
            io_handler = ConsoleIOHandler(debug_enabled=False)
        self.io = io_handler

        # Filesystem provider (defaults to real filesystem if not provided)
        if filesystem_provider is None:
            from src.filesystem import RealFileSystemProvider
            filesystem_provider = RealFileSystemProvider()
        self.fs = filesystem_provider

        # File I/O module (defaults to real filesystem if not provided)
        # Web UI passes SandboxedFileIO for browser localStorage
        # Local UIs pass None to use RealFileIO
        if file_io is None:
            from src.file_io import RealFileIO
            file_io = RealFileIO()
        self.file_io = file_io

        # Resource limits (defaults to local limits if not provided)
        if limits is None:
            from src.resource_limits import create_local_limits
            limits = create_local_limits()
        self.limits = limits

        # Settings manager (defaults to global settings if not provided)
        if settings_manager is None:
            from src.settings import get_settings_manager
            settings_manager = get_settings_manager()
        self.settings_manager = settings_manager

        # Breakpoint callback - called when a breakpoint is hit
        # Callback should take (line_number, statement_index) and return True to continue, False to stop
        self.breakpoint_callback = breakpoint_callback

        # Execution state for tick-based execution
        self.state = InterpreterState(_interpreter=self)

    @staticmethod
    def _make_token_info(node):
        """Create a token info object from an AST node for variable tracking.

        Args:
            node: AST node with line_num and column attributes

        Returns:
            Object with line and position attributes, or None if node is None
        """
        if node is None:
            return None

        class TokenInfo:
            def __init__(self, line, position):
                self.line = line
                self.position = position

        return TokenInfo(
            getattr(node, 'line_num', 0),
            getattr(node, 'column', 0)
        )

    def _setup_break_handler(self):
        """Setup Ctrl+C handler to set break flag"""
        def signal_handler(_sig, _frame):
            self.runtime.break_requested = True

        # Save old handler to restore later
        self.old_signal_handler = signal.signal(signal.SIGINT, signal_handler)

    def _restore_break_handler(self):
        """Restore original Ctrl+C handler"""
        if hasattr(self, 'old_signal_handler'):
            signal.signal(signal.SIGINT, self.old_signal_handler)

    # ========================================================================
    # New Tick-Based Execution API
    # ========================================================================

    def start(self):
        """Initialize program for execution.

        Sets up the runtime environment and prepares for tick-based execution.

        Returns:
            InterpreterState: Initial state (typically 'idle' or 'error' if setup fails)
        """
        try:
            # Setup runtime tables
            self.runtime.setup()

            # Initialize state
            self.state = InterpreterState(_interpreter=self)
            # PC is already set to running state by setup(), no need to set halted flag
            self.state.is_first_line = True

            # Setup Ctrl+C handler
            self._setup_break_handler()

            return self.state

        except Exception as e:
            # Setup failed - set PC to halted state
            self.runtime.pc = PC.halted()
            self.state.error_info = ErrorInfo(
                error_code=5,  # Illegal function call (generic error)
                pc=PC.halted(),  # No valid PC during setup
                error_message=str(e)
            )
            return self.state

    def has_work(self):
        """Check if interpreter has work to do (should execution continue?).

        Returns:
            bool: True if there is work to do, False if stopped
        """
        return self.runtime.pc.is_running()

    def tick(self, mode='run', max_statements=100):
        """Execute a quantum of work and return updated state.

        Args:
            mode: Execution mode:
                - 'run': Execute up to max_statements
                - 'step_line': Execute next line, then pause
                - 'step_statement': Execute next statement, then pause
            max_statements: Maximum statements to execute before yielding (for 'run' mode)

        Returns:
            InterpreterState: Updated state after execution quantum
        """
        # Use new PC-based execution
        return self.tick_pc(mode, max_statements)

    def tick_pc(self, mode='run', max_statements=100):
        """Execute a quantum of work using PC-based execution (NEW).

        This is the new PC-based execution loop that replaces the old
        line_index/line_table iteration with direct PC navigation.

        Args:
            mode: Execution mode:
                - 'run': Execute up to max_statements
                - 'step_line': Execute next line, then pause
                - 'step_statement': Execute next statement, then pause
            max_statements: Maximum statements to execute before yielding (for 'run' mode)

        Returns:
            InterpreterState: Updated state after execution quantum
        """
        import time
        start_time = time.time()
        statements_in_tick = 0
        last_traced_line = None

        try:
            while statements_in_tick < max_statements:
                # Check for pause request
                if self.state.pause_requested:
                    self.runtime.pc = self.runtime.pc.stop("USER")
                    self.state.pause_requested = False
                    return self.state

                # Get current PC
                pc = self.runtime.pc

                import sys
                if mode in ('step_statement', 'step_line'):
                    print(f"DEBUG tick: Starting tick() with PC={pc}, is_running={pc.is_running()}, stop_reason={pc.stop_reason}", file=sys.stderr)

                # Check if not running (stopped/halted/error)
                # Allow execution to continue in step mode even if stopped at BREAK/USER
                if not pc.is_running() and not (mode in ('step_statement', 'step_line') and pc.stop_reason in ('BREAK', 'USER')):
                    # Already stopped - PC has stop_reason set
                    self._restore_break_handler()
                    return self.state

                # In step mode from breakpoint: clear stop_reason without messing with flags
                if mode in ('step_statement', 'step_line') and not pc.is_running():
                    print(f"DEBUG tick: Step from stopped PC {pc}, resuming", file=sys.stderr)
                    # Just clear the stop_reason to allow execution, don't touch flags
                    pc = pc.resume()
                    self.runtime.pc = pc
                    print(f"DEBUG tick: After resume, PC={pc}", file=sys.stderr)

                # Check for Ctrl+C break
                if self.runtime.break_requested:
                    self.runtime.break_requested = False
                    self.runtime.pc = pc.stop("BREAK")
                    self.io.output("")
                    self.io.output(f"Break in {pc}")
                    # PC keeps current position for resume via CONT
                    return self.state

                # Check for breakpoint (supports both line-level and statement-level)
                # Check exact PC first (statement-level), then line-level
                at_breakpoint = False
                if mode == 'run':
                    if pc in self.runtime.breakpoints:
                        # Exact PC match (statement-level breakpoint)
                        at_breakpoint = True
                    else:
                        # Check if any breakpoint is set at this line (line-level match)
                        for bp in self.runtime.breakpoints:
                            if bp.line == pc.line_num:
                                at_breakpoint = True
                                break

                if at_breakpoint:
                    if not self.state.skip_next_breakpoint_check:
                        self.runtime.pc = pc.stop("BREAK")
                        self.state.skip_next_breakpoint_check = True
                        return self.state
                    else:
                        self.state.skip_next_breakpoint_check = False

                # Trace output
                if self.runtime.trace_on:
                    if self.runtime.trace_detail == 'statement':
                        # Statement-level trace: show [10.0], [10.1], [10.2]
                        self.io.output(f"[{pc}]")
                    elif pc.line_num != last_traced_line:
                        # Line-level trace: show [10] only once per line
                        self.io.output(f"[{pc.line_num}]")
                        last_traced_line = pc.line_num

                # Get statement
                stmt = self.runtime.statement_table.get(pc)
                if stmt is None:
                    raise RuntimeError(f"Invalid PC: {pc}")

                # Execute statement
                try:
                    import sys
                    if mode in ('step_statement', 'step_line'):
                        print(f"DEBUG tick: Executing statement at {pc}: {type(stmt).__name__}", file=sys.stderr)
                    self.execute_statement(stmt)
                    statements_in_tick += 1
                    self.state.statements_executed += 1

                except BreakException:
                    # User pressed Ctrl+C during INPUT
                    self.runtime.pc = pc.stop("BREAK")
                    self.io.output(f"Break in {pc}")
                    return self.state

                except Exception as e:
                    # Check if we're already in an error handler (prevent recursive errors)
                    already_in_error_handler = (self.state.error_info is not None)

                    # Set ErrorInfo for both handler and no-handler cases (needed by RESUME)
                    error_code = self._map_exception_to_error_code(e)
                    self.state.error_info = ErrorInfo(
                        error_code=error_code,
                        pc=pc,
                        error_message=str(e)
                    )

                    # Check if we have an error handler and not already handling an error
                    if self.runtime.has_error_handler() and not already_in_error_handler:
                        self._invoke_error_handler(error_code, pc)
                        # Error handler set npc - apply it and continue execution
                        # (don't use continue here - we need to let normal flow handle NPC)
                        statements_in_tick += 1
                        self.state.statements_executed += 1
                        # Fall through to NPC handling below
                    else:
                        # No error handler (or recursive error) - set PC to error state and raise
                        self.runtime.pc = pc.with_error(
                            error_code,
                            str(e),
                            self.runtime.on_error_goto if self.runtime.has_error_handler() else None
                        )
                        self._restore_break_handler()
                        raise

                # Check if we're waiting for input
                if self.state.input_prompt is not None:
                    return self.state

                # Advance PC: if NPC was set by statement (GOTO/GOSUB/RETURN/etc.), use it;
                # otherwise advance to next sequential statement
                if self.runtime.npc is not None:
                    next_pc = self.runtime.npc
                    self.runtime.npc = None
                    import sys
                    if mode in ('step_statement', 'step_line'):
                        print(f"DEBUG tick: NPC was set to {next_pc}", file=sys.stderr)
                else:
                    next_pc = self.runtime.statement_table.next_pc(pc)
                    import sys
                    if mode in ('step_statement', 'step_line'):
                        print(f"DEBUG tick: next_pc from statement_table: {next_pc}", file=sys.stderr)

                # Check for step mode before updating PC
                if mode == 'step_statement':
                    # Stop at next PC for stepping
                    import sys
                    print(f"DEBUG tick: Step mode, stopping at next_pc={next_pc}, is_running={next_pc.is_running()}", file=sys.stderr)
                    self.runtime.pc = next_pc.stop("BREAK") if next_pc.is_running() else next_pc
                    print(f"DEBUG tick: Final PC set to {self.runtime.pc}", file=sys.stderr)
                    return self.state
                elif mode == 'step_line' and pc.is_step_point(next_pc, 'step_line'):
                    # Stop at next line for stepping
                    self.runtime.pc = next_pc.stop("BREAK") if next_pc.is_running() else next_pc
                    return self.state

                # Update PC for next iteration (unless already stopped by END/STOP)
                if self.runtime.pc.is_running():
                    self.runtime.pc = next_pc

                # Yield control periodically
                if mode == 'run' and statements_in_tick >= max_statements:
                    return self.state

        except Exception as e:
            # Unhandled error
            if self.state.error_info is None:
                pc = self.runtime.pc
                self.runtime.pc = pc.with_error(5, str(e)) if pc.is_running() else PC.error_at(None, 0, 5, str(e))
                self.state.error_info = ErrorInfo(
                    error_code=5,
                    pc=self.runtime.pc,
                    error_message=str(e)
                )
            raise
        finally:
            # Update execution time
            elapsed = (time.time() - start_time) * 1000
            self.state.execution_time_ms += elapsed

        return self.state

    def provide_input(self, value: str):
        """Provide input when state.input_prompt is set.

        Args:
            value: User input string (will be parsed based on variable type)

        Returns:
            InterpreterState: Updated state
        """
        if self.state.input_prompt is None:
            raise RuntimeError("Not waiting for input")

        # Add value to input buffer
        self.state.input_buffer.append(value)

        # Clear input prompt - execution will resume automatically
        self.state.input_prompt = None

        return self.state

    def pause(self):
        """Request pause of execution.

        This can be called asynchronously (e.g., from UI thread).

        Returns:
            InterpreterState: Current state
        """
        self.state.pause_requested = True
        return self.state

    def continue_execution(self):
        """Continue from stopped state (resume execution).

        Returns:
            InterpreterState: Updated state
        """
        if self.runtime.pc.is_running():
            raise RuntimeError("Not stopped")

        # Resume from current PC position
        self.runtime.pc = self.runtime.pc.resume()
        return self.state

    def reset(self):
        """Reset program to initial state.

        Returns:
            InterpreterState: Reset state
        """
        self.state = InterpreterState(_interpreter=self)
        return self.state

    def get_state(self):
        """Get current state without executing.

        Returns:
            InterpreterState: Current state
        """
        return self.state

    def set_breakpoint(self, line_or_pc: Union[int, PC], stmt_offset: int = None):
        """Add a breakpoint at the specified line or statement.

        Args:
            line_or_pc: Line number (int) or PC object for breakpoint
            stmt_offset: Optional statement offset (0-based). If None, breaks on entire line.
                        Ignored if line_or_pc is a PC object.

        Examples:
            set_breakpoint(100)           # Line-level
            set_breakpoint(100, 2)        # Statement-level (line 100, 3rd statement)
            set_breakpoint(PC(100, 2))    # PC object (preferred)
        """
        # Delegate to runtime
        self.runtime.set_breakpoint(line_or_pc, stmt_offset)

    def clear_breakpoint(self, line_or_pc: Union[int, PC], stmt_offset: int = None):
        """Remove a breakpoint at the specified line or statement.

        Args:
            line_or_pc: Line number (int) or PC object for breakpoint
            stmt_offset: Optional statement offset. If None, removes line-level breakpoint.
                        Ignored if line_or_pc is a PC object.

        Examples:
            clear_breakpoint(100)           # Line-level
            clear_breakpoint(100, 2)        # Statement-level
            clear_breakpoint(PC(100, 2))    # PC object (preferred)
        """
        # Delegate to runtime
        self.runtime.clear_breakpoint(line_or_pc, stmt_offset)

    # ========================================================================
    # Legacy Execution Methods (kept for backward compatibility)
    # ========================================================================

    def run(self):
        """Execute the program from start to finish (CLI-compatible wrapper).

        This wraps the new tick-based API with synchronous input handling
        for backward compatibility with CLI usage.

        Catches ChainException to restart execution with new program after CHAIN.
        """
        # Outer loop to handle CHAIN - restart execution when ChainException is raised
        while True:
            try:
                # Start execution
                state = self.start()

                if state.error_info:
                    raise RuntimeError(state.error_info.error_message)

                # Run until done
                while self.runtime.pc.is_running() and not state.error_info:
                    state = self.tick(mode='run', max_statements=10000)

                    # Handle input synchronously for CLI
                    if state.input_prompt:
                        # Synchronous input for CLI
                        try:
                            value = input()  # Use built-in input() for CLI
                            state = self.provide_input(value)
                        except KeyboardInterrupt:
                            # User pressed Ctrl+C during input
                            self.io.output(f"Break in {state.current_line or '?'}")
                            return
                        except EOFError:
                            self.io.output("")
                            return

                # Handle final errors
                if state.error_info:
                    raise RuntimeError(state.error_info.error_message)

                # Normal completion - exit the outer loop
                break

            except ChainException:
                # CHAIN was called - restart execution with new program
                # The runtime has already been reset by cmd_chain()
                continue


    # OLD EXECUTION METHODS REMOVED (version 1.0.299)
    # Note: The project has an internal implementation version (tracked in src/version.py)
    # which is separate from the MBASIC 5.21 language version being implemented.
    # Removed from Interpreter class:
    #   - Methods: run_from_current(), _run_loop(), step_once() (v1.0.299)
    #   - Fields: current_line, next_line for tracking execution position (v1.0.299)
    # These have been replaced by PC-based execution with tick_pc() method
    # The CONT command now uses tick() directly with PC positioning

    def _map_exception_to_error_code(self, exception):
        """Map Python exception to MBASIC error code"""
        error_msg = str(exception).lower()

        # Division by zero
        if isinstance(exception, ZeroDivisionError) or "division by zero" in error_msg:
            return 11  # Division by zero

        # Type mismatch
        if isinstance(exception, (TypeError, ValueError)):
            # Check for specific type mismatch messages
            if "type mismatch" in error_msg or "invalid literal" in error_msg:
                return 13  # Type mismatch
            return 5  # Illegal function call

        # Out of range
        if isinstance(exception, IndexError) or "subscript out of range" in error_msg:
            return 9  # Subscript out of range

        # Key errors (undefined variable/function)
        if isinstance(exception, KeyError) or "undefined" in error_msg:
            if "function" in error_msg:
                return 18  # Undefined user function
            return 8  # Undefined line number

        # Out of data
        if "out of data" in error_msg:
            return 4  # Out of DATA

        # NEXT without FOR
        if "next without for" in error_msg:
            return 1  # NEXT without FOR

        # RETURN without GOSUB
        if "return without gosub" in error_msg:
            return 3  # RETURN without GOSUB

        # Overflow
        if isinstance(exception, OverflowError):
            return 6  # Overflow

        # Default to illegal function call
        return 5  # Illegal function call

    def _invoke_error_handler(self, error_code, error_pc):
        """Invoke the error handler"""
        # Note: error_info is always set in the exception handler in tick_pc() when an error
        # occurs (line 385), regardless of whether an error handler exists. This method is
        # only called if a handler exists (checked at line 392), so we're now ready to invoke it.

        # Set ERR%, ERL%, and ERS% system variables
        self.runtime.set_variable_raw('err%', error_code)
        self.runtime.set_variable_raw('erl%', error_pc.line_num)
        self.runtime.set_variable_raw('ers%', error_pc.stmt_offset)

        # Jump to error handler
        if self.runtime.error_handler_is_gosub:
            # ON ERROR GOSUB - push return address (next statement after error)
            next_pc = self.runtime.statement_table.next_pc(error_pc)
            if next_pc.is_running():
                self.runtime.push_gosub(next_pc.line_num, next_pc.stmt_offset)

        # Jump to error handler line
        self.runtime.npc = PC.from_line(self.runtime.error_handler)

    def find_matching_wend(self, start_line, start_stmt):
        """Find the matching WEND for a WHILE statement

        Args:
            start_line: Line number where WHILE is located
            start_stmt: Statement index where WHILE is located

        Returns:
            (line_number, stmt_index) of matching WEND, or None if not found
        """
        # Start searching from the statement after the WHILE
        depth = 1  # Track nesting depth

        # Get all line numbers from statement_table
        line_numbers = sorted(set(pc.line_num for pc in self.runtime.statement_table.statements.keys()))
        try:
            line_idx = line_numbers.index(start_line)
        except ValueError:
            return None

        # Start from the next statement in the same line
        stmt_idx = start_stmt + 1

        while line_idx < len(line_numbers):
            line_num = line_numbers[line_idx]
            line_statements = self.runtime.statement_table.get_line_statements(line_num)

            # Search through statements in this line
            while stmt_idx < len(line_statements):
                stmt = line_statements[stmt_idx]

                if isinstance(stmt, ast_nodes.WhileStatementNode):
                    depth += 1
                elif isinstance(stmt, ast_nodes.WendStatementNode):
                    depth -= 1
                    if depth == 0:
                        # Found matching WEND
                        return (line_num, stmt_idx)

                stmt_idx += 1

            # Move to next line
            line_idx += 1
            stmt_idx = 0  # Start from first statement in next line

        return None

    def execute_statement(self, stmt):
        """Execute a single statement"""
        # Get statement type name
        stmt_type = type(stmt).__name__

        # Dispatch to appropriate handler
        handler_name = f"execute_{stmt_type.replace('Node', '').replace('Statement', '').lower()}"
        handler = getattr(self, handler_name, None)

        if handler:
            handler(stmt)
        else:
            raise NotImplementedError(f"Statement not implemented: {stmt_type}")

    # ========================================================================
    # Statement Execution
    # ========================================================================

    def execute_let(self, stmt):
        """Execute LET (assignment) statement.

        Handles both simple variables and array element assignment:
        - LET X = 5 (simple variable)
        - LET A(I) = 10 (array element)
        - X = 5 (implicit LET, no keyword)

        Type coercion is performed based on the variable's type suffix:
        - % (integer): truncates to integer
        - $ (string): converts to string
        - !, # or no suffix (float): ensures numeric type
        """
        value = self.evaluate_expression(stmt.expression)

        # Type coercion based on type suffix
        if stmt.variable.type_suffix == '%':
            # Integer - truncate towards zero
            value = int(value)
        elif stmt.variable.type_suffix == '$':
            # String
            value = str(value)
        elif stmt.variable.type_suffix in ('!', '#', None):
            # Single or double precision float (or no suffix) - ensure it's numeric
            if not isinstance(value, (int, float)):
                value = float(value) if value else 0

        if stmt.variable.subscripts:
            # Array assignment
            subscripts = [int(self.evaluate_expression(sub)) for sub in stmt.variable.subscripts]
            self.runtime.set_array_element(
                stmt.variable.name,
                stmt.variable.type_suffix,
                subscripts,
                value,
                token=self._make_token_info(stmt.variable)
            )
        else:
            # Simple variable assignment
            self.runtime.set_variable(
                stmt.variable.name,
                stmt.variable.type_suffix,
                value,
                token=self._make_token_info(stmt.variable),
                limits=self.limits,
                original_case=getattr(stmt.variable, 'original_case', stmt.variable.name),
                settings_manager=self.settings_manager
            )

    def execute_swap(self, stmt):
        """Execute SWAP statement - exchange values of two variables"""
        # Get values of both variables
        if stmt.var1.subscripts:
            # Array element
            subscripts1 = [int(self.evaluate_expression(sub)) for sub in stmt.var1.subscripts]
            value1 = self.runtime.get_array_element(stmt.var1.name, stmt.var1.type_suffix, subscripts1, token=self._make_token_info(stmt.var1))
        else:
            # Simple variable
            value1 = self.runtime.get_variable(stmt.var1.name, stmt.var1.type_suffix, token=self._make_token_info(stmt.var1))

        if stmt.var2.subscripts:
            # Array element
            subscripts2 = [int(self.evaluate_expression(sub)) for sub in stmt.var2.subscripts]
            value2 = self.runtime.get_array_element(stmt.var2.name, stmt.var2.type_suffix, subscripts2, token=self._make_token_info(stmt.var2))
        else:
            # Simple variable
            value2 = self.runtime.get_variable(stmt.var2.name, stmt.var2.type_suffix, token=self._make_token_info(stmt.var2))

        # Swap the values
        if stmt.var1.subscripts:
            self.runtime.set_array_element(
                stmt.var1.name,
                stmt.var1.type_suffix,
                subscripts1,
                value2,
                token=self._make_token_info(stmt.var1)
            )
        else:
            self.runtime.set_variable(
                stmt.var1.name,
                stmt.var1.type_suffix,
                value2,
                token=self._make_token_info(stmt.var1),
                limits=self.limits
            )

        if stmt.var2.subscripts:
            self.runtime.set_array_element(
                stmt.var2.name,
                stmt.var2.type_suffix,
                subscripts2,
                value1,
                token=self._make_token_info(stmt.var2)
            )
        else:
            self.runtime.set_variable(
                stmt.var2.name,
                stmt.var2.type_suffix,
                value1,
                token=self._make_token_info(stmt.var2),
                limits=self.limits
            )

    def execute_print(self, stmt):
        """Execute PRINT statement - print to screen or file"""
        # Check if printing to file
        if stmt.file_number is not None:
            file_num = int(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise RuntimeError(f"File #{file_num} not open")
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_handle = None

        output_parts = []

        for i, expr in enumerate(stmt.expressions):
            value = self.evaluate_expression(expr)

            # Check for special TAB/SPC markers
            if isinstance(value, TabMarker) or isinstance(value, SpcMarker):
                # Keep marker object for later processing
                output_parts.append(value)
            # Convert to string
            elif isinstance(value, float):
                # Format numbers like BASIC does
                if value == int(value):
                    s = str(int(value))
                else:
                    s = str(value)
                # Add space for positive numbers
                if value >= 0:
                    s = " " + s
                s = s + " "
                output_parts.append(s)
            else:
                s = str(value)
                output_parts.append(s)

        # Handle separators and build output
        output = ""
        for i, part in enumerate(output_parts):
            # Handle TAB and SPC markers
            if isinstance(part, TabMarker):
                # TAB(n) - move to column n (1-based)
                target_col = part.column
                current_col = len(output) + 1  # 1-based column
                if current_col < target_col:
                    # Add spaces to reach target column
                    output += " " * (target_col - current_col)
                # If already past target, don't move backwards
            elif isinstance(part, SpcMarker):
                # SPC(n) - print n spaces
                output += " " * part.count
            else:
                # Regular string
                output += part
            if i < len(stmt.separators):
                sep = stmt.separators[i]
                if sep == ',':
                    # Tab to next zone (14-character zones in MBASIC)
                    current_len = len(output)
                    next_zone = ((current_len // 14) + 1) * 14
                    output += " " * (next_zone - current_len)
                elif sep == ';':
                    # No spacing (already handled in number formatting)
                    pass
                elif sep == '\n':
                    # Newline
                    output += '\n'

        # Output to file or screen
        if file_handle:
            # Print to file (don't add newline if last separator was ; or ,)
            if stmt.separators and stmt.separators[-1] in [';', ',', '\n']:
                file_handle.write(output)
            else:
                file_handle.write(output + '\n')
            file_handle.flush()  # Ensure data is written
        else:
            # Print to screen (don't add newline if last separator was ; or , or \n)
            if stmt.separators and stmt.separators[-1] in [';', ',', '\n']:
                self.io.output(output, end='')
            else:
                self.io.output(output)

    def execute_printusing(self, stmt):
        """Execute PRINT USING statement - formatted print to screen or file"""
        # Check if printing to file
        if stmt.file_number is not None:
            file_num = int(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise RuntimeError(f"File #{file_num} not open")
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_handle = None

        # Evaluate format string
        format_str = str(self.evaluate_expression(stmt.format_string))

        # Check for empty format string
        if not format_str:
            raise RuntimeError("Illegal function call")

        # Evaluate all expressions
        values = []
        for expr in stmt.expressions:
            value = self.evaluate_expression(expr)
            values.append(value)

        # Create formatter and format values
        formatter = UsingFormatter(format_str)
        output = formatter.format_values(values)

        # Output to file or screen
        if file_handle:
            file_handle.write(output + '\n')
            file_handle.flush()
        else:
            self.io.output(output)

    def execute_if(self, stmt):
        """Execute IF statement"""
        condition = self.evaluate_expression(stmt.condition)

        # In BASIC, any non-zero value is true
        if condition:
            # Execute THEN clause
            if stmt.then_line_number is not None:
                # THEN line_number
                self.runtime.npc = PC.from_line(stmt.then_line_number)
            elif stmt.then_statements:
                # THEN statement(s)
                for then_stmt in stmt.then_statements:
                    self.execute_statement(then_stmt)
                    if self.runtime.npc is not None:
                        break
        else:
            # Execute ELSE clause
            if stmt.else_line_number is not None:
                # ELSE line_number
                self.runtime.npc = PC.from_line(stmt.else_line_number)
            elif stmt.else_statements:
                # ELSE statement(s)
                for else_stmt in stmt.else_statements:
                    self.execute_statement(else_stmt)
                    if self.runtime.npc is not None:
                        break

    def execute_goto(self, stmt):
        """Execute GOTO statement"""
        # If we're in an error handler and GOTOing out, clear the error state
        if self.state.error_info is not None:
            self.state.error_info = None
            self.runtime.set_variable_raw('err%', 0)
        # Set both old and new PC
        self.runtime.npc = PC.from_line(stmt.line_number)

    def execute_gosub(self, stmt):
        """Execute GOSUB statement"""
        # Check resource limits
        self.limits.push_gosub(stmt.line_number)

        # Push return address using PC
        return_pc = self.runtime.statement_table.next_pc(self.runtime.pc)
        # Store return address as (line_number, statement_offset) for RETURN
        self.runtime.push_gosub(
            return_pc.line_num if return_pc.is_running() else 0,
            return_pc.stmt_offset if return_pc.is_running() else 0
        )

        # Jump to subroutine
        self.runtime.npc = PC.from_line(stmt.line_number)

    def execute_ongoto(self, stmt):
        """Execute ON...GOTO statement - computed GOTO

        Syntax: ON expression GOTO line1, line2, line3, ...

        If expression evaluates to 1, jump to line1
        If expression evaluates to 2, jump to line2
        If expression is 0 or > number of lines, continue to next statement
        """
        # Evaluate the expression
        value = self.evaluate_expression(stmt.expression)

        # Convert to integer (round towards zero like MBASIC)
        index = int(value)

        # Check if index is valid (1-based indexing)
        if 1 <= index <= len(stmt.line_numbers):
            # If we're in an error handler and GOTOing out, clear the error state
            if self.state.error_info is not None:
                self.state.error_info = None
                self.runtime.set_variable_raw('err%', 0)
            self.runtime.npc = PC.from_line(stmt.line_numbers[index - 1])
        # If index is out of range, just continue to next statement (no jump)

    def execute_ongosub(self, stmt):
        """Execute ON...GOSUB statement - computed GOSUB

        Syntax: ON expression GOSUB line1, line2, line3, ...

        If expression evaluates to 1, gosub to line1
        If expression evaluates to 2, gosub to line2
        If expression is 0 or > number of lines, continue to next statement
        """
        # Evaluate the expression
        value = self.evaluate_expression(stmt.expression)

        # Convert to integer (round towards zero like MBASIC)
        index = int(value)

        # Check if index is valid (1-based indexing)
        if 1 <= index <= len(stmt.line_numbers):
            # Check resource limits
            self.limits.push_gosub(stmt.line_numbers[index - 1])

            # Push return address using PC
            return_pc = self.runtime.statement_table.next_pc(self.runtime.pc)
            self.runtime.push_gosub(
                return_pc.line_num if return_pc.is_running() else 0,
                return_pc.stmt_offset if return_pc.is_running() else 0
            )
            # Jump to subroutine
            self.runtime.npc = PC.from_line(stmt.line_numbers[index - 1])
        # If index is out of range, just continue to next statement (no jump)

    def execute_return(self, stmt):
        """Execute RETURN statement"""
        # Pop from resource limits
        self.limits.pop_gosub()

        # Pop return address
        return_line, return_stmt = self.runtime.pop_gosub()

        # If returning from error handler, clear error state
        if self.state.error_info is not None:
            self.state.error_info = None
            self.runtime.set_variable_raw('err%', 0)

        # Validate that the return address still exists
        if not self.runtime.statement_table.line_exists(return_line):
            raise RuntimeError(f"RETURN error: line {return_line} no longer exists")

        line_statements = self.runtime.statement_table.get_line_statements(return_line)
        # return_stmt is 0-indexed offset into statements array.
        # Valid range: 0 to len(statements) (inclusive).
        # - 0 to len(statements)-1: Normal statement positions
        # - len(statements): Sentinel value indicating "past the last statement" (move to next line).
        #   This occurs when GOSUB is the last statement on a line. When RETURN jumps back,
        #   statement_table.next_pc() creates this sentinel value to indicate the next sequential PC.
        # Values > len(statements) indicate the statement was deleted (validation error).
        if return_stmt > len(line_statements):
            raise RuntimeError(f"RETURN error: statement {return_stmt} in line {return_line} no longer exists")

        # Jump back to the line and statement after GOSUB
        self.runtime.npc = PC.running_at(return_line, return_stmt)

    def execute_for(self, stmt):
        """Execute FOR statement - initialize loop variable and register loop.

        Syntax: FOR variable = start TO end [STEP step]

        The loop variable typically has numeric type suffixes (%, !, #). The variable
        type determines how values are stored. String variables ($) are syntactically
        valid (parser accepts them) but cause a "Type mismatch" error at runtime when
        set_variable() attempts to assign numeric loop values to a string variable.

        After FOR, the variable is set to start value and the loop is registered.
        NEXT will increment/decrement and check the end condition.
        """
        # Evaluate start, end, step
        start = self.evaluate_expression(stmt.start_expr)
        end = self.evaluate_expression(stmt.end_expr)
        step = self.evaluate_expression(stmt.step_expr) if stmt.step_expr else 1

        # Set loop variable to start
        var_name = stmt.variable.name + (stmt.variable.type_suffix or "")
        self.runtime.set_variable(
            stmt.variable.name,
            stmt.variable.type_suffix,
            start,
            token=self._make_token_info(stmt.variable),
            limits=self.limits,
            original_case=getattr(stmt.variable, 'original_case', stmt.variable.name),
            settings_manager=self.settings_manager
        )

        # Check resource limits
        self.limits.push_for_loop(var_name)

        # Register loop - use PC for position
        self.runtime.push_for_loop(
            var_name,
            end,
            step,
            self.runtime.pc.line,
            self.runtime.pc.statement
        )

    def execute_next(self, stmt):
        """Execute NEXT statement

        Syntax: NEXT [variable [, variable ...]]

        NEXT I, J, K processes variables left-to-right: I first, then J, then K.
        For each variable, _execute_next_single() increments it and checks if the loop
        should continue:
        - Returns True (loop continues): Execution jumps back to FOR body, remaining
          variables are not processed
        - Returns False (loop finished): That loop is popped, next variable is processed

        Note: This method handles a single NEXT statement, which may contain comma-separated
        variables (NEXT I, J, K). The parser treats colon-separated NEXT statements
        (NEXT I: NEXT J: NEXT K) as distinct statements, each calling execute_next()
        independently. This method does NOT handle the colon-separated case - that's
        handled by the parser creating multiple statements.
        """
        # Determine which variables to process
        if stmt.variables:
            # Process variables left-to-right: NEXT I, J, K processes I first, then J, then K.
            # Each variable is incremented; if it loops back to FOR, subsequent vars are skipped.
            # If a variable's loop completes, it's popped and the next variable is processed.
            var_list = stmt.variables
        else:
            # NEXT without variable - scan back lexically to find most recent FOR
            var_name = self._find_most_recent_for_variable()
            if not var_name:
                raise RuntimeError("NEXT without FOR")
            # Create a dummy list with just this variable
            class DummyVarNode:
                def __init__(self, name, suffix):
                    self.name = name
                    self.type_suffix = suffix
            base_name = var_name.rstrip('$%!#')
            type_suffix = var_name[-1] if var_name and var_name[-1] in '$%!#' else None
            var_list = [DummyVarNode(base_name, type_suffix)]

        # Process each variable in order
        for var_node in var_list:
            var_name = var_node.name + (var_node.type_suffix or "")
            # Process this NEXT
            should_continue = self._execute_next_single(var_name, var_node=var_node)
            # If this loop continues (jumps back), don't process remaining variables
            if should_continue:
                return

    def _find_most_recent_for_variable(self):
        """Find the variable of the most recent FOR loop by scanning back lexically.

        Returns:
            Variable name with suffix (e.g., 'i!') or None if no FOR found
        """
        # Scan backward from current PC to find most recent FOR statement
        current_pc = self.runtime.pc
        if not current_pc.is_running():
            return None

        # Walk backward through statements
        pc = PC.running_at(current_pc.line, current_pc.statement - 1)
        while True:
            # Try to get previous statement
            pc = self.runtime.statement_table.prev_pc(pc)
            if pc is None or not pc.is_running():
                return None

            # Check if this statement is a FOR
            stmt = self.runtime.statement_table.get_statement(pc)
            if stmt and hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'ForStatementNode':
                # Found a FOR statement - return its variable name
                var_name = stmt.variable.name + (stmt.variable.type_suffix or "")
                return var_name

    def _execute_next_single(self, var_name, var_node=None):
        """Execute NEXT for a single variable.

        Args:
            var_name: Full variable name with suffix
            var_node: Optional VariableNode for token info

        Returns:
            True if loop continues (jumped back), False if loop finished
        """
        # Get loop info
        loop_info = self.runtime.get_for_loop(var_name)
        if not loop_info:
            raise RuntimeError(f"NEXT without FOR: {var_name}")

        # Create token info for tracking
        token = self._make_token_info(var_node) if var_node else None

        # Increment loop variable
        base_name = var_name.rstrip('$%!#')
        type_suffix = var_name[-1] if var_name[-1] in '$%!#' else None

        if token:
            current = self.runtime.get_variable(base_name, type_suffix, token=token)
        else:
            # NEXT without variable - use current line for token
            class TokenInfo:
                def __init__(self, line):
                    self.line = line
                    self.position = 0
            token = TokenInfo(self.runtime.pc.line_num if self.runtime.pc.is_running() else 0)
            current = self.runtime.get_variable(base_name, type_suffix, token=token)

        step = loop_info['step']
        new_value = current + step

        # Check if loop should continue
        if (step > 0 and new_value <= loop_info['end']) or (step < 0 and new_value >= loop_info['end']):
            # Validate that the FOR return address still exists
            return_line = loop_info['return_line']
            return_stmt = loop_info['return_stmt']

            if not self.runtime.statement_table.line_exists(return_line):
                raise RuntimeError(f"NEXT error: FOR loop line {return_line} no longer exists")

            line_statements = self.runtime.statement_table.get_line_statements(return_line)
            # return_stmt is 0-indexed offset into statements array.
            # Valid range:
            #   - 0 to len(statements)-1: Normal statement positions (existing statements)
            #   - len(statements): Special sentinel value - FOR was last statement on line,
            #                      continue execution at next line (no more statements to execute on current line)
            #   - > len(statements): Invalid - indicates the statement was deleted
            #
            # Validation: Check for strictly greater than (== len is OK as sentinel)
            if return_stmt > len(line_statements):
                raise RuntimeError(f"NEXT error: FOR statement in line {return_line} no longer exists")

            # Continue loop - update variable and jump to statement AFTER the FOR
            self.runtime.set_variable(base_name, type_suffix, new_value, token=token, limits=self.limits)
            # Jump back to statement AFTER the FOR
            for_pc = PC.running_at(return_line, return_stmt)
            next_pc = self.runtime.statement_table.next_pc(for_pc)
            self.runtime.npc = next_pc
            return True  # Loop continues
        else:
            # Loop finished
            self.limits.pop_for_loop()
            self.runtime.pop_for_loop(var_name)
            return False  # Loop finished

    def execute_while(self, stmt):
        """Execute WHILE statement"""
        # Evaluate the condition
        condition = self.evaluate_expression(stmt.condition)

        if not condition:
            # Condition is false - skip to after matching WEND
            wend_pos = self.find_matching_wend(
                self.runtime.pc.line_num,
                self.runtime.pc.stmt_offset
            )

            if wend_pos is None:
                raise RuntimeError(f"WHILE without matching WEND at line {self.runtime.pc.line_num}")

            wend_line, wend_stmt = wend_pos

            # Jump to the statement AFTER the WEND using statement_table
            wend_pc = PC.running_at(wend_line, wend_stmt)
            next_pc = self.runtime.statement_table.next_pc(wend_pc)
            if not next_pc.is_running():
                # No more statements - program ends
                self.runtime.pc = PC.halted()
            else:
                self.runtime.npc = next_pc
        else:
            # Condition is true - enter the loop
            # Check resource limits
            self.limits.push_while_loop()

            # Push loop info so WEND knows where to return (use PC)
            self.runtime.push_while_loop(
                self.runtime.pc.line_num,
                self.runtime.pc.stmt_offset
            )

    def execute_wend(self, stmt):
        """Execute WEND statement"""
        # Pop the matching WHILE loop info
        loop_info = self.runtime.peek_while_loop()

        if loop_info is None:
            raise RuntimeError(f"WEND without matching WHILE at line {self.runtime.pc.line_num}")

        # Jump back to the WHILE statement to re-evaluate the condition
        self.runtime.npc = PC.running_at(loop_info['while_line'], loop_info['while_stmt'])

        # Pop the loop from the stack (after setting npc above, before WHILE re-executes).
        # Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.
        # The WHILE will re-push if its condition is still true, or skip the loop body
        # if false. This ensures clean stack state and proper error handling if the
        # WHILE condition evaluation fails (loop already popped, won't corrupt stack).
        self.limits.pop_while_loop()
        self.runtime.pop_while_loop()

    def execute_onerror(self, stmt):
        """Execute ON ERROR GOTO/GOSUB statement"""
        # Set error handler
        # Line number 0 means disable error handling (ON ERROR GOTO 0)
        if stmt.line_number == 0:
            self.runtime.error_handler = None
            self.runtime.error_handler_is_gosub = False
        else:
            self.runtime.error_handler = stmt.line_number
            self.runtime.error_handler_is_gosub = stmt.is_gosub

    def execute_resume(self, stmt):
        """Execute RESUME statement"""
        if self.state.error_info is None:
            raise RuntimeError("RESUME without error")

        # Get error PC from ErrorInfo
        if not self.state.error_info.pc:
            raise RuntimeError("No error position to resume from")

        error_pc = self.state.error_info.pc

        # Clear error state
        self.state.error_info = None
        self.runtime.set_variable_raw('err%', 0)

        # Determine where to resume
        if stmt.line_number is None or stmt.line_number == 0:
            # RESUME or RESUME 0 - retry the statement that caused the error
            # Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
            # Parser preserves the distinction (None vs 0) for source text regeneration,
            # but runtime execution treats both identically.
            self.runtime.npc = error_pc
        elif stmt.line_number == -1:
            # RESUME NEXT - continue at statement after the error
            next_pc = self.runtime.statement_table.next_pc(error_pc)
            if not next_pc.is_running():
                # No next statement, program ends
                self.runtime.pc = PC.halted()
            else:
                self.runtime.npc = next_pc
        else:
            # RESUME line_number - jump to specific line
            self.runtime.npc = PC.from_line(stmt.line_number)

    def execute_end(self, stmt):
        """Execute END statement"""
        self.runtime.pc = self.runtime.pc.stop("END")

    def execute_remark(self, stmt):
        """Execute REM statement (do nothing)"""
        pass

    def execute_poke(self, stmt):
        """Execute POKE statement (no-op for compatibility).

        POKE cannot modify memory in Python interpreter but is parsed and accepted
        for compatibility with MBASIC programs that use it.
        """
        pass

    def execute_deftype(self, stmt):
        """Execute DEFINT/DEFSNG/DEFDBL/DEFSTR statement (do nothing at runtime)"""
        # These are compile-time directives handled by the parser
        # At runtime, they do nothing
        pass

    def execute_deffn(self, stmt):
        """Execute DEF FN statement - define user function

        Syntax: DEF FNname[(param1, param2, ...)] = expression

        Example:
            DEF FND(X) = X * 2 + 1
            PRINT FND(5)  -> 11
        """
        # Store function definition in runtime
        # The function name is already normalized to lowercase
        self.runtime.user_functions[stmt.name] = stmt

    def execute_data(self, stmt):
        """Execute DATA statement (do nothing, data already indexed)"""
        pass

    def execute_read(self, stmt):
        """Execute READ statement"""
        for var_node in stmt.variables:
            # Read next data value (returns AST node)
            data_node = self.runtime.read_data()

            # Evaluate the data node to get actual value
            value = self.evaluate_expression(data_node)

            # Convert to appropriate type based on variable suffix
            if var_node.type_suffix == '$':
                value = str(value)
            elif var_node.type_suffix == '%':
                value = int(value)
            else:
                # Ensure numeric types are float
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = 0

            # Store in variable
            if var_node.subscripts:
                subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
                self.runtime.set_array_element(var_node.name, var_node.type_suffix, subscripts, value, token=self._make_token_info(var_node))
            else:
                self.runtime.set_variable(
                    var_node.name,
                    var_node.type_suffix,
                    value,
                    token=self._make_token_info(var_node),
                    limits=self.limits,
                    original_case=getattr(var_node, 'original_case', var_node.name),
                    settings_manager=self.settings_manager
                )

    def execute_restore(self, stmt):
        """Execute RESTORE statement"""
        self.runtime.restore_data(stmt.line_number if hasattr(stmt, 'line_number') else None)

    def execute_dim(self, stmt):
        """Execute DIM statement"""
        from src.ast_nodes import TypeInfo

        for array_def in stmt.arrays:
            # array_def is an ArrayDeclNode with name and dimensions
            dimensions = [int(self.evaluate_expression(dim)) for dim in array_def.dimensions]
            # Extract type suffix from name if present
            name = array_def.name
            type_suffix = None
            if name and name[-1] in '$%!#':
                type_suffix = name[-1]
                name = name[:-1]

            # Check resource limits before allocating
            var_type = TypeInfo.from_suffix(type_suffix)
            full_name = (name + (type_suffix or '')).lower()
            self.limits.allocate_array(full_name, dimensions, var_type)

            # Proceed with actual allocation, pass token for tracking
            token = getattr(stmt, 'token', None)
            self.runtime.dimension_array(name, type_suffix, dimensions, token=token)

    def execute_erase(self, stmt):
        """Execute ERASE statement

        ERASE removes arrays from memory to reclaim space.
        After ERASE, the array must be re-dimensioned with DIM before use.

        Syntax: ERASE array1, array2, ...
        """
        for array_name in stmt.array_names:
            # Free from resource limits tracking
            self.limits.free_variable(array_name.lower())

            # Array name already includes type suffix from parser
            # Delete using raw method (already have full name)
            self.runtime.delete_array_raw(array_name)

    def execute_clear(self, stmt):
        """Execute CLEAR statement

        CLEAR resets all variables and closes all open files.
        Optional arguments for string space and stack space are parsed but ignored.

        Syntax: CLEAR [,[string_space][,stack_space]]

        Effects:
        - All simple variables are deleted
        - All arrays are erased
        - All open files are closed
        - COMMON variables list is preserved (for CHAIN compatibility)
        - String space and stack space parameters are ignored (Python manages memory automatically)
        """
        # Clear resource limits tracking
        self.limits.clear_all()

        # Clear all variables
        self.runtime.clear_variables()

        # Clear all arrays
        self.runtime.clear_arrays()

        # Close all open files
        # Note: Only OS-level file errors are silently ignored to match MBASIC behavior.
        # In Python 3, IOError is an alias for OSError, so we catch both for compatibility.
        # This differs from RESET which allows errors to propagate.
        # We intentionally do NOT catch all exceptions (e.g., AttributeError) to avoid
        # hiding programming errors.
        for file_num in list(self.runtime.files.keys()):
            try:
                file_obj = self.runtime.files[file_num]
                if hasattr(file_obj, 'close'):
                    file_obj.close()
            except (OSError, IOError):
                # Silently ignore OS-level file close errors (e.g., already closed, permission denied)
                pass
        self.runtime.files.clear()
        self.runtime.field_buffers.clear()

        # State preservation for CHAIN compatibility:
        #
        # PRESERVED by CLEAR (not cleared):
        #   - runtime.common_vars (list of COMMON variable names - the list itself, not values)
        #   - runtime.user_functions (DEF FN functions)
        #
        # NOT PRESERVED (cleared above):
        #   - All variables and arrays
        #   - All open files (closed and cleared)
        #   - Field buffers
        #
        # Note: We ignore string_space and stack_space parameters (Python manages memory automatically)

    def execute_randomize(self, stmt):
        """Execute RANDOMIZE statement

        Reseeds the random number generator.

        Syntax:
            RANDOMIZE           - Use timer/system value as seed
            RANDOMIZE seed      - Use specific seed value

        Example:
            10 RANDOMIZE
            20 RANDOMIZE 42
            30 RANDOMIZE TIMER
        """
        import random
        import time

        if stmt.seed:
            # Use specified seed value
            seed = self.evaluate_expression(stmt.seed)
            random.seed(int(seed))
        else:
            # Use timer/system value (current time)
            random.seed(time.time())

    def execute_optionbase(self, stmt):
        """Execute OPTION BASE statement

        Sets the lower bound for array indices (0 or 1).

        MBASIC 5.21 restrictions (strictly enforced):
        - OPTION BASE can only be executed once per program run
        - Must be executed BEFORE any arrays are dimensioned (implicit or explicit)
        - Violating either condition raises "Duplicate Definition" error

        Syntax: OPTION BASE 0 | 1
        Note: Parser validates that base value is 0 or 1 (parse error if not)

        Raises:
            RuntimeError: "Duplicate Definition" if OPTION BASE already executed OR if any arrays exist
        """
        # MBASIC 5.21 gives "Duplicate Definition" if:
        # 1. OPTION BASE has already been executed, OR
        # 2. Any arrays have been created (both explicitly via DIM and implicitly via first use like A(5)=10)
        #    The error occurs even if arrays were created with the same base value that OPTION BASE
        #    would set (e.g., arrays already use base 0, and OPTION BASE 0 would still raise error).
        # Note: The check len(self.runtime._arrays) > 0 catches all array creation because both
        # explicit DIM and implicit array access (via set_array_element) update runtime._arrays.
        if self.runtime.option_base_executed:
            raise RuntimeError("Duplicate Definition")

        if len(self.runtime._arrays) > 0:
            raise RuntimeError("Duplicate Definition")

        self.runtime.array_base = stmt.base
        self.runtime.option_base_executed = True

    def execute_error(self, stmt):
        """Execute ERROR statement

        Simulates an error with the specified error code.
        Sets ERR and ERL, then raises a RuntimeError.

        Syntax: ERROR error_code
        """
        error_code = int(self.evaluate_expression(stmt.error_code))

        # Set error information in variable table (integer variables, lowercase)
        self.runtime.set_variable_raw('err%', error_code)
        if self.runtime.pc.is_running():
            self.runtime.set_variable_raw('erl%', self.runtime.pc.line_num)
            self.runtime.set_variable_raw('ers%', self.runtime.pc.stmt_offset)
        else:
            self.runtime.set_variable_raw('erl%', 0)
            self.runtime.set_variable_raw('ers%', 0)

        # Raise the error
        raise RuntimeError(f"ERROR {error_code}")

    def execute_input(self, stmt):
        """Execute INPUT statement - read from keyboard or file

        State machine for keyboard input (file input is synchronous):
        1. If state.input_buffer has data: Use buffered input (from provide_input())
        2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
        3. UI calls provide_input() with user's input line
        4. On next tick(), buffered input is used (step 1) and input_prompt/input_variables are cleared

        Note: input_file_number is designed to be set to None for keyboard input and file#
        for file input. This would allow the UI to distinguish between keyboard prompts
        (show in UI) and file input (internal, no prompt needed). However, currently always
        set to None because file input (stmt.file_number is not None) takes a separate code
        path that reads synchronously without setting the state machine.

        Design note: File input bypasses the state machine and reads synchronously because
        file data is immediately available (blocking I/O), unlike keyboard input which
        requires async handling in the UI event loop.
        """
        # Check if reading from file
        if stmt.file_number is not None:
            file_num = int(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise RuntimeError(f"File #{file_num} not open")
            file_info = self.runtime.files[file_num]
            if file_info['mode'] != 'I':
                raise RuntimeError(f"File #{file_num} not open for input")

            # Read from file (synchronous - files don't need state machine)
            line = self._read_line_from_file(file_num)
            if line is None:
                raise RuntimeError("Input past end of file")
        else:
            # Reading from keyboard - check if we have buffered input
            if self.state.input_buffer:
                # Use buffered input from provide_input()
                line = self.state.input_buffer.pop(0)
            else:
                # No buffered input - need to wait for user input
                # Show prompt (check suppress_question flag for INPUT; syntax)
                if stmt.prompt:
                    prompt_value = self.evaluate_expression(stmt.prompt)
                    self.io.output(prompt_value, end='')
                    if not stmt.suppress_question:
                        self.io.output("? ", end='')
                        full_prompt = prompt_value + "? "
                    else:
                        full_prompt = prompt_value
                else:
                    if not stmt.suppress_question:
                        self.io.output("? ", end='')
                        full_prompt = "? "
                    else:
                        full_prompt = ""

                # Set input prompt - execution will pause
                # Sets: input_prompt (prompt text), input_variables (var list),
                #       input_file_number (None for keyboard input, file # for file input)
                self.state.input_prompt = full_prompt
                self.state.input_variables = stmt.variables  # Save variables for resumption
                self.state.input_file_number = None  # None indicates keyboard input (not file)

                # Save statement for resumption
                # We'll need to re-execute this statement when input is provided
                # The tick() loop will detect input_prompt and return
                return

        # Parse comma-separated values
        values = [v.strip() for v in line.split(',')]

        # Assign to variables
        for i, var_node in enumerate(stmt.variables):
            if i >= len(values):
                raise RuntimeError("Input past end of file")

            value = values[i]

            # Convert type
            if var_node.type_suffix == '$':
                value = str(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    value = 0

            # Store
            if var_node.subscripts:
                subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
                self.runtime.set_array_element(var_node.name, var_node.type_suffix, subscripts, value, token=self._make_token_info(var_node))
            else:
                self.runtime.set_variable(
                    var_node.name,
                    var_node.type_suffix,
                    value,
                    token=self._make_token_info(var_node),
                    limits=self.limits,
                    original_case=getattr(var_node, 'original_case', var_node.name),
                    settings_manager=self.settings_manager
                )

        # Clear input state after successful completion
        self.state.input_variables = []
        self.state.input_prompt = None

    def _read_line_from_file(self, file_num):
        """Read a line from file, respecting ^Z as EOF (CP/M style)

        CP/M Background:
        On CP/M 1.x and 2.x, files were stored in 128-byte sectors. When a text
        file didn't end on a sector boundary, a ^Z (Control-Z, ASCII 26) character
        was used to mark the actual end of file.

        Encoding:
        Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
        CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
        Unicode U+0000-U+00FF, allowing round-trip byte preservation.
        Note: CP/M systems often used code pages like CP437 or CP850 for characters
        128-255, which do NOT match latin-1. Latin-1 preserves the BYTE VALUES but
        not necessarily the CHARACTER MEANING for non-ASCII CP/M text.
        Future enhancement: Add optional encoding conversion setting for CP437/CP850 display.

        EOF Detection (three methods):
        1. EOF flag already set (file_info['eof'] == True) → returns None immediately
        2. read() returns empty bytes (physical EOF) → sets EOF flag, returns partial line or None
        3. Byte value 26 (^Z) encountered → sets EOF flag, returns partial line or None

        Line Ending Handling:
        - LF (byte 10): Line complete, return
        - CR+LF (bytes 13+10): Line complete, consume both, return
        - CR alone (byte 13): Line complete (old Mac format), return

        Returns: line string or None if EOF
        """
        file_info = self.runtime.files[file_num]
        file_handle = file_info['handle']

        if file_info['eof']:
            return None

        # Read bytes until newline or ^Z
        line_bytes = bytearray()
        while True:
            byte = file_handle.read(1)
            if not byte:
                # End of file
                file_info['eof'] = True
                if line_bytes:
                    # Return partial line
                    return line_bytes.decode('latin-1', errors='replace').rstrip('\r\n')
                return None

            b = byte[0]
            if b == 26:  # ^Z (EOF marker in CP/M)
                file_info['eof'] = True
                if line_bytes:
                    return line_bytes.decode('latin-1', errors='replace').rstrip('\r\n')
                return None
            elif b == 10:  # LF
                # End of line - LF or CRLF (CR already consumed)
                return line_bytes.decode('latin-1', errors='replace')
            elif b == 13:  # CR
                # Peek ahead to see if next byte is LF
                next_byte = file_handle.read(1)
                if next_byte and next_byte[0] == 10:  # LF
                    # CRLF sequence - return line, LF already consumed
                    return line_bytes.decode('latin-1', errors='replace')
                else:
                    # CR alone (old Mac format) - return line
                    # Put back the peeked byte if it exists
                    if next_byte:
                        file_handle.seek(-1, 1)  # Seek back one byte from current position
                    return line_bytes.decode('latin-1', errors='replace')
            else:
                line_bytes.append(b)

    def execute_lineinput(self, stmt):
        """Execute LINE INPUT statement - read entire line

        In tick-based execution mode, this may transition to 'waiting_for_input' state
        instead of blocking. When input is provided via provide_input(), execution
        resumes from the input buffer.
        """
        # Check if reading from file
        if stmt.file_number is not None:
            file_num = int(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise RuntimeError(f"File #{file_num} not open")
            file_info = self.runtime.files[file_num]
            if file_info['mode'] != 'I':
                raise RuntimeError(f"File #{file_num} not open for input")

            # Read from file (synchronous - files don't need state machine)
            line = self._read_line_from_file(file_num)
            if line is None:
                raise RuntimeError("Input past end of file")
        else:
            # Reading from keyboard - check if we have buffered input
            if self.state.input_buffer:
                # Use buffered input from provide_input()
                line = self.state.input_buffer.pop(0)
            else:
                # No buffered input - need to wait for user input
                # Show prompt
                if stmt.prompt:
                    prompt_value = self.evaluate_expression(stmt.prompt)
                    self.io.output(prompt_value, end='')
                    full_prompt = prompt_value
                else:
                    full_prompt = ""

                # Set input prompt - execution will pause
                self.state.input_prompt = full_prompt
                self.state.input_variables = [stmt.variable]  # Save variable for resumption
                self.state.input_file_number = None

                # The tick() loop will detect input_prompt and return
                return

        # Assign entire line to variable (no parsing)
        var_node = stmt.variable
        if var_node.subscripts:
            subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
            self.runtime.set_array_element(var_node.name, var_node.type_suffix, subscripts, line, token=self._make_token_info(var_node))
        else:
            self.runtime.set_variable(
                var_node.name,
                var_node.type_suffix,
                line,
                token=self._make_token_info(var_node),
                limits=self.limits,
                original_case=getattr(var_node, 'original_case', var_node.name),
                settings_manager=self.settings_manager
            )

        # Clear input state after successful completion
        self.state.input_variables = []
        self.state.input_prompt = None

    def execute_write(self, stmt):
        """Execute WRITE statement - output comma-delimited data

        WRITE outputs values separated by commas, with strings quoted.
        Syntax:
            WRITE expr1, expr2    - Write to screen
            WRITE #n, expr1       - Write to file
        """
        # Check if writing to file
        if stmt.file_number is not None:
            file_num = int(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise RuntimeError(f"File #{file_num} not open")
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_handle = None

        # Format values
        output_parts = []
        for expr in stmt.expressions:
            value = self.evaluate_expression(expr)

            if isinstance(value, str):
                # Quote strings
                output_parts.append(f'"{value}"')
            elif isinstance(value, float):
                # Numbers without spaces
                if value == int(value):
                    output_parts.append(str(int(value)))
                else:
                    output_parts.append(str(value))
            else:
                output_parts.append(str(value))

        output = ','.join(output_parts)

        # Output to file or screen
        if file_handle:
            file_handle.write(output + '\n')
            file_handle.flush()
        else:
            self.io.output(output)

    def execute_load(self, stmt):
        """Execute LOAD statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("LOAD requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_load(filename)
        else:
            raise RuntimeError("LOAD not available in this context")

    def execute_save(self, stmt):
        """Execute SAVE statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("SAVE requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_save(filename)
        else:
            raise RuntimeError("SAVE not available in this context")

    def execute_run(self, stmt):
        """Execute RUN statement - CLEAR variables and restart/goto

        RUN                - CLEAR + GOTO first line
        RUN line_number    - CLEAR + GOTO line_number
        RUN "filename"     - LOAD file + CLEAR + GOTO first line
        """
        # Evaluate target if present
        if stmt.target:
            target_value = self.evaluate_expression(stmt.target)

            if isinstance(target_value, str):
                # RUN "filename" - load and run file
                if hasattr(self, 'interactive_mode') and self.interactive_mode:
                    self.interactive_mode.cmd_load(target_value)
                    self.interactive_mode.cmd_run()
                else:
                    raise RuntimeError("RUN filename not available in this context")
            else:
                # RUN line_number - CLEAR variables then GOTO line
                line_num = int(target_value)

                # If in interactive mode, delegate to cmd_run with start line
                if hasattr(self, 'interactive_mode') and self.interactive_mode:
                    self.interactive_mode.cmd_run(start_line=line_num)
                else:
                    # In non-interactive context (running program), do inline
                    self.runtime.clear_variables()
                    # Set NPC to target line (like GOTO)
                    # On next tick(), NPC will be moved to PC
                    self.runtime.npc = PC.from_line(line_num)
                    # PC stays running - execution continues at new line
        else:
            # RUN without arguments - CLEAR + signal restart needed
            if hasattr(self, 'interactive_mode') and self.interactive_mode:
                self.interactive_mode.cmd_run()
            else:
                # In non-interactive context, signal that restart is needed
                # Note: RUN without args stops current execution,
                # signaling the caller (e.g., UI tick loop) that it should restart
                # execution from the beginning if desired. This is different from
                # RUN line_number which continues execution inline.
                # The caller is responsible for actually restarting execution.
                self.runtime.clear_variables()
                self.runtime.pc = self.runtime.pc.stop("END")

    def execute_common(self, stmt):
        """Execute COMMON statement

        COMMON variable1, variable2, array1(), ...

        Declares variables to be shared across CHAIN operations.
        Variable order and type matter, not names.
        """
        # Add variable names to common_vars list in order
        for var_name in stmt.variables:
            # Note: We store the variable name as-is
            if var_name not in self.runtime.common_vars:
                self.runtime.common_vars.append(var_name)

    def execute_chain(self, stmt):
        """Execute CHAIN statement

        CHAIN [MERGE] filename$ [, [line_number] [, ALL] [, DELETE range]]

        Loads and executes another BASIC program, optionally:
        - MERGE: Merges program as overlay instead of replacing
        - line_number: Starts execution at specified line
        - ALL: Passes all variables to the new program
        - DELETE range: Deletes line range after merge
        """
        # Evaluate filename
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("CHAIN requires string filename")

        # Evaluate starting line if provided
        start_line = None
        if stmt.start_line:
            start_line = int(self.evaluate_expression(stmt.start_line))

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_chain(
                filename,
                start_line=start_line,
                merge=stmt.merge,
                all_flag=stmt.all_flag,
                delete_range=stmt.delete_range
            )
        else:
            raise RuntimeError("CHAIN not available in this context")

    def execute_system(self, stmt):
        """Execute SYSTEM statement - exit to OS"""
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_system()
        else:
            # In non-interactive context, use file_io to handle exit
            # (in web UI this will raise an error instead of exiting)
            self.io.output("Goodbye")
            self.file_io.system_exit()

    def execute_limits(self, stmt):
        """Execute LIMITS statement - display resource usage"""
        report = self.limits.get_usage_report()
        self.io.output(report)

    def execute_showsettings(self, stmt):
        """Execute SHOWSETTINGS statement - display settings"""
        from src.settings import get_settings_manager
        from src.settings_definitions import SETTING_DEFINITIONS

        settings_manager = get_settings_manager()

        # Get filter if provided
        filter_prefix = None
        if stmt.filter:
            filter_val = self.evaluate_expression(stmt.filter)
            if isinstance(filter_val, str):
                filter_prefix = filter_val.lower()

        # Display settings
        output_lines = []
        for key in sorted(SETTING_DEFINITIONS.keys()):
            # Apply filter if specified
            if filter_prefix and not key.lower().startswith(filter_prefix):
                continue

            value = settings_manager.get(key)
            output_lines.append(f"{key} = {value}")

        if output_lines:
            self.io.output("\n".join(output_lines))
        else:
            if filter_prefix:
                self.io.output(f"No settings matching '{filter_prefix}'")
            else:
                self.io.output("No settings available")

    def execute_setsetting(self, stmt):
        """Execute SETSETTING statement - modify a setting"""
        from src.settings import get_settings_manager
        from src.settings_definitions import validate_value, SettingScope

        settings_manager = get_settings_manager()

        # Evaluate key
        key = self.evaluate_expression(stmt.key)
        if not isinstance(key, str):
            raise RuntimeError("SETSETTING key must be a string")

        # Evaluate value
        value = self.evaluate_expression(stmt.value)

        # Validate and set
        try:
            is_valid, error_msg = validate_value(key, value)
            if not is_valid:
                raise RuntimeError(f"Invalid value for {key}: {error_msg}")

            settings_manager.set(key, value)
            settings_manager.save(SettingScope.GLOBAL)

            self.io.output(f"Setting updated: {key} = {value}")

        except KeyError:
            raise RuntimeError(f"Unknown setting: {key}")

    def execute_merge(self, stmt):
        """Execute MERGE statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("MERGE requires string filename")

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            self.interactive_mode.cmd_merge(filename)
        else:
            raise RuntimeError("MERGE not available in this context")

    def execute_new(self, stmt):
        """Execute NEW statement - clear program and variables.

        Clears the AST (statement_table) and all variables.
        UI should serialize the empty AST back to text after this executes.
        """
        # Clear the statement table
        self.runtime.statement_table.statements.clear()
        self.runtime.statement_table._keys_cache = None

        # Clear the line text map
        self.runtime.line_text_map.clear()

        # Clear the internal AST storage
        if isinstance(self.runtime._ast_or_line_table, dict):
            self.runtime._ast_or_line_table.clear()

        # Clear variables and arrays
        self.runtime.clear_variables()
        self.runtime.clear_arrays()

        # Halt execution
        self.runtime.pc = PC.halted()
        self.runtime.npc = PC.halted()

    def execute_delete(self, stmt):
        """Execute DELETE statement - remove lines from program AST.

        DELETE 100       - Delete line 100
        DELETE 10-50     - Delete lines 10 through 50
        DELETE 10-       - Delete lines 10 to end
        DELETE -50       - Delete lines from beginning to 50
        DELETE           - Delete all lines

        Note: This implementation preserves variables and ALL runtime state when deleting
        lines. DELETE only removes lines from the program AST, leaving variables, open
        files, error handlers, and loop stacks intact. This differs from NEW which clears
        both lines and variables (via clear_variables/clear_arrays).
        """
        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # Convert stmt to string args for cmd_delete
            args = ""
            if stmt.start and stmt.end:
                start = int(self.evaluate_expression(stmt.start))
                end = int(self.evaluate_expression(stmt.end))
                args = f"{start}-{end}"
            elif stmt.start:
                start = int(self.evaluate_expression(stmt.start))
                args = f"{start}-"
            elif stmt.end:
                end = int(self.evaluate_expression(stmt.end))
                args = f"-{end}"

            self.interactive_mode.cmd_delete(args)
            return

        # Fallback: Evaluate start and end expressions
        start_line = None
        end_line = None

        if stmt.start:
            start_line = int(self.evaluate_expression(stmt.start))

        if stmt.end:
            end_line = int(self.evaluate_expression(stmt.end))

        # Get all line numbers from statement table
        all_line_nums = list(set(pc.line_num for pc in self.runtime.statement_table.statements.keys() if pc.line_num is not None))

        # Determine which lines to delete
        lines_to_delete = []
        for line_num in all_line_nums:
            # Check start boundary
            if start_line is not None and line_num < start_line:
                continue
            # Check end boundary
            if end_line is not None and line_num > end_line:
                continue

            lines_to_delete.append(line_num)

        # Delete the lines
        for line_num in lines_to_delete:
            # Remove from line_text_map
            if line_num in self.runtime.line_text_map:
                del self.runtime.line_text_map[line_num]

            # Remove from internal AST storage if it's a dict
            if isinstance(self.runtime._ast_or_line_table, dict):
                if line_num in self.runtime._ast_or_line_table:
                    del self.runtime._ast_or_line_table[line_num]

            # Remove statements from statement_table
            self.runtime.statement_table.delete_line(line_num)

    def execute_renum(self, stmt):
        """Execute RENUM statement - renumber program lines.

        Note: RENUM is implemented via delegation to interactive_mode.cmd_renum.
        This architecture allows the interactive UI to handle AST modifications directly.
        The interactive mode implementation handles:
        1. Renumbering lines in line_asts
        2. Updating statement_table PC keys
        3. Updating GOTO/GOSUB/ON GOTO target line numbers in AST nodes
        4. Updating RESTORE line number references

        In non-interactive contexts, RENUM is not available.
        """
        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # Convert stmt to string args for cmd_renum
            args = ""
            new_start = None
            old_start = None
            increment = None

            if stmt.new_start:
                new_start = int(self.evaluate_expression(stmt.new_start))
            if stmt.old_start:
                old_start = int(self.evaluate_expression(stmt.old_start))
            if stmt.increment:
                increment = int(self.evaluate_expression(stmt.increment))

            # Format: RENUM [new_start][,[old_start][,increment]]
            if new_start is not None:
                args = str(new_start)
                if old_start is not None:
                    args += f",{old_start}"
                    if increment is not None:
                        args += f",{increment}"
                elif increment is not None:
                    args += f",,{increment}"

            self.interactive_mode.cmd_renum(args)
            return

        raise RuntimeError("RENUM not yet implemented - TODO")

    def execute_files(self, stmt):
        """Execute FILES statement - list files using FileIO module."""
        # Evaluate filespec expression
        filespec = ""
        if stmt.filespec:
            filespec = self.evaluate_expression(stmt.filespec)
            if not isinstance(filespec, str):
                raise RuntimeError("FILES requires string filespec")

        # Use file_io module (sandboxed for web UI, real filesystem for local UIs)
        files = self.file_io.list_files(filespec)
        pattern = filespec if filespec else "*"

        if not files:
            self.io.output(f"No files matching: {pattern}")
            return

        # Display files
        for filename, size, is_dir in files:
            if is_dir:
                self.io.output(f"{filename:<30}        <DIR>")
            elif size is not None:
                self.io.output(f"{filename:<30} {size:>12} bytes")
            else:
                self.io.output(f"{filename:<30}            ?")

        self.io.output(f"\n{len(files)} File(s)")

    def execute_kill(self, stmt):
        """Execute KILL statement - delete file

        Syntax: KILL filename$
        Example: KILL "TEMP.DAT"
        """
        import os

        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("KILL requires string filename")

        # Delete the file
        try:
            if os.path.exists(filename):
                os.remove(filename)
            else:
                raise RuntimeError(f"File not found: {filename}")
        except OSError as e:
            raise RuntimeError(f"Cannot delete {filename}: {e.strerror}")

    def execute_name(self, stmt):
        """Execute NAME statement - rename file

        Syntax: NAME oldfile$ AS newfile$
        Example: NAME "TEMP.DAT" AS "FINAL.DAT"
        """
        import os

        # Evaluate old and new filename expressions
        old_filename = self.evaluate_expression(stmt.old_filename)
        new_filename = self.evaluate_expression(stmt.new_filename)

        if not isinstance(old_filename, str):
            raise RuntimeError("NAME requires string for old filename")
        if not isinstance(new_filename, str):
            raise RuntimeError("NAME requires string for new filename")

        # Rename the file
        try:
            if not os.path.exists(old_filename):
                raise RuntimeError(f"File not found: {old_filename}")
            if os.path.exists(new_filename):
                raise RuntimeError(f"File already exists: {new_filename}")
            os.rename(old_filename, new_filename)
        except OSError as e:
            raise RuntimeError(f"Cannot rename {old_filename} to {new_filename}: {e.strerror}")

    def execute_open(self, stmt):
        """Execute OPEN statement - open file for I/O

        Syntax:
            OPEN "I", #1, "filename"        - Open for input
            OPEN "O", #2, "filename"        - Open for output
            OPEN "A", #3, "filename"        - Open for append
            OPEN "R", #4, "filename", 128   - Open for random access (FIELD, GET, PUT, LSET, RSET supported)

        Note: CP/M files used ^Z (ASCII 26) as EOF marker. We respect this on input.
        """
        # Evaluate mode, file number, and filename
        mode = stmt.mode.upper()  # "I", "O", "A", "R"
        file_num = int(self.evaluate_expression(stmt.file_number))
        filename = self.evaluate_expression(stmt.filename)

        # Check file number range (MBASIC 5.21: #1 through #15)
        if file_num < 1 or file_num > 15:
            raise RuntimeError("Bad file number")

        if not isinstance(filename, str):
            raise RuntimeError("OPEN requires string filename")

        # Check if file number is already open
        if file_num in self.runtime.files:
            raise RuntimeError(f"File #{file_num} already open")

        # Validate and open file with appropriate mode using filesystem provider
        # Valid modes: I (input), O (output), A (append), R (random access)
        # Any other mode raises error listing valid modes
        try:
            if mode == "I":
                # Open for input - binary mode so we can detect ^Z
                file_handle = self.fs.open(filename, "r", binary=True)
            elif mode == "O":
                # Open for output
                file_handle = self.fs.open(filename, "w", binary=False)
            elif mode == "A":
                # Open for append
                file_handle = self.fs.open(filename, "a", binary=False)
            elif mode == "R":
                # Random access - open for both read and write, create if doesn't exist
                try:
                    file_handle = self.fs.open(filename, "r+", binary=True)
                except (IOError, OSError):
                    # File doesn't exist, create it
                    file_handle = self.fs.open(filename, "w+", binary=True)
            else:
                raise RuntimeError(f"Invalid OPEN mode: {mode} (valid modes: I, O, A, R)")

            # Store file handle and mode
            self.runtime.files[file_num] = {
                'handle': file_handle,
                'mode': mode,
                'filename': filename,
                'eof': False
            }

        except (OSError, IOError, PermissionError) as e:
            raise RuntimeError(f"Cannot open {filename}: {str(e)}")

    def execute_close(self, stmt):
        """Execute CLOSE statement - close file(s)

        Syntax:
            CLOSE #1        - Close file 1
            CLOSE #1, #2    - Close files 1 and 2
            CLOSE           - Close all files

        Note: Silently ignores closing unopened files (MBASIC 5.21 compatibility).
        This allows defensive CLOSE patterns like: CLOSE #1: CLOSE #2: CLOSE #3
        which ensure files are closed without needing to track which files are open.
        """
        if not stmt.file_numbers:
            # CLOSE with no arguments - close all files
            for file_num in list(self.runtime.files.keys()):
                self.runtime.files[file_num]['handle'].close()
                del self.runtime.files[file_num]
        else:
            # Close specific file numbers
            for file_num_expr in stmt.file_numbers:
                file_num = int(self.evaluate_expression(file_num_expr))
                if file_num in self.runtime.files:
                    self.runtime.files[file_num]['handle'].close()
                    del self.runtime.files[file_num]
                # Silently ignore closing unopened files (like MBASIC)

    def execute_reset(self, stmt):
        """Execute RESET statement - close all open files

        Syntax: RESET

        Note: Unlike CLEAR (which silently ignores file close errors), RESET allows
        errors during file close to propagate to the caller. This is intentional
        different behavior between the two statements.
        """
        # Close all open files (errors propagate to caller)
        for file_num in list(self.runtime.files.keys()):
            self.runtime.files[file_num]['handle'].close()
            del self.runtime.files[file_num]

        # Reset filesystem provider
        self.fs.reset()

    def execute_field(self, stmt):
        """Execute FIELD statement - define random-access file buffer

        Syntax: FIELD #n, width AS var$, width AS var$, ...

        Defines the layout of a record buffer for random file access.
        Each variable is mapped to a position and width in the buffer.

        The file must be opened in "R" (random) mode first.
        After FIELD, use GET/PUT to read/write records, and LSET/RSET to
        modify field variable values before PUT.
        """
        file_num = int(self.evaluate_expression(stmt.file_number))

        if file_num not in self.runtime.files:
            raise RuntimeError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'R':
            raise RuntimeError(f"File #{file_num} not open for random access")

        # Initialize field buffer for this file if not exists
        if file_num not in self.runtime.field_buffers:
            self.runtime.field_buffers[file_num] = {
                'buffer': bytearray(),
                'fields': {},  # var_name -> (offset, width)
                'current_record': 0
            }

        buffer_info = self.runtime.field_buffers[file_num]
        offset = 0

        # Process each field
        for width_expr, var_node in stmt.fields:
            width = int(self.evaluate_expression(width_expr))
            var_name = var_node.name + (var_node.type_suffix or '')

            # Store field mapping
            buffer_info['fields'][var_name] = (offset, width)
            offset += width

        # Initialize buffer to appropriate size
        buffer_info['buffer'] = bytearray(offset)

    def execute_get(self, stmt):
        """Execute GET statement - read record from random-access file

        Syntax:
            GET #n          - Read next record
            GET #n, record  - Read specific record number
        """
        file_num = int(self.evaluate_expression(stmt.file_number))

        if file_num not in self.runtime.files:
            raise RuntimeError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'R':
            raise RuntimeError(f"File #{file_num} not open for random access")

        if file_num not in self.runtime.field_buffers:
            raise RuntimeError(f"File #{file_num} has no FIELD defined")

        buffer_info = self.runtime.field_buffers[file_num]
        file_handle = file_info['handle']

        # Determine record number
        if stmt.record_number:
            record_num = int(self.evaluate_expression(stmt.record_number))
        else:
            # Use next record
            record_num = buffer_info['current_record'] + 1

        # Seek to record position (records are 1-based)
        record_size = len(buffer_info['buffer'])
        file_handle.seek((record_num - 1) * record_size)

        # Read data into buffer
        data = file_handle.read(record_size)
        if len(data) < record_size:
            # Pad with spaces if we read past EOF
            data += b' ' * (record_size - len(data))

        buffer_info['buffer'] = bytearray(data)
        buffer_info['current_record'] = record_num

        # Update field variables from buffer
        for var_name, (offset, width) in buffer_info['fields'].items():
            value = buffer_info['buffer'][offset:offset+width].decode('latin-1')
            # Strip variable name to get base name and suffix
            if var_name.endswith('$'):
                self.runtime.set_variable_raw(var_name, value)
            else:
                # For non-string fields (unusual but possible), convert to number
                try:
                    self.runtime.set_variable_raw(var_name, float(value.strip()))
                except ValueError:
                    self.runtime.set_variable_raw(var_name, 0.0)

    def execute_put(self, stmt):
        """Execute PUT statement - write record to random-access file

        Syntax:
            PUT #n          - Write to next record
            PUT #n, record  - Write to specific record number
        """
        file_num = int(self.evaluate_expression(stmt.file_number))

        if file_num not in self.runtime.files:
            raise RuntimeError(f"File #{file_num} not open")

        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'R':
            raise RuntimeError(f"File #{file_num} not open for random access")

        if file_num not in self.runtime.field_buffers:
            raise RuntimeError(f"File #{file_num} has no FIELD defined")

        buffer_info = self.runtime.field_buffers[file_num]
        file_handle = file_info['handle']

        # Determine record number
        if stmt.record_number:
            record_num = int(self.evaluate_expression(stmt.record_number))
        else:
            # Use next record
            record_num = buffer_info['current_record'] + 1

        # Seek to record position (records are 1-based)
        record_size = len(buffer_info['buffer'])
        file_handle.seek((record_num - 1) * record_size)

        # Write buffer to file
        file_handle.write(buffer_info['buffer'])
        file_handle.flush()

        buffer_info['current_record'] = record_num

    def execute_lset(self, stmt):
        """Execute LSET statement - left-justify string in field variable

        Syntax: LSET var$ = expr$

        Assigns value to a field variable, left-justified and padded with spaces.
        Used with random access files.
        """
        var_name = stmt.variable.name + (stmt.variable.type_suffix or '')
        value = str(self.evaluate_expression(stmt.expression))

        # Find which file buffer this variable belongs to
        found = False
        for file_num, buffer_info in self.runtime.field_buffers.items():
            if var_name in buffer_info['fields']:
                offset, width = buffer_info['fields'][var_name]

                # Left-justify and pad/truncate to width
                if len(value) < width:
                    value = value + ' ' * (width - len(value))
                else:
                    value = value[:width]

                # Update buffer
                buffer_info['buffer'][offset:offset+width] = value.encode('latin-1')

                # Also update variable
                self.runtime.set_variable_raw(var_name, value)
                found = True
                break

        if not found:
            # If not a field variable, fall back to normal assignment (no formatting applied).
            # Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field
            # variables (used with FIELD statement for random file access). This fallback
            # is a deliberate extension that performs simple assignment without left-justification.
            # The formatting only applies when used with FIELD variables.
            # Note: This extension behavior allows LSET/RSET to work as simple assignment
            # operators when not used with FIELD, which is intentional flexibility in this
            # implementation, not a bug or incomplete feature.
            self.runtime.set_variable_raw(var_name, value)

    def execute_rset(self, stmt):
        """Execute RSET statement - right-justify string in field variable

        Syntax: RSET var$ = expr$

        Assigns value to a field variable, right-justified and padded with spaces.
        Used with random access files.
        """
        var_name = stmt.variable.name + (stmt.variable.type_suffix or '')
        value = str(self.evaluate_expression(stmt.expression))

        # Find which file buffer this variable belongs to
        found = False
        for file_num, buffer_info in self.runtime.field_buffers.items():
            if var_name in buffer_info['fields']:
                offset, width = buffer_info['fields'][var_name]

                # Right-justify: pad on left if too short, truncate from left if too long
                if len(value) < width:
                    # Pad on left with spaces (right-justify)
                    value = ' ' * (width - len(value)) + value
                else:
                    # Truncate from left (keep rightmost characters)
                    value = value[-width:]

                # Update buffer
                buffer_info['buffer'][offset:offset+width] = value.encode('latin-1')

                # Also update variable
                self.runtime.set_variable_raw(var_name, value)
                found = True
                break

        if not found:
            # If not a field variable, fall back to normal assignment (no formatting applied).
            # Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field
            # variables (used with FIELD statement for random file access). This fallback
            # is a deliberate extension that performs simple assignment without right-justification.
            # The formatting only applies when used with FIELD variables. This is documented
            # behavior, not a bug.
            self.runtime.set_variable_raw(var_name, value)

    def execute_midassignment(self, stmt):
        """Execute MID$ assignment statement - replace substring in-place

        Syntax: MID$(string_var, start[, length]) = value
        - length is optional; if omitted, uses length of replacement value

        Replaces 'length' characters in string_var starting at position 'start' (1-based).
        - If value is shorter than length, only those characters are replaced
        - If value is longer than length, only 'length' characters are used
        - If start is out of bounds (< 1 or > string length), no replacement occurs
        - The string variable is modified in-place
        """
        # Evaluate the current value of the string variable
        current_value = self.evaluate_expression(stmt.string_var)
        if not isinstance(current_value, str):
            current_value = str(current_value)

        # Evaluate the parameters
        start = int(self.evaluate_expression(stmt.start))
        new_value = str(self.evaluate_expression(stmt.value))
        # Length is optional - if not provided, use length of replacement string
        length = int(self.evaluate_expression(stmt.length)) if stmt.length else len(new_value)

        # Convert to 0-based index
        start_idx = start - 1

        # Validate start position: must be 0 <= start_idx < len(current_value)
        # If out of bounds, no replacement is performed (MBASIC 5.21 behavior)
        if start_idx < 0 or start_idx >= len(current_value):
            return

        # Calculate how many characters to actually replace
        # min(length, len(new_value), available_space) where:
        #   length = requested replacement length (from MID$ stmt)
        #   len(new_value) = chars available in replacement string
        #   available_space = chars from start_idx to end of string (prevents overrun)
        chars_to_replace = min(length, len(new_value), len(current_value) - start_idx)

        # Build the new string
        # prefix: everything before start position
        # replacement: the first 'chars_to_replace' characters from new_value
        # suffix: everything after the replaced section
        prefix = current_value[:start_idx]
        replacement = new_value[:chars_to_replace]
        suffix = current_value[start_idx + chars_to_replace:]

        modified_value = prefix + replacement + suffix

        # Assign the modified string back to the variable
        # Handle both simple variables and array elements
        if isinstance(stmt.string_var, ast_nodes.VariableNode):
            var_node = stmt.string_var
            if var_node.subscripts:
                # Array element
                subscripts = [int(self.evaluate_expression(sub)) for sub in var_node.subscripts]
                self.runtime.set_array_element(
                    var_node.name,
                    var_node.type_suffix,
                    subscripts,
                    modified_value,
                    token=self._make_token_info(var_node)
                )
            else:
                # Simple variable
                self.runtime.set_variable(
                    var_node.name,
                    var_node.type_suffix,
                    modified_value,
                    token=self._make_token_info(var_node),
                    limits=self.limits
                )
        else:
            # If it's a more complex expression, we can't modify it in-place
            raise RuntimeError("MID$ assignment requires a variable, not an expression")

    def execute_list(self, stmt):
        """Execute LIST statement - output program lines.

        LIST           - List all lines
        LIST 100       - List line 100
        LIST 10-50     - List lines 10 through 50
        LIST 10-       - List lines 10 to end
        LIST -50       - List lines from beginning to 50

        Implementation note: Outputs from line_text_map (original source text), not regenerated from AST.
        This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager
        and should be kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE).
        If ProgramManager fails to maintain this sync, LIST output may show stale or incorrect line text.
        """
        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # Convert stmt to string args for cmd_list
            args = ""
            if stmt.start and stmt.end:
                start = int(self.evaluate_expression(stmt.start))
                end = int(self.evaluate_expression(stmt.end))
                args = f"{start}-{end}"
            elif stmt.start:
                start = int(self.evaluate_expression(stmt.start))
                if stmt.single_line:
                    args = f"{start}"
                else:
                    args = f"{start}-"
            elif stmt.end:
                end = int(self.evaluate_expression(stmt.end))
                args = f"-{end}"

            self.interactive_mode.cmd_list(args)
            return

        # Fallback: Evaluate start and end expressions
        start_line = None
        end_line = None

        if stmt.start:
            start_line = int(self.evaluate_expression(stmt.start))

        if stmt.end:
            end_line = int(self.evaluate_expression(stmt.end))

        # Get all line numbers from statement table (which comes from AST)
        all_line_nums = sorted(set(pc.line_num for pc in self.runtime.statement_table.statements.keys() if pc.line_num is not None))

        # Filter by range
        lines_to_list = []
        for line_num in all_line_nums:
            # Check start boundary
            if start_line is not None and line_num < start_line:
                continue
            # Check end boundary
            if end_line is not None and line_num > end_line:
                continue
            # Single line mode
            if stmt.single_line and start_line is not None and line_num != start_line:
                continue

            lines_to_list.append(line_num)

        # Output the lines
        for line_num in lines_to_list:
            # Get the line text from runtime.line_text_map
            if line_num in self.runtime.line_text_map:
                line_text = self.runtime.line_text_map[line_num]
                self.io.output(line_text)

    def execute_stop(self, stmt):
        """Execute STOP statement

        STOP pauses program execution and returns to interactive mode.
        All state is preserved:
        - Variables and arrays
        - GOSUB return stack
        - FOR loop stack
        - Current execution position

        User can examine/modify variables, edit lines, then use CONT to resume.
        """
        # Save the current execution position
        # We need to resume from the NEXT statement after STOP

        # Move NPC to PC so CONT can resume from the next statement
        # runtime.npc (next program counter) is set by tick() to point to the next statement
        # to execute after the current one completes
        if self.runtime.npc:
            self.runtime.pc = self.runtime.npc.stop("STOP")
        else:
            self.runtime.pc = self.runtime.pc.stop("STOP")

        # Print "Break in <line>" message
        if self.runtime.pc and self.runtime.pc.line_num:
            self.io.output(f"Break in {self.runtime.pc.line_num}")
        else:
            self.io.output("Break")

    def execute_tron(self, stmt):
        """Execute TRON statement - enable execution trace

        When trace is enabled, each line number is printed in square brackets
        as the line is executed. This is useful for debugging.
        """
        self.runtime.trace_on = True

    def execute_troff(self, stmt):
        """Execute TROFF statement - disable execution trace"""
        self.runtime.trace_on = False

    def execute_cls(self, stmt):
        """Execute CLS statement - clear screen (no-op)

        CLS is accepted for compatibility with programs that use it,
        but does not perform any action. Terminal clearing varies widely
        across platforms and would require complex terminal control logic.
        """
        # No-op - do nothing
        pass

    def execute_width(self, stmt):
        """Execute WIDTH statement - set output width (no-op)

        WIDTH is accepted for compatibility with programs that use it,
        but does not perform any action. Modern terminals handle line
        width automatically and WIDTH settings are not meaningful in
        a modern terminal context.
        """
        # No-op - do nothing
        pass

    def execute_cont(self, stmt):
        """Execute CONT statement

        CONT resumes execution after a STOP statement.
        Only works in interactive mode.

        Behavior (MBASIC 5.21 compatibility):
        Both STOP and Break (Ctrl+C) set PC stop_reason to "STOP" or "BREAK".
        The PC stop_reason allows CONT to resume from the saved position.

        PC handling difference:
        - STOP: execute_stop() (lines 2828-2831) sets PC via NPC.stop("STOP"),
          ensuring CONT resumes from the statement AFTER the STOP.
        - Break (Ctrl+C): BreakException handler (lines ~376-381) does NOT update PC,
          leaving PC pointing to the statement that was interrupted. This means CONT
          will re-execute the interrupted statement (typically INPUT where Break occurred).
        """
        if not hasattr(self, 'interactive_mode') or not self.interactive_mode:
            raise RuntimeError("CONT only available in interactive mode")

        if self.runtime.pc.is_running():
            raise RuntimeError("Can't continue - no program stopped")

        # Resume execution from where we stopped
        self.interactive_mode.cmd_cont()

    def execute_step(self, stmt):
        """Execute STEP statement (debug command) - NOT IMPLEMENTED

        STEP is intended to execute one or more statements, then pause.

        CURRENT STATUS: This method outputs an informational message but does NOT
        actually perform stepping. It's a stub that acknowledges the command but
        doesn't execute the intended behavior.

        Note: The tick_pc() method has working step infrastructure (modes 'step_statement'
        and 'step_line') that is used by UI debuggers. This STEP command (for typing
        "STEP" in immediate mode) would need to be connected to that infrastructure
        by setting a runtime flag and coordinating with the UI's tick loop, but this
        integration does not currently exist.

        UIs should use tick_pc(mode='step_statement') directly for debugging, not this
        STEP command which is for interactive use in immediate mode.
        """
        count = stmt.count if stmt.count else 1
        self.io.output(f"STEP {count} - Debug stepping not fully implemented")

    # ========================================================================
    # Expression Evaluation
    # ========================================================================

    def evaluate_expression(self, expr):
        """Evaluate an expression node"""
        expr_type = type(expr).__name__

        handler_name = f"evaluate_{expr_type.replace('Node', '').lower()}"
        handler = getattr(self, handler_name, None)

        if handler:
            return handler(expr)
        else:
            raise NotImplementedError(f"Expression not implemented: {expr_type}")

    def evaluate_number(self, expr):
        """Evaluate number literal"""
        return expr.value

    def evaluate_string(self, expr):
        """Evaluate string literal"""
        return expr.value

    def evaluate_variable(self, expr):
        """Evaluate variable reference"""
        if expr.subscripts:
            # Array access - track access
            subscripts = [int(self.evaluate_expression(sub)) for sub in expr.subscripts]
            return self.runtime.get_array_element(expr.name, expr.type_suffix, subscripts, token=self._make_token_info(expr))
        else:
            # Simple variable
            return self.runtime.get_variable(
                expr.name,
                expr.type_suffix,
                token=self._make_token_info(expr),
                original_case=getattr(expr, 'original_case', expr.name),
                settings_manager=self.settings_manager
            )

    def evaluate_binaryop(self, expr):
        """Evaluate binary operation"""
        left = self.evaluate_expression(expr.left)
        right = self.evaluate_expression(expr.right)

        op = expr.operator

        # Arithmetic
        if op == TokenType.PLUS:
            result = left + right
            # Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)
            # Note: This check only applies to concatenation via PLUS operator.
            # Other string operations (MID$, INPUT) and LSET/RSET do not enforce this limit.
            if isinstance(result, str) and len(result) > 255:
                raise RuntimeError("String too long")
            return result
        elif op == TokenType.MINUS:
            return left - right
        elif op == TokenType.MULTIPLY:
            return left * right
        elif op == TokenType.DIVIDE:
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif op == TokenType.BACKSLASH:  # Integer division
            if right == 0:
                raise RuntimeError("Division by zero")
            return int(left // right)
        elif op == TokenType.POWER:
            return left ** right
        elif op == TokenType.MOD:
            return left % right

        # Relational
        elif op == TokenType.EQUAL:
            return -1 if left == right else 0
        elif op == TokenType.NOT_EQUAL:
            return -1 if left != right else 0
        elif op == TokenType.LESS_THAN:
            return -1 if left < right else 0
        elif op == TokenType.GREATER_THAN:
            return -1 if left > right else 0
        elif op == TokenType.LESS_EQUAL:
            return -1 if left <= right else 0
        elif op == TokenType.GREATER_EQUAL:
            return -1 if left >= right else 0

        # Logical (bitwise in BASIC)
        elif op == TokenType.AND:
            return int(left) & int(right)
        elif op == TokenType.OR:
            return int(left) | int(right)
        elif op == TokenType.XOR:
            return int(left) ^ int(right)
        elif op == TokenType.EQV:
            # Logical equivalence: A EQV B = NOT (A XOR B)
            # In BASIC: -1 = TRUE, 0 = FALSE
            # Bitwise: invert XOR result
            return ~(int(left) ^ int(right))
        elif op == TokenType.IMP:
            # Logical implication: A IMP B = (NOT A) OR B
            # In BASIC: -1 = TRUE, 0 = FALSE
            # Bitwise: (~A) | B
            return (~int(left)) | int(right)

        else:
            raise NotImplementedError(f"Binary operator not implemented: {op}")

    def evaluate_unaryop(self, expr):
        """Evaluate unary operation"""
        operand = self.evaluate_expression(expr.operand)

        if expr.operator == TokenType.MINUS:
            return -operand
        elif expr.operator == TokenType.NOT:
            return ~int(operand)
        elif expr.operator == TokenType.PLUS:
            return operand
        else:
            raise NotImplementedError(f"Unary operator not implemented: {expr.operator}")

    def evaluate_builtinfunction(self, expr):
        """Evaluate built-in function call"""
        # Get function name
        func_name = expr.name

        # Evaluate arguments
        args = [self.evaluate_expression(arg) for arg in expr.arguments]

        # Call builtin function
        func = getattr(self.builtins, func_name, None)
        if not func:
            raise RuntimeError(f"Unknown function: {func_name}")

        return func(*args)

    def evaluate_functioncall(self, expr):
        """Evaluate function call (built-in or user-defined)"""
        # First, check if it's a built-in function
        # Strip $ suffix for builtin lookup (CHR$ -> CHR, INPUT$ -> INPUT, etc.)
        func_name = expr.name.rstrip('$')
        func = getattr(self.builtins, func_name, None)
        if func:
            # It's a builtin function
            args = [self.evaluate_expression(arg) for arg in expr.arguments]
            return func(*args)

        # Not a builtin, check for user-defined function
        func_def = self.runtime.user_functions.get(expr.name)
        if not func_def:
            raise RuntimeError(f"Undefined function: {expr.name}")

        # Evaluate arguments
        args = [self.evaluate_expression(arg) for arg in expr.arguments]

        # Create token info from function call expression
        call_token = self._make_token_info(expr)

        # Save parameter values (function parameters shadow variables)
        # Note: get_variable_for_debugger() and debugger_set=True are used to avoid
        # triggering variable access tracking. This save/restore is internal function
        # call machinery, not user-visible variable access. The tracking system
        # (if enabled) should distinguish between:
        # - User code variable access (tracked for debugging/variables window)
        # - Internal implementation details (not tracked)
        # Maintainer warning: Ensure all internal variable operations use debugger_set=True
        saved_vars = {}
        for i, param in enumerate(func_def.parameters):
            param_name = param.name + (param.type_suffix or "")
            saved_vars[param_name] = self.runtime.get_variable_for_debugger(param.name, param.type_suffix)
            if i < len(args):
                # Set parameter to argument value - this is part of function call
                # Use debugger_set=True to avoid tracking this internal variable operation
                self.runtime.set_variable(param.name, param.type_suffix, args[i], token=call_token, limits=self.limits, debugger_set=True)

        # Evaluate function expression
        result = self.evaluate_expression(func_def.expression)

        # Restore parameter values (use debugger_set=True to avoid tracking)
        for param_name, saved_value in saved_vars.items():
            base_name = param_name.rstrip('$%!#')
            type_suffix = param_name[-1] if param_name[-1] in '$%!#' else None
            self.runtime.set_variable(base_name, type_suffix, saved_value, debugger_set=True)

        return result

    # ========================================================================
    # Settings Commands
    # ========================================================================

    def execute_setsetting(self, stmt):
        """Execute SET setting command

        Syntax: SET "setting.name" value
        """
        from src.settings import get_settings_manager, SettingScope
        from src.settings_definitions import get_definition, validate_value

        # Evaluate value expression
        value = self.evaluate_expression(stmt.value)

        # Get setting definition
        definition = get_definition(stmt.setting_name)
        if not definition:
            self.io.output(f"?Unknown setting: {stmt.setting_name}")
            return

        # Convert value based on definition type
        from src.settings_definitions import SettingType
        if definition.type == SettingType.BOOLEAN:
            # Accept 0/1, "true"/"false", "yes"/"no"
            if isinstance(value, (int, float)):
                value = bool(value)
            elif isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ('true', 'yes', '1'):
                    value = True
                elif value_lower in ('false', 'no', '0'):
                    value = False
                else:
                    self.io.output(f"?Invalid boolean value: {value}")
                    return
        elif definition.type == SettingType.INTEGER:
            value = int(value)
        elif definition.type == SettingType.STRING:
            value = str(value)
        elif definition.type == SettingType.ENUM:
            value = str(value)

        # Validate value
        if not validate_value(stmt.setting_name, value):
            self.io.output(f"?Invalid value for {stmt.setting_name}: {value}")
            if definition.choices:
                self.io.output(f"  Valid choices: {', '.join(str(c) for c in definition.choices)}")
            return

        # Set and save setting
        try:
            settings_mgr = get_settings_manager()
            settings_mgr.set(stmt.setting_name, value, scope=SettingScope.GLOBAL)
            settings_mgr.save(scope=SettingScope.GLOBAL)
            self.io.output(f"Setting '{stmt.setting_name}' = {value}")
        except Exception as e:
            self.io.output(f"?Error setting {stmt.setting_name}: {e}")

    def execute_showsettings(self, stmt):
        """Execute SHOW SETTINGS command

        Syntax: SHOW SETTINGS ["pattern"]
        """
        from src.settings import get_settings_manager

        settings_mgr = get_settings_manager()
        all_settings = settings_mgr.get_all_settings()

        # Filter by pattern if provided
        if stmt.pattern:
            pattern = stmt.pattern.lower()
            filtered = {k: v for k, v in all_settings.items() if pattern in k.lower()}
        else:
            filtered = all_settings

        if not filtered:
            if stmt.pattern:
                self.io.output(f"No settings matching '{stmt.pattern}'")
            else:
                self.io.output("No settings configured")
            return

        # Group by category
        categories = {}
        for key, value in sorted(filtered.items()):
            parts = key.split('.', 1)
            category = parts[0] if len(parts) > 1 else 'General'
            if category not in categories:
                categories[category] = []
            categories[category].append((key, value))

        # Display settings by category
        for category in sorted(categories.keys()):
            self.io.output(f"\n{category}:")
            for key, value in categories[category]:
                self.io.output(f"  {key} = {value}")

    def execute_helpsetting(self, stmt):
        """Execute HELP SET command

        Syntax: HELP SET "setting.name"
        """
        from src.settings_definitions import get_definition

        definition = get_definition(stmt.setting_name)
        if not definition:
            self.io.output(f"?Unknown setting: {stmt.setting_name}")
            return

        # Display setting information
        self.io.output(f"\n{stmt.setting_name}")
        self.io.output(f"  Type: {definition.type.value}")
        self.io.output(f"  Default: {definition.default}")

        if definition.choices:
            self.io.output(f"  Choices: {', '.join(str(c) for c in definition.choices)}")

        if definition.min_value is not None:
            self.io.output(f"  Min: {definition.min_value}")
        if definition.max_value is not None:
            self.io.output(f"  Max: {definition.max_value}")

        self.io.output(f"\n  {definition.description}")

        if definition.help_text:
            self.io.output(f"\n{definition.help_text}")
