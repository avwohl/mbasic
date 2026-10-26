"""
MBASIC 5.21 Interpreter

Executes BASIC programs from AST.
"""

import copy
import itertools
import re
import sys
import signal
from dataclasses import dataclass, field
from typing import Literal, Optional, Callable, Any, Union
from src.runtime import Runtime, ProgramString, FREE_MEMORY, HIGHEST_MEMORY, STACK_SPACE, MIN_STACK_SPACE
from src.js_type_check import builtin_arg_kinds
from src.deftypes import name_with_suffix
from src.ast_nodes import StringNode, FunctionCallNode, arity_type_checks, BUILTIN_ARG_RANGES, instr_shape_error, clause_tail_after, clause_slice, parameter_suffix
from src.basic_builtins import BuiltinFunctions, TabMarker, SpcMarker, UsingFormatter
from src.tokens import TokenType
from src.pc import PC
from src.win_console import win_flush_pending
from src.number_format import (format_for_print, format_number, int_divide, int_modulo,
                               numeric_digits,
                               MBF_INFINITY_SINGLE, to_int_operand, to_subscript, to_conint, to_frcint,
                               exceeds_range, machine_infinity, radix_word,
                               SINGLE_LIMIT, DOUBLE_MAX,
                               to_integer, to_single, coerce_to_type,
                               INTEGER_DIGITS, SINGLE_DIGITS, DOUBLE_DIGITS)
from src.iohandler.base import KeyInputPending
from src.print_column import (SCREEN_WIDTH, FILE_WIDTH, advance_column, wrap_text,
                              tab_target, comma_step, spc_count,
                              screen_wrap_width, INFINITE)
from src.error_codes import (error_code_for, format_error_message,
                             get_error_message)
from src.input_fields import (split_keyboard_fields, keyboard_number, val_number,
                              read_file_field, val_text, MAX_FLOAT)
import src.ast_nodes as ast_nodes
from src.cpm_names import cpm_name_error, cpm_new_name_error
from src.string_temps import string_temps, STRING_TEMPORARIES


def _while_wend_walk(statement):
    """Every WHILE and WEND in a statement, including inside THEN/ELSE clauses.

    Yields (node, nested). Same reasoning as _for_next_walk: a clause has no PC
    of its own, but it still counts towards the nesting.
    """
    if isinstance(statement, (ast_nodes.WhileStatementNode, ast_nodes.WendStatementNode)):
        yield statement, False
        return
    if isinstance(statement, ast_nodes.IfStatementNode):
        for clause in (statement.then_statements, statement.else_statements):
            for inner in clause or ():
                for node, _ in _while_wend_walk(inner):
                    yield node, True


def _for_next_walk(statement):
    """Every FOR and NEXT in a statement, including inside THEN/ELSE clauses.

    Yields (node, nested). A clause is not addressable by PC - the statement
    table holds one entry for the whole IF - but it still counts towards the
    nesting, and missing that was fatal:

        0 PRINT "...":FOR I=-32767 TO 32767:X$=INKEY$:IF LEN(X$)=1 THEN GOTO 1 ELSE NEXT I

    is how basic/utilities/million.bas waits for a keypress. Counting only
    top-level statements found no NEXT at all and called it "FOR Without NEXT".
    """
    if isinstance(statement, (ast_nodes.ForStatementNode, ast_nodes.NextStatementNode)):
        yield statement, False
        return
    if isinstance(statement, ast_nodes.IfStatementNode):
        for clause in (statement.then_statements, statement.else_statements):
            for inner in clause or ():
                for node, _ in _for_next_walk(inner):
                    yield node, True

_DATA_DECIMAL = re.compile(r'(\d*\.?\d*)(?:[EeDd]([+-]?\d*))?[%!#]?\Z')


def data_text_to_number(text):
    """Read the text of an unquoted DATA item the way READ into a number variable does.

    Measured on the binary: leading spaces, a sign with spaces behind it, spaces
    inside the digits ("1 2" is 12), a lone "1E" or "&H" or "-" (value 0 or 1),
    a type suffix at the end, and &H / &O / & digits.  Returns the number.
    Raises ValueError("data") for text that is a Syntax error reported at the
    DATA line, and ValueError("read") for &O8 and &9, which the binary reports
    at the READ line.  A hex or octal value over 65535 raises OverflowError.
    """
    s = text.strip(' \t')
    negative = False
    if s[:1] in ('+', '-'):
        negative = s[0] == '-'
        s = s[1:].lstrip(' ')
        if s[:1] in ('+', '-', '&'):
            raise ValueError("data")
    if s[:1] == '&':
        body = s[1:]
        radix = 16 if body[:1] in ('H', 'h') else 8
        if body[:1] in ('H', 'h'):
            body = body[1:]
        else:
            if body[:1] in ('O', 'o'):
                body = body[1:]
            body = body.lstrip(' ')
        digits = '0123456789ABCDEFabcdef' if radix == 16 else '01234567'
        end = 0
        while end < len(body) and body[end] in digits:
            end += 1
        if end < len(body):
            if radix == 8 and body[end] in '89':
                raise ValueError("read")
            raise ValueError("data")
        value = int(body[:end], radix) if end else 0
        if value > 65535:
            raise OverflowError
        return value - 65536 if value > 32767 else value
    s = s.replace(' ', '')
    m = _DATA_DECIMAL.match(s)
    if not m:
        raise ValueError("data")
    mantissa = m.group(1)
    exponent = m.group(2)
    value = float((mantissa if mantissa not in ('', '.') else '0') +
                  ('e' + (exponent if exponent not in ('', '+', '-') else '0') if exponent is not None else ''))
    return -value if negative else value


class MBasicError(RuntimeError):
    """An error raised as an MBASIC error *number* rather than as a message.

    ERROR n needs to report code n whatever the wording, so it carries the code
    and lets error_code_for() read it straight off.
    """

    def __init__(self, code, error_pc=None):
        super().__init__(get_error_message(code)[1])
        self.mbasic_code = code
        # Where to report the error, when that is not the statement that
        # raised it (ON ERROR GOTO 0 in a handler reports the original line).
        self.error_pc = error_pc


MAX_FILE_NUMBER = 15      # the binary started with /F:15; with the default /F:3 only 1 to 3 are files


def _loop_is_done(current, end, step):
    """Whether a FOR loop has passed its limit.

    MBASIC's test (FINNXT in bimisc.mac) compares the control variable with the
    limit and subtracts the sign of the step: the loop ends when
    sign(current - end) equals sign(step). Written as two inequalities the
    zero-step case falls through the gap - sign(0) is 0, so a STEP 0 loop only
    ends when it lands exactly on the limit, which is why FOR I = 1 TO 0 STEP 0
    runs for ever on the real binary and FOR I = 5 TO 5 STEP 0 does not run
    at all.
    """
    return ((current > end) - (current < end)) == ((step > 0) - (step < 0))

#: The record length OPEN gives a random file, and the most it allows: one CP/M sector.
DEFAULT_RECORD_LENGTH = 128

#: Marker for "this node has not been typed yet" - None is a real answer
#: (INTEGER_DIGITS), so it cannot stand for the missing value.
_UNCACHED = object()

# The operators a pair of strings may use: concatenation and comparison.
_STRING_BINARY_OPS = frozenset((
    TokenType.PLUS, TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
    TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL))


class BreakException(Exception):
    """Raised when user presses Ctrl+C to break execution"""
    pass


class ChainException(Exception):
    """Raised by CHAIN to signal program change - caught by run() to restart execution"""
    pass


@dataclass
class ErrorInfo:
    """Information about a runtime error.

    error_message is the Python exception's own text, kept for the debug log.
    It is not what a user should be shown - see message().
    """
    error_code: int
    pc: PC
    error_message: str
    report_pc: Optional[PC] = None   # where the error is reported, when not at pc (READ: the DATA line)

    def message(self, with_line=True):
        """The line MBASIC prints for this error.

        Every UI had been showing error_message, which is the Python
        exception's wording: "Cannot open NOSUCH.DAT: Cannot open
        NOSUCH.DAT: No such file or directory" where the binary says
        "File not found in 50". Six backends each spelled that badly in their
        own way, so the rendering lives here instead.

        Pass with_line=False where the surface already shows the line number
        separately - the curses UI's error box does.
        """
        return format_error_message(
            self.error_code, self.pc.line_num if with_line else None)


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
    #: True when the program is paused inside INPUT$/INKEY$ because the I/O
    #: handler cannot answer without blocking - see KeyInputPending. The UI
    #: stops ticking and starts again when a key arrives; the statement is
    #: re-executed, which is why nothing may be consumed on the way out.
    waiting_for_key: bool = False
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
    # error_info is a FATAL error: one no handler took. Every UI and the run
    # loops read it as "the program failed", so it stays None while a handler
    # runs. The error a handler is working on is pending_error; it holds what
    # RESUME needs, and the binary's "in a handler" flag (ONEFLG) is whether
    # it is set. Only RESUME clears it - not GOTO, and not END's effect on the
    # report: END ends the program and clears it.
    error_info: Optional[ErrorInfo] = None
    pending_error: Optional[ErrorInfo] = None
    pending_error_tail: Optional[list] = None   # clause statements behind the error
    pending_error_rerun: Optional[list] = None  # clause statements RESUME runs again

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

        # Set by a zero-trip FOR for the NEXT it jumps to, and cleared there:
        # which name in that NEXT to enter at, and a signal to skip the
        # increment. See execute_for.
        self._for_entry_index = None
        # A FOR inside a THEN or ELSE clause has no PC for its body, so the
        # clause executor loops it (see execute_clause_statements).
        self._clause_stack = []         # [statements, index] of running clauses
        self._clause_jump = None        # (statements, index) a NEXT goes back to
        self._clause_for = {}           # loop variable -> (statements, FOR index)
        # (line, ERL) after a RESUME whose error was reported at another line: the binary's
        # current line is then ERL until a new line starts, so errors there report ERL
        self._sticky_erl = None

        # I/O handler (defaults to console if not provided)
        if io_handler is None:
            from src.iohandler.console import ConsoleIOHandler
            io_handler = ConsoleIOHandler(debug_enabled=False)
        self.io = io_handler
        # A run starts at the left margin: MBASIC puts "Ok" on a new line
        # after a program that stopped in the middle of one.
        self._screen_line_ended()

        # INKEY$ and INPUT$ read the keyboard through the handler, so they are
        # given a way to reach it. A lambda rather than the handler itself
        # because the curses UI assigns interpreter.io after construction
        # (src/ui/curses_ui.py), and a builtin holding the handler it was built
        # with would go on reading the one being replaced.
        self.builtins = BuiltinFunctions(runtime, io_provider=lambda: self.io)

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

        # Undo record for a statement that has to be retried after pausing for
        # a key. Built on first use and reused, since it is touched once per
        # statement on the one backend that needs it.
        self._statement_attempt = None

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

        # Arming twice must not save our own handler as the "old" one, or the
        # REPL's handler could never be restored.
        if getattr(self, '_break_handler_armed', False):
            return
        # Save old handler to restore later
        self.old_signal_handler = signal.signal(signal.SIGINT, signal_handler)
        self._break_handler_armed = True

    def _restore_break_handler(self):
        """Restore original Ctrl+C handler"""
        if getattr(self, '_break_handler_armed', False):
            signal.signal(signal.SIGINT, self.old_signal_handler)
            self._break_handler_armed = False

    def arm_break_handler(self):
        """Make Ctrl+C set the break flag while a resumed program runs (CONT).

        start() does this for RUN. A caller that resumes the PC itself must
        call this before its tick loop; the tick loop restores the handler at
        every stop.
        """
        self._setup_break_handler()

    def release_break_handler(self):
        """Give Ctrl+C back to the REPL. Safe to call when the handler is not armed."""
        self._restore_break_handler()

    def read_input_line(self):
        """Read the answer to a keyboard INPUT for the CLI.

        The break handler only sets a flag, which a blocking read never looks
        at, so the handler is released around the read and Ctrl+C raises
        KeyboardInterrupt there. The caller then calls break_at_input().
        A Ctrl+C that arrived before the read counts as one during it.
        """
        from src.iohandler.console import input_without_history
        if self.runtime.break_requested:
            self.runtime.break_requested = False
            raise KeyboardInterrupt
        self._restore_break_handler()
        try:
            # Program INPUT answers are data, not commands - they must not
            # land in the readline history.
            return input_without_history()
        finally:
            self._setup_break_handler()

    def break_at_input(self):
        """Stop the program at the INPUT that Ctrl+C interrupted.

        MBASIC prints "Break in <line>" at once and CONT asks for the answer
        again: the PC stays on the INPUT statement, so the next tick runs it
        again and prints the prompt again.
        """
        pc = self.runtime.pc
        self.state.input_prompt = None
        self.runtime.pc = pc.stop("BREAK")
        self._restore_break_handler()
        self.io.output("")
        self.io.output(f"Break in {pc.line_num}")

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
            # Drop any half-delivered keystroke left by the previous program.
            # On Windows a special key expands to several characters and INKEY$
            # hands back one per call, so a program that stops mid-sequence
            # would otherwise leak the remainder into this one. No-op elsewhere.
            win_flush_pending()

            # Setup runtime tables
            self.runtime.setup()

            # Initialize state
            self.state = InterpreterState(_interpreter=self)
            # CHAIN with a starting line: begin there instead of at the first line
            chain_start = getattr(self.runtime, 'chain_start_line', None)
            if chain_start is not None:
                self.runtime.chain_start_line = None
                self.runtime.pc = PC.from_line(chain_start)
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
                    self._restore_break_handler()       # see the arm below
                    self.io.output("")
                    # pc.line_num, not pc: MBASIC reports "Break in 30", and
                    # str(PC) is a debugging repr - this printed the literal
                    # text "Break in PC(30.0)". STOP already gets this right
                    # (see execute_stop).
                    self.io.output(f"Break in {pc.line_num}")
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

                # Trace output. MBASIC prints the line number as it *enters* a
                # line, with no newline of its own, so a traced program reads
                #
                #     [130][140][150][160]Result: 50
                #
                # and not one bracket per line. Entering the line is the whole
                # test: a RETURN that lands back in the middle of 440 does not
                # re-print [440], a NEXT that jumps back to the PRINT in
                # "370 FOR I=1 TO 3 : PRINT I; : NEXT I" does not re-print
                # [370], and "490 TRON : X = 100 : TROFF" prints nothing at all
                # because the trace was off when 490 started.
                if self.runtime.trace_on:
                    if self.runtime.trace_detail == 'statement':
                        # Statement-level trace: show [10.0], [10.1], [10.2].
                        # Ours, not MBASIC's - the debugger uses it.
                        self.io.output(f"[{pc}]", end='')
                    elif pc.stmt_offset == 0:
                        self.io.output(f"[{pc.line_num}]", end='')

                # Get statement
                stmt = self.runtime.statement_table.get(pc)
                if stmt is None:
                    raise RuntimeError(f"Invalid PC: {pc}")

                # About to run a statement, so any earlier "waiting for a key"
                # is over: either the key arrived or the UI gave up on it.
                self.state.waiting_for_key = False

                # A statement that pauses for a key runs again from the start,
                # so the keys it read have to be given back first - a
                # statement can read more than once, and the second read is
                # what pauses. Only handlers that defer pay for this; a
                # terminal blocks instead of raising and could not put a
                # keystroke back anyway.
                deferring = getattr(self.io, 'defers_key_reads', False)
                if deferring:
                    self.io.begin_key_transaction()
                    # RND and INPUT$(n,#f) record into this what they change,
                    # so an abandoned attempt does not leave the generator
                    # advanced or a file read past. Reused rather than rebuilt
                    # per statement.
                    if self._statement_attempt is None:
                        from src.statement_attempt import StatementAttempt
                        self._statement_attempt = StatementAttempt()
                    else:
                        self._statement_attempt.reset()
                    self.runtime.statement_attempt = self._statement_attempt

                # Execute statement
                try:
                    import sys
                    if mode in ('step_statement', 'step_line'):
                        print(f"DEBUG tick: Executing statement at {pc}: {type(stmt).__name__}", file=sys.stderr)
                    self.execute_statement(stmt)
                    statements_in_tick += 1
                    self.state.statements_executed += 1
                    if deferring:
                        # Finished: what it changed, it meant to change.
                        self.runtime.statement_attempt = None

                except KeyInputPending:
                    # INKEY$/INPUT$ on a handler that cannot wait without
                    # deadlocking - the web UI, whose keys arrive on the same
                    # asyncio loop that runs this. Leave the PC exactly where
                    # it is: when the UI ticks again the statement runs from
                    # the start, and by then a key is queued.
                    if deferring:
                        self.io.rollback_key_transaction()
                        self._statement_attempt.rollback(self.runtime)
                        self.runtime.statement_attempt = None
                    self.state.waiting_for_key = True
                    return self.state

                except BreakException:
                    # A break is the user's decision, not a retry: what the
                    # statement changed stands, and CONT re-runs it as it
                    # always has.
                    self.runtime.statement_attempt = None
                    # Ctrl+C during INPUT$. Nothing raised this until INPUT$
                    # started reading in raw mode, where ISIG is off and the
                    # 0x03 byte is delivered to the reader instead of becoming
                    # a SIGINT - so this arm had never actually run, and its
                    # message would have printed "Break in PC(30.0)".
                    self.runtime.pc = pc.stop("BREAK")
                    # Without this the interpreter's own SIGINT handler stays
                    # installed after the program stops, and since all it does
                    # is set break_requested, the REPL's Ctrl+C - including
                    # three-presses-to-quit - is dead for the rest of the
                    # session. Every other exit from this loop restores it.
                    self._restore_break_handler()
                    # Raw mode does not echo the ^C, and the program may have
                    # left the cursor mid-line with a trailing-semicolon PRINT.
                    self.io.output("")
                    self.io.output(f"Break in {pc.line_num}")
                    return self.state

                except Exception as e:
                    self.runtime.statement_attempt = None
                    # Check if we're already in an error handler (prevent recursive errors)
                    already_in_error_handler = (self.state.pending_error is not None)

                    error_code = self._map_exception_to_error_code(e)
                    # ON ERROR GOTO 0 in a handler raises the error the handler
                    # is working on again, and it is reported where it began.
                    # (pc is the statement RESUME NEXT is running when it
                    # re-runs the rest of a clause: stmt_pc is the IF.)
                    pc = getattr(e, 'stmt_pc', None) or pc
                    error_pc = getattr(e, 'error_pc', None) or pc
                    if (getattr(e, 'error_pc', None) is None and self._sticky_erl is not None
                            and self._sticky_erl[0] == pc.line_num):
                        error_pc = PC.running_at(self._sticky_erl[1], pc.stmt_offset)
                    info = ErrorInfo(
                        error_code=error_code,
                        pc=error_pc,
                        error_message=str(e)
                    )

                    # Check if we have an error handler and not already handling an error
                    if self.runtime.has_error_handler() and not already_in_error_handler:
                        # The handler works on this error: RESUME needs it, but
                        # it is not a failure of the program yet (error_info).
                        # RESUME goes back to the statement that ran; ERL is the line
                        # the error is reported at (READ of a bad DATA item: the DATA line).
                        self.state.pending_error = ErrorInfo(
                            error_code=error_code, pc=pc, error_message=str(e),
                            report_pc=error_pc)
                        if (not hasattr(e, 'clause_tail')
                                and type(stmt).__name__ == 'IfStatementNode'):
                            # an error in the condition, or in the first
                            # statement of a clause (see clause_tail_after)
                            e.clause_tail = clause_tail_after(stmt, None, 0)
                        self.state.pending_error_rerun = getattr(e, 'clause_rerun', None)
                        self.state.pending_error_tail = getattr(e, 'clause_tail', None)
                        self._invoke_error_handler(error_code, pc, error_pc)
                        # Error handler set npc - apply it and continue execution
                        # (don't use continue here - we need to let normal flow handle NPC)
                        statements_in_tick += 1
                        self.state.statements_executed += 1
                        # Fall through to NPC handling below
                    else:
                        # No error handler (or an error inside a handler, which
                        # the binary does not trap) - fatal
                        self._fatal_error(info)
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

                # Running off the end of the program inside a handler (before
                # any RESUME) is "No RESUME", reported at the last line that ran.
                if (self.state.pending_error is not None
                        and not next_pc.is_running()
                        and self.runtime.pc.is_running()):
                    exc = MBasicError(19)
                    self._fatal_error(ErrorInfo(
                        error_code=19, pc=pc, error_message=str(exc)))
                    raise exc

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
                if self._sticky_erl is not None and (
                        not next_pc.is_running() or next_pc.line_num != self._sticky_erl[0]):
                    self._sticky_erl = None     # a new line starts

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
                    raise MBasicError(state.error_info.error_code)

                # Run until done
                while self.runtime.pc.is_running() and not state.error_info:
                    state = self.tick(mode='run', max_statements=10000)

                    # Handle input synchronously for CLI
                    if state.input_prompt is not None:
                        # Synchronous input for CLI
                        try:
                            value = self.read_input_line()
                            state = self.provide_input(value)
                        except KeyboardInterrupt:
                            # User pressed Ctrl+C during input
                            self.break_at_input()
                            return
                        except EOFError:
                            self.io.output("")
                            return

                # Handle final errors
                if state.error_info:
                    raise MBasicError(state.error_info.error_code)

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
        """The MBASIC error number for a Python exception.

        This used to be a second, looser copy of the same guesswork that the
        reporter does, and the two disagreed: the printed message came out
        right while ERR read 5 for a dozen errors that have codes of their own.
        Both now go through src/error_codes.py.
        """
        return error_code_for(exception)

    def _fatal_error(self, info):
        """Make info the program's fatal error: stop the PC on it and report.

        The caller re-raises the exception; print_error then reads the line
        from the PC set here.
        """
        self.state.pending_error = None
        self.state.error_info = info
        self.runtime.pc = info.pc.with_error(
            info.error_code,
            info.error_message,
            self.runtime.error_handler if self.runtime.has_error_handler() else None
        )
        self._restore_break_handler()
        # The binary starts a new line before a fatal error
        # message when the cursor is not in column 0.
        if self._output_column(None) > 0:
            self.io.output('')

    def _invoke_error_handler(self, error_code, error_pc, report_pc=None):
        """Invoke the error handler"""
        # Note: error_info is always set in the exception handler in tick_pc() when an error
        # occurs (line 385), regardless of whether an error handler exists. This method is
        # only called if a handler exists (checked at line 392), so we're now ready to invoke it.

        # Set ERR%, ERL%, and ERS% system variables
        self.runtime.set_variable_raw('err%', error_code)
        self.runtime.set_variable_raw('erl%', (report_pc or error_pc).line_num)
        self.runtime.set_variable_raw('ers%', error_pc.stmt_offset)

        # Jump to error handler
        if self.runtime.error_handler_is_gosub:
            # ON ERROR GOSUB - push return address (next statement after error)
            next_pc = self.runtime.statement_table.next_pc(error_pc)
            if next_pc.is_running():
                self.runtime.push_gosub(next_pc.line_num, next_pc.stmt_offset)

        # Jump to error handler line
        self.runtime.npc = PC.from_line(self.runtime.error_handler)

    def find_matching_next(self, start_line, start_stmt, tail=None):
        """Find the NEXT that closes a FOR, the way MBASIC's NXTSCN does.

        The scan is a pure nesting count and never looks at variable names:
        every FOR pushes the count up by one and every *variable* on a NEXT
        brings it down by one, so "NEXT J,I" closes two loops. That is how
        MBASIC decides where a loop ends - by counting, not by matching names,
        which is why the name on the NEXT it lands on can turn out to be the
        wrong one and be rejected there.

        Returns:
            (line_number, stmt_index, variable_index, nested, node) of the
            matching NEXT (node is its statement), or None. variable_index is which name in a "NEXT J,I" it was
            that brought the count to zero - the scan stops on that one, and it
            is the one the loop is entered through. `nested` is True when the
            NEXT is inside a THEN or ELSE clause, where it has no PC of its own
            and stmt_index addresses the IF that contains it.
        """
        depth = 1

        # A FOR inside a clause: the rest of that clause comes first. A match
        # there has no line (None) and its index is counted in tail.
        for tail_idx, tail_stmt in enumerate(tail or ()):
            for stmt, nested in _for_next_walk(tail_stmt):
                if isinstance(stmt, ast_nodes.ForStatementNode):
                    depth += 1
                    continue
                names = max(1, len(stmt.variables or []))
                if depth <= names:
                    return (None, tail_idx, depth - 1, nested, stmt)
                depth -= names

        line_numbers = sorted(set(pc.line_num
                                  for pc in self.runtime.statement_table.statements.keys()))
        try:
            line_idx = line_numbers.index(start_line)
        except ValueError:
            return None

        stmt_idx = start_stmt + 1

        while line_idx < len(line_numbers):
            line_num = line_numbers[line_idx]
            line_statements = self.runtime.statement_table.get_line_statements(line_num)

            while stmt_idx < len(line_statements):
                for stmt, nested in _for_next_walk(line_statements[stmt_idx]):
                    if isinstance(stmt, ast_nodes.ForStatementNode):
                        depth += 1
                        continue
                    # A bare NEXT closes exactly one loop; NEXT I,J closes two.
                    # DECNXT counts them down one at a time and returns the
                    # moment the count reaches zero, so a NEXT can be entered
                    # part way along its own list.
                    names = max(1, len(stmt.variables or []))
                    if depth <= names:
                        return (line_num, stmt_idx, depth - 1, nested, stmt)
                    depth -= names

                stmt_idx += 1

            line_idx += 1
            stmt_idx = 0

        return None

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
                for stmt, nested in _while_wend_walk(line_statements[stmt_idx]):
                    if isinstance(stmt, ast_nodes.WhileStatementNode):
                        depth += 1
                        continue
                    depth -= 1
                    if depth == 0:
                        # Found matching WEND
                        return (line_num, stmt_idx, nested)

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

        # Type coercion based on type suffix. BASIC does not convert across the
        # string/number line in either direction - A$ = 5 and A = "X" are both
        # "Type mismatch" on the real binary. str(value) quietly turned the
        # first into A$ = "5", so a mistyped expression showed up much later as
        # something else.
        if stmt.variable.type_suffix == '%':
            # Integer - MBASIC rounds to nearest, halves away from zero.
            # A% = 3.7 is 4 on the real binary, not 3, and A% = -3.7 is -4.
            value = to_int_operand(value)
        elif stmt.variable.type_suffix == '$':
            if not isinstance(value, str):
                raise TypeError("Type mismatch")
        elif stmt.variable.type_suffix in ('!', '#', None):
            # Single or double precision float (or no suffix) - ensure it's numeric
            if isinstance(value, str):
                raise TypeError("Type mismatch")
            if not isinstance(value, (int, float)):
                value = float(value) if value else 0
            if (stmt.variable.type_suffix != '#' and type(value) is float
                    and abs(value) >= SINGLE_LIMIT):
                # A double too big for a single variable: A! = 1D39
                value = self._overflow(value < 0, SINGLE_DIGITS)

        if stmt.variable.subscripts:
            # Array assignment
            subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in stmt.variable.subscripts]
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
        # The two variables must have the same type: an integer and a single,
        # or a string and a number, are "Type mismatch" (measured), and
        # nothing is swapped. With a DEFtype in the program the types are read
        # from the table of the run.
        if (stmt.var1.type_suffix or '!') != (stmt.var2.type_suffix or '!'):
            raise TypeError("Type mismatch")
        # Get values of both variables
        if stmt.var1.subscripts:
            # Array element
            subscripts1 = [to_subscript(self.evaluate_expression(sub)) for sub in stmt.var1.subscripts]
            value1 = self.runtime.get_array_element(stmt.var1.name, stmt.var1.type_suffix, subscripts1, token=self._make_token_info(stmt.var1))
        else:
            # Simple variable
            value1 = self.runtime.get_variable(stmt.var1.name, stmt.var1.type_suffix, token=self._make_token_info(stmt.var1))

        if not stmt.var2.subscripts:
            # The second variable of a SWAP must exist already (measured): a name
            # never used before is Illegal function call. The first variable is
            # made by its lookup, so SWAP A,A is fine.
            full2, _ = self.runtime._resolve_variable_name(stmt.var2.name, stmt.var2.type_suffix)
            if full2 not in self.runtime._variables:
                raise RuntimeError("Illegal function call")
        if stmt.var2.subscripts:
            # Array element
            subscripts2 = [to_subscript(self.evaluate_expression(sub)) for sub in stmt.var2.subscripts]
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

    # ------------------------------------------------------------------
    # How many digits PRINT shows
    # ------------------------------------------------------------------

    def _numeric_digits(self, expr):
        """Significant figures PRINT should show for this expression.

        The rules live in number_format.numeric_digits(), shared with the
        JavaScript code generator.
        """
        return numeric_digits(expr)

    def _output_column(self, file_info):
        """The 0-based cursor column of the screen or of an open file."""
        if file_info is not None:
            return file_info.get('col', 0)
        column = getattr(self.io, 'column', None)
        if not isinstance(column, int):
            column = getattr(self, '_fallback_column', 0)
        # The column of an infinite screen (WIDTH 255) stops at 255
        return min(column, INFINITE) if self._output_width(None) >= INFINITE else column

    def _output_width(self, file_info):
        """The line width of the screen (set by WIDTH) or of a file."""
        if file_info is not None:
            return file_info.get('width', FILE_WIDTH)
        width = getattr(self.io, 'width', SCREEN_WIDTH)
        return width if isinstance(width, int) and width >= 0 else SCREEN_WIDTH

    def _screen_line_ended(self, kept_text=None):
        """A line typed at the keyboard ends with Enter: the cursor is at column 0.

        INPUT; keeps the cursor after the typed answer instead: kept_text is
        the answer, and the column grows by its length.
        """
        try:
            if kept_text is not None:
                col = self._output_column(None) + len(kept_text)
                self.io.column = col
                self._fallback_column = col
                return
            self.io.column = 0
        except AttributeError:
            pass
        self._fallback_column = 0

    def _send_output(self, file_info, file_handle, text):
        """Send text to the file or the screen and keep the column.

        A trailing newline goes out as the end of the output() call, as a
        PRINT without a final ';' always did.
        """
        if file_handle:
            file_handle.write(text)
            file_handle.flush()
            file_info['col'] = advance_column(file_info.get('col', 0), text)
            # the size the text has in a CP/M file, where a line ends in CR LF (for LOC)
            file_info['cpm_bytes'] = file_info.get('cpm_bytes', 0) + len(text) + text.count('\n')
            return
        if text.endswith('\n'):
            self.io.output(text[:-1])
        elif text:
            self.io.output(text, end='')
        if not isinstance(getattr(self.io, 'column', None), int):
            self._fallback_column = advance_column(
                getattr(self, '_fallback_column', 0), text)

    def execute_print(self, stmt):
        """Execute PRINT statement - print to screen or file

        The line is laid out from the real cursor column, which earlier
        statements and INPUT leave behind, and wrapped at the line width the
        way MBASIC 5.21 does (src/print_column.py has the rules).
        """
        # Check if printing to file
        if stmt.file_number is not None:
            file_num = to_conint(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise self._file_not_open(file_num)
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_info = None
            file_handle = None

        width = self._output_width(file_info)
        # A screen of width 255 is infinite: nothing wraps (files do wrap)
        infinite = file_info is None and width >= INFINITE
        wrap_width = screen_wrap_width(width) if file_info is None else width
        col = self._output_column(file_info)
        pieces = []
        top = (1 << 30) if not infinite else INFINITE     # an infinite screen's column stops here

        def put(text):
            nonlocal col
            pieces.append(text)
            col = advance_column(col, text)

        resync = False

        def flush():
            # Called by _notice(): the message goes out after the text so far
            # and moves the real cursor, so col is read again afterwards.
            nonlocal resync
            resync = True
            if pieces:
                self._send_output(file_info, file_handle, ''.join(pieces))
                del pieces[:]

        retry = False
        self._print_flush = flush if file_info is None else None
        try:
            for i, expr in enumerate(stmt.expressions):
                col = min(col, top)
                # Each item is evaluated when its turn comes, so POS(0) sees
                # the text of the items before it.
                if file_info is None:
                    self.builtins.print_column = col
                value = self.evaluate_expression(expr)
                if resync:
                    # An Overflow or Division by zero message was printed
                    resync = False
                    col = min(self._output_column(file_info), top)

                if isinstance(value, TabMarker):
                    # TAB(n): column n (1-based); a cursor already past it
                    # starts a new line first.
                    target = tab_target(value.column, width, infinite)
                    if col > target:
                        put('\n')
                    put(' ' * (target - col))
                elif isinstance(value, SpcMarker):
                    # SPC(n): n spaces; the count wraps at the width
                    text, new_col = wrap_text(
                        col, wrap_width,
                        ' ' * spc_count(value.count, width, infinite), False)
                    pieces.append(text)
                    col = new_col
                else:
                    if (isinstance(value, (int, float))
                            and not isinstance(value, bool)):
                        # MBASIC shows 6 significant figures for a
                        # single-precision value and 16 for a double, with a
                        # leading space unless the number is negative and a
                        # trailing space always. Which of the two applies is
                        # a property of the expression, not the value - see
                        # _numeric_digits(). src/number_format.py has the
                        # rules.
                        text = format_for_print(
                            value, self._numeric_digits(expr))
                    else:
                        text = str(value)
                    # On the screen an item that does not fit goes whole to
                    # the next line; a file splits it at the width.
                    text, new_col = wrap_text(
                        col, wrap_width, text, file_info is None)
                    pieces.append(text)
                    col = new_col

                col = min(col, top)
                if i < len(stmt.separators):
                    sep = stmt.separators[i]
                    if sep == ',':
                        # Next 14-column zone; the last zone starts a new line
                        if file_info is None:
                            action, count = comma_step(col, width, infinite)
                        else:
                            # a file has no last-zone rule: it pads, wrapping
                            action, count = 'pad', (col // 14 + 1) * 14 - col
                        if action == 'newline':
                            put('\n')
                        else:
                            text, new_col = wrap_text(
                                col, wrap_width, ' ' * count, False)
                            pieces.append(text)
                            col = new_col
                    elif sep == '\n':
                        put('\n')
                    # ';' adds nothing (number formatting has the spaces)

            if not stmt.separators:
                put('\n')                  # a bare PRINT
        except KeyInputPending:
            # The statement runs again from its start: print nothing now
            retry = True
            raise
        finally:
            self.builtins.print_column = None
            self._print_flush = None
            if pieces and not retry:
                self._send_output(file_info, file_handle, ''.join(pieces))

    def execute_printusing(self, stmt):
        """Execute PRINT USING statement - formatted print to screen or file"""
        # Check if printing to file
        if stmt.file_number is not None:
            file_num = to_conint(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise self._file_not_open(file_num)
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_info = None
            file_handle = None

        # Evaluate format string
        format_str = str(self.evaluate_expression(stmt.format_string))

        # Check for empty format string
        if not format_str:
            raise RuntimeError("Illegal function call")

        # Evaluate all expressions, keeping each one's precision: PRINT USING
        # converts through the same routine PRINT does, so a single-precision
        # value is six significant figures there too and 12345.67 comes out of
        # "##,###.##" as 12,345.70. See UsingFormatter.format_numeric_field.
        values = []
        digits = []
        for expr in stmt.expressions:
            values.append(self.evaluate_expression(expr))
            digits.append(self._expression_digits(expr))

        # Create formatter and format values
        formatter = UsingFormatter(format_str)
        output = formatter.format_values(values, digits)

        # Output to file or screen. A ';' or ',' at the end of the value list
        # suppresses the newline, as it does on a plain PRINT.
        newline = '' if getattr(stmt, 'trailing_separator', False) else '\n'
        no_field = values and not formatter.has_field()
        if no_field:
            newline = ''    # the error comes before the end of the line (measured)
        if file_handle:
            self._send_output(file_info, file_handle, output + newline)
        else:
            self.io.output(output, end=newline)
            if not isinstance(getattr(self.io, 'column', None), int):
                self._fallback_column = advance_column(
                    getattr(self, '_fallback_column', 0), output + newline)

        if no_field:
            # MBASIC scans the whole USING string, prints the literal text it
            # found, and only then complains that there was never a field to
            # put the value in: PRINT USING "A.B"; 5 prints A.B and stops with
            # Illegal function call.
            raise RuntimeError("Illegal function call")

    def execute_clause_statements(self, statements, resume_pc=None, restart=False):
        """Run the statements of a THEN or ELSE clause.

        A clause is not addressable by PC - the statement table holds one entry
        for the whole IF - so a GOSUB inside one has nowhere to point its return
        address except the statement *after* the IF. The rest of the clause was
        therefore dropped:

            30 IF I > 0 THEN GOSUB 100: PRINT "NEVER PRINTED"

        Real MBASIC 5.21 prints it. In basic/games/startrek.bas this is how
        every Klingon and star is placed -

            380 IF I > 0 THEN GOSUB 540: S(X, Y) = 5: I = I - 1: GOTO 380

        - so the galaxy came up empty: the GOSUB picked a free sector and the
        three statements that used it never ran.

        The tail is handed to the GOSUB frame instead, and RETURN finishes it.
        """
        entry = [statements, 0]
        self._clause_stack.append(entry)
        try:
            self._run_clause_list(statements, entry, resume_pc, restart)
        finally:
            self._clause_stack.pop()

    def _run_clause_list(self, statements, entry, resume_pc, restart):
        index = 0
        while index < len(statements):
            entry[1] = index
            clause_stmt = statements[index]
            try:
                self.execute_statement(clause_stmt)
            except Exception as e:
                self._note_clause_error(e, statements, index, clause_stmt, restart)
                raise
            jump = self._clause_jump
            if jump is not None:
                # A NEXT (or a FOR that is not entered) goes to a statement of
                # a clause: this one, or one that holds this one.
                base = getattr(statements, 'base', None) or statements
                if jump[0] is not base:
                    return
                self._clause_jump = None
                if jump[1] < getattr(statements, 'offset', 0):
                    # back to a FOR before the part that runs again
                    statements = entry[0] = base
                    index = jump[1]
                else:
                    index = jump[1] - getattr(statements, 'offset', 0)
                continue
            index += 1
            if self.runtime.npc is None:
                continue
            remaining = clause_slice(statements, index)
            if type(clause_stmt).__name__ == 'GosubStatementNode':
                if resume_pc is not None:
                    # This GOSUB is itself running from a clause tail, so it
                    # worked out its return address from inside the subroutine
                    # that just returned. Where it should come back to is where
                    # the clause was going to end up.
                    self.runtime.set_gosub_return(
                        resume_pc.line_num if resume_pc.is_running() else 0,
                        resume_pc.stmt_offset if resume_pc.is_running() else 0)
            if remaining and type(clause_stmt).__name__ == 'GosubStatementNode':
                # The frame this GOSUB just pushed is on top; the rest of the
                # clause belongs to it. Any other jump (GOTO, THEN <line>) is
                # a departure, and what follows it is unreachable - which is
                # what MBASIC does too.
                self.runtime.set_gosub_continuation(remaining)
            break

    def _note_clause_error(self, error, statements, index, clause_stmt, restart):
        """Work out what RESUME NEXT runs after an error inside a THEN or ELSE clause."""
        if hasattr(error, 'clause_tail'):
            return
        # An error that MBASIC reports after the statement ran (WIDTH n,x) has
        # the text pointer inside that statement; any other error in the first
        # statement of a clause leaves it at the start of the enclosing statement.
        # A list that starts again behind a ':' (the tail RESUME NEXT runs, the
        # rest of a clause after RETURN) has the main loop start each statement.
        if index == 0 and not restart and not getattr(error, 'late_error', False):
            error.clause_climb = True
            return
        try:
            error.clause_tail = clause_tail_after(clause_stmt, statements, index)
            error.clause_rerun = clause_slice(statements, index)    # RESUME starts here again
        except AttributeError:
            pass

    def execute_if(self, stmt):
        """Execute IF statement"""
        condition = self.evaluate_expression(stmt.condition)
        if isinstance(condition, str):
            raise TypeError("Type mismatch")     # IF "a" THEN: a string is no condition

        # In BASIC, any non-zero value is true
        if condition:
            # Execute THEN clause
            if stmt.then_line_number is not None:
                # THEN line_number
                self._jump_to(stmt.then_line_number)
            elif stmt.then_statements:
                self.execute_clause_statements(stmt.then_statements)
        else:
            # Execute ELSE clause
            if stmt.else_line_number is not None:
                # ELSE line_number
                self._jump_to(stmt.else_line_number)
            elif stmt.else_statements:
                self.execute_clause_statements(stmt.else_statements)

    def _matching_next(self, stmt, tail=None):
        """The NEXT that closes this FOR, found once and remembered.

        MBASIC scans for it every time a FOR is set up, and says
        "FOR Without NEXT" at the FOR's own line when there is none. Scanning
        the program on every entry to an inner loop would be far too slow here,
        so the answer is cached on the statement - keyed on the statement table
        and its version, so that MERGE or an edit invalidates it.
        """
        table = self.runtime.statement_table
        key = (id(table), table.version)
        cached = getattr(stmt, '_mb_next', None)
        if cached is not None and cached[0] == key:
            return cached[1]
        target = self.find_matching_next(
            self.runtime.pc.line_num, self.runtime.pc.stmt_offset, tail)
        if target is None:
            raise RuntimeError("FOR without NEXT")
        try:
            stmt._mb_next = (key, target)
        except AttributeError:
            pass                            # a node with __slots__: recompute
        return target

    def _divide_by_zero(self, dividend, digits=SINGLE_DIGITS):
        r"""What a floating-point divide by zero does on 5.21.

        Not an error at all, unless a handler is armed. The ANSI overflow
        routine prints a bare "Division by zero" - no line number, no "Ok" -
        substitutes machine infinity with the dividend's sign, and returns to
        the middle of the expression it was called from, so the statement
        finishes and the program carries on:

            10 A = 1/0
            15 PRINT "A=";A        ->  Division by zero
            20 PRINT "AFTER"           A= 1.70141E+38
                                       AFTER

        We used to raise, which stopped the program. The integer forms - 5 \ 0
        and 5 MOD 0 - are different: those go through the normal error
        dispatcher and do stop, which is why they still raise.

        With ON ERROR armed it IS trappable, with ERR 11, and the assignment
        never completes - so there the ordinary error path is the right one.
        A double expression gets the double machine infinity.
        """
        if self.runtime.has_error_handler():
            raise RuntimeError("Division by zero")
        self._notice("Division by zero")
        try:
            return machine_infinity(digits, dividend < 0)
        except TypeError:
            return machine_infinity(digits)

    _print_flush = None

    def _notice(self, text):
        """Print a bare error message that does not stop the program.

        A PRINT that is half done shows what it has so far first, so the
        message lands after "A=" and the number follows on the next line.
        The cursor column stays in one place, the I/O handler's column;
        execute_print reads it again after the item that printed the message.
        """
        if self._print_flush is not None:
            self._print_flush()
        # The message goes through the width logic of PRINT, one character at a
        # time: next to the right edge the word is split (measured: "Overflo" and "w").
        wrap_width = screen_wrap_width(self._output_width(None))
        wrapped, _ = wrap_text(self._output_column(None), wrap_width, text, False)
        self._send_output(None, None, wrapped + '\n')

    def _overflow(self, negative, digits):
        """A result too big for its precision: the same routine, "Overflow".

        Prints a bare "Overflow", substitutes machine infinity with the sign
        of the true result and carries on - or, with ON ERROR armed, is ERR 6
        and the statement never completes. "Too big" means infinite in the
        IEEE format of the precision (the MBF range is not emulated; see
        docs/dev/MBASIC_521_DIVERGENCES_TODO.md, section 10).
        """
        if self.runtime.has_error_handler():
            raise OverflowError("Overflow")
        self._notice("Overflow")
        return machine_infinity(digits, negative)

    def _range_checked(self, result, digits):
        """A float result at its precision; Overflow if the precision cannot hold it."""
        if digits == SINGLE_DIGITS:
            if abs(result) >= SINGLE_LIMIT:
                return self._overflow(result < 0, digits)
            return to_single(result)
        if digits == DOUBLE_DIGITS and abs(result) > DOUBLE_MAX:
            return self._overflow(result < 0, digits)
        return result

    def _power(self, left, right, digits):
        """MBASIC's ^ : a float result, with the real binary's error cases.

        0 ^ negative is a (non-fatal) division by zero; a negative base with a
        fraction in the exponent is Illegal function call, where Python would
        hand back a complex number; a result too big is Overflow.
        """
        if isinstance(left, str) or isinstance(right, str):
            raise TypeError("Type mismatch")
        if left == 0 and right < 0:
            return self._divide_by_zero(1, digits)
        if left < 0 and right != int(right):
            raise ValueError("Illegal function call")
        try:
            if isinstance(left, int) and isinstance(right, int) and 0 <= right <= 256:
                return left ** right
            return float(left) ** float(right)
        except OverflowError:
            odd = right == int(right) and int(right) % 2 == 1
            return self._overflow(left < 0 and odd, digits)

    def _jump_to(self, line_number):
        """Set the next PC to a program line, checking that it is there.

        Without the check the bad line number travels all the way to the
        statement fetch, which reported it as "Invalid PC: PC(9999.0)" - a
        Python repr, at the line being jumped TO rather than the line doing the
        jumping. The real binary says "Undefined line number in 10".
        """
        if not self.runtime.statement_table.line_exists(line_number):
            raise RuntimeError(f"Undefined line number {line_number}")
        self.runtime.npc = PC.from_line(line_number)

    def execute_goto(self, stmt):
        """Execute GOTO statement"""
        # A GOTO out of a handler does not end the handler: only RESUME does
        # (b2/b4 in the issue 47 notes - the binary leaves later errors
        # untrapped after "GOTO 30" out of a handler).
        # Set both old and new PC
        self._jump_to(stmt.line_number)

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
        self._jump_to(stmt.line_number)

    def execute_ongoto(self, stmt):
        """Execute ON...GOTO statement - computed GOTO

        Syntax: ON expression GOTO line1, line2, line3, ...

        If expression evaluates to 1, jump to line1
        If expression evaluates to 2, jump to line2
        If expression is 0 or > number of lines, continue to next statement
        """
        # Evaluate the expression
        value = self.evaluate_expression(stmt.expression)

        # CONINT: ON 1.7 GOTO takes the second target, 40000 is Overflow and
        # 256 or -1 is Illegal function call, even with fewer targets than that
        index = to_conint(value)

        # Check if index is valid (1-based indexing)
        if 1 <= index <= len(stmt.line_numbers):
            self._jump_to(stmt.line_numbers[index - 1])
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

        index = to_conint(value)       # as for ON...GOTO

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
            self._jump_to(stmt.line_numbers[index - 1])
        # If index is out of range, just continue to next statement (no jump)

    def execute_return(self, stmt):
        """Execute RETURN statement"""
        # Pop from resource limits
        self.limits.pop_gosub()

        # Pop return address, and any tail of a THEN/ELSE clause the GOSUB was
        # sitting in - see execute_clause_statements().
        continuation = self.runtime.peek_gosub_continuation()
        return_line, return_stmt = self.runtime.pop_gosub()

        # RETURN from an ON ERROR GOSUB handler ends the handler. (The binary
        # has no such form; it is a syntax error there.)
        if self.runtime.error_handler_is_gosub and self.state.pending_error is not None:
            self.state.pending_error = None
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

        if continuation:
            # The GOSUB was inside a THEN/ELSE clause and the rest of that
            # clause has been waiting for it. Run it now, before the return
            # address takes effect - and let it win if it jumps somewhere
            # itself, which is how "THEN GOSUB x: ... : GOTO y" loops work.
            resume_pc = self.runtime.npc
            self.runtime.npc = None
            self.execute_clause_statements(continuation, resume_pc=resume_pc, restart=True)
            if self.runtime.npc is None:
                self.runtime.npc = resume_pc

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
        # Each value is checked as it is read: a string anywhere, or a number for a
        # string variable, is Type mismatch before the next expression runs, and
        # before a loop is registered (the NEXT after the trapped error is then
        # NEXT without FOR).
        start = self.evaluate_expression(stmt.start_expr)
        if isinstance(start, str) or stmt.variable.type_suffix == '$':
            raise MBasicError(13)
        # An integer loop variable takes its start, limit and step through
        # FRCINT, in this order (measured): FOR I%=1 TO 2.5 runs to 3,
        # STEP .5 is STEP 1, and a value over 32767 is Overflow at the FOR.
        integer_loop = stmt.variable.type_suffix == '%'
        if integer_loop:
            start = to_frcint(start)
        # The loop this FOR started earlier, and every loop opened inside it, are
        # dropped as soon as the start value is in: an error in the limit or the
        # step does not bring them back (measured).
        var_name = stmt.variable.name + (stmt.variable.type_suffix or "")
        old_state = self.runtime.for_loop_states.get(var_name)
        if old_state is not None and old_state['pc'].line == self.runtime.pc.line \
                and old_state['pc'].statement == self.runtime.pc.statement:
            self.runtime.drop_for_loops(var_name, newer=True, itself=True)
        end = self.evaluate_expression(stmt.end_expr)
        if isinstance(end, str):
            raise MBasicError(13)
        if integer_loop:
            end = to_frcint(end)
        step = self.evaluate_expression(stmt.step_expr) if stmt.step_expr else 1
        if isinstance(step, str):
            raise MBasicError(13)
        if integer_loop:
            step = to_frcint(step)

        # FOR scans for its NEXT before it does anything to the variable or the
        # loop stack (NXTSCN); without one the FOR is the error and the variable
        # keeps its value.
        in_clause = None
        if self._clause_stack:
            clause, position = self._clause_stack[-1]
            if clause[position] is stmt:
                in_clause = (getattr(clause, 'base', None) or clause,
                             getattr(clause, 'offset', 0) + position)
        target = self._matching_next(
            stmt, in_clause[0][in_clause[1] + 1:] if in_clause else None)
        next_line, next_stmt, var_index, nested, next_node = target
        site = (self._next_uid(next_node), var_index)
        # The FOR enters the NEXT its scan ended at, which checks its name there: another
        # name is NEXT without FOR at the FOR, reported at the line of the NEXT, before
        # the variable is set (measured: FOR I=1 TO 2:PRINT "a":NEXT J prints no "a")
        next_vars = getattr(next_node, 'variables', None) or []
        if var_index < len(next_vars):
            named = next_vars[var_index]
            if named.name + (named.type_suffix or "") != var_name:
                exc = RuntimeError("NEXT without FOR")
                if next_line is not None:
                    exc.error_pc = PC.running_at(next_line, next_stmt)
                raise exc

        # Set loop variable to start
        self.runtime.set_variable(
            stmt.variable.name,
            stmt.variable.type_suffix,
            start,
            token=self._make_token_info(stmt.variable),
            limits=self.limits,
            original_case=getattr(stmt.variable, 'original_case', stmt.variable.name),
            settings_manager=self.settings_manager
        )

        # Register loop - use PC for position. The loops are kept in the order
        # they were entered, as MBASIC keeps them on its stack; entering a loop
        # again drops the older entry of the same variable.
        self.runtime.push_for_loop(
            var_name,
            end,
            step,
            self.runtime.pc.line,
            self.runtime.pc.statement,
            site
        )
        # The site holds only while the program is the one FOR scanned: a MERGE
        # makes new statements, and the NEXT check is then skipped for this loop
        table = self.runtime.statement_table
        self.runtime.for_loop_states[var_name]['table'] = (id(table), table.version)

        # MBASIC tests the loop before running it, so FOR I = 10 TO 1 runs the
        # body no times at all and leaves I at 10. It does that by never
        # falling into the body: FOR scans forward for its NEXT (NXTSCN) and
        # jumps *to* it with the increment suppressed, so the ordinary
        # termination test in NEXT is what ends the loop.
        #
        # Entering through the NEXT rather than skipping past it is what makes
        #   10 FOR I=10 TO 1 / 20 PRINT "BODY" / 30 NEXT J
        # report "NEXT without FOR in 30": the NEXT still runs, and still
        # checks the name it was given.
        if in_clause is not None:
            self._clause_for[var_name] = in_clause
        else:
            self._clause_for.pop(var_name, None)
        if _loop_is_done(start, end, step):
            if next_line is None:
                # The NEXT is in the same clause as the FOR: go on there. One
                # inside a clause within it ends the clause instead.
                clause, position = in_clause
                if nested:
                    self.runtime.pop_for_loop(var_name)
                    self._clause_jump = (clause, len(clause))
                else:
                    self._for_entry_index = var_index
                    self._clause_jump = (clause, position + 1 + next_stmt)
            elif nested:
                # The NEXT is inside a THEN or ELSE clause, which has no PC to
                # jump to. Finish the loop here instead and carry on after the
                # statement that contains it - where the clause would have left
                # us anyway, the NEXT being the last thing in it.
                self.runtime.pop_for_loop(var_name)
                self.runtime.npc = self.runtime.statement_table.next_pc(
                    PC.running_at(next_line, next_stmt))
            else:
                self._for_entry_index = var_index
                self.runtime.npc = PC.running_at(next_line, next_stmt)

    _next_uid_counter = itertools.count(1)

    def _next_uid(self, node):
        """A number that tells one NEXT statement from the others.

        FOR remembers the NEXT its scan ended at, and the loop is valid only
        there.  The number is kept on the statement; a NEXT is looked up
        by what it is and not by the line it runs in, because the tail of a
        THEN clause runs after a RETURN, in the line of the RETURN.
        """
        uid = getattr(node, '_mb_uid', None)
        if uid is None:
            uid = next(Interpreter._next_uid_counter)
            try:
                node._mb_uid = uid
            except AttributeError:
                pass
        return uid

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
        # A zero-trip FOR jumps straight here with the increment suppressed and,
        # for a NEXT that closes several loops, with the name it is to be
        # entered at - see execute_for.
        entry_index = self._for_entry_index
        self._for_entry_index = None
        uid = self._next_uid(stmt)

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

        # Process each variable in order. Coming from a zero-trip FOR, the
        # names before the one the scan stopped on belong to loops that were
        # never entered, so they are not touched at all.
        first = entry_index if entry_index and entry_index < len(var_list) else 0
        var_list = var_list[first:]

        for index, var_node in enumerate(var_list):
            var_name = var_node.name + (var_node.type_suffix or "")
            # Process this NEXT; the loop must be the one whose scan ended here
            should_continue = self._execute_next_single(
                var_name, var_node=var_node,
                suppress_increment=(entry_index is not None and index == 0),
                site=(uid, first + index))
            # If this loop continues (jumps back), don't process remaining variables
            if should_continue:
                return

    def _find_most_recent_for_variable(self):
        """Find the variable of the FOR loop a bare NEXT belongs to.

        MBASIC matches a NEXT with no variable to the innermost FOR that is
        currently *running*, which is a question about runtime state rather
        than about the text. This used to scan backwards through the source
        instead, and that fails whenever the NEXT is reached by a jump:

            580 FOR I = 0 TO 7: IF K3(I) <= 0 THEN 605
            ...
            605 NEXT: RETURN

        is line 580 in basic/games/startrek.bas jumping over its own body to
        its own NEXT - the scan walked back from 605 and never found the FOR,
        so the game died with "NEXT without FOR". (It also called a
        StatementTable method that does not exist, so before that it died with
        AttributeError.)

        runtime.for_loop_states is keyed by variable and, being a dict, keeps
        the order the loops were entered - so the innermost active loop is
        simply the last one still in it.

        Returns:
            Variable name with suffix (e.g. 'i!'), or None if no loop is running
        """
        visible = self.runtime.visible_for_loops()
        return visible[-1] if visible else None

    def _execute_next_single(self, var_name, var_node=None, suppress_increment=False, site=None):
        """Execute NEXT for a single variable.

        Args:
            var_name: Full variable name with suffix
            var_node: Optional VariableNode for token info
            suppress_increment: leave the control variable where it is instead
                of stepping it. This is how a zero-trip FOR arrives - MBASIC
                enters the NEXT with NXTFLG clear so that the termination test
                runs against the start value.

        Returns:
            True if loop continues (jumped back), False if loop finished
        """
        # Get loop info
        loop_info = self.runtime.get_for_loop(var_name)
        if not loop_info or var_name not in self.runtime.visible_for_loops():
            raise RuntimeError(f"NEXT without FOR: {var_name}")
        table = self.runtime.statement_table
        if (site is not None and loop_info.get('site') not in (None, site)
                and loop_info.get('table') in (None, (id(table), table.version))):
            # A NEXT other than the one the FOR found: NEXT without FOR, and the
            # entry on the stack is spoilt by then, with every loop below it
            # (measured: the loops opened later stay).
            self.runtime.drop_for_loops(var_name, newer=False, older=True, itself=True)
            raise RuntimeError(f"NEXT without FOR: {var_name}")
        # The loops opened inside this one and left by a jump are gone
        self.runtime.drop_for_loops(var_name)

        for _ in range(self.runtime.unwind_loops_above_for(var_name)):
            self.limits.pop_while_loop()

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
        new_value = current if suppress_increment else current + step

        # MBASIC increments first and leaves the variable at the value that
        # ended the loop, so FOR I=1 TO 3: NEXT: PRINT I prints 4, not 3.
        # Storing it only on the continuing branch left the last value that
        # still fit, which is what a program reads after the loop.
        try:
            self.runtime.set_variable(base_name, type_suffix, new_value, token=token, limits=self.limits)
        except Exception:
            # An error (Overflow of an integer variable) spoils the entry as a
            # NEXT of another place does; the next NEXT is NEXT without FOR
            self.runtime.drop_for_loops(var_name, newer=False, older=True, itself=True)
            raise

        # Check if loop should continue - see _loop_is_done for why this is a
        # sign comparison and not two inequalities.
        if not _loop_is_done(new_value, loop_info['end'], step):
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

            clause = self._clause_for.get(var_name)
            if clause is not None and any(
                    (getattr(entry[0], 'base', None) or entry[0]) is clause[0]
                    for entry in self._clause_stack):
                # The FOR is in a clause that is still running: its body is
                # the rest of that clause.
                self._clause_jump = (clause[0], clause[1] + 1)
                return True

            # Jump back to statement AFTER the FOR
            for_pc = PC.running_at(return_line, return_stmt)
            next_pc = self.runtime.statement_table.next_pc(for_pc)
            self.runtime.npc = next_pc
            if clause is not None:
                # The FOR is in a clause that has ended (its NEXT is on a
                # later line): the body is the rest of that clause. Run it
                # now, the way RETURN runs the rest of a clause, and go on
                # behind the IF as the clause would have.
                tail = clause_slice(clause[0], clause[1] + 1)
                if tail:
                    self.runtime.npc = None
                    self.execute_clause_statements(
                        tail, resume_pc=next_pc, restart=True)
                    if self.runtime.npc is None:
                        self.runtime.npc = next_pc
            return True  # Loop continues
        else:
            # Loop finished - unbind the variable from this loop
            # Note: No nesting tracking to pop - FOR loops are variable-indexed, not stack-based
            self.runtime.pop_for_loop(var_name)
            return False  # Loop finished

    def _matching_wend(self, stmt):
        """The WEND that closes this WHILE, found once and remembered.

        Same reasoning as _matching_next: the check has to happen whether the
        condition is true or not, because "WHILE without WEND" is raised when
        the loop is set up, and scanning on every entry would be too slow.
        """
        table = self.runtime.statement_table
        key = (id(table), table.version)
        cached = getattr(stmt, '_mb_wend', None)
        if cached is not None and cached[0] == key:
            return cached[1]
        target = self.find_matching_wend(
            self.runtime.pc.line_num, self.runtime.pc.stmt_offset)
        if target is None:
            raise RuntimeError("WHILE without WEND")
        try:
            stmt._mb_wend = (key, target)
        except AttributeError:
            pass
        return target

    def execute_while(self, stmt):
        """Execute WHILE statement"""
        # Checked whether or not the loop is entered - the real binary reports
        # a missing WEND at the WHILE, before running the body.
        wend_pos = self._matching_wend(stmt)

        # Evaluate the condition
        condition = self.evaluate_expression(stmt.condition)
        if isinstance(condition, str):
            # Raised before the loop is entered, so a RESUME NEXT runs the body
            # and its WEND finds no WHILE ("WEND without WHILE", as on the binary)
            raise TypeError("Type mismatch")

        if not condition:
            # Condition is false - skip to after matching WEND. When the WEND
            # is inside a clause it has no PC of its own and wend_stmt is the
            # statement containing it, which is where we want to land anyway.
            wend_line, wend_stmt, _nested = wend_pos

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
                self.runtime.pc.stmt_offset,
                (wend_pos[0], wend_pos[1])
            )

    def execute_wend(self, stmt):
        """Execute WEND statement"""
        # Pop the matching WHILE loop info
        loop_info = self.runtime.peek_while_loop()

        # The binary matches a WEND to the entry that holds this WEND's own
        # place, not to the newest WHILE: a WHILE that failed (Type mismatch)
        # leaves no entry, and its WEND finds none even inside an outer loop.
        if (loop_info is None or loop_info.get('wend_key') !=
                (self.runtime.pc.line_num, self.runtime.pc.stmt_offset)):
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
            pending = self.state.pending_error
            if pending is not None:
                # Inside a handler this also raises the error again, at the
                # line where it first happened. The handler is off now, so the
                # error is fatal.
                self.state.pending_error = None
                raise MBasicError(pending.error_code, pending.report_pc or pending.pc)
        else:
            # The binary looks the line up when the statement runs
            if not self.runtime.statement_table.line_exists(stmt.line_number):
                raise RuntimeError(f"Undefined line number {stmt.line_number}")
            self.runtime.error_handler = stmt.line_number
            self.runtime.error_handler_is_gosub = stmt.is_gosub

    def execute_resume(self, stmt):
        """Execute RESUME statement"""
        if self.state.pending_error is None:
            raise RuntimeError("RESUME without error")

        # Get error PC from ErrorInfo
        if not self.state.pending_error.pc:
            raise RuntimeError("No error position to resume from")

        error_pc = self.state.pending_error.pc
        report_pc = self.state.pending_error.report_pc
        # RESUME and RESUME NEXT make ERL the current line again (measured): when
        # the error was reported at another line, later errors on this line report it
        self._sticky_erl = None
        if (stmt.line_number in (None, 0, -1) and report_pc is not None
                and report_pc.line_num != error_pc.line_num):
            self._sticky_erl = (error_pc.line_num, report_pc.line_num)
        clause_tail = self.state.pending_error_tail
        self.state.pending_error_tail = None
        clause_rerun = self.state.pending_error_rerun
        self.state.pending_error_rerun = None

        # Clear error state
        self.state.pending_error = None
        self.runtime.set_variable_raw('err%', 0)

        # Determine where to resume
        if stmt.line_number is None or stmt.line_number == 0:
            # RESUME or RESUME 0 - retry the statement that caused the error
            # Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
            # Parser preserves the distinction (None vs 0) for source text regeneration,
            # but runtime execution treats both identically.
            self.runtime.npc = error_pc
            if clause_rerun:
                # The error was in a later statement of a THEN or ELSE clause: the
                # binary runs again from that statement, not from the IF.
                self.runtime.npc = None
                following = self.runtime.statement_table.next_pc(error_pc)
                if not following.is_running():
                    self.runtime.pc = PC.halted()
                    following = None
                else:
                    self.runtime.npc = following
                self._run_clause_again(clause_rerun, following, error_pc)
        elif stmt.line_number == -1:
            # RESUME NEXT - continue at statement after the error
            next_pc = self.runtime.statement_table.next_pc(error_pc)
            if not next_pc.is_running():
                # No next statement, program ends
                self.runtime.pc = PC.halted()
            else:
                self.runtime.npc = next_pc
            if clause_tail:
                # The error was in a THEN or ELSE clause: the statements
                # behind it in the clause still run.  An error in one of them
                # is reported at the IF, not at the RESUME.  A jump in them
                # replaces the next statement.
                self._run_clause_again(clause_tail, self.runtime.npc, error_pc)
        else:
            # RESUME line_number - jump to specific line
            self._jump_to(stmt.line_number)

    def _run_clause_again(self, statements, following, error_pc):
        """Run the statements of a clause that RESUME or RESUME NEXT goes on with.

        following is where the program goes on when they end (None: the program ends).
        """
        self.runtime.npc = None
        try:
            self.execute_clause_statements(statements, resume_pc=following, restart=True)
        except Exception as e:
            try:
                e.stmt_pc = error_pc
            except AttributeError:
                pass
            raise
        if self.runtime.npc is None:
            self.runtime.npc = following

    def execute_end(self, stmt):
        """Execute END statement"""
        # END in a handler just ends the program: no error is reported
        self.state.pending_error = None
        # CONT after END resumes at the statement after the END, as it does
        # after STOP (measured on MBASIC 5.21). Nothing is left after the last
        # statement, and CONT then does nothing.
        next_pc = self.runtime.statement_table.next_pc(self.runtime.pc)
        self.runtime.cont_pc = next_pc if next_pc is not None and next_pc.line_num is not None else None
        self.runtime.pc = self.runtime.pc.stop("END")

    def execute_syntaxerror(self, stmt):
        """A statement that did not parse when its line was entered or loaded.

        MBASIC stores such a line without a message and stops with Syntax
        error when execution reaches the bad statement.
        """
        if getattr(stmt, 'stray_else', False):
            return      # the parser took the rest of the line into this statement
        for name, args in getattr(stmt, 'partial_calls', ()):
            for i, arg in enumerate(args):
                self._early_range_check(name.rstrip('$'), i, self.evaluate_expression(arg))
        raise MBasicError(getattr(stmt, 'error_code', 2))

    def execute_remark(self, stmt):
        """Execute REM statement (do nothing)"""
        pass

    def execute_poke(self, stmt):
        """Accepted and discarded, deliberately.

        There is no memory model to write to - see PEEK, and
        docs/dev/NO_MEMORY_MODEL.md. A program that POKEs and then PEEKs the
        same address does not get its byte back. A program that needs that
        should run the real com/mbasic.com under an 8080 emulator.
        """
        self._poke_arguments(stmt)

    def execute_out(self, stmt):
        """OUT port, byte - accepted and discarded, like POKE (and INP gives 0).

        The operands are still checked: both are bytes, so OUT 70000,1 is
        Overflow and OUT 1,256 is Illegal function call.
        """
        to_conint(self.evaluate_expression(stmt.port))
        to_conint(self.evaluate_expression(stmt.value))

    def execute_wait(self, stmt):
        """WAIT port, mask[, select] - the operands are checked as bytes.

        There are no ports (INP gives 0), so a WAIT that would have to wait
        for a port to change can never finish. It stops with Illegal function
        call instead of hanging; a WAIT whose test is true at once, such as
        a mask of 0, simply returns. The operand errors match the binary:
        40000 is Overflow and 256 is Illegal function call.
        """
        port = to_conint(self.evaluate_expression(stmt.port))
        mask = to_conint(self.evaluate_expression(stmt.mask))
        select = to_conint(self.evaluate_expression(stmt.select)) if stmt.select else 0
        if not ((0 ^ select) & mask):
            raise ValueError("Illegal function call")

    def _poke_arguments(self, stmt):
        """Evaluate and check the operands of POKE the way the binary does.

        The address is -32768 to 65535 (a negative one is the same word as the
        unsigned one) and the value is a byte. 40000 is Overflow for the value,
        and so is 65536 for the address; 256 for the value is Illegal function
        call. Nothing is stored.
        """
        radix_word(self.evaluate_expression(stmt.address))
        to_conint(self.evaluate_expression(stmt.value))

    def execute_defusr(self, stmt):
        """DEF USR[n] = address - the address is checked and then dropped.

        Like the address of POKE it is -32768 to 65535: 65536 is Overflow and
        a string is Type mismatch. A call of USR is Illegal function call
        whatever the address, as there is no machine code to run.
        """
        radix_word(self.evaluate_expression(stmt.address))

    def execute_deftype(self, stmt):
        """Execute DEFINT/DEFSNG/DEFDBL/DEFSTR statement.

        The statement changes the DEFtype table of the run. A program that
        has a DEFtype statement types its unsuffixed names from that table
        (src/deftypes.py), as the binary does.
        """
        self.runtime.def_table.apply(stmt)

    def execute_deffn(self, stmt):
        """Execute DEF FN statement - define user function

        Syntax: DEF FNname[(param1, param2, ...)] = expression

        Example:
            DEF FND(X) = X * 2 + 1
            PRINT FND(5)  -> 11
        """
        # Store function definition in runtime
        # The function name is already normalized to lowercase
        if type(stmt) is not ast_nodes.DefFnStatementNode:
            # The type of FNA is the DEFtype of A when DEF FN runs; a DEFINT that
            # runs later makes FNA another function (Undefined user function)
            fixed = copy.copy(stmt)
            fixed.__class__ = ast_nodes.DefFnStatementNode
            fixed.type_suffix = stmt.type_suffix
            stmt = fixed
        self.runtime.user_functions[stmt.name] = stmt

    def execute_data(self, stmt):
        """Execute DATA statement (do nothing, data already indexed)"""
        pass

    def execute_read(self, stmt):
        """Execute READ statement"""
        start_pointer = self.runtime.data_pointer   # a failing item rewinds the whole statement
        for var_node in stmt.variables:
            # Read next data value (returns AST node)
            data_node = self.runtime.read_data()
            data_index = self.runtime.data_pointer - 1

            # Evaluate the data node to get actual value
            bad_item = None
            if isinstance(data_node, ast_nodes.StringNode) and var_node.type_suffix != '$':
                # The text of a DATA item is read as a number only now
                data_line = self.runtime.data_line_map.get(data_index)
                try:
                    if not data_node.raw:
                        raise ValueError("data")        # a quoted item
                    value = data_text_to_number(data_node.value)
                except ValueError as e:
                    self.runtime.data_pointer = start_pointer   # the statement is read again
                    where = PC.from_line(data_line) if str(e) == "data" and data_line is not None else None
                    bad_item = MBasicError(2, where)
                    # The variable still gets the number the item starts with (measured:
                    # 12x gives 12, 7.6x gives 8 to an integer, "q" and x y give 0), and
                    # then the item is a Syntax error
                    value = val_text(data_node.value) if data_node.raw else 0
                    if value in (float('inf'), float('-inf')):
                        raise MBasicError(6)
                except OverflowError:
                    self.runtime.data_pointer = start_pointer
                    raise MBasicError(6)
            else:
                value = self.evaluate_expression(data_node)

            # Convert to appropriate type based on variable suffix
            if var_node.type_suffix == '$':
                # DATA text is not crunched: A$ gets the item as it was typed.
                # The text points into the program on the binary and takes no
                # string space, so it keeps the ProgramString mark.
                if isinstance(data_node, ast_nodes.NumberNode) and isinstance(data_node.literal, str):
                    value = ProgramString(data_node.literal)
                elif (isinstance(data_node, ast_nodes.UnaryOpNode)
                      and isinstance(data_node.operand, ast_nodes.NumberNode)
                      and isinstance(data_node.operand.literal, str)
                      and data_node.operator in (TokenType.MINUS, TokenType.PLUS)):
                    value = ProgramString(('-' if data_node.operator == TokenType.MINUS else '+')
                                          + data_node.operand.literal)
                elif type(value) is not ProgramString:
                    value = str(value)
            elif var_node.type_suffix == '%':
                value = to_integer(value)      # rounds, like every other
                                               # assignment to an integer
            else:
                # Ensure numeric types are float
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = 0

            # Store in variable
            if var_node.subscripts:
                subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in var_node.subscripts]
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
            if bad_item is not None:
                raise bad_item
            if getattr(data_node, 'bad_tail', False):
                # "q"x: the string was read and stored; the text behind the
                # closing quote is a Syntax error at the DATA line, and the
                # statement is read again from its first item
                data_line = self.runtime.data_line_map.get(data_index)
                self.runtime.data_pointer = start_pointer
                raise MBasicError(2, PC.from_line(data_line) if data_line is not None else None)

    def execute_restore(self, stmt):
        """Execute RESTORE statement

        RESTORE n of a line that is not in the program is Undefined line number,
        and the DATA pointer is then past the last item: the next READ is Out of
        DATA (measured).
        """
        line_number = getattr(stmt, 'line_number', None)
        if line_number is not None and not self.runtime.statement_table.line_exists(line_number):
            self.runtime.data_pointer = len(self.runtime.data_items)
            raise RuntimeError(f"Undefined line number {line_number}")
        self.runtime.restore_data(line_number)

    def execute_dim(self, stmt):
        """Execute DIM statement"""
        from src.ast_nodes import TypeInfo

        for array_def in stmt.arrays:
            # array_def is an ArrayDeclNode with name and dimensions
            dimensions = [to_subscript(self.evaluate_expression(dim))
                          for dim in array_def.dimensions]   # DIM B(2.7) is B(3)
            # Extract type suffix from name if present
            name = name_with_suffix(array_def.name.rstrip('$%!#'), array_def.bare,
                                    self.runtime.def_table) if array_def.bare else array_def.name
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
        After ERASE the array does not exist: a DIM can size it again, and a
        use without a DIM makes it 0..10.  ERASE of an array that does not exist
        (never dimensioned or used, or erased already) is Illegal function call.

        Syntax: ERASE array1, array2, ...
        """
        for index, array_name in enumerate(stmt.array_names):
            if stmt.bare and stmt.bare[index]:
                array_name = name_with_suffix(array_name.rstrip('$%!#'), True,
                                              self.runtime.def_table)
            # Free from resource limits tracking
            # The parser gives the name as written, which for a single has no
            # suffix - the storage key does. See Runtime.erase_array.
            if not self.runtime.erase_array(array_name):
                raise MBasicError(5)
            self.limits.free_variable(array_name.lower())

    def _clear_memory_arguments(self, stmt):
        """The memory top and stack space of CLEAR, checked as the binary does.

        Measured: 0 is Illegal function call for both; a number that is not
        16 bits is Overflow; -1 is 65535 for the memory top; and a string
        space that comes out below nothing, or a stack under 82 bytes, is
        Out of memory.
        """
        if stmt.string_space is not None:
            # Read as an integer: Overflow beyond 16 bits, Illegal function
            # call below 0 (measured), and then not used.
            string_space = to_integer(self.evaluate_expression(stmt.string_space))
            if not -32768 <= string_space <= 32767:
                raise RuntimeError("Overflow")
            if string_space < 0:
                raise MBasicError(5)
        memory_top = stack_space = None
        if stmt.memory_top is not None:
            memory_top = to_integer(self.evaluate_expression(stmt.memory_top))
            if not -32768 <= memory_top <= 65535:
                raise RuntimeError("Overflow")
            if memory_top == 0:
                raise MBasicError(5)
            memory_top &= 0xFFFF
        if stmt.stack_space is not None:
            stack_space = to_integer(self.evaluate_expression(stmt.stack_space))
            if not -32768 <= stack_space <= 65535:
                raise RuntimeError("Overflow")
            if stack_space == 0:
                raise MBasicError(5)
            stack_space &= 0xFFFF
        top = self.runtime.memory_top if memory_top is None else memory_top
        stack = self.runtime.stack_space if stack_space is None else stack_space
        if (stack < MIN_STACK_SPACE
                or FREE_MEMORY + (top - HIGHEST_MEMORY) - (stack - STACK_SPACE) < 0):
            raise MBasicError(7)
        return memory_top, stack_space

    def execute_clear(self, stmt):
        """Execute CLEAR statement

        CLEAR resets all variables and closes all open files.
        Syntax: CLEAR [,[memory_top][,stack_space]]

        Effects:
        - All simple variables are deleted
        - All arrays are erased
        - All open files are closed
        - ON ERROR GOTO is forgotten, so the next error is fatal, and a handler
          that is running is over (its RESUME is "RESUME without error"). ERR
          and ERL keep their values.
        - DEFINT, DEFSNG, DEFDBL and DEFSTR are forgotten: every letter is
          single precision again (the names typed by the old table are other
          variables from now on).
        - The FOR and GOSUB/WHILE stacks are emptied, OPTION BASE may be given
          again (the base is 0), the DATA pointer goes back to the first item,
          and the DEF FN functions defined so far are forgotten.
        - COMMON variables list is preserved (for CHAIN compatibility)
        - memory_top and stack_space change the string space (Runtime.set_memory),
          which is what Out of string space is measured against. The number before
          the first comma is read and not used, as on the binary.
        """
        memory_top, stack_space = self._clear_memory_arguments(stmt)

        # Clear resource limits tracking
        self.limits.clear_all()

        # Restart the random sequence. CLEAR, RUN and NEW share one routine on
        # the real machine (0x4358), which reloads the seed and zeroes the
        # counters - so CLEAR then RND gives .245121 again, measured.
        self.runtime.rnd.reset()

        # Clear all variables. ERR and ERL are not variables of the program on
        # the binary: CLEAR leaves them as they are (measured, in a handler).
        runtime = self.runtime
        kept = {name: runtime.get_variable_for_debugger(name[:-1], '%')
                for name in ('err%', 'erl%', 'ers%')}
        runtime.clear_variables()
        for name, value in kept.items():
            runtime.set_variable_raw(name, value)

        # The error handler goes, and a handler that is running is over
        runtime.error_handler = None
        runtime.error_handler_is_gosub = False
        self.state.pending_error = None

        # The stacks, OPTION BASE, the DATA pointer and DEF FN
        runtime.execution_stack.clear()
        runtime.for_loop_states.clear()
        runtime.array_base = 0
        runtime.option_base_executed = False
        runtime.data_pointer = 0
        runtime.user_functions.clear()
        runtime.def_table.reset()

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
        #   - ERR and ERL
        #
        # NOT PRESERVED (cleared above):
        #   - All variables and arrays
        #   - All open files (closed and cleared)
        #   - Field buffers
        #
        self.runtime.set_memory(memory_top, stack_space)

    def execute_randomize(self, stmt):
        """Execute RANDOMIZE statement

        Reseeds the random number generator.

        Syntax:
            RANDOMIZE           - ask for a seed, the way the real binary does
            RANDOMIZE seed      - use this seed

        Example:
            10 RANDOMIZE
            20 RANDOMIZE 42

        The seed is a 16-bit integer that replaces the middle two bytes of the
        generator's seed - see src/mbasic_rnd.py. With no argument MBASIC 5.21
        prints "Random number seed (-32768 to 32767)? " and waits, which is
        what the pause below does; seeding from the clock instead would make a
        program that says RANDOMIZE unrepeatable, and MBASIC's is repeatable.
        """
        if stmt.seed:
            seed = self.evaluate_expression(stmt.seed)
        elif self.state.input_buffer:
            answer = self.state.input_buffer.pop(0).strip()
            self._screen_line_ended()
            try:
                seed = float(answer) if answer else 0
            except ValueError:
                raise RuntimeError("Redo from start")
        else:
            prompt = "Random number seed (-32768 to 32767)? "
            self.io.output(prompt, end='')
            # Pause exactly as INPUT does; the statement runs again with the
            # answer waiting in the buffer.
            self.state.input_prompt = prompt
            self.state.input_variables = []
            self.state.input_file_number = None
            return

        self.runtime.rnd.randomize(to_frcint(seed))     # 40000 is Overflow

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
        error_code = to_conint(self.evaluate_expression(stmt.error_code))
        if error_code == 0:
            raise ValueError("Illegal function call")

        # Set error information in variable table (integer variables, lowercase)
        self.runtime.set_variable_raw('err%', error_code)
        if self.runtime.pc.is_running():
            self.runtime.set_variable_raw('erl%', self.runtime.pc.line_num)
            self.runtime.set_variable_raw('ers%', self.runtime.pc.stmt_offset)
        else:
            self.runtime.set_variable_raw('erl%', 0)
            self.runtime.set_variable_raw('ers%', 0)

        # Raise it as the error it is. The message used to be the literal text
        # "ERROR 21", which mapped back to code 5 and printed "Illegal function
        # call"; MBASIC looks the number up in its message table, so ERROR 21
        # is "Unprintable error in 10" and ERR reads 21.
        raise MBasicError(error_code)

    def execute_input(self, stmt):
        """Execute INPUT statement - read from keyboard or file

        State machine for keyboard input (file input is synchronous):
        1. If state.input_buffer has data: Use buffered input (from provide_input())
        2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
        3. UI calls provide_input() with user's input line
        4. On next tick(), buffered input is used (step 1) and input_prompt/input_variables are cleared
        5. If the line is bad, "?Redo from start" is printed and step 2 runs again with the
           same prompt. Every UI already handles a new input_prompt, so none needs to know.

        The prompt is "? " unless a comma follows the prompt string (prompt_comma).
        A semicolon right after INPUT only keeps the cursor on the line after the answer;
        the "? " stays. suppress_question is not used here.

        The answer is split and converted by src/input_fields.py with MBASIC 5.21's rules.
        A file read (INPUT #) takes its fields straight from the file stream, has no Redo,
        and reads a bad number as 0.
        """
        if stmt.file_number is not None:
            self._input_from_file(stmt)
            return

        if self.state.input_buffer:
            line = self.state.input_buffer.pop(0)
            # INPUT; keeps the cursor after the answer
            self._screen_line_ended(line if stmt.suppress_question else None)
        else:
            self._pause_for_input(stmt)
            return

        values = self._convert_input_line(line, stmt.variables)
        if values is None:
            self.io.output("?Redo from start")
            self._pause_for_input(stmt)
            return

        self._assign_input_values(stmt.variables, values)

        # Clear input state after successful completion
        self.state.input_variables = []
        self.state.input_prompt = None

    def _pause_for_input(self, stmt):
        """Print the INPUT prompt and pause execution until provide_input() is called."""
        prompt_value = ""
        if stmt.prompt:
            prompt_value = self.evaluate_expression(stmt.prompt)
        full_prompt = prompt_value if (stmt.prompt and stmt.prompt_comma) else prompt_value + "? "
        self.io.output(full_prompt, end='')

        # Sets: input_prompt (prompt text), input_variables (var list),
        #       input_file_number (None for keyboard input, file # for file input)
        self.state.input_prompt = full_prompt
        self.state.input_variables = stmt.variables
        self.state.input_file_number = None

    def _convert_input_line(self, line, variables):
        """Convert one keyboard answer for the variables, or None for ?Redo from start.

        Nothing is assigned here, so a bad line changes no variable.
        Overflow of an integer variable is an error, as on the real binary.
        """
        fields = split_keyboard_fields(line)
        if fields is None or len(fields) != len(variables):
            return None
        values = []
        for var_node, (text, quoted) in zip(variables, fields):
            suffix = self._input_var_suffix(var_node)
            if suffix == '$':
                values.append(text)
                continue
            if quoted:
                return None
            number = keyboard_number(text)
            if number is None:
                return None
            if suffix == '%':
                number = coerce_to_type(number, '%')  # rounds; raises Overflow when over 16 bits
            else:
                if abs(number) > MAX_FLOAT:
                    self.io.output("Overflow")
                    return None
                number = coerce_to_type(number, suffix)
            values.append(number)
        return values

    def _input_var_suffix(self, var_node):
        """Type suffix of an INPUT target after DEFINT/DEFSNG/DEFDBL/DEFSTR."""
        _, suffix = self.runtime._resolve_variable_name(var_node.name, var_node.type_suffix, None)
        return suffix

    def _assign_input_values(self, variables, values):
        """Store already converted INPUT values in their variables."""
        for var_node, value in zip(variables, values):
            if var_node.subscripts:
                subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in var_node.subscripts]
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

    def _input_from_file(self, stmt):
        """INPUT #n: read one field per variable straight from the file."""
        file_num = to_conint(self.evaluate_expression(stmt.file_number))
        if file_num not in self.runtime.files:
            raise self._file_not_open(file_num)
        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'I':
            raise RuntimeError(f"File #{file_num} not open for input")
        handle = file_info['handle']

        def read_byte():
            if file_info['eof']:
                return None
            byte = handle.read(1)
            if not byte:
                file_info['eof'] = True
                return None
            if byte[0] == 26:  # ^Z ends a CP/M file
                file_info['eof'] = True
                return None
            return byte[0]

        def unread_byte():
            handle.seek(-1, 1)

        for var_node in stmt.variables:
            suffix = self._input_var_suffix(var_node)
            field = read_file_field(read_byte, unread_byte, suffix != '$')
            if field is None:
                raise RuntimeError("Input past end of file")
            text, _quoted = field
            if suffix == '$':
                value = text
            else:
                value = val_number(text)
                if suffix != '%' and abs(value) > MAX_FLOAT:
                    # Real MBASIC prints Overflow, keeps going, and stores its largest number
                    self.io.output("Overflow")
                    value = MAX_FLOAT if value > 0 else -MAX_FLOAT
                value = coerce_to_type(value, suffix)
            self._assign_input_values([var_node], [value])

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
            file_num = to_conint(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise self._file_not_open(file_num)
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
                self._screen_line_ended()
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
            subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in var_node.subscripts]
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
            file_num = to_conint(self.evaluate_expression(stmt.file_number))
            if file_num not in self.runtime.files:
                raise self._file_not_open(file_num)
            file_info = self.runtime.files[file_num]
            if file_info['mode'] not in ['O', 'A']:
                raise RuntimeError(f"File #{file_num} not open for output")
            file_handle = file_info['handle']
        else:
            file_info = None
            file_handle = None

        # WRITE #n with no ',' and no items is a Syntax error when it runs
        if (stmt.file_number is not None and not stmt.expressions
                and not getattr(stmt, 'file_comma', True)):
            raise MBasicError(2)

        # Format values
        output_parts = []
        for expr in stmt.expressions:
            value = self.evaluate_expression(expr)

            if isinstance(value, str):
                # Quote strings
                output_parts.append(f'"{value}"')
            elif isinstance(value, (int, float)):
                # Numbers in PRINT's format, minus the padding spaces
                output_parts.append(
                    format_number(value, self._numeric_digits(expr)))
            else:
                output_parts.append(str(value))

        output = ','.join(output_parts)

        # WRITE with a ',' or ';' after the last item: MBASIC writes the items
        # and a ',' with no end of line, then stops with Missing operand.
        # Measured on 5.21, on the screen and in a file alike.
        if getattr(stmt, 'bad_separator', False):
            # A leading or doubled separator: the items before it and a ','
            # go out, then Syntax error.
            self._send_output(file_info, file_handle, output + (',' if output else ''))
            raise MBasicError(2)
        if getattr(stmt, 'trailing_separator', None):
            self._send_output(file_info, file_handle, output + ',')
            raise MBasicError(22)

        # Output to file or screen
        self._send_output(file_info, file_handle, output + '\n')

    def _in_program_line(self):
        """True when the running statement belongs to a program line, False
        for a statement typed at the Ok prompt (run as line 0)."""
        return bool(self.runtime.pc and self.runtime.pc.line_num)

    def _stop_after_read_abort(self):
        """LOAD/MERGE hit a bad file line. MBASIC prints the bare message
        (already printed) and returns to Ok: no ON ERROR handler runs and the
        running program stops."""
        if self._in_program_line():
            self.runtime.pc = self.runtime.pc.stop("END")

    def execute_load(self, stmt):
        """Execute LOAD statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("LOAD requires string filename")
        self._check_file_name(filename)

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            if self.interactive_mode.cmd_load(filename, from_program=self._in_program_line()):
                self._stop_after_read_abort()
        else:
            raise RuntimeError("LOAD not available in this context")

    def execute_save(self, stmt):
        """Execute SAVE statement"""
        # Evaluate filename expression
        filename = self.evaluate_expression(stmt.filename)
        if not isinstance(filename, str):
            raise RuntimeError("SAVE requires string filename")
        self._check_file_name(filename, creates=True)

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
                self._check_file_name(target_value)
                if hasattr(self, 'interactive_mode') and self.interactive_mode:
                    if self.interactive_mode.cmd_load(target_value, from_program=self._in_program_line()):
                        # A bad file line ends RUN "file" before the run
                        self._stop_after_read_abort()
                        return
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
                    self.runtime.def_table.reset()
                    # Set NPC to target line (like GOTO)
                    # On next tick(), NPC will be moved to PC
                    self._jump_to(line_num)
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
                self.runtime.def_table.reset()
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
        self._check_file_name(filename)

        # Evaluate starting line if provided
        start_line = None
        if stmt.start_line:
            start_line = int(self.evaluate_expression(stmt.start_line))

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            if self.interactive_mode.cmd_chain(
                filename,
                start_line=start_line,
                merge=stmt.merge,
                all_flag=stmt.all_flag,
                delete_range=stmt.delete_range
            ):
                self._stop_after_read_abort()
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
        self._check_file_name(filename)

        # Delegate to interactive mode if available
        if hasattr(self, 'interactive_mode') and self.interactive_mode:
            # quiet: MBASIC prints nothing when a running program MERGEs -
            # the summary belongs to the interactive command only.
            if self.interactive_mode.cmd_merge(filename, quiet=True, from_program=self._in_program_line()):
                self._stop_after_read_abort()
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
        3. Updating the line number references in the text of each line
           (see src/renum.py) and parsing the changed lines again

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
            # Leave out trailing parts; keep the commas of a part that is
            # left out in the middle (RENUM ,50,20 and RENUM 100,,20).
            parts = ['' if v is None else str(v)
                     for v in (new_start, old_start, increment)]
            while parts and parts[-1] == '':
                parts.pop()
            args = ','.join(parts)

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

    def _check_file_name(self, filename, creates=False):
        """Bad file name or Too many files for a name CP/M cannot hold.

        See src/cpm_names.py. A name with a slash or a backslash is a host
        path, which CP/M has no form for, so it passes. The setting
        cpm_file_names turns the check off for host names that have neither,
        such as inputfile.txt.
        """
        if '/' in filename or '\\' in filename:
            return
        if self.settings_manager.get('cpm_file_names', True):
            code = cpm_name_error(filename, creates)
            if code is not None:
                raise MBasicError(code)

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
        self._check_file_name(filename)

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
        self._check_file_name(old_filename)
        # The new name goes through namfil too: Bad file name for a malformed
        # one, and Illegal function call for a drive letter (measured: the
        # rename would cross drives). Refused characters are not checked.
        code = cpm_new_name_error(new_filename, old_filename) \
            if self.settings_manager.get('cpm_file_names', True) \
            and '/' not in new_filename and '\\' not in new_filename else None
        if code is not None:
            raise MBasicError(code)

        # Rename the file
        try:
            if not os.path.exists(old_filename):
                raise RuntimeError(f"File not found: {old_filename}")
            if os.path.exists(new_filename):
                raise RuntimeError(f"File already exists: {new_filename}")
            os.rename(old_filename, new_filename)
        except OSError as e:
            raise RuntimeError(f"Cannot rename {old_filename} to {new_filename}: {e.strerror}")

    @staticmethod
    def _file_not_open(file_num):
        """The error for a file number that no OPEN made, in a statement that uses a file.

        Measured on the binary (PRINT#, WRITE#, INPUT#, LINE INPUT#, GET and PUT):
        a number up to the highest file (15 here) is Bad file mode, a bigger byte
        is Bad file number. The number was range-checked before this (to_conint).
        """
        return MBasicError(54 if file_num <= MAX_FILE_NUMBER else 52)

    def execute_open(self, stmt):
        """Execute OPEN statement - open file for I/O

        Syntax:
            OPEN "I", #1, "filename"        - Open for input
            OPEN "O", #2, "filename"        - Open for output
            OPEN "R", #4, "filename", 128   - Open for random access (FIELD, GET, PUT, LSET, RSET supported)

        Note: CP/M files used ^Z (ASCII 26) as EOF marker. We respect this on input.
        """
        # Evaluate mode, file number, and filename
        # The mode comes first (measured): a number is Type mismatch, and an
        # empty or unknown mode is Bad file mode, before the file number
        # is looked at. Only the first letter counts ("Input" opens for input).
        mode = stmt.mode.upper()  # "I", "O", "A", "R"
        if stmt.mode_expr is not None:
            mode_value = self.evaluate_expression(stmt.mode_expr)
            if not isinstance(mode_value, str):
                raise MBasicError(13)
            mode = mode_value[:1].upper()
        if mode not in ("I", "O", "A", "R"):
            raise MBasicError(54)
        file_num = to_conint(self.evaluate_expression(stmt.file_number))
        filename = self.evaluate_expression(stmt.filename)
        # Check file number range (MBASIC 5.21: #1 through #15)
        if file_num < 1 or file_num > MAX_FILE_NUMBER:
            raise RuntimeError("Bad file number")

        if not isinstance(filename, str):
            raise MBasicError(13)       # OPEN "O",#1,1

        # Check if file number is already open
        if file_num in self.runtime.files:
            raise RuntimeError(f"File #{file_num} already open")

        # The record length, which FIELD checks its widths against. Measured
        # on the binary: it is checked after the file number and before the
        # name (FRCINT, so 40000 is Overflow). A CP/M sector holds 128 bytes,
        # so 129 and up is an Illegal function call, and 0 is accepted but
        # leaves no room for any field.
        record_length = DEFAULT_RECORD_LENGTH
        syntax_error_after_open = False
        if stmt.record_length is not None:
            if mode in ("I", "O"):
                # Measured: the length is not read at all. The file is opened
                # (File not found comes first, and the file stays open) and
                # then the statement ends with Syntax error.
                syntax_error_after_open = True
            else:
                record_length = to_frcint(self.evaluate_expression(stmt.record_length))
                if not 0 <= record_length <= DEFAULT_RECORD_LENGTH:
                    raise MBasicError(5)

        self._check_file_name(filename, creates=mode in ("O", "R"))

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
                raise MBasicError(54)

            # LOF is the size the file had when it was opened, in sectors of
            # 128 bytes (measured); writing does not change it.
            sector_count = 0
            if mode != "O":
                file_handle.seek(0, 2)
                sector_count = (file_handle.tell() + 127) // 128
                file_handle.seek(0, 2 if mode == "A" else 0)

            # Store file handle and mode
            self.runtime.files[file_num] = {
                'lof': sector_count,
                'handle': file_handle,
                'mode': mode,
                'filename': filename,
                'record_length': record_length,
                'eof': False
            }
            if stmt.record_length is not None and mode in ("I", "O"):
                # Only a random file has a record length. The binary opens the file
                # first (so File not found comes before this) and leaves it open.
                raise MBasicError(2)

        except (OSError, IOError, PermissionError) as e:
            raise RuntimeError(f"Cannot open {filename}: {str(e)}")
        if syntax_error_after_open:
            raise MBasicError(2)

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
            self.runtime.field_buffers.clear()
        else:
            # Close specific file numbers
            for file_num_expr in stmt.file_numbers:
                file_num = to_conint(self.evaluate_expression(file_num_expr))
                if file_num > MAX_FILE_NUMBER:
                    raise RuntimeError("Bad file number")      # CLOSE #16
                if file_num in self.runtime.files:
                    self.runtime.files[file_num]['handle'].close()
                    del self.runtime.files[file_num]
                # The field variables keep the text they show, but are not in a record any more
                self.runtime.field_buffers.pop(file_num, None)
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
        self.runtime.field_buffers.clear()

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
        file_num = to_conint(self.evaluate_expression(stmt.file_number))

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
                'shown': {},   # var_name -> the text the variable was given from the record
                'current_record': 0
            }

        buffer_info = self.runtime.field_buffers[file_num]
        offset = 0
        layout = {}

        # Lay out the fields over the record. The widths together must fit in
        # the record length of OPEN (128 if none was given), else FIELD
        # overflow. The binary binds the variables before the overflowing one
        # and then stops; here nothing changes.
        for width_expr, var_node in stmt.fields:
            width = to_conint(self.evaluate_expression(width_expr))
            if not 0 <= width <= 255:
                raise MBasicError(5)
            var_name = var_node.name + (var_node.type_suffix or '')

            layout[var_name] = (offset, width)
            offset += width
            if offset > file_info['record_length']:
                raise MBasicError(50)

        # The buffer is the record: as long as the record length, whatever the
        # fields add up to, so GET and PUT keep the part no field covers.
        # (The contents of a new record are memory garbage on the binary; spaces here.)
        if len(buffer_info['buffer']) != file_info['record_length']:
            buffer_info['buffer'] = bytearray(b' ' * file_info['record_length'])

        # The variables are views of the record: each takes its part of it now, and
        # shows what GET, LSET, RSET and MID$ put there, as long as it is given no
        # other string (see _field_show). A variable is in one record only. A
        # number variable is Type mismatch, after the variables before it.
        for var_name, (offset, width) in layout.items():
            for other in self.runtime.field_buffers.values():
                other['fields'].pop(var_name, None)
                other['shown'].pop(var_name, None)
            if not var_name.endswith('$'):
                raise MBasicError(13)
            buffer_info['fields'][var_name] = (offset, width)
            self._field_put_text(buffer_info, var_name)

    def _field_value(self, var_name):
        """The value of a field variable, read without marking an access."""
        return self.runtime.get_variable_for_debugger(var_name[:-1], var_name[-1])

    def _field_put_text(self, buffer_info, var_name):
        """Give the variable its part of the record."""
        offset, width = buffer_info['fields'][var_name]
        text = buffer_info['buffer'][offset:offset + width].decode('latin-1')
        self.runtime.set_variable(var_name[:-1], var_name[-1], text, debugger_set=True)
        buffer_info['shown'][var_name] = text

    def _field_show(self, buffer_info):
        """The record changed: the variables that are still in it show their parts.

        A variable that was given another string (A$ = "x") is out of the record
        for good: its value is not the text it was shown last.
        """
        for var_name in list(buffer_info['fields']):
            if self._field_value(var_name) != buffer_info['shown'].get(var_name):
                del buffer_info['fields'][var_name]
                buffer_info['shown'].pop(var_name, None)
                continue
            self._field_put_text(buffer_info, var_name)

    def _field_record(self, var_name):
        """The record buffer a variable is a view of, or None."""
        for buffer_info in self.runtime.field_buffers.values():
            if var_name in buffer_info['fields']:
                if self._field_value(var_name) != buffer_info['shown'].get(var_name):
                    del buffer_info['fields'][var_name]
                    buffer_info['shown'].pop(var_name, None)
                    continue
                return buffer_info
        return None

    def _field_justify(self, stmt, right):
        """LSET and RSET: a field variable changes its part of the record; any other
        string variable keeps its length (measured: LSET A$="x" on "hello" gives "x    ")."""
        var_name = stmt.variable.name + (stmt.variable.type_suffix or '')
        value = str(self.evaluate_expression(stmt.expression))
        buffer_info = self._field_record(var_name)
        if buffer_info is not None:
            offset, width = buffer_info['fields'][var_name]
        else:
            width = len(self.runtime.get_variable_for_debugger(
                stmt.variable.name, stmt.variable.type_suffix))
        text = value[:width]
        text = text.rjust(width) if right else text.ljust(width)
        if buffer_info is None:
            self.runtime.set_variable_raw(var_name, text)
            return
        buffer_info['buffer'][offset:offset + width] = text.encode('latin-1', 'replace')
        self._field_show(buffer_info)

    def execute_get(self, stmt):
        """Execute GET statement - read record from random-access file

        Syntax:
            GET #n          - Read next record
            GET #n, record  - Read specific record number
        """
        file_num = to_conint(self.evaluate_expression(stmt.file_number))

        if file_num not in self.runtime.files:
            raise self._file_not_open(file_num)

        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'R':
            raise RuntimeError(f"File #{file_num} not open for random access")

        buffer_info = self._record_buffer(file_num, file_info)
        file_handle = file_info['handle']

        # Determine record number
        if stmt.record_number:
            record_num = to_frcint(self.evaluate_expression(stmt.record_number))
            if record_num < 0:
                raise ValueError("Illegal function call")
            if record_num == 0:
                raise MBasicError(63)    # Bad record number
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

        # The field variables that are still in the record show it; a variable
        # that was given another string since is not bound again (measured)
        self._field_show(buffer_info)

    def _record_buffer(self, file_num, file_info):
        """The record buffer of a random file; GET and PUT work before any FIELD.

        The binary has the buffer from OPEN on. A PUT before anything is in it
        writes what was in that memory; here the buffer starts as spaces.
        """
        if file_num not in self.runtime.field_buffers:
            self.runtime.field_buffers[file_num] = {
                'buffer': bytearray(b' ' * file_info['record_length']),
                'fields': {},
                'shown': {},
                'current_record': 0
            }
        return self.runtime.field_buffers[file_num]

    def execute_put(self, stmt):
        """Execute PUT statement - write record to random-access file

        Syntax:
            PUT #n          - Write to next record
            PUT #n, record  - Write to specific record number
        """
        file_num = to_conint(self.evaluate_expression(stmt.file_number))

        if file_num not in self.runtime.files:
            raise self._file_not_open(file_num)

        file_info = self.runtime.files[file_num]
        if file_info['mode'] != 'R':
            raise RuntimeError(f"File #{file_num} not open for random access")

        buffer_info = self._record_buffer(file_num, file_info)
        file_handle = file_info['handle']

        # Determine record number
        if stmt.record_number:
            record_num = to_frcint(self.evaluate_expression(stmt.record_number))
            if record_num < 0:
                raise ValueError("Illegal function call")
            if record_num == 0:
                raise MBasicError(63)    # Bad record number
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

        A field variable changes its part of the record, left-justified and padded
        with spaces.  Any other string variable keeps its length.
        """
        self._field_justify(stmt, right=False)

    def execute_rset(self, stmt):
        """Execute RSET statement - right-justify string in field variable

        Syntax: RSET var$ = expr$

        The same as LSET, right-justified.
        """
        self._field_justify(stmt, right=True)

    def _mid_value_is_destination(self, stmt):
        """Whether the value of a MID$ statement is the very variable it changes."""
        dest, value = stmt.string_var, stmt.value
        if not (isinstance(dest, ast_nodes.VariableNode) and isinstance(value, ast_nodes.VariableNode)):
            return False
        if (dest.name, dest.type_suffix) != (value.name, value.type_suffix):
            return False
        if bool(dest.subscripts) != bool(value.subscripts):
            return False
        if not dest.subscripts:
            return True
        return ([to_subscript(self.evaluate_expression(sub)) for sub in dest.subscripts]
                == [to_subscript(self.evaluate_expression(sub)) for sub in value.subscripts])

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
            raise MBasicError(13)    # Type mismatch: MID$(A,2)="X" with a number A

        # Evaluate the parameters
        # Start and length are CONINT arguments as in the MID$ function:
        # 0 or above 255 is Illegal function call, above 32767 is Overflow.
        start = to_conint(self.evaluate_expression(stmt.start))
        if start == 0:
            raise ValueError("Illegal function call")
        new_value = self.evaluate_expression(stmt.value)
        if not isinstance(new_value, str):
            raise MBasicError(13)    # Type mismatch
        # Length is optional - if not provided, use length of replacement string
        length = to_conint(self.evaluate_expression(stmt.length)) if stmt.length else len(new_value)
        # A start beyond the end of the target is Illegal function call on
        # the binary, unless the length given is 0 (so also for an empty
        # target or an empty replacement with a length above 0).
        if (stmt.length is None and not new_value) or length == 0:
            return
        if start > len(current_value):
            raise ValueError("Illegal function call")

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
        value_node = stmt.value
        if (isinstance(stmt.string_var, ast_nodes.VariableNode) and isinstance(value_node, ast_nodes.VariableNode)
                and not stmt.string_var.subscripts and not value_node.subscripts
                and (stmt.string_var.name.lower(), stmt.string_var.type_suffix)
                == (value_node.name.lower(), value_node.type_suffix)):
            # The value is the target itself: the binary copies byte by byte, forward,
            # over the same buffer, so the first characters repeat (hello gives hhhho)
            buf = list(current_value)
            for i in range(chars_to_replace):
                buf[start_idx + i] = buf[i]
            modified_value = ''.join(buf)

        if self._mid_value_is_destination(stmt):
            # The value is the destination string itself (also in
            # parentheses): the binary copies a byte at a time inside the
            # one string, so a byte it has just written is copied again.
            # Measured: A$="HELLO":MID$(A$,3)=A$ gives HEHEH, and
            # MID$(A$,2,3)=A$ gives HHHHO.  A$+"", LEFT$(A$,5) and a copy of
            # A$ in another variable are separate strings: HEHEL.
            chars = list(current_value)
            for i in range(chars_to_replace):
                chars[start_idx + i] = chars[i]
            modified_value = ''.join(chars)

        # A field variable is a view of the record: the change reaches the record
        field_record = None
        if isinstance(stmt.string_var, ast_nodes.VariableNode) and not stmt.string_var.subscripts \
                and stmt.string_var.type_suffix == '$':
            field_name = stmt.string_var.name + '$'
            field_record = self._field_record(field_name)

        # Assign the modified string back to the variable
        # Handle both simple variables and array elements
        if isinstance(stmt.string_var, ast_nodes.VariableNode):
            var_node = stmt.string_var
            if var_node.subscripts:
                # Array element
                subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in var_node.subscripts]
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
                if field_record is not None:
                    offset, width = field_record['fields'][field_name]
                    field_record['buffer'][offset:offset + width] = modified_value.encode('latin-1', 'replace')
                    field_record['shown'][field_name] = modified_value
                    self._field_show(field_record)
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
        # CONT resumes at the statement AFTER the STOP, but "Break in" names
        # the line of the STOP itself.
        stop_line = self.runtime.pc.line_num if self.runtime.pc else None
        if self.runtime.npc:
            # GOTO/GOSUB-style jump already pending
            next_pc = self.runtime.npc
        else:
            next_pc = self.runtime.statement_table.next_pc(self.runtime.pc)
        if next_pc is not None and next_pc.line_num is not None:
            self.runtime.pc = next_pc.stop("STOP")
        else:
            # STOP was the last statement: nothing is left to resume, and
            # CONT then does nothing, as in MBASIC.
            self.runtime.pc = PC.halted()

        # Print "Break in <line>" message; the binary starts a new line first
        # when the cursor is not in column 0
        if self._output_column(None) > 0:
            self.io.output('')
        if stop_line:
            self.io.output(f"Break in {stop_line}")
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

    def execute_null(self, stmt):
        """Execute NULL statement - check the count, a byte (0 to 255)

        On the binary NULL sets the number of nulls sent after each line, for
        slow terminals. Nothing prints them here; only the errors remain: a
        string is Type mismatch, -1 and 256 are Illegal function call.
        """
        count = self.evaluate_expression(stmt.count)
        if isinstance(count, str):
            raise MBasicError(13)
        to_conint(count)

    def execute_width(self, stmt):
        """Execute WIDTH statement - set the screen line width

        PRINT wraps at this width and measures TAB and the comma zones against
        it. The width is a byte, 0 to 255: 40000 is Overflow, and 256 and -1
        are Illegal function call. A width of 0 is accepted (the binary does
        so); see wrap_text for what it does to PRINT, and tab_target for TAB.
        WIDTH LPRINT n checks the byte and does nothing else: there is no
        line printer. WIDTH n, device sets the width and then is a Syntax
        error, as on the binary; nothing after the ',' runs.
        """
        width = self.evaluate_expression(stmt.width)
        if isinstance(width, str):
            raise RuntimeError("Type mismatch")
        width = to_conint(width)
        if stmt.lprint:
            return
        self.io.width = width
        if stmt.bad_device:
            error = MBasicError(2)
            error.late_error = True     # reported after the WIDTH ran: see clause_tail_after
            raise error

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
        """Evaluate a numeric literal, in the precision it was written in.

        A single-precision literal loses what a single cannot hold at the
        moment it is read, not when it is used: B# = .1 is .1000000014901161
        on the real binary, and B# = .1# is .1.

        Cached on the node - the answer never changes, and this runs on every
        pass through a loop.
        """
        value = getattr(expr, '_mb_value', _UNCACHED)
        if value is _UNCACHED:
            value = expr.value
            if type(value) is float and self._expression_digits(expr) == SINGLE_DIGITS:
                value = to_single(value)
            try:
                expr._mb_value = value
            except AttributeError:
                pass                    # a node with __slots__: recompute
        return value

    def evaluate_string(self, expr):
        """Evaluate string literal"""
        value = getattr(expr, '_mb_program_string', None)
        if value is None or value != expr.value:
            value = ProgramString(expr.value)
            try:
                expr._mb_program_string = value
            except AttributeError:
                return value
        return value

    def evaluate_variable(self, expr):
        """Evaluate variable reference"""
        if expr.subscripts:
            # Array access - track access
            subscripts = [to_subscript(self.evaluate_expression(sub)) for sub in expr.subscripts]
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

    def _check_string_temps(self, expr):
        """String formula too complex, raised before the expression runs."""
        if string_temps(expr)[0] > STRING_TEMPORARIES:
            raise MBasicError(16)

    def evaluate_binaryop(self, expr):
        """Evaluate a binary operation at the precision MBASIC would use.

        MBASIC computes in single precision unless something in the expression
        is double, and a single holds 24 bits of mantissa. Rounding each
        result rather than only the final assignment is what reproduces the
        real machine digit for digit: 1/3 stored in a double really is
        .3333333432674408 there, because the division itself was single.

        Exact integer results are left alone - rounding them would turn
        subscripts and string lengths into floats for no gain, and MBASIC's
        integers are 16-bit anyway, far inside what a single holds exactly.
        """
        self._check_string_temps(expr)
        result = self._binaryop_value(expr)
        kind = type(result)
        if kind is float:
            return self._range_checked(result, self._expression_digits(expr))
        if kind is int and expr.operator == TokenType.POWER:
            # 10^40 is an exact Python int; the single it really is cannot hold it.
            digits = self._expression_digits(expr)
            if exceeds_range(result, digits):
                return self._overflow(result < 0, digits)
        return result

    def _expression_digits(self, expr):
        """_numeric_digits, cached on the node.

        Every arithmetic operation asks, so an inner loop would otherwise walk
        its subtree once per iteration. The answer is static - it comes from
        the shape of the expression, which does not change - so it is computed
        once and kept.
        """
        digits = getattr(expr, '_mb_digits', _UNCACHED)
        if digits is _UNCACHED:
            digits = self._numeric_digits(expr)
            try:
                expr._mb_digits = digits
            except AttributeError:
                pass                    # a node with __slots__: just recompute
        return digits

    def _binaryop_value(self, expr):
        """The arithmetic itself, before precision is applied."""
        left = self.evaluate_expression(expr.left)
        right = self.evaluate_expression(expr.right)

        op = expr.operator

        # A string with a number, or two strings under anything but + and the
        # comparisons, is Type mismatch on the binary. Python would raise its
        # own TypeError (reported as Illegal function call), so test first.
        left_is_str = isinstance(left, str)
        if left_is_str != isinstance(right, str) or (
                left_is_str and op not in _STRING_BINARY_OPS):
            raise TypeError("Type mismatch")

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
                return self._divide_by_zero(left, self._expression_digits(expr))
            try:
                return left / right
            except OverflowError:       # int / int, too big for a float
                return self._overflow((left < 0) != (right < 0),
                                      self._expression_digits(expr))
        elif op == TokenType.BACKSLASH:  # Integer division
            # Not Python's // : MBASIC truncates toward zero, rounds both
            # operands to integers first and requires them to fit 16 bits.
            # See src/number_format.py.
            return int_divide(left, right)
        elif op == TokenType.POWER:
            return self._power(left, right, self._expression_digits(expr))
        elif op == TokenType.MOD:
            # Not Python's % : the remainder takes the sign of the dividend.
            return int_modulo(left, right)

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
            return to_int_operand(left) & to_int_operand(right)
        elif op == TokenType.OR:
            return to_int_operand(left) | to_int_operand(right)
        elif op == TokenType.XOR:
            return to_int_operand(left) ^ to_int_operand(right)
        elif op == TokenType.EQV:
            # Logical equivalence: A EQV B = NOT (A XOR B)
            # In BASIC: -1 = TRUE, 0 = FALSE
            # Bitwise: invert XOR result
            return ~(to_int_operand(left) ^ to_int_operand(right))
        elif op == TokenType.IMP:
            # Logical implication: A IMP B = (NOT A) OR B
            # In BASIC: -1 = TRUE, 0 = FALSE
            # Bitwise: (~A) | B
            return (~to_int_operand(left)) | to_int_operand(right)

        else:
            raise NotImplementedError(f"Binary operator not implemented: {op}")

    def evaluate_unaryop(self, expr):
        """Evaluate unary operation"""
        operand = self.evaluate_expression(expr.operand)

        if isinstance(operand, str) and expr.operator == TokenType.MINUS:
            raise TypeError("Type mismatch")
        if expr.operator == TokenType.MINUS:
            return -operand
        elif expr.operator == TokenType.NOT:
            return ~to_int_operand(operand)     # rounds, and 16 bits: NOT 2.7 is -4
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
        self._check_string_temps(expr)
        result = self._functioncall_value(expr)
        # SQR(2) is 1.414213538169861 on the real binary even when the result
        # is put straight into a double, and SQR(2#) is the same: MBASIC's
        # maths functions work in single precision. CDBL and VAL say otherwise
        # in _FUNCTION_PRECISION, and a DEF FN goes by its name.
        if type(result) is float:
            return self._range_checked(result, self._expression_digits(expr))
        return result

    def _early_range_check(self, func_name, index, value):
        """The range test of a number argument that the binary makes as it reads the argument.

        See BUILTIN_ARG_RANGES: this is why MID$("A",0,2,3) is Illegal function
        call and not Syntax error.
        """
        kind = BUILTIN_ARG_RANGES.get(func_name, {}).get(index)
        if kind and not isinstance(value, str):
            if to_conint(value) == 0 and kind == 's':
                raise MBasicError(5)

    def _functioncall_value(self, expr):
        """The call itself, before precision is applied."""
        # First, check if it's a built-in function
        # Strip $ suffix for builtin lookup (CHR$ -> CHR, INPUT$ -> INPUT, etc.)
        func_name = expr.name.rstrip('$')
        if func_name == 'INSTR' and len(expr.arguments) >= 2:
            # Which error depends on the types, not only the count.
            args = []
            for i, arg in enumerate(expr.arguments):
                args.append(self.evaluate_expression(arg))
                if i == 0:
                    self._early_range_check('INSTR', 0, args[0])
            error = instr_shape_error([isinstance(a, str) for a in args])
            if error is not None:
                raise MBasicError(error)
            return self.builtins.INSTR(*args)
        if expr.arity_error is not None:
            # Wrong number of arguments: the binary evaluates the ones it
            # can use, then stops with Syntax error (ABS(1,2), LEFT$(A$)).
            # An argument of the wrong type is Type mismatch first (see
            # BUILTIN_ARG_TYPES).
            wanted = arity_type_checks(expr.name, len(expr.arguments))
            for i, arg in enumerate(expr.arguments[:expr.arity_error]):
                value = self.evaluate_expression(arg)
                if i < len(wanted) and wanted[i] != 'A' and \
                        isinstance(value, str) != (wanted[i] == 'S'):
                    raise MBasicError(13)
                self._early_range_check(func_name, i, value)
            raise MBasicError(2)
        func = getattr(self.builtins, func_name, None)
        if func:
            # It's a builtin function
            # A string where a number is wanted (ABS("a")) or the other way
            # round (LEFT$(1,2)) is Type mismatch, checked as each argument
            # is evaluated.
            kinds = builtin_arg_kinds(func_name, len(expr.arguments))
            args = []
            for index, (kind, arg) in enumerate(zip(kinds, expr.arguments)):
                value = self.evaluate_expression(arg)
                if kind != '*' and isinstance(value, str) != (kind == 's'):
                    raise MBasicError(13)
                # a range error in this argument comes before a type error in a later one
                # (measured: MID$("a",-1,"x") is Illegal function call)
                self._early_range_check(func_name, index, value)
                args.append(value)
            if func_name == 'STR' and len(args) == 1:
                # STR$ converts like PRINT, so the argument's type matters
                return func(args[0], self._numeric_digits(expr.arguments[0]))
            return func(*args)

        # Not a builtin, check for user-defined function
        func_def = self.runtime.user_functions.get(expr.name)
        if not func_def or (func_def.type_suffix or '!') != (expr.type_suffix or '!'):
            # FNA and FNA% are two names: the function is the one of that type
            raise RuntimeError(f"Undefined function: {expr.name}")

        # A function is its name and its type: DEF FNA$ is not FNA (measured: Undefined
        # user function). Both types are the ones the DEF types give at the DEF and at the call.
        if expr.def_types is not None and (expr.type_suffix or '!') != (func_def.type_suffix or '!'):
            raise MBasicError(18)

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
                value = args[i]
                # The parameter has the type the DEF types give when the call runs (a
                # DEFINT behind the DEF FN rounds the argument); it is kept under the
                # name the body reads.
                call_suffix = parameter_suffix(expr, param)
                keep = False
                if (call_suffix or '!') != (param.type_suffix or '!'):
                    value = coerce_to_type(value, call_suffix)
                    keep = '$' not in (call_suffix, param.type_suffix)
                # Set parameter to argument value - this is part of function call
                # Use debugger_set=True to avoid tracking this internal variable operation
                self.runtime.set_variable(param.name, param.type_suffix, value, token=call_token, limits=self.limits, debugger_set=True, keep_value=keep)

        # Evaluate function expression
        result = self.evaluate_expression(func_def.expression)

        # The result has the type of the function (FNA% rounds to an integer, a
        # $ function must give a string and the others a number); with a DEFtype
        # statement in the program the type is read from the table of the run
        fn_type = func_def.type_suffix
        if fn_type == '$':
            if not isinstance(result, str):
                raise TypeError("Type mismatch")
        elif isinstance(result, str):
            raise TypeError("Type mismatch")
        elif fn_type == '%':
            result = to_int_operand(result)

        # Restore parameter values (use debugger_set=True to avoid tracking)
        for param_name, saved_value in saved_vars.items():
            base_name = param_name.rstrip('$%!#')
            type_suffix = param_name[-1] if param_name[-1] in '$%!#' else None
            self.runtime.set_variable(base_name, type_suffix, saved_value, debugger_set=True)

        # The result becomes the type of the function (measured): FNA% rounds
        # through FRCINT (Overflow over 32767), and a string body for a number
        # function, or the reverse, is Type mismatch.
        if func_def.type_suffix:
            result = coerce_to_type(result, func_def.type_suffix)

        # A DEF FN that hands back a string it was given (a variable or a
        # parameter) returns a copy in string space on the binary. Only a body
        # that is itself a literal stays free. A body that calls another DEF FN
        # stays free too: that inner call already made the copy when it needed one.
        if type(result) is ProgramString and not isinstance(
                func_def.expression, (StringNode, FunctionCallNode)):
            result = str(result)
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
