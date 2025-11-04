"""
Program Counter (PC) and Statement Table for MBASIC interpreter.

This module implements a hardware-inspired program counter design where:
- PC identifies a statement by (line_number, statement_offset)
- Statements are stored in an ordered collection indexed by PC
- Control flow uses PC and NPC (next program counter) like hardware
- No need to track current_line/current_stmt/next_line/next_stmt separately

This design:
- Reduces error surface (can't partially set position)
- Enables statement-level breakpoints (e.g., break at 100.2)
- Simplifies control flow (GOTO just sets npc)
- Matches hardware architecture (PC/NPC pattern from 1970s CPUs)
"""


class PC:
    """
    Immutable program counter - identifies a statement by (line, offset).

    Examples:
        PC(10, 0)  - First statement on line 10
        PC(10, 2)  - Third statement on line 10 (after two colons)
        PC(None, 0) - Halted (no valid line)
    """

    def __init__(self, line_num=None, stmt_offset=0):
        """
        Create a program counter.

        Args:
            line_num: Line number, or None for halted state
            stmt_offset: Statement index within line (0-based)
        """
        self.line_num = line_num
        self.stmt_offset = stmt_offset

    def halted(self):
        """Check if this PC represents halted state (past end of program)"""
        return self.line_num is None

    def __hash__(self):
        """Allow PC to be used as dict key or in sets"""
        return hash((self.line_num, self.stmt_offset))

    def __eq__(self, other):
        """Check equality for dict lookups and comparisons"""
        return isinstance(other, PC) and \
               (self.line_num, self.stmt_offset) == (other.line_num, other.stmt_offset)

    def __repr__(self):
        """String representation for debugging and trace output"""
        if self.halted():
            return "PC(HALTED)"
        return f"PC({self.line_num}.{self.stmt_offset})"

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
            return self.line_num != other_pc.line_num
        return False

    @classmethod
    def from_line(cls, line_num):
        """
        Create PC for GOTO target - start of line (offset 0).

        Args:
            line_num: Target line number

        Returns:
            PC pointing to first statement of line
        """
        return cls(line_num, 0)

    @classmethod
    def halted_pc(cls):
        """
        Create a halted PC (past end of program).

        Returns:
            PC with line_num=None representing halted state
        """
        return cls(None, 0)


class StatementTable:
    """
    Ordered collection of statements indexed by PC.

    Uses Python 3.7+ ordered dict to maintain statement execution order.
    Provides navigation methods (first_pc, next_pc) for sequential execution.
    """

    def __init__(self):
        """Initialize empty statement table"""
        self.statements = {}  # PC -> stmt_node (ordered dict)
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
            return PC.halted_pc()

    def next_pc(self, pc):
        """
        Get next PC after given PC (sequential execution).

        Args:
            pc: Current program counter

        Returns:
            Next PC in sequence, or halted PC if at end
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

        return PC.halted_pc()

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
            List of statement nodes for that line, in order by stmt_offset
        """
        result = []
        for pc, stmt in self.statements.items():
            if pc.line_num == line_num:
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
        return any(pc.line_num == line_num for pc in self.statements.keys())

    def delete_line(self, line_num):
        """
        Delete all statements for a given line number.

        Args:
            line_num: Line number to delete
        """
        # Remove all PCs for this line
        to_remove = [pc for pc in self.statements.keys() if pc.line_num == line_num]
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
            pc = PC(line_num, stmt_offset)
            self.add(pc, stmt)
