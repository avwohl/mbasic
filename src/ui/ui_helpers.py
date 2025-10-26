"""
UI Helper Functions - Portable logic for all UIs

This module contains UI-agnostic helper functions that can be used by
any UI (CLI, Tk, Web, Curses). No UI-specific dependencies allowed.

Functions for:
- Line renumbering with GOTO/GOSUB reference updates
- Smart line insertion with gap calculation
- Line number validation and utilities
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
    # Pattern matches: GOTO/GOSUB/THEN/ELSE followed by line numbers
    # Also handles: ON <expr> GOTO/GOSUB
    # Also handles: IF...THEN line_num, IF...ELSE line_num

    def replace_line_ref(match):
        keyword = match.group(1)
        old_target = int(match.group(2))
        new_target = line_mapping.get(old_target, old_target)
        return f'{keyword} {new_target}'

    # Match: keyword + space + line number
    # Keywords: GOTO, GOSUB, THEN, ELSE, or "ON <expr> GOTO/GOSUB"
    pattern = re.compile(
        r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+[^G]+\s+GOTO|ON\s+[^G]+\s+GOSUB)\s+(\d+)',
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
