"""
UI Helper Functions - Portable logic for all UIs

This module contains UI-agnostic helper functions that can be used by
any UI (CLI, Tk, Web, Curses). No UI-framework dependencies (Tk, curses, web)
are allowed. Standard library modules (os, glob, re) and core interpreter
modules (runtime, parser, AST nodes) are permitted.

Functions for:
- Line renumbering with GOTO/GOSUB reference updates
- Smart line insertion with gap calculation
- Line number validation and utilities
- Error message formatting and display
- Position calculations and conversions
"""

from typing import Dict, List, Tuple, Optional, Set
import re


# Line Number Constants
MIN_LINE_NUMBER = 0
MAX_LINE_NUMBER = 65529
DEFAULT_START = 10
DEFAULT_INCREMENT = 10


def validate_line_number(line_num: int) -> bool:
    """Check if line number is in valid range.

    Args:
        line_num: Line number to validate

    Returns:
        True if valid (0-65529), False otherwise
    """
    return MIN_LINE_NUMBER <= line_num <= MAX_LINE_NUMBER


def parse_line_number(line_text: str) -> Optional[int]:
    """Extract line number from start of line text.

    Args:
        line_text: Line of BASIC code

    Returns:
        Line number or None if no number found

    Examples:
        >>> parse_line_number("10 PRINT")
        10
        >>> parse_line_number("  20 FOR I=1 TO 10")
        20
        >>> parse_line_number("REM comment")
        None
    """
    match = re.match(r'^\s*(\d+)', line_text)
    if match:
        return int(match.group(1))
    return None


def calculate_midpoint(line_before: int, line_after: int) -> Optional[int]:
    """Calculate line number between two lines.

    Args:
        line_before: Line number before insertion point
        line_after: Line number after insertion point

    Returns:
        Midpoint line number, or None if no room

    Examples:
        >>> calculate_midpoint(10, 20)
        15
        >>> calculate_midpoint(10, 11)
        None
        >>> calculate_midpoint(10, 30)
        20
    """
    if line_after - line_before <= 1:
        return None  # No room
    return (line_before + line_after) // 2


def find_insert_line_number(
    line_before: int,
    line_after: Optional[int],
    increment: int = DEFAULT_INCREMENT
) -> int:
    """Find appropriate line number for insertion.

    Args:
        line_before: Line number before insertion point
        line_after: Line number after insertion point (None if at end)
        increment: Preferred increment

    Returns:
        Suggested line number for new line

    Examples:
        >>> find_insert_line_number(10, 30, 10)
        20
        >>> find_insert_line_number(10, 11, 10)
        11  # Will trigger renumber suggestion
        >>> find_insert_line_number(30, None, 10)
        40
    """
    # If at end of program
    if line_after is None:
        return line_before + increment

    # Try midpoint first
    midpoint = calculate_midpoint(line_before, line_after)
    if midpoint is not None:
        return midpoint

    # No room - use line_before + 1 (caller should detect and renumber)
    return line_before + 1


def needs_renumber_for_insert(
    line_before: int,
    line_after: Optional[int],
    lines_to_insert: int = 1,
    increment: int = DEFAULT_INCREMENT
) -> bool:
    """Check if renumber needed to make room for insertion.

    Args:
        line_before: Line before insertion point
        line_after: Line after insertion point (None if at end)
        lines_to_insert: How many lines to insert
        increment: Desired increment between lines

    Returns:
        True if renumber needed, False if room available
    """
    if line_after is None:
        return False  # At end, always room

    available_space = line_after - line_before - 1
    needed_space = lines_to_insert * increment

    return available_space < needed_space


def build_line_mapping(
    old_lines: List[int],
    new_start: int,
    old_start: int,
    increment: int
) -> Dict[int, int]:
    """Build mapping from old to new line numbers for renumbering.

    Args:
        old_lines: Sorted list of current line numbers
        new_start: First new line number
        old_start: First old line number to renumber (earlier lines unchanged)
        increment: Increment between new line numbers

    Returns:
        Dictionary mapping old_line_num -> new_line_num

    Examples:
        >>> build_line_mapping([10, 20, 30, 40], 100, 20, 10)
        {10: 10, 20: 100, 30: 110, 40: 120}
    """
    mapping = {}

    # Lines before old_start stay the same
    for line_num in old_lines:
        if line_num < old_start:
            mapping[line_num] = line_num

    # Lines from old_start onward get renumbered
    new_num = new_start
    for line_num in old_lines:
        if line_num >= old_start:
            mapping[line_num] = new_num
            new_num += increment

    return mapping


def update_line_references(code: str, line_mapping: Dict[int, int]) -> str:
    """Update GOTO/GOSUB/THEN/ELSE line number references in code.

    Uses regex-based approach (fast, good for most cases).

    Args:
        code: BASIC code line (without line number prefix)
        line_mapping: Dictionary of old_line -> new_line

    Returns:
        Code with updated line number references

    Examples:
        >>> mapping = {10: 100, 20: 200}
        >>> update_line_references("GOTO 10", mapping)
        'GOTO 100'
        >>> update_line_references("ON X GOTO 10,20", mapping)
        'ON X GOTO 100,200'
    """
    # Two-pattern approach (applied sequentially in a single pass):
    # Pattern 1: Match keyword + first line number (GOTO/GOSUB/THEN/ELSE/ON...GOTO/ON...GOSUB)
    # Pattern 2: Match comma-separated line numbers (for ON...GOTO/GOSUB lists)

    def replace_line_ref(match):
        keyword = match.group(1)
        old_target = int(match.group(2))
        new_target = line_mapping.get(old_target, old_target)
        return f'{keyword} {new_target}'

    # Match: keyword + space + line number
    # Keywords: GOTO, GOSUB, THEN, ELSE, or "ON <expr> GOTO/GOSUB"
    # Note: Pattern uses .+? (non-greedy) to match expression in ON statements,
    # which correctly handles edge cases like "ON FLAG GOTO" (variable starting with 'G'),
    # "ON X+Y GOTO" (expressions), and "ON A$ GOTO" (string variables)
    pattern = re.compile(
        r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+.+?\s+GOTO|ON\s+.+?\s+GOSUB)\s+(\d+)',
        re.IGNORECASE
    )

    code = pattern.sub(replace_line_ref, code)

    # Handle comma-separated line lists (ON...GOTO/GOSUB)
    # Match: comma + optional spaces + line number
    def replace_comma_line(match):
        old_target = int(match.group(1))
        new_target = line_mapping.get(old_target, old_target)
        return f',{new_target}'

    comma_pattern = re.compile(r',\s*(\d+)')
    code = comma_pattern.sub(replace_comma_line, code)

    return code


def renumber_program_lines(
    lines: Dict[int, str],
    new_start: int = DEFAULT_START,
    old_start: int = 0,
    increment: int = DEFAULT_INCREMENT
) -> Tuple[Dict[int, str], Dict[int, int]]:
    """Renumber program lines and update all line number references.

    Args:
        lines: Dictionary of line_number -> line_text
        new_start: New starting line number (default 10)
        old_start: First line to renumber (lines before unchanged, default 0)
        increment: Increment between lines (default 10)

    Returns:
        Tuple of (new_lines_dict, line_mapping)
        - new_lines_dict: Renumbered lines with updated references
        - line_mapping: Old line -> new line mapping

    Example:
        >>> lines = {10: "10 PRINT 'START'", 20: "20 GOTO 10"}
        >>> new_lines, mapping = renumber_program_lines(lines, 100, 0, 10)
        >>> new_lines[100]
        "100 PRINT 'START'"
        >>> new_lines[110]
        "110 GOTO 100"
    """
    if not lines:
        return {}, {}

    # Build line number mapping
    old_lines = sorted(lines.keys())
    line_mapping = build_line_mapping(old_lines, new_start, old_start, increment)

    # Renumber lines and update references
    new_lines = {}

    for old_num in old_lines:
        new_num = line_mapping[old_num]
        old_line_text = lines[old_num]

        # Extract code after line number
        match = re.match(r'^\s*\d+\s+(.*)$', old_line_text)
        if match:
            code = match.group(1)
        else:
            # Line has no code (just number?)
            code = ""

        # Update line number references in code
        updated_code = update_line_references(code, line_mapping)

        # Build new line with new number
        new_line_text = f'{new_num} {updated_code}' if updated_code else str(new_num)
        new_lines[new_num] = new_line_text

    return new_lines, line_mapping


def find_lines_needing_space(
    all_line_numbers: List[int],
    increment: int = DEFAULT_INCREMENT
) -> List[Tuple[int, int, int]]:
    """Find pairs of lines with insufficient space between them.

    Args:
        all_line_numbers: Sorted list of line numbers
        increment: Desired minimum increment

    Returns:
        List of (line_before, line_after, available_space) tuples
        where available_space < increment

    Example:
        >>> find_lines_needing_space([10, 11, 20, 30], increment=10)
        [(10, 11, 1)]
    """
    problems = []

    for i in range(len(all_line_numbers) - 1):
        line_before = all_line_numbers[i]
        line_after = all_line_numbers[i + 1]
        available = line_after - line_before - 1

        if available < increment:
            problems.append((line_before, line_after, available))

    return problems


def suggest_renumber_params(
    all_line_numbers: List[int],
    desired_increment: int = DEFAULT_INCREMENT
) -> Tuple[int, int, int]:
    """Suggest renumber parameters based on program size.

    Args:
        all_line_numbers: List of current line numbers
        desired_increment: Desired increment (default 10)

    Returns:
        Tuple of (new_start, old_start, increment)

    Examples:
        >>> suggest_renumber_params([10, 20, 30])
        (10, 0, 10)
        >>> suggest_renumber_params([5, 10, 15, 20] * 50)  # 200 lines
        (100, 0, 100)
    """
    line_count = len(all_line_numbers)

    # Choose increment based on program size
    if line_count < 50:
        increment = 10
    elif line_count < 200:
        increment = 20
    else:
        increment = 100

    # Use desired increment if specified
    if desired_increment and desired_increment > increment:
        increment = desired_increment

    # New start: keep it simple
    new_start = DEFAULT_START

    # Old start: renumber everything by default
    old_start = 0

    return new_start, old_start, increment


def parse_renum_args(args: str) -> Tuple[int, int, int]:
    """Parse RENUM command arguments.

    Args:
        args: Argument string, format: "new_start,old_start,increment"
              Can omit parameters (e.g., "100" or "100,,20")

    Returns:
        Tuple of (new_start, old_start, increment)

    Examples:
        >>> parse_renum_args("")
        (10, 0, 10)
        >>> parse_renum_args("100")
        (100, 0, 10)
        >>> parse_renum_args("100,50,20")
        (100, 50, 20)
        >>> parse_renum_args("100,,20")
        (100, 0, 20)
    """
    new_start = DEFAULT_START
    old_start = 0
    increment = DEFAULT_INCREMENT

    if not args or not args.strip():
        return new_start, old_start, increment

    parts = args.split(',')

    # Parse new_start
    if len(parts) >= 1 and parts[0].strip():
        new_start = int(parts[0].strip())

    # Parse old_start
    if len(parts) >= 2 and parts[1].strip():
        old_start = int(parts[1].strip())

    # Parse increment
    if len(parts) >= 3 and parts[2].strip():
        increment = int(parts[2].strip())

    return new_start, old_start, increment


def parse_delete_args(args: str, all_line_numbers: List[int]) -> Tuple[int, int]:
    """Parse DELETE command arguments.

    Args:
        args: Argument string, format: "start-end", "start", "-end", or "start-"
        all_line_numbers: List of existing line numbers for defaults

    Returns:
        Tuple of (start_line, end_line)

    Syntax:
        DELETE 40       - Delete single line 40
        DELETE 40-100   - Delete lines 40 through 100 (inclusive)
        DELETE -40      - Delete all lines up to and including 40
        DELETE 40-      - Delete from line 40 to end of program

    Examples:
        >>> parse_delete_args("40", [10, 20, 30, 40, 50])
        (40, 40)
        >>> parse_delete_args("40-100", [10, 20, 30, 40, 50, 60])
        (40, 100)
        >>> parse_delete_args("-40", [10, 20, 30, 40, 50])
        (10, 40)
        >>> parse_delete_args("40-", [10, 20, 30, 40, 50])
        (40, 50)
    """
    if not args or not args.strip():
        raise ValueError("DELETE requires line number or range")

    args = args.strip()

    # Get min and max for defaults
    min_line = min(all_line_numbers) if all_line_numbers else 0
    max_line = max(all_line_numbers) if all_line_numbers else 0

    # Check if it's a range
    if '-' in args:
        parts = args.split('-', 1)

        # DELETE -40 (from start to 40)
        if not parts[0]:
            start = min_line
            end = int(parts[1].strip())
        # DELETE 40- (from 40 to end)
        elif not parts[1]:
            start = int(parts[0].strip())
            end = max_line
        # DELETE 40-100 (range)
        else:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
    else:
        # DELETE 40 (single line)
        start = end = int(args)

    return start, end


def delete_line_range(
    lines: Dict[int, str],
    start: int,
    end: int
) -> Dict[int, str]:
    """Delete a range of lines from a program.

    Args:
        lines: Dictionary of line_number -> line_text
        start: First line number to delete (inclusive)
        end: Last line number to delete (inclusive)

    Returns:
        New dictionary with lines deleted

    Example:
        >>> lines = {10: "10 PRINT A", 20: "20 PRINT B", 30: "30 PRINT C"}
        >>> delete_line_range(lines, 10, 20)
        {30: "30 PRINT C"}
    """
    new_lines = {}
    for line_num, line_text in lines.items():
        if not (start <= line_num <= end):
            new_lines[line_num] = line_text
    return new_lines


def delete_lines_from_program(program_manager, args: str, runtime=None):
    """Delete lines from program using DELETE command syntax.

    This is the consolidated DELETE command implementation for all UIs.

    Args:
        program_manager: ProgramManager instance with .lines and .line_asts
        args: DELETE command arguments (e.g., "40", "40-100", "-40", "40-")
        runtime: Optional runtime object with statement_table to update

    Returns:
        List of deleted line numbers, or None if error

    Raises:
        ValueError: If arguments are invalid

    Examples:
        >>> deleted = delete_lines_from_program(pm, "40")  # Delete line 40
        >>> deleted = delete_lines_from_program(pm, "40-100")  # Delete range
        >>> deleted = delete_lines_from_program(pm, "-40")  # Delete from start
        >>> deleted = delete_lines_from_program(pm, "40-")  # Delete to end
    """
    if not hasattr(program_manager, 'lines') or not program_manager.lines:
        raise ValueError("No program to delete from")

    # Parse arguments
    all_line_numbers = sorted(program_manager.lines.keys())
    start, end = parse_delete_args(args, all_line_numbers)

    # Find lines in range
    to_delete = [n for n in all_line_numbers if start <= n <= end]

    if not to_delete:
        raise ValueError(f"No lines in range {start}-{end}")

    # Delete from lines dict
    for line_num in to_delete:
        if line_num in program_manager.lines:
            del program_manager.lines[line_num]

        # Delete from line_asts if present
        if hasattr(program_manager, 'line_asts') and line_num in program_manager.line_asts:
            del program_manager.line_asts[line_num]

        # Update runtime if provided
        if runtime:
            if hasattr(runtime, 'statement_table'):
                runtime.statement_table.delete_line(line_num)

    return to_delete


def list_files(filespec: str = ""):
    """List files matching filespec (FILES command implementation).

    This is the consolidated FILES command implementation for all UIs.

    Args:
        filespec: File pattern to match (e.g., "*.BAS", "*.txt")
                  Empty string means "*" (all files)

    Returns:
        List of tuples: (filename, size_bytes, is_dir)
        size_bytes is None if file cannot be accessed

    Examples:
        >>> files = list_files("*.bas")
        >>> for name, size, is_dir in files:
        ...     print(f"{name} - {size} bytes")
    """
    import glob
    import os

    # Default pattern if no argument
    if not filespec:
        pattern = "*"
    else:
        # Remove quotes if present
        pattern = filespec.strip().strip('"').strip("'")

        # If pattern is empty after stripping, use default
        if not pattern:
            pattern = "*"

    # Get matching files
    files = sorted(glob.glob(pattern))

    # Build result list
    result = []
    for filename in files:
        try:
            if os.path.isdir(filename):
                result.append((filename, None, True))
            elif os.path.isfile(filename):
                size = os.path.getsize(filename)
                result.append((filename, size, False))
            else:
                result.append((filename, None, False))
        except OSError:
            result.append((filename, None, False))

    return result


def renum_program(program_manager, args: str, renum_callback, runtime=None):
    """Renumber program lines and update GOTO/GOSUB references.

    This is the consolidated RENUM command implementation for all UIs.

    Args:
        program_manager: ProgramManager instance with .lines and .line_asts
        args: RENUM command arguments (e.g., "100", "100,0,10", "100,50")
        renum_callback: Function(stmt: StatementNode, line_map: Dict[int, int]) -> None
                        that updates statement line number references by directly modifying
                        the statement node's attributes (e.g., stmt.line_number for GOTO).
                        Called for ALL statements; callback is responsible for identifying and
                        updating statements with line number references (GOTO, GOSUB, ON GOTO,
                        ON GOSUB, IF THEN/ELSE line numbers). See update_statement_references()
                        in curses_ui.py for an example implementation.
        runtime: Optional runtime object to update with new line numbers

    Returns:
        Tuple of (old_lines, line_mapping) where:
            old_lines: List of original line numbers in order
            line_mapping: Dict mapping old line numbers to new line numbers

    Raises:
        ValueError: If arguments are invalid or program is empty

    Examples:
        >>> def update_refs(stmt, line_map):
        ...     # Update statement line number references
        ...     pass
        >>> old, mapping = renum_program(pm, "100, 0, 10", update_refs)
    """
    if not hasattr(program_manager, 'line_asts') or not program_manager.line_asts:
        raise ValueError("No program to renumber")

    # Parse arguments using existing helper
    new_start, old_start, increment = parse_renum_args(args)

    # Build line mapping using existing helper
    old_lines = sorted(program_manager.line_asts.keys())
    line_map = build_line_mapping(old_lines, new_start, old_start, increment)

    # Walk each line AST and update line number references
    for line_node in program_manager.line_asts.values():
        # Update line number references in statements using callback
        for stmt in line_node.statements:
            renum_callback(stmt, line_map)
        # Update the line's own number
        line_node.line_number = line_map[line_node.line_number]

    # Rebuild line_asts dict with new line numbers
    new_line_asts = {}
    new_lines = {}
    for old_num in old_lines:
        new_num = line_map[old_num]
        line_node = program_manager.line_asts[old_num]
        new_line_asts[new_num] = line_node
        # Serialize using ui_helpers
        new_lines[new_num] = serialize_line(line_node)

    # Update the program manager
    program_manager.line_asts = new_line_asts
    program_manager.lines = new_lines

    # Update runtime if provided
    if runtime:
        if hasattr(runtime, 'statement_table'):
            # Rebuild statement table from new line_asts
            runtime.statement_table.statements.clear()
            runtime.statement_table._keys_cache = None
            for line_node in new_line_asts.values():
                for stmt_offset, stmt in enumerate(line_node.statements):
                    from src.pc import PC
                    pc = PC(line_node.line_number, stmt_offset)
                    runtime.statement_table.add(pc, stmt)

    return old_lines, line_map


# ============================================================================
# Error Formatting and Display
# ============================================================================

def format_error_message(
    message: str,
    line_number: Optional[int] = None,
    line_text: Optional[str] = None,
    column: Optional[int] = None,
    mbasic_style: bool = True
) -> str:
    """Format an error message with optional line context and position indicator.

    Args:
        message: Error message text
        line_number: BASIC line number where error occurred
        line_text: Full text of the line with error
        column: Column position of error (1-indexed, absolute position)
        mbasic_style: If True, prefix with "?" like MBASIC 5.21

    Returns:
        Formatted error message string

    Examples:
        >>> format_error_message("Division by zero", 100)
        '?Error in 100: Division by zero'

        >>> format_error_message("Syntax error", 20, "20 PRINT X Y", 12)
        '''?Syntax error in 20
        20 PRINT X Y
                   ^'''
    """
    parts = []

    # Build error line
    if mbasic_style:
        parts.append("?")

    if line_number is not None:
        parts.append(f"{message} in {line_number}")
    else:
        parts.append(message)

    result = ''.join(parts)

    # Add line context and position indicator if available
    if line_text and column is not None:
        result += f"\n{line_text}"
        # Add caret indicator at error position
        # Column is 1-indexed, so adjust for 0-indexed string
        if column > 0:
            result += f"\n{' ' * (column - 1)}^"

    return result


def format_syntax_error(
    line_number: int,
    line_text: str,
    column: Optional[int] = None,
    specific_message: Optional[str] = None
) -> str:
    """Format a syntax error with line context.

    Args:
        line_number: BASIC line number with error
        line_text: Full line text
        column: Optional column position of error
        specific_message: Optional specific error detail

    Returns:
        Formatted error message

    Example:
        >>> format_syntax_error(100, "100 PRINT X Y", 13, "Expected : or newline")
        '''?Syntax error in 100: Expected : or newline
        100 PRINT X Y
                    ^'''
    """
    if specific_message:
        message = f"Syntax error: {specific_message}"
    else:
        message = "Syntax error"

    return format_error_message(message, line_number, line_text, column)


def format_runtime_error(
    error_code: int,
    error_message: str,
    line_number: Optional[int] = None
) -> str:
    """Format a runtime error in MBASIC style.

    Args:
        error_code: Error code number (e.g., 11 for division by zero)
        error_message: Human-readable error description
        line_number: Line where error occurred

    Returns:
        Formatted error message

    Example:
        >>> format_runtime_error(11, "Division by zero", 250)
        '?11 Error in 250: Division by zero'
    """
    if line_number is not None:
        return f"?{error_code} Error in {line_number}: {error_message}"
    else:
        return f"?{error_code} Error: {error_message}"


def get_relative_column(line_text: str, absolute_column: int) -> int:
    """Convert absolute column position to relative (after line number).

    Args:
        line_text: Full line text with line number
        absolute_column: Absolute column position (1-indexed)

    Returns:
        Relative column position (spaces after line number)

    Example:
        >>> get_relative_column("10 PRINT X", 4)
        1
        >>> get_relative_column("100 PRINT X", 5)
        1
    """
    # Extract line number
    match = re.match(r'^(\d+)(\s+)', line_text)
    if match:
        line_num_len = len(match.group(1))
        spaces_len = len(match.group(2))
        # Relative position = absolute - line_num_len - 1
        # (subtract 1 because columns are 1-indexed)
        return absolute_column - line_num_len - 1
    else:
        # No line number, absolute = relative
        return absolute_column


def get_absolute_column(line_text: str, relative_column: int) -> int:
    """Convert relative column position to absolute.

    Args:
        line_text: Full line text with line number
        relative_column: Relative column position (spaces after line number)

    Returns:
        Absolute column position (1-indexed)

    Example:
        >>> get_absolute_column("10 PRINT X", 1)
        4
        >>> get_absolute_column("100 PRINT X", 1)
        5
    """
    # Extract line number
    match = re.match(r'^(\d+)(\s+)', line_text)
    if match:
        line_num_len = len(match.group(1))
        # Absolute = line_num_len + relative + 1
        # (add 1 because columns are 1-indexed)
        return line_num_len + relative_column + 1
    else:
        # No line number, relative = absolute
        return relative_column


def create_error_indicator(
    line_text: str,
    column: int,
    length: int = 1,
    indicator_char: str = '^'
) -> str:
    """Create a visual error indicator line.

    Args:
        line_text: The line with the error
        column: Column position of error (1-indexed)
        length: Number of characters to underline
        indicator_char: Character to use for indicator (default: ^)

    Returns:
        String with spaces and indicator characters

    Examples:
        >>> create_error_indicator("10 PRINT X", 10, 1)
        '         ^'
        >>> create_error_indicator("10 PRINT HELLO", 10, 5, '~')
        '         ~~~~~'
    """
    if column < 1:
        column = 1

    # Create indicator: spaces up to column, then indicator chars
    spaces = ' ' * (column - 1)
    indicators = indicator_char * max(1, length)

    return spaces + indicators


def format_parse_error_with_context(
    line_text: str,
    error_message: str,
    column: Optional[int] = None,
    token_length: Optional[int] = None
) -> str:
    """Format a parse error with line context and visual indicator.

    Args:
        line_text: The line being parsed
        error_message: Error description
        column: Column where error occurred
        token_length: Length of problematic token (for multi-char underline)

    Returns:
        Multi-line formatted error message

    Example:
        >>> format_parse_error_with_context(
        ...     "100 PRINT X Y",
        ...     "Expected : or newline",
        ...     13
        ... )
        '''Parse error: Expected : or newline
        100 PRINT X Y
                    ^'''
    """
    result = f"Parse error: {error_message}\n{line_text}"

    if column is not None:
        length = token_length if token_length else 1
        indicator = create_error_indicator(line_text, column, length)
        result += f"\n{indicator}"

    return result


def standardize_error_format(error_str: str) -> str:
    """Standardize error message format across different sources.

    Converts various error formats to consistent MBASIC-style format.

    Args:
        error_str: Raw error message

    Returns:
        Standardized error message

    Examples:
        >>> standardize_error_format("Syntax error")
        '?Syntax error'
        >>> standardize_error_format("Parse error at line 1, column 5: Expected :")
        '?Parse error: Expected :'
    """
    # Already in MBASIC format
    if error_str.startswith('?'):
        return error_str

    # Remove "Parse error at line X, column Y:" prefix
    error_str = re.sub(r'^Parse error at line \d+, column \d+:\s*', '', error_str)

    # Remove "Parse error:" prefix if present
    error_str = re.sub(r'^Parse error:\s*', '', error_str)

    # Add ? prefix for MBASIC style
    return f"?{error_str}"


def extract_error_location(error_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract line and column numbers from error message.

    Args:
        error_str: Error message that may contain position info

    Returns:
        Tuple of (line_number, column_number) or (None, None)

    Examples:
        >>> extract_error_location("Parse error at line 5, column 10: message")
        (5, 10)
        >>> extract_error_location("?Syntax error in 100")
        (100, None)
    """
    # Try "Parse error at line X, column Y" format
    match = re.search(r'line (\d+), column (\d+)', error_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # Try "in line X" or "in X" format (BASIC line number)
    match = re.search(r'in (?:line )?(\d+)', error_str)
    if match:
        return (int(match.group(1)), None)

    return (None, None)


# ============================================================================
# AST Serialization
# ============================================================================

def serialize_line(line_node):
    """Serialize a LineNode back to source text, preserving indentation.

    Args:
        line_node: LineNode AST to serialize

    Returns:
        str: Source text for the line

    Example:
        >>> from parser import Parser
        >>> from lexer import Lexer
        >>> line = "20   PRINT I"
        >>> lexer = Lexer(line)
        >>> tokens = lexer.tokenize()
        >>> parser = Parser(tokens, {}, source=line)
        >>> ast = parser.parse_line()
        >>> serialize_line(ast)
        '20   PRINT i'
    """
    # Start with line number
    line_num_str = str(line_node.line_number)
    parts = [line_num_str]

    # Preserve RELATIVE indentation (spaces after line number) from original source
    # This ensures indentation survives RENUM when line numbers change width
    if line_node.statements:
        # Try to calculate relative indentation from source_text if available
        relative_indent = 1  # Default: single space (fallback if source_text unavailable)

        if hasattr(line_node, 'source_text') and line_node.source_text:
            # Extract original line number and count spaces after it
            match = re.match(r'^(\d+)(\s+)', line_node.source_text)
            if match:
                # Spaces after line number in original
                relative_indent = len(match.group(2))
            # Note: If source_text doesn't match pattern (or is unavailable), falls back to relative_indent=1.
            # When does this occur?
            # 1. Programmatically inserted lines (no source_text attribute)
            # 2. Lines where source_text doesn't start with line_number + spaces (edge case)
            # Result: These lines get single-space indentation instead of preserving original spacing.
            # This is expected behavior - programmatically inserted lines use standard formatting.

        # Apply the relative indentation
        parts.append(' ' * relative_indent)

        # Serialize each statement
        for i, stmt in enumerate(line_node.statements):
            stmt_text = serialize_statement(stmt)
            if i == 0:
                parts.append(stmt_text)
            else:
                # Check if this is an inline comment (REM or apostrophe)
                # Comments should have spacing before them, not colon separator
                if type(stmt).__name__ == 'RemarkStatementNode':
                    # Inline comment - use standard spacing (4 spaces), no colon
                    parts.append('    ' + stmt_text)
                else:
                    parts.append(' : ' + stmt_text)

    return ''.join(parts)


def serialize_statement(stmt):
    """Serialize a statement node back to source text.

    Args:
        stmt: Statement AST node to serialize

    Returns:
        str: Source text for the statement

    Example:
        >>> # Assume we have a PrintStatementNode
        >>> serialize_statement(print_stmt)
        'PRINT "HELLO"'
    """
    stmt_type = type(stmt).__name__

    if stmt_type == 'PrintStatementNode':
        parts = ['PRINT']
        for i, expr in enumerate(stmt.expressions):
            if i > 0 and i <= len(stmt.separators):
                # Add separator from previous expression
                sep = stmt.separators[i-1] if i-1 < len(stmt.separators) else ''
                if sep:
                    parts.append(sep)
            parts.append(' ' if not parts[-1].endswith(' ') else '')
            parts.append(serialize_expression(expr))
        return ''.join(parts)

    elif stmt_type == 'GotoStatementNode':
        return f"GOTO {stmt.line_number}"

    elif stmt_type == 'GosubStatementNode':
        return f"GOSUB {stmt.line_number}"

    elif stmt_type == 'LetStatementNode':
        var_text = serialize_variable(stmt.variable)
        expr_text = serialize_expression(stmt.expression)
        return f"{var_text} = {expr_text}"

    elif stmt_type == 'EndStatementNode':
        return "END"

    elif stmt_type == 'ReturnStatementNode':
        return "RETURN"

    elif stmt_type == 'StopStatementNode':
        return "STOP"

    elif stmt_type == 'RemarkStatementNode':
        # Preserve comments using original syntax (REM or ')
        # Note: REMARK is converted to REM during parsing, not here
        if stmt.comment_type == "APOSTROPHE":
            return f"' {stmt.text}"
        else:  # REM, REMARK, or default
            return f"REM {stmt.text}"

    elif stmt_type == 'IfStatementNode':
        parts = ['IF ', serialize_expression(stmt.condition)]
        if stmt.then_line_number is not None:
            parts.append(f' THEN {stmt.then_line_number}')
        elif stmt.then_statements:
            parts.append(' THEN ')
            parts.append(' : '.join(serialize_statement(s) for s in stmt.then_statements))
        if stmt.else_line_number is not None:
            parts.append(f' ELSE {stmt.else_line_number}')
        elif stmt.else_statements:
            parts.append(' ELSE ')
            parts.append(' : '.join(serialize_statement(s) for s in stmt.else_statements))
        return ''.join(parts)

    elif stmt_type == 'ForStatementNode':
        var = serialize_variable(stmt.variable)
        start = serialize_expression(stmt.start_expr)
        end = serialize_expression(stmt.end_expr)
        parts = [f"FOR {var} = {start} TO {end}"]
        if stmt.step_expr:
            step = serialize_expression(stmt.step_expr)
            parts.append(f" STEP {step}")
        return ''.join(parts)

    elif stmt_type == 'NextStatementNode':
        if stmt.variables:
            vars_text = ', '.join(serialize_variable(v) for v in stmt.variables)
            return f"NEXT {vars_text}"
        return "NEXT"

    elif stmt_type == 'OnGotoStatementNode':
        expr = serialize_expression(stmt.expression)
        lines = ','.join(str(line) for line in stmt.line_numbers)
        return f"ON {expr} GOTO {lines}"

    elif stmt_type == 'OnGosubStatementNode':
        expr = serialize_expression(stmt.expression)
        lines = ','.join(str(line) for line in stmt.line_numbers)
        return f"ON {expr} GOSUB {lines}"

    elif stmt_type == 'OnErrorStatementNode':
        if stmt.line_number is not None:
            return f"ON ERROR GOTO {stmt.line_number}"
        else:
            return "ON ERROR GOTO 0"

    elif stmt_type == 'ErrorStatementNode':
        error_code = serialize_expression(stmt.error_code)
        return f"ERROR {error_code}"

    elif stmt_type == 'WhileStatementNode':
        cond = serialize_expression(stmt.condition)
        return f"WHILE {cond}"

    elif stmt_type == 'WendStatementNode':
        return "WEND"

    # For unhandled statement types, raise an error to prevent silent data corruption
    # Prevention strategy: Explicitly fail (with ValueError) rather than silently omitting
    # statements during RENUM, which would corrupt the program.
    # Note: There is no compile-time verification that all AST statement types are handled.
    # If new statement types are added to the parser, they won't be caught until runtime
    # when RENUM is attempted on code containing them. This is acceptable because the error
    # is explicit and prevents corruption (better than silently dropping statements).
    else:
        from src.debug_logger import debug_log
        error_msg = f"Unhandled statement type '{stmt_type}' in serialize_statement() - cannot serialize during RENUM"
        debug_log(f"ERROR: {error_msg}")
        raise ValueError(error_msg)


def serialize_variable(var):
    """Serialize a variable reference.

    Args:
        var: VariableNode to serialize

    Returns:
        str: Variable reference text

    Example:
        >>> # Assume we have a VariableNode for "X$"
        >>> serialize_variable(var_node)
        'x$'
    """
    # Use original case if available, otherwise fall back to normalized name
    text = getattr(var, 'original_case', var.name) or var.name
    # Only add type suffix if it was explicit in the original source
    # Don't add suffixes that were inferred from DEF statements
    # Note: explicit_type_suffix is not always set (depends on parser implementation),
    # so getattr defaults to False if missing, preventing incorrect suffix output
    if var.type_suffix and getattr(var, 'explicit_type_suffix', False):
        text += var.type_suffix
    if var.subscripts:
        subs = ','.join(serialize_expression(sub) for sub in var.subscripts)
        text += f"({subs})"
    return text


def token_to_operator(token_type):
    """Convert a TokenType operator to its string representation.

    Args:
        token_type: TokenType enum value

    Returns:
        str: Operator string

    Example:
        >>> from tokens import TokenType
        >>> token_to_operator(TokenType.PLUS)
        '+'
    """
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
        TokenType.AND: 'AND',
        TokenType.OR: 'OR',
        TokenType.NOT: 'NOT',
        TokenType.MOD: 'MOD',
        TokenType.BACKSLASH: '\\',
    }

    return operator_map.get(token_type, str(token_type))


def serialize_expression(expr):
    """Serialize an expression node to source text.

    Args:
        expr: Expression AST node to serialize

    Returns:
        str: Expression source text

    Note:
        ERR and ERL are special system variables that are serialized without
        parentheses (e.g., "ERR" not "ERR()") when they appear as FunctionCallNode
        with no arguments, matching MBASIC 5.21 syntax.

    Example:
        >>> # Assume we have a NumberNode with value 100
        >>> serialize_expression(num_node)
        '100'
    """
    expr_type = type(expr).__name__

    if expr_type == 'NumberNode':
        # Preserve integer vs float representation
        # If the value is a whole number, show it without decimal point
        if isinstance(expr.value, float) and expr.value.is_integer():
            return str(int(expr.value))
        else:
            return str(expr.value)

    elif expr_type == 'StringNode':
        return f'"{expr.value}"'

    elif expr_type == 'VariableNode':
        return serialize_variable(expr)

    elif expr_type == 'BinaryOpNode':
        left = serialize_expression(expr.left)
        right = serialize_expression(expr.right)
        # Convert TokenType operator to string
        op_str = token_to_operator(expr.operator)
        return f"{left} {op_str} {right}"

    elif expr_type == 'UnaryOpNode':
        operand = serialize_expression(expr.operand)
        op_str = token_to_operator(expr.operator) if hasattr(expr.operator, 'name') else str(expr.operator)
        return f"{op_str}{operand}"

    elif expr_type == 'FunctionCallNode':
        # ERR and ERL are system variables (not functions) - serialize without ()
        # In BASIC: ERR returns error code, ERL returns error line (no parentheses)
        if expr.name in ('ERR', 'ERL') and len(expr.arguments) == 0:
            return expr.name
        args = ','.join(serialize_expression(arg) for arg in expr.arguments)
        return f"{expr.name}({args})"

    else:
        return "?"


def serialize_program(line_asts: Dict[int, 'LineNode']) -> Dict[int, str]:
    """Serialize all lines of a program from AST to text.

    Args:
        line_asts: Dictionary of line_number -> LineNode

    Returns:
        Dictionary of line_number -> line_text

    Example:
        >>> serialized = serialize_program(program.line_asts)
        >>> for line_num in sorted(serialized.keys()):
        ...     print(serialized[line_num])
    """
    result = {}
    for line_num in sorted(line_asts.keys()):
        line_node = line_asts[line_num]
        result[line_num] = serialize_line(line_node)
    return result
