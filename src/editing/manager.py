"""Program manager for MBASIC interpreter.

Manages program lines, ASTs, parsing, and file operations.
Extracted from InteractiveMode to enable reuse across all UIs (CLI, Curses, Tk, Web).
Note: This module uses direct filesystem access which does not work in web environments.
Web UI LOAD/SAVE commands are not yet implemented (would require FileIO integration).

FILE I/O ARCHITECTURE:
This manager provides direct Python file I/O methods (load_from_file, save_to_file)
for loading/saving .BAS program files. Used by both UI menus and BASIC commands.

Current implementation (LOCAL UIs):
- LOAD/SAVE/MERGE commands (interactive.py) call ProgramManager methods directly
- UI menu operations (File > Open/Save) also call ProgramManager methods directly
- Local UIs (CLI, Curses, Tk) use direct filesystem access via ProgramManager
- Cross-platform compiler paths are hardcoded (e.g., the uc80 library directory,
  or the z88dk snap path when building with the alternate toolchain)

Planned improvements:
- FileIO (src/file_io.py) - Abstraction layer for cross-platform support
  - RealFileIO: direct filesystem access for local UIs
  - SandboxedFileIO: in-memory virtual filesystem for web UI (not yet integrated)
  - Would support configurable compiler paths and cross-platform file access

Web UI limitation:
- Web UI currently does not support LOAD/SAVE commands (would require async refactor)
- Would need to use SandboxedFileIO for in-memory session-based file storage

Related filesystem abstractions:
1. FileSystemProvider (src/filesystem/base.py) - For runtime BASIC file I/O
   - Used during program execution (OPEN, INPUT#, PRINT#, CLOSE, etc.)
   - Separate from program loading (LOAD/SAVE which load .BAS source files)

2. CodeGenBackend (src/codegen_backend.py) - For compiler path handling
   - Currently hardcodes toolchain paths (uc80's library directory, and the
     z88dk snap path) - temporary until FileIO integration

ProgramManager.load_from_file() returns (success, errors) tuple where errors
is a list of (line_number, error_message) tuples for direct UI error reporting.
This integrated parsing + error reporting is why LOAD commands currently bypass
the FileIO abstraction and call ProgramManager directly.
"""

import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from src.input_sanitizer import sanitize_and_clear_parity
from src.lexer import Lexer, LexerOverflow, create_keyword_case_manager, tokenize
from src.parser import Parser
from src.debug_logger import debug_log


def _lines_until_eof_mark(f):
    """Yield lines from f, stopping at the CP/M end of file mark (^Z, 0x1A).

    Text before the mark on the same line is kept. Real MBASIC treats ^Z as
    end of file, and CP/M files are often padded with it.
    """
    for line in f:
        if '\x1a' in line:
            line = line.split('\x1a', 1)[0]
            if line:
                yield line
            return
        yield line


class ProgramManager:
    """Manages BASIC program lines and ASTs.

    This class handles:
    - Line storage (line_number -> text)
    - AST storage (line_number -> parsed LineNode)
    - Parsing (with error handling)
    - File operations (SAVE, LOAD, MERGE)
    - Line editing (NEW, DELETE, RENUM)

    Usage:
        # Create manager with DEF type map
        manager = ProgramManager(def_type_map)

        # Add lines
        success = manager.add_line(10, "10 PRINT \"HELLO\"")

        # Save/load
        manager.save_to_file("program.bas")
        manager.load_from_file("program.bas")
        manager.merge_from_file("overlay.bas")  # Merges without clearing

        # Get program AST for execution
        program_ast = manager.get_program_ast()
    """

    def __init__(self, def_type_map: dict):
        """Initialize program manager.

        Args:
            def_type_map: Dictionary mapping first letter to TypeInfo
                         (from DEFINT/DEFSNG/DEFDBL/DEFSTR statements)
        """
        self.lines: Dict[int, str] = {}  # line_number -> line_text
        self.line_asts: Dict[int, 'LineNode'] = {}  # line_number -> parsed AST
        self.def_type_map = def_type_map
        self.current_file: Optional[str] = None
        #: Bare messages MBASIC prints while a line is entered without
        #: rejecting it ("Overflow" for a literal such as 1E39).
        self.notices: List[str] = []

    def take_notices(self) -> List[str]:
        """The messages gathered since the last call, oldest first."""
        notices, self.notices = self.notices, []
        return notices

    def add_line(self, line_number: int, line_text: str) -> Tuple[bool, Optional[str]]:
        """Add or replace a program line.

        Args:
            line_number: BASIC line number
            line_text: Complete line text including line number

        Returns:
            Tuple of (success, error_message)
            success: True if line parsed successfully
            error_message: Error message if parsing failed, None otherwise
        """
        # Parse the line
        line_ast, error = self.parse_single_line(line_text, line_number)

        if line_ast is None:
            # Parse error - don't add the line
            return (False, error)

        # Store line text and AST
        self.lines[line_number] = line_text
        self.line_asts[line_number] = line_ast
        return (True, None)

    def delete_line(self, line_number: int) -> bool:
        """Delete a single line.

        Args:
            line_number: Line number to delete

        Returns:
            True if line existed and was deleted, False if line didn't exist
        """
        if line_number in self.lines:
            del self.lines[line_number]
            if line_number in self.line_asts:
                del self.line_asts[line_number]
            return True
        return False

    def delete_range(self, start: int, end: int) -> int:
        """Delete a range of lines (inclusive).

        Args:
            start: Starting line number
            end: Ending line number

        Returns:
            Number of lines deleted
        """
        count = 0
        line_numbers = sorted(self.lines.keys())
        for ln in line_numbers:
            if start <= ln <= end:
                self.delete_line(ln)
                count += 1
        return count

    def clear(self) -> None:
        """Clear all lines (NEW command)."""
        self.lines.clear()
        self.line_asts.clear()
        self.current_file = None

    def get_line(self, line_number: int) -> Optional[str]:
        """Get line text by line number.

        Args:
            line_number: Line number

        Returns:
            Line text or None if line doesn't exist
        """
        return self.lines.get(line_number)

    def get_lines(self, start: Optional[int] = None, end: Optional[int] = None) -> List[Tuple[int, str]]:
        """Get lines in range, sorted by line number.

        Args:
            start: Starting line number (None = from beginning)
            end: Ending line number (None = to end)

        Returns:
            List of (line_number, line_text) tuples, sorted
        """
        line_numbers = sorted(self.lines.keys())
        result = []

        for ln in line_numbers:
            if start is not None and ln < start:
                continue
            if end is not None and ln > end:
                break
            result.append((ln, self.lines[ln]))

        return result

    def get_all_line_numbers(self) -> List[int]:
        """Get all line numbers, sorted.

        Returns:
            List of line numbers in ascending order
        """
        return sorted(self.lines.keys())

    def renumber(self, new_start: int, old_start: int, increment: int) -> List[str]:
        """Renumber lines (RENUM command).

        Edits the text of each line, so only the line numbers and the digits
        of line number references change, as in MBASIC 5.21 (see
        src/renum.py).  The changed lines are parsed again.

        Args:
            new_start: New starting line number
            old_start: Old starting line number (lines before this are unchanged)
            increment: Increment between new line numbers

        Returns:
            Messages "Undefined line n in m" for references to missing lines
            (those references are left as they are)

        Raises:
            RenumError: "Illegal function call" if the new numbers would
                overlap a line that stays or go above 65529
        """
        from src.ui.ui_helpers import renum_program

        messages: List[str] = []
        renum_program(self, f"{new_start},{old_start},{increment}",
                      messages=messages)
        return messages

    def save_to_file(self, filename: str) -> None:
        """Save program to file.

        Args:
            filename: Path to file

        Raises:
            IOError: If file cannot be written
        """
        with open(filename, 'w') as f:
            for line_number in sorted(self.lines.keys()):
                f.write(self.lines[line_number] + '\n')

        self.current_file = filename

    def load_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]]]:
        """Load program from file.

        Args:
            filename: Path to file

        Returns:
            Tuple of (success, errors)
            success: True if at least one line loaded successfully
            errors: List of (BASIC line number, diagnostic) for rejected lines.
                Diagnostics include filename and physical file line; number 0
                denotes an unnumbered line or file-level error.

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        # Clear existing program
        self.clear()
        self.notices = []

        errors = []
        success_count = 0

        with open(filename, 'r') as f:
            for file_line, line in enumerate(_lines_until_eof_mark(f), 1):
                line = line.strip()
                if not line:
                    continue

                # Sanitize input: clear parity bits and filter control characters
                line, was_modified = sanitize_and_clear_parity(line)

                # Extract line number
                match = re.match(r'^(\d+)', line)
                if not match:
                    errors.append((0, f'{filename}: file line {file_line}: expected a BASIC line number'))
                    continue

                line_num = int(match.group(1))
                if not line[match.end():].strip():
                    # Bare line number: like typing it, this deletes the line
                    self.delete_line(line_num)
                    success_count += 1
                    continue
                success, error = self.add_line(line_num, line)

                if success:
                    success_count += 1
                else:
                    errors.append((line_num, f'{filename}: file line {file_line}, BASIC line {line_num}: {error}'))

        if success_count > 0:
            self.current_file = filename
            return (True, errors)
        else:
            if not errors:
                errors.append((0, f'{filename}: No numbered program lines found'))
            return (False, errors)

    def merge_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]], int, int]:
        """Merge program from file into current program.

        Lines from file are added to or replace existing lines.
        Does NOT clear existing program (unlike load_from_file).

        Args:
            filename: Path to file

        Returns:
            Tuple of (success, errors, lines_added, lines_replaced)
            success: True if at least one line loaded successfully
            errors: List of (BASIC line number, diagnostic) for rejected lines.
                Diagnostics include filename and physical file line; number 0
                denotes an unnumbered line or file-level error.
            lines_added: Count of new lines added
            lines_replaced: Count of existing lines replaced

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        errors = []
        lines_added = 0
        lines_replaced = 0
        lines_deleted = 0

        with open(filename, 'r') as f:
            for file_line, line in enumerate(_lines_until_eof_mark(f), 1):
                line = line.strip()
                if not line:
                    continue

                # Sanitize input: clear parity bits and filter control characters
                line, was_modified = sanitize_and_clear_parity(line)

                # Extract line number
                match = re.match(r'^(\d+)', line)
                if not match:
                    errors.append((0, f'{filename}: file line {file_line}: expected a BASIC line number'))
                    continue

                line_num = int(match.group(1))
                if not line[match.end():].strip():
                    # Bare line number: like typing it, this deletes the line
                    self.delete_line(line_num)
                    lines_deleted += 1
                    continue

                # Check if line already exists
                is_replacement = line_num in self.lines

                success, error = self.add_line(line_num, line)

                if success:
                    if is_replacement:
                        lines_replaced += 1
                    else:
                        lines_added += 1
                else:
                    errors.append((line_num, f'{filename}: file line {file_line}, BASIC line {line_num}: {error}'))

        total_success = lines_added + lines_replaced
        if total_success > 0 or lines_deleted > 0:
            return (True, errors, lines_added, lines_replaced)
        else:
            if not errors:
                errors.append((0, f'{filename}: No numbered program lines found'))
            return (False, errors, 0, 0)

    def get_program_ast(self) -> 'ProgramNode':
        """Build ProgramNode from current lines for execution.

        Returns:
            ProgramNode containing all LineNodes in order
        """
        from src.ast_nodes import ProgramNode

        # Get line ASTs in sorted order
        line_numbers = sorted(self.line_asts.keys())
        lines = [self.line_asts[ln] for ln in line_numbers]

        return ProgramNode(lines=lines, def_type_statements=self.def_type_map)

    def parse_single_line(self, line_text: str, basic_line_num: Optional[int] = None) -> Tuple[Optional['LineNode'], Optional[str]]:
        """Parse a single line into a LineNode AST.

        Args:
            line_text: The text of the line to parse
            basic_line_num: Optional BASIC line number for error reporting

        Returns:
            Tuple of (LineNode, error_message)
            LineNode: Parsed AST or None if parse failed
            error_message: Error message if parsing failed, None otherwise
        """
        try:
            debug_log(f"parse_single_line: {repr(line_text)}", level=2)
            lexer = Lexer(line_text, keyword_case_manager=create_keyword_case_manager())
            tokens = list(lexer.tokenize())
            parser = Parser(tokens, self.def_type_map, source=line_text)
            line_node = parser.parse_line()
            if lexer.overflow_literals:
                # 1E39: MBASIC says Overflow as the line is entered and stores
                # machine infinity in its place.
                self.notices.append("Overflow")
            return (line_node, None)

        except LexerOverflow:
            # &H10000 and the like: MBASIC refuses the line with Overflow
            # rather than Syntax error.
            full_error = ("Overflow in %d" % basic_line_num
                          if basic_line_num is not None else "Overflow")
            return (None, full_error)

        except Exception as e:
            # Strip "Parse error at line X, " from parser error messages
            error_msg = str(e)
            # Remove "Parse error at line N, " prefix if present (we show BASIC line number)
            error_msg = re.sub(r'^Parse error at line \d+, ', '', error_msg)

            if basic_line_num is not None:
                full_error = f"Syntax error in {basic_line_num}: {error_msg}"
            else:
                full_error = f"Syntax error: {error_msg}"

            debug_log(f"parse_single_line error for {repr(line_text)}: {full_error}", level=1)
            return (None, full_error)

    def has_lines(self) -> bool:
        """Check if program has any lines.

        Returns:
            True if program has at least one line
        """
        return len(self.lines) > 0

    def line_count(self) -> int:
        """Get number of lines in program.

        Returns:
            Number of lines
        """
        return len(self.lines)
