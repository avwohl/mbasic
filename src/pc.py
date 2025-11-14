"""
Program Counter (PC) for MBASIC interpreter.

This module implements an immutable program counter design where:
- PC is the SINGLE source of truth for execution state
- PC is immutable (frozen dataclass) - cannot be modified after creation
- All state changes create new PC objects
- No separate stopped/halted/running flags needed

Design principles:
- PC identifies statement by (line, statement) tuple
- stop_reason field indicates why execution stopped (None = running)
- error field contains error details if stop_reason == "ERROR"
- UIs cannot mutate PC - must create new ones via factory methods

This eliminates entire classes of bugs:
- No duplicate state (runtime.stopped vs pc.halted)
- No mutation from unexpected places (UIs can't poke internals)
- No race conditions (immutable = thread-safe)
- Clear semantics (is_running() is the only question)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ErrorInfo:
    """
    Error details for execution errors.

    Note: Does NOT contain line/statement - PC already has that.
    """
    code: int
    message: str
    on_error_handler: Optional[int] = None  # Line to jump to if ON ERROR GOTO active


@dataclass(frozen=True)
class PC:
    """
    Immutable program counter - single source of truth for execution state.

    Fields:
        line: Line number where we are (None = not in program)
        statement: Statement index on the line (0-based)
        stop_reason: Why we stopped (None = running, "STOP"/"END"/"ERROR"/"BREAK"/"USER")
        error: Error details (only set if stop_reason == "ERROR")

    Examples:
        PC(10, 0, None, None)                     # Running at line 10, first statement
        PC(10, 2, None, None)                     # Running at line 10, third statement
        PC(150, 0, "STOP", None)                  # Stopped at line 150 (STOP statement)
        PC(150, 2, "ERROR", ErrorInfo(...))       # Error at line 150, third statement
        PC(None, 0, "END", None)                  # Ended (fell off end of program)

    The statement index is 0-based: first statement has index 0, second has index 1, etc.
    Multiple statements can appear on one line, separated by colons.
    (See stmt_offset property for compatibility with code using the older name)
    """

    line: Optional[int]
    statement: int
    stop_reason: Optional[str] = None
    error: Optional[ErrorInfo] = None

    def is_running(self) -> bool:
        """
        Check if execution is running.

        This is the ONLY way to check execution state. No separate flags needed.

        Returns:
            True if stop_reason is None (running), False otherwise
        """
        return self.stop_reason is None

    def is_valid(self, program) -> bool:
        """
        Check if this PC points to a valid executable position.

        Used by CONT to determine if we can resume execution.

        Args:
            program: Program object with lines dict or statement_table

        Returns:
            True if line exists in program and we can execute from here
        """
        if self.line is None:
            return False

        # Check if line exists in program
        # Support both program.lines dict and runtime.statement_table
        if hasattr(program, 'lines'):
            return self.line in program.lines
        elif hasattr(program, 'line_exists'):
            return program.line_exists(self.line)

        return False

    def __eq__(self, other):
        """Compare PCs by position only (line, statement), not state (stop_reason, error).

        This allows PC lookups in statement_table and breakpoints to work correctly
        regardless of whether the PC is running or stopped.
        """
        if not isinstance(other, PC):
            return False
        return self.line == other.line and self.statement == other.statement

    def __hash__(self):
        """Hash by position only (line, statement), not state (stop_reason, error).

        Must match __eq__ per Python's hash/equality contract.
        """
        return hash((self.line, self.statement))

    def __repr__(self):
        """String representation for debugging"""
        if self.line is None:
            # Program halted (line is None means not in program)
            if self.stop_reason:
                # Explicit stop reason (e.g., "END" from halted factory)
                if self.error:
                    return f"PC(HALTED:{self.stop_reason} Error#{self.error.code})"
                return f"PC(HALTED:{self.stop_reason})"
            # No explicit stop reason (shouldn't occur normally)
            return "PC(HALTED)"

        if self.stop_reason:
            if self.error:
                return f"PC({self.line}.{self.statement} STOPPED:{self.stop_reason} Error#{self.error.code})"
            return f"PC({self.line}.{self.statement} STOPPED:{self.stop_reason})"

        return f"PC({self.line}.{self.statement})"

    # Factory methods to create new PCs

    @classmethod
    def running_at(cls, line: int, statement: int = 0):
        """
        Create a PC that's running at a specific position.

        Args:
            line: Line number
            statement: Statement index (0-based, default 0 for first statement)

        Returns:
            New PC in running state
        """
        return cls(line=line, statement=statement, stop_reason=None, error=None)

    @classmethod
    def stopped(cls, line: int, statement: int, reason: str):
        """
        Create a PC that's stopped at a specific position.

        Args:
            line: Line number where we stopped
            statement: Statement index where we stopped
            reason: Why we stopped ("STOP", "END", "BREAK", "USER")

        Returns:
            New PC in stopped state
        """
        return cls(line=line, statement=statement, stop_reason=reason, error=None)

    @classmethod
    def error_at(cls, line: int, statement: int, code: int, message: str,
                 on_error_handler: Optional[int] = None):
        """
        Create a PC stopped on an error.

        Args:
            line: Line number where error occurred
            statement: Statement index where error occurred
            code: Error code (e.g., 11 for division by zero)
            message: Error message
            on_error_handler: Line number to jump to if ON ERROR GOTO active

        Returns:
            New PC in error state
        """
        return cls(
            line=line,
            statement=statement,
            stop_reason="ERROR",
            error=ErrorInfo(code=code, message=message, on_error_handler=on_error_handler)
        )

    @classmethod
    def halted(cls):
        """
        Create a halted PC (not in program, fell off end).

        Returns:
            New PC in halted state
        """
        return cls(line=None, statement=0, stop_reason="END", error=None)

    @classmethod
    def from_line(cls, line: int):
        """
        Create running PC at start of line (for GOTO targets).

        Args:
            line: Target line number

        Returns:
            New PC pointing to first statement (index 0) of line
        """
        return cls.running_at(line, statement=0)

    # Methods to create new PCs from existing one

    def advance(self, new_line: int, new_statement: int):
        """
        Create new PC at advanced position (still running).

        Args:
            new_line: New line number
            new_statement: New statement index

        Returns:
            New PC at advanced position in running state
        """
        return PC.running_at(new_line, new_statement)

    def stop(self, reason: str):
        """
        Create new PC that's stopped at current position.

        Args:
            reason: Why we stopped ("STOP", "END", "BREAK", "USER")

        Returns:
            New PC at same position but stopped
        """
        return PC.stopped(self.line, self.statement, reason)

    def resume(self):
        """
        Create new PC that's running from current position.

        Used by CONT command to resume after STOP/BREAK.

        Returns:
            New PC at same position but running
        """
        return PC.running_at(self.line, self.statement)

    def with_error(self, code: int, message: str, on_error_handler: Optional[int] = None):
        """
        Create new PC with error at current position.

        Args:
            code: Error code
            message: Error message
            on_error_handler: ON ERROR GOTO line if active

        Returns:
            New PC at same position but with error
        """
        return PC.error_at(self.line, self.statement, code, message, on_error_handler)

    # Legacy compatibility methods (for gradual migration)

    @property
    def line_num(self):
        """Compatibility: old code used line_num instead of line"""
        return self.line

    @property
    def stmt_offset(self):
        """Compatibility: old code used stmt_offset instead of statement"""
        return self.statement

    def halted_check(self):
        """Compatibility: old code used halted() method"""
        return self.line is None

    def is_step_point(self, other_pc, step_mode):
        """
        Check if execution should pause when moving from self to other_pc.

        Args:
            other_pc: The next PC we're about to execute
            step_mode: 'step_statement' or 'step_line'

        Returns:
            True if we should pause before executing other_pc
        """
        if step_mode == 'step_statement':
            return True  # Stop at every statement
        elif step_mode == 'step_line':
            # Only stop if we're moving to a different line
            return self.line != other_pc.line
        return False


class StatementTable:
    """
    Ordered collection of statements indexed by PC.

    Uses regular dict which maintains insertion order (Python 3.7+).
    Provides navigation methods (first_pc, next_pc) for sequential execution.
    """

    def __init__(self):
        """Initialize empty statement table"""
        self.statements = {}  # PC -> stmt_node (insertion-ordered)
        self._keys_cache = None  # Cache for next_pc() lookups

    def add(self, pc, stmt_node):
        """
        Add statement at given PC.

        Args:
            pc: Program counter identifying this statement
            stmt_node: AST node for the statement
        """
        self.statements[pc] = stmt_node
        self._keys_cache = None  # Invalidate cache when table changes

    def get(self, pc):
        """
        Get statement at PC.

        Args:
            pc: Program counter

        Returns:
            Statement AST node, or None if PC is invalid
        """
        return self.statements.get(pc)

    def first_pc(self):
        """
        Get first PC in program.

        Returns:
            PC of first statement, or halted PC if table is empty
        """
        try:
            return next(iter(self.statements))
        except StopIteration:
            return PC.halted()

    def next_pc(self, pc):
        """
        Get next PC after given PC (sequential execution).

        Sequential execution means:
        - Next statement on same line (increment statement index), OR
        - First statement of next line (if at end of current line)

        Args:
            pc: Current program counter

        Returns:
            Next PC in sequence, or halted PC if at end or PC not found in table
        """
        # Build/rebuild keys cache if needed
        if self._keys_cache is None:
            self._keys_cache = list(self.statements.keys())

        try:
            idx = self._keys_cache.index(pc)
            if idx + 1 < len(self._keys_cache):
                return self._keys_cache[idx + 1]
        except ValueError:
            # PC not found in table
            pass

        return PC.halted()

    def prev_pc(self, pc):
        """
        Get previous PC before given PC (backward navigation).

        Used for finding the most recent FOR statement when NEXT is used
        without a variable name.

        Args:
            pc: Current program counter

        Returns:
            Previous PC in sequence, or None if at beginning or PC not found in table
        """
        # Build/rebuild keys cache if needed
        if self._keys_cache is None:
            self._keys_cache = list(self.statements.keys())

        try:
            idx = self._keys_cache.index(pc)
            if idx > 0:
                return self._keys_cache[idx - 1]
        except ValueError:
            # PC not found in table
            pass

        return None

    def __contains__(self, pc):
        """Check if PC exists in table (for breakpoint checks)"""
        return pc in self.statements

    def __len__(self):
        """Get number of statements in table"""
        return len(self.statements)

    def __repr__(self):
        """String representation for debugging"""
        return f"StatementTable({len(self.statements)} statements)"

    def get_line_statements(self, line_num):
        """
        Get all statements for a given line number.

        Args:
            line_num: Line number to get statements for

        Returns:
            List of statement nodes for that line, in order by statement index
        """
        result = []
        for pc, stmt in self.statements.items():
            if pc.line == line_num:
                result.append(stmt)
        return result

    def line_exists(self, line_num):
        """
        Check if a line exists in the program.

        Args:
            line_num: Line number to check

        Returns:
            True if line has any statements
        """
        return any(pc.line == line_num for pc in self.statements.keys())

    def delete_line(self, line_num):
        """
        Delete all statements for a given line number.

        Args:
            line_num: Line number to delete
        """
        # Remove all PCs for this line
        to_remove = [pc for pc in self.statements.keys() if pc.line == line_num]
        for pc in to_remove:
            del self.statements[pc]
        self._keys_cache = None  # Invalidate cache

    def replace_line(self, line_num, line_node):
        """
        Replace all statements for a given line with new statements from LineNode.

        Args:
            line_num: Line number to replace
            line_node: LineNode containing new statements
        """
        # Delete old statements for this line
        self.delete_line(line_num)

        # Add new statements
        for stmt_offset, stmt in enumerate(line_node.statements):
            pc = PC.running_at(line_num, stmt_offset)
            self.add(pc, stmt)
