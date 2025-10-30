"""
Abstract Syntax Tree (AST) node definitions for MBASIC 5.21
"""

from typing import List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from src.tokens import TokenType, Token


# ============================================================================
# Type System
# ============================================================================

class VarType(Enum):
    """Variable type enumeration for BASIC variables"""
    INTEGER = 'INTEGER'  # % suffix or DEFINT
    SINGLE = 'SINGLE'    # ! suffix or DEFSNG (default)
    DOUBLE = 'DOUBLE'    # # suffix or DEFDBL
    STRING = 'STRING'    # $ suffix or DEFSTR


# ============================================================================
# Base Classes
# ============================================================================

class Node:
    """Base class for all AST nodes"""
    def __init__(self, line_num: int = 0, column: int = 0):
        self.line_num = line_num
        self.column = column


# ============================================================================
# Program Structure
# ============================================================================

@dataclass
class ProgramNode:
    """Root node of the AST - represents entire program"""
    lines: List['LineNode']
    def_type_statements: dict  # Global DEF type mappings
    line_num: int = 0
    column: int = 0


@dataclass
class LineNode:
    """A single line in a BASIC program (line_number + statements)

    The AST is the single source of truth. Text is always regenerated from
    the AST using token positions. Never store source_text - it creates
    a duplicate copy that gets out of sync.
    """
    line_number: int
    statements: List['StatementNode']
    line_num: int = 0
    column: int = 0


# ============================================================================
# Statements
# ============================================================================

@dataclass
class StatementNode:
    """Base class for all statements"""
    line_num: int = 0
    column: int = 0
    char_start: int = 0  # Character offset from start of line for highlighting
    char_end: int = 0    # Character offset end position for highlighting


@dataclass
class PrintStatementNode:
    """PRINT statement - output to screen or file

    Syntax:
        PRINT expr1, expr2          - Print to screen
        PRINT #filenum, expr1       - Print to file
    """
    expressions: List['ExpressionNode']
    separators: List[str]  # ";" or "," or None for newline
    file_number: Optional['ExpressionNode'] = None  # For PRINT #n, ...
    line_num: int = 0
    column: int = 0
    keyword_token: Optional[Token] = None  # Token for PRINT keyword (for case handling)


@dataclass
class PrintUsingStatementNode:
    """PRINT USING statement - formatted output to screen or file

    Syntax:
        PRINT USING format$; expr1; expr2          - Print to screen
        PRINT #filenum, USING format$; expr1       - Print to file
    """
    format_string: 'ExpressionNode'  # Format string expression
    expressions: List['ExpressionNode']  # Values to format
    file_number: Optional['ExpressionNode'] = None  # For PRINT #n, USING...
    line_num: int = 0
    column: int = 0


@dataclass
class LprintStatementNode:
    """LPRINT statement - output to line printer

    Syntax:
        LPRINT expr1, expr2         - Print to printer
        LPRINT #filenum, expr1      - Print to file (rare but valid)
    """
    expressions: List['ExpressionNode']
    separators: List[str]  # ";" or "," or None for newline
    file_number: Optional['ExpressionNode'] = None  # For LPRINT #n, ...
    line_num: int = 0
    column: int = 0


@dataclass
class InputStatementNode:
    """INPUT statement - read from keyboard or file

    Syntax:
        INPUT var1, var2           - Read from keyboard (shows "? ")
        INPUT "prompt", var1       - Read with prompt (shows "prompt? ")
        INPUT "prompt"; var1       - Read with prompt (shows "prompt? ")
        INPUT; var1                - Read without prompt (no "?")
        INPUT #filenum, var1       - Read from file

    Note: Both comma and semicolon after prompt show "?" in real MBASIC.
    Only INPUT; (semicolon immediately after INPUT) suppresses the "?".
    """
    prompt: Optional['ExpressionNode']
    variables: List['VariableNode']
    file_number: Optional['ExpressionNode'] = None  # For INPUT #n, ...
    suppress_question: bool = False  # True if INPUT; (semicolon immediately after INPUT)
    line_num: int = 0
    column: int = 0


@dataclass
class LetStatementNode:
    """LET or implicit assignment statement"""
    variable: 'VariableNode'
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class IfStatementNode:
    """IF statement with optional THEN and ELSE"""
    condition: 'ExpressionNode'
    then_statements: List['StatementNode']
    then_line_number: Optional[int]  # For IF...THEN line_number GOTO style
    else_statements: Optional[List['StatementNode']]
    else_line_number: Optional[int]
    line_num: int = 0
    column: int = 0
    keyword_token: Optional[Token] = None  # Token for IF keyword
    then_token: Optional[Token] = None     # Token for THEN keyword
    else_token: Optional[Token] = None     # Token for ELSE keyword (if present)


@dataclass
class ForStatementNode:
    """FOR loop statement"""
    variable: 'VariableNode'
    start_expr: 'ExpressionNode'
    end_expr: 'ExpressionNode'
    step_expr: Optional['ExpressionNode']  # Default is 1
    line_num: int = 0
    column: int = 0
    keyword_token: Optional[Token] = None  # Token for FOR keyword
    to_token: Optional[Token] = None       # Token for TO keyword
    step_token: Optional[Token] = None     # Token for STEP keyword (if present)


@dataclass
class NextStatementNode:
    """NEXT statement - end of FOR loop"""
    variables: List['VariableNode']  # Can be NEXT I or NEXT I,J,K
    line_num: int = 0
    column: int = 0


@dataclass
class WhileStatementNode:
    """WHILE loop statement"""
    condition: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WendStatementNode:
    """WEND statement - end of WHILE loop"""
    line_num: int = 0
    column: int = 0


@dataclass
class GotoStatementNode:
    """GOTO statement - unconditional jump"""
    line_number: int
    line_num: int = 0
    column: int = 0


@dataclass
class GosubStatementNode:
    """GOSUB statement - call subroutine at line number"""
    line_number: int
    line_num: int = 0
    column: int = 0


@dataclass
class ReturnStatementNode:
    """RETURN statement - return from GOSUB"""
    line_num: int = 0
    column: int = 0


@dataclass
class OnGotoStatementNode:
    """ON...GOTO statement - computed GOTO"""
    expression: 'ExpressionNode'
    line_numbers: List[int]
    line_num: int = 0
    column: int = 0


@dataclass
class OnGosubStatementNode:
    """ON...GOSUB statement - computed GOSUB"""
    expression: 'ExpressionNode'
    line_numbers: List[int]
    line_num: int = 0
    column: int = 0


@dataclass
class DimStatementNode:
    """DIM statement - declare array dimensions"""
    arrays: List['ArrayDeclNode']
    line_num: int = 0
    column: int = 0
    token: Optional[Any] = None  # Token for tracking access time


@dataclass
class EraseStatementNode:
    """ERASE statement - delete array(s) to reclaim memory

    Syntax:
        ERASE array1, array2, ...

    Example:
        ERASE A, B$, C
    """
    array_names: List[str]  # Just the array names, not full variable nodes
    line_num: int = 0
    column: int = 0


@dataclass
class MidAssignmentStatementNode:
    """MID$ statement - assign to substring of string variable

    Syntax:
        MID$(string_var, start, length) = value

    Example:
        MID$(A$, 3, 5) = "HELLO"
        MID$(P$(I), J, 1) = " "
    """
    string_var: 'ExpressionNode'  # String variable (can be array element)
    start: 'ExpressionNode'  # Starting position (1-based)
    length: 'ExpressionNode'  # Number of characters to replace
    value: 'ExpressionNode'  # Value to assign
    line_num: int = 0
    column: int = 0


@dataclass
class ArrayDeclNode:
    """Array declaration in DIM statement"""
    name: str
    dimensions: List['ExpressionNode']  # Must be constant expressions in compiled BASIC
    line_num: int = 0
    column: int = 0


@dataclass
class DefTypeStatementNode:
    """DEFINT/DEFSNG/DEFDBL/DEFSTR statement

    Defines default types for variables based on their first letter.
    Example: DEFINT I-K makes all variables starting with I, J, K default to INTEGER.
    """
    var_type: VarType  # Variable type (VarType.INTEGER, SINGLE, DOUBLE, or STRING)
    letters: Set[str]  # Set of lowercase letters affected by this declaration
    line_num: int = 0
    column: int = 0


@dataclass
class ReadStatementNode:
    """READ statement - read from DATA"""
    variables: List['VariableNode']
    line_num: int = 0
    column: int = 0


@dataclass
class DataStatementNode:
    """DATA statement - stores data values"""
    values: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class RestoreStatementNode:
    """RESTORE statement - reset DATA pointer"""
    line_number: Optional[int]
    line_num: int = 0
    column: int = 0


@dataclass
class OpenStatementNode:
    """OPEN statement - open file for I/O"""
    mode: str  # "I", "O", "R", "A"
    file_number: 'ExpressionNode'
    filename: 'ExpressionNode'
    record_length: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class CloseStatementNode:
    """CLOSE statement - close file(s)"""
    file_numbers: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class ResetStatementNode:
    """RESET statement - close all open files

    Syntax:
        RESET

    Example:
        RESET
    """
    line_num: int = 0
    column: int = 0


@dataclass
class KillStatementNode:
    """KILL statement - delete file

    Syntax:
        KILL filename$

    Example:
        KILL "TEMP.DAT"
        KILL F$
    """
    filename: 'ExpressionNode'  # String expression with filename
    line_num: int = 0
    column: int = 0


@dataclass
class ChainStatementNode:
    """CHAIN statement - chain to another BASIC program

    Syntax:
        CHAIN [MERGE] filename$ [, [line_number] [, ALL] [, DELETE range]]

    Examples:
        CHAIN "MENU"                    # Load and run MENU
        CHAIN "PROG", 1000              # Start at line 1000
        CHAIN "PROG", , ALL             # Pass all variables
        CHAIN MERGE "OVERLAY"           # Merge as overlay
        CHAIN MERGE "SUB", 1000, ALL, DELETE 100-200  # Full syntax
    """
    filename: 'ExpressionNode'  # String expression with filename
    start_line: 'ExpressionNode' = None  # Optional starting line number
    merge: bool = False  # True if MERGE option specified
    all_flag: bool = False  # True if ALL option specified (pass all variables)
    delete_range: tuple = None  # (start, end) for DELETE option, or None
    line_num: int = 0
    column: int = 0


@dataclass
class NameStatementNode:
    """NAME statement - rename file

    Syntax:
        NAME oldfile$ AS newfile$

    Example:
        NAME "TEMP.DAT" AS "FINAL.DAT"
        NAME L$ AS L$
    """
    old_filename: 'ExpressionNode'  # String expression with old filename
    new_filename: 'ExpressionNode'  # String expression with new filename
    line_num: int = 0
    column: int = 0


@dataclass
class LsetStatementNode:
    """LSET statement - left-justify string in field variable

    Syntax:
        LSET field_var = string_expr

    Used with random access files to assign data to FIELDed variables.
    Left-justifies and pads with spaces.

    Example:
        LSET A$ = B$
        LSET NAME$ = "JOHN"
    """
    variable: 'VariableNode'
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class RsetStatementNode:
    """RSET statement - right-justify string in field variable

    Syntax:
        RSET field_var = string_expr

    Used with random access files to assign data to FIELDed variables.
    Right-justifies and pads with spaces.

    Example:
        RSET A$ = B$
        RSET AMOUNT$ = STR$(BALANCE)
    """
    variable: 'VariableNode'
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class EndStatementNode:
    """END statement - terminate program"""
    line_num: int = 0
    column: int = 0


@dataclass
class StopStatementNode:
    """STOP statement - halt execution (for debugging)"""
    line_num: int = 0
    column: int = 0


@dataclass
class TronStatementNode:
    """TRON statement - enable execution trace (shows line numbers)"""
    line_num: int = 0
    column: int = 0


@dataclass
class TroffStatementNode:
    """TROFF statement - disable execution trace"""
    line_num: int = 0
    column: int = 0


@dataclass
class ClsStatementNode:
    """CLS statement - clear screen (no-op for compatibility)"""
    line_num: int = 0
    column: int = 0


@dataclass
class SystemStatementNode:
    """SYSTEM statement - return control to operating system

    Syntax:
        SYSTEM    - Exit BASIC and return to OS

    Similar to END but specifically returns to the operating system
    (commonly used in CP/M and MS-DOS BASIC variants)
    """
    line_num: int = 0
    column: int = 0


@dataclass
class LimitsStatementNode:
    """LIMITS statement - display resource usage information

    Syntax:
        LIMITS    - Display current resource usage and limits

    Shows memory usage, stack depths, execution time, and other resource information.
    """
    line_num: int = 0
    column: int = 0


@dataclass
class ShowSettingsStatementNode:
    """SHOWSETTINGS statement - display current settings

    Syntax:
        SHOWSETTINGS          - Display all settings
        SHOWSETTINGS filter   - Display settings matching filter (e.g., "editor")

    Shows current setting values with optional filter prefix.
    """
    filter: Optional[Any] = None  # Optional filter expression
    line_num: int = 0
    column: int = 0


@dataclass
class SetSettingStatementNode:
    """SETSETTING statement - modify a setting value

    Syntax:
        SETSETTING key value  - Set setting to value

    Example:
        SETSETTING editor.auto_number_step 100
    """
    key: Any  # Key expression (string)
    value: Any  # Value expression
    line_num: int = 0
    column: int = 0


@dataclass
class RunStatementNode:
    """RUN statement - execute program or line

    Syntax:
        RUN                - Restart current program from beginning
        RUN line_number    - Start execution at specific line number
        RUN "filename"     - Load and run another program file
    """
    target: Optional['ExpressionNode']  # Filename (string) or line number, None = restart
    line_num: int = 0
    column: int = 0


@dataclass
class LoadStatementNode:
    """LOAD statement - load program from disk

    Syntax:
        LOAD "filename"    - Load program file
        LOAD "filename",R  - Load and run program file
    """
    filename: 'ExpressionNode'  # String expression with filename
    run_flag: bool = False      # True if ,R option specified
    line_num: int = 0
    column: int = 0


@dataclass
class SaveStatementNode:
    """SAVE statement - save program to disk

    Syntax:
        SAVE "filename"    - Save program file
        SAVE "filename",A  - Save as ASCII text
    """
    filename: 'ExpressionNode'  # String expression with filename
    ascii_flag: bool = False    # True if ,A option specified
    line_num: int = 0
    column: int = 0


@dataclass
class MergeStatementNode:
    """MERGE statement - merge program from disk into current program

    Syntax:
        MERGE "filename"   - Merge program file
    """
    filename: 'ExpressionNode'  # String expression with filename
    line_num: int = 0
    column: int = 0


@dataclass
class NewStatementNode:
    """NEW statement - clear program and variables

    Syntax:
        NEW    - Clear everything and start fresh
    """
    line_num: int = 0
    column: int = 0


@dataclass
class DeleteStatementNode:
    """DELETE statement - delete range of program lines

    Syntax:
        DELETE start-end   - Delete lines from start to end
        DELETE -end        - Delete from beginning to end
        DELETE start-      - Delete from start to end of program
    """
    start: 'ExpressionNode'  # Start line number (or None for beginning)
    end: 'ExpressionNode'    # End line number (or None for end)
    line_num: int = 0
    column: int = 0


@dataclass
class RenumStatementNode:
    """RENUM statement - renumber program lines

    Syntax:
        RENUM                              - Renumber starting at 10, increment 10
        RENUM new_start                    - Renumber starting at new_start, increment 10
        RENUM new_start,old_start          - Renumber from old_start onwards
        RENUM new_start,old_start,increment - Full control over renumbering

    Parameters can be omitted using commas:
        RENUM 100,,20  - new_start=100, old_start=0 (default), increment=20
        RENUM ,50,20   - new_start=10 (default), old_start=50, increment=20
    """
    new_start: 'ExpressionNode' = None  # New starting line number (default 10)
    old_start: 'ExpressionNode' = None  # First old line to renumber (default 0)
    increment: 'ExpressionNode' = None  # Increment (default 10)
    line_num: int = 0
    column: int = 0


@dataclass
class FilesStatementNode:
    """FILES statement - display directory listing

    Syntax:
        FILES            - List all .bas files
        FILES filespec   - List files matching pattern
    """
    filespec: 'ExpressionNode' = None  # File pattern (default "*.bas")
    line_num: int = 0
    column: int = 0


@dataclass
class ListStatementNode:
    """LIST statement - list program lines

    Syntax:
        LIST             - List all lines
        LIST line        - List single line
        LIST start-end   - List range of lines
        LIST -end        - List from beginning to end
        LIST start-      - List from start to end
    """
    start: 'ExpressionNode' = None  # Start line number (None = beginning)
    end: 'ExpressionNode' = None    # End line number (None = end of program)
    single_line: bool = False       # True if listing single line (no dash)
    line_num: int = 0
    column: int = 0


@dataclass
class StopStatementNode:
    """STOP statement - pause program execution

    STOP pauses the program and returns to interactive mode.
    Variables, the program counter, and the call stack are preserved.
    Use CONT to resume execution from the statement after STOP.
    """
    line_num: int = 0
    column: int = 0


@dataclass
class ContStatementNode:
    """CONT statement - continue execution after STOP

    CONT resumes execution from where the program was stopped.
    This can only be used after a STOP or after Ctrl+C (Break).
    """
    line_num: int = 0
    column: int = 0


@dataclass
class StepStatementNode:
    """STEP statement - single-step execution (debug command)

    Syntax: STEP [count]

    STEP executes one or more statements in debug mode, pausing after each.
    """
    count: int = None
    line_num: int = 0
    column: int = 0


@dataclass
class RandomizeStatementNode:
    """RANDOMIZE statement - initialize random number generator

    Syntax:
        RANDOMIZE          - Use timer as seed
        RANDOMIZE seed     - Use specific seed value
    """
    seed: Optional['ExpressionNode']  # Seed value (None = use timer)
    line_num: int = 0
    column: int = 0


@dataclass
class RemarkStatementNode:
    """REM/REMARK statement - comment"""
    text: str
    comment_type: str = "REM"  # "REM", "REMARK", or "APOSTROPHE" - preserves original syntax
    line_num: int = 0
    column: int = 0


@dataclass
class SwapStatementNode:
    """SWAP statement - exchange values of two variables"""
    var1: 'VariableNode'
    var2: 'VariableNode'
    line_num: int = 0
    column: int = 0


@dataclass
class ErrorStatementNode:
    """ERROR statement - simulate an error

    Syntax: ERROR error_code

    Sets ERR to the specified error code and triggers error handling.
    Used for testing error handlers or simulating errors.
    """
    error_code: 'ExpressionNode'  # Error code to simulate
    line_num: int = 0
    column: int = 0


@dataclass
class OnErrorStatementNode:
    """ON ERROR GOTO/GOSUB statement - error handling"""
    line_number: int
    is_gosub: bool = False  # True for ON ERROR GOSUB, False for ON ERROR GOTO
    line_num: int = 0
    column: int = 0


@dataclass
class ResumeStatementNode:
    """RESUME statement - continue after error"""
    line_number: Optional[int]  # None means RESUME, 0 means RESUME NEXT
    line_num: int = 0
    column: int = 0


@dataclass
class PokeStatementNode:
    """POKE statement - write to memory"""
    address: 'ExpressionNode'
    value: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class OutStatementNode:
    """OUT statement - write to I/O port"""
    port: 'ExpressionNode'
    value: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class CallStatementNode:
    """CALL statement - call machine language routine (MBASIC 5.21)

    Standard MBASIC 5.21 Syntax:
        CALL address           - Call machine code at numeric address

    Examples:
        CALL 16384             - Call decimal address
        CALL &HC000            - Call hex address
        CALL A                 - Call address in variable
        CALL DIO+1             - Call computed address

    Note: Parser also accepts extended syntax for compatibility with
    other BASIC dialects (e.g., CALL ROUTINE(args)), but this is not
    standard MBASIC 5.21.
    """
    target: 'ExpressionNode'  # Memory address expression
    arguments: List['ExpressionNode']  # Arguments (non-standard, for compatibility)
    line_num: int = 0
    column: int = 0


@dataclass
class DefFnStatementNode:
    """DEF FN statement - define single-line function"""
    name: str
    parameters: List['VariableNode']
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0
    column: int = 0


@dataclass
class WidthStatementNode:
    """WIDTH statement - set output width"""
    width: 'ExpressionNode'
    device: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class ClearStatementNode:
    """CLEAR statement - clear variables and set memory"""
    string_space: Optional['ExpressionNode']
    stack_space: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class OptionBaseStatementNode:
    """OPTION BASE statement - set array index base

    Syntax:
        OPTION BASE 0  - Arrays start at index 0 (default)
        OPTION BASE 1  - Arrays start at index 1

    Must appear before any array DIM statements.
    """
    base: int  # 0 or 1
    line_num: int = 0
    column: int = 0


@dataclass
class CommonStatementNode:
    """COMMON statement - declare shared variables for CHAIN

    Syntax:
        COMMON var1, var2, array1(), ...

    Variables listed in COMMON are passed to CHAINed programs
    (unless ALL option is used, which passes all variables).
    Variable order and type matter, not names.
    """
    variables: List[str]  # List of variable names
    line_num: int = 0
    column: int = 0


@dataclass
class FieldStatementNode:
    """FIELD statement - define random-access file buffer"""
    file_number: 'ExpressionNode'
    fields: List[tuple]  # List of (width, variable) tuples
    line_num: int = 0
    column: int = 0


@dataclass
class GetStatementNode:
    """GET statement - read record from random-access file"""
    file_number: 'ExpressionNode'
    record_number: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class PutStatementNode:
    """PUT statement - write record to random-access file"""
    file_number: 'ExpressionNode'
    record_number: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class LineInputStatementNode:
    """LINE INPUT statement - read entire line"""
    file_number: Optional['ExpressionNode']
    prompt: Optional['ExpressionNode']
    variable: 'VariableNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WriteStatementNode:
    """WRITE statement - formatted output"""
    file_number: Optional['ExpressionNode']
    expressions: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


# ============================================================================
# Expressions
# ============================================================================

@dataclass
class ExpressionNode:
    """Base class for all expressions"""
    pass


@dataclass
class NumberNode:
    """Numeric literal"""
    value: float
    literal: str  # Original text representation
    line_num: int = 0
    column: int = 0


@dataclass
class StringNode:
    """String literal"""
    value: str
    line_num: int = 0
    column: int = 0


@dataclass
class VariableNode:
    """Variable reference"""
    name: str  # Normalized lowercase name for lookups
    type_suffix: Optional[str] = None  # $, %, !, #
    subscripts: Optional[List['ExpressionNode']] = None  # For array access
    original_case: Optional[str] = None  # Original case as typed by user (for display)
    explicit_type_suffix: bool = False  # True if type_suffix was in original source, False if inferred from DEF
    line_num: int = 0
    column: int = 0


@dataclass
class BinaryOpNode:
    """Binary operation (arithmetic, relational, logical)"""
    operator: TokenType
    left: 'ExpressionNode'
    right: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class UnaryOpNode:
    """Unary operation (-, NOT, +)"""
    operator: TokenType
    operand: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class FunctionCallNode:
    """Built-in or user-defined function call"""
    name: str
    arguments: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


# ============================================================================
# Settings Commands
# ============================================================================

@dataclass
class SetSettingStatementNode:
    """SET statement - set a configuration setting

    Syntax:
        SET setting_name value
        SET setting_name = value

    Examples:
        SET variables.case_conflict first_wins
        SET editor.auto_number true
        SET ui.font_size 14
    """
    setting_name: str  # Setting key (e.g., "variables.case_conflict")
    value: 'ExpressionNode'  # Value to set
    line_num: int = 0
    column: int = 0


@dataclass
class ShowSettingsStatementNode:
    """SHOW SETTINGS statement - display current settings

    Syntax:
        SHOW SETTINGS           - Show all settings
        SHOW SETTINGS pattern   - Show settings matching pattern

    Examples:
        SHOW SETTINGS
        SHOW SETTINGS variables
        SHOW SETTINGS editor.auto
    """
    pattern: Optional[str] = None  # Optional pattern to filter settings
    line_num: int = 0
    column: int = 0


@dataclass
class HelpSettingStatementNode:
    """HELP SET statement - show help for a setting

    Syntax:
        HELP SET setting_name

    Examples:
        HELP SET variables.case_conflict
        HELP SET editor.auto_number
    """
    setting_name: str  # Setting key to show help for
    line_num: int = 0
    column: int = 0


# ============================================================================

class TypeInfo:
    """Type information utilities for variables

    Note: This class provides convenience methods for working with VarType enum.
    Kept for backwards compatibility but could be refactored away.
    """
    # Expose enum values as class attributes for compatibility
    INTEGER = VarType.INTEGER
    SINGLE = VarType.SINGLE
    DOUBLE = VarType.DOUBLE
    STRING = VarType.STRING

    @staticmethod
    def from_suffix(suffix: Optional[str]) -> VarType:
        """Get type from variable suffix

        Args:
            suffix: Type suffix character (%, !, #, $, or None)

        Returns:
            VarType enum value
        """
        if suffix == '%':
            return VarType.INTEGER
        elif suffix == '!':
            return VarType.SINGLE
        elif suffix == '#':
            return VarType.DOUBLE
        elif suffix == '$':
            return VarType.STRING
        else:
            return VarType.SINGLE  # Default type in MBASIC

    @staticmethod
    def from_def_statement(token_type) -> VarType:
        """Get type from DEF statement token type

        Args:
            token_type: TokenType enum (DEFINT, DEFSNG, DEFDBL, DEFSTR)

        Returns:
            VarType enum value
        """
        # Import here to avoid circular dependency
        from src.tokens import TokenType

        if token_type == TokenType.DEFINT:
            return VarType.INTEGER
        elif token_type == TokenType.DEFSNG:
            return VarType.SINGLE
        elif token_type == TokenType.DEFDBL:
            return VarType.DOUBLE
        elif token_type == TokenType.DEFSTR:
            return VarType.STRING
        else:
            raise ValueError(f"Unknown DEF statement token type: {token_type}")
