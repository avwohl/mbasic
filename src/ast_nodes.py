"""
Abstract Syntax Tree (AST) node definitions for MBASIC 5.21

Note: 5.21 refers to the Microsoft BASIC-80 language version, not this package version.
This is an independent open-source implementation (package version 0.99.0).

This module defines all AST node types for representing BASIC programs.
Nodes are organized into:
- Program structure (ProgramNode, LineNode)
- Statements (PrintStatementNode, ForStatementNode, etc.)
- Expressions (NumberNode, BinaryOpNode, etc.)
"""

from typing import List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from src.tokens import TokenType, Token


# ============================================================================
# Type System
# ============================================================================

class VarType(Enum):
    """Variable type enumeration for BASIC variables

    Types are specified by suffix characters or DEF statements:
    - INTEGER: % suffix (e.g., COUNT%) or DEFINT A-Z
    - SINGLE: ! suffix (e.g., VALUE!) or DEFSNG A-Z (default type)
    - DOUBLE: # suffix (e.g., TOTAL#) or DEFDBL A-Z
    - STRING: $ suffix (e.g., NAME$) or DEFSTR A-Z
    """
    INTEGER = 'INTEGER'  # % suffix or DEFINT
    SINGLE = 'SINGLE'    # ! suffix or DEFSNG (default)
    DOUBLE = 'DOUBLE'    # # suffix or DEFDBL
    STRING = 'STRING'    # $ suffix or DEFSTR


# ============================================================================
# Base Classes
# ============================================================================

class Node:
    """Base class for all AST nodes

    Provides line_num and column attributes for source location tracking.
    Most nodes use dataclasses instead of this base class.
    """
    def __init__(self, line_num: int = 0, column: int = 0):
        self.line_num = line_num
        self.column = column


# ============================================================================
# Program Structure
# ============================================================================

@dataclass
class ProgramNode:
    """Root node of the AST - represents entire program.

    Contains a list of LineNode objects. Each LineNode represents one
    numbered line in the BASIC program and contains a list of statements
    (since multiple statements can appear on one line, separated by colons).

    Example:
        10 PRINT "HELLO"
        20 FOR I=1 TO 10: PRINT I: NEXT I
        30 END

    Attributes:
        lines: List of LineNode objects
        def_type_statements: Global DEF type mappings (DEFINT/DEFSNG/DEFDBL/DEFSTR)
    """
    lines: List['LineNode']
    def_type_statements: dict  # Global DEF type mappings
    line_num: int = 0
    column: int = 0


@dataclass
class LineNode:
    """A single line in a BASIC program (line number + statements)

    Example:
        20 FOR I=1 TO 10: PRINT I: NEXT I

    The AST is the single source of truth. Text is always regenerated from
    the AST using statement token information (each statement has char_start/char_end
    and tokens preserve original_case for keywords and identifiers).

    Design note: This class intentionally does not have a source_text field to avoid
    maintaining duplicate copies that could get out of sync with the AST during editing.
    Text regeneration is handled by the src.position_serializer module which reconstructs
    source text from statement nodes and their token information.

    How text regeneration works without storing original text:
    - Each StatementNode has char_start/char_end offsets that mark its position in the line
    - Each token in a statement has original_case information (original keyword casing/identifier names)
    - The position_serializer uses these token values with their char_start/char_end positions
      to reconstruct the source text character-by-character
    - This approach preserves original formatting and keyword casing while avoiding duplication
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
    """Base class for all statements

    All statement nodes inherit from this class. Statement nodes represent
    executable commands in BASIC programs. Subclasses include PrintStatementNode,
    ForStatementNode, GotoStatementNode, etc.

    Note: char_start/char_end are populated by the parser and used by:
    - UI highlighting: tk_ui._highlight_current_statement() highlights the currently executing
      statement by underlining the text from char_start to char_end
    - Position serializer: Preserves exact character positions for text regeneration
    - Cursor positioning: Determines which statement the cursor is in during editing
    """
    line_num: int = 0
    column: int = 0
    char_start: int = 0  # Character offset from start of line (see class docstring)
    char_end: int = 0    # Character offset end position (see class docstring)


@dataclass
class PrintStatementNode:
    """PRINT statement - output to screen or file

    Syntax:
        PRINT expr1, expr2          - Print to screen
        PRINT #filenum, expr1       - Print to file

    Separators:
        , (comma)  - Tab to next print zone
        ; (semicolon) - No spacing between items
        (none) - Newline after output
    """
    expressions: List['ExpressionNode']
    separators: List[str]  # ";" or "," or None for newline
    file_number: Optional['ExpressionNode'] = None  # For PRINT #n, ...
    line_num: int = 0
    column: int = 0


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

    The suppress_question field controls "?" display:
    - suppress_question=False (default): Adds "?" after prompt
      Examples: INPUT var → "? ", INPUT "Name", var → "Name? "
    - suppress_question=True: No "?" added (for INPUT; syntax)
      Examples: INPUT; var → "" (no prompt), INPUT "prompt"; var → "prompt" (no "?")

    Important: Semicolon placement changes meaning:
    - INPUT; var → semicolon IMMEDIATELY after INPUT keyword (suppress_question=True)
      This suppresses the "?" question mark entirely
    - INPUT "prompt"; var → semicolon AFTER the prompt string (suppress_question=False)
      This is parsed as: prompt="prompt", then semicolon separates the prompt from the variable
      The "?" is still added after the prompt

    Parser note: The parser determines suppress_question=True only when it sees INPUT
    followed directly by semicolon with no prompt expression between them.
    """
    prompt: Optional['ExpressionNode']
    variables: List['VariableNode']
    file_number: Optional['ExpressionNode'] = None  # For INPUT #n, ...
    suppress_question: bool = False  # True if INPUT; (semicolon immediately after INPUT, no prompt)
    line_num: int = 0
    column: int = 0


@dataclass
class LetStatementNode:
    """LET or implicit assignment statement

    Syntax:
        LET variable = expression
        variable = expression           - LET keyword is optional
    """
    variable: 'VariableNode'
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class IfStatementNode:
    """IF statement with optional THEN and ELSE

    Syntax:
        IF condition THEN statement
        IF condition THEN line_number
        IF condition THEN statement ELSE statement
    """
    condition: 'ExpressionNode'
    then_statements: List['StatementNode']
    then_line_number: Optional[int]  # For IF...THEN line number GOTO style
    else_statements: Optional[List['StatementNode']]
    else_line_number: Optional[int]
    line_num: int = 0
    column: int = 0


@dataclass
class ForStatementNode:
    """FOR loop statement

    Syntax:
        FOR variable = start TO end
        FOR variable = start TO end STEP increment
    """
    variable: 'VariableNode'
    start_expr: 'ExpressionNode'
    end_expr: 'ExpressionNode'
    step_expr: Optional['ExpressionNode']  # Default is 1
    line_num: int = 0
    column: int = 0


@dataclass
class NextStatementNode:
    """NEXT statement - end of FOR loop

    Syntax:
        NEXT variable
        NEXT variable1, variable2, ...
    """
    variables: List['VariableNode']  # Can be NEXT I or NEXT I,J,K
    line_num: int = 0
    column: int = 0


@dataclass
class WhileStatementNode:
    """WHILE loop statement

    Syntax:
        WHILE condition
    """
    condition: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WendStatementNode:
    """WEND statement - end of WHILE loop

    Syntax:
        WEND
    """
    line_num: int = 0
    column: int = 0


@dataclass
class GotoStatementNode:
    """GOTO statement - unconditional jump

    Syntax:
        GOTO line_number
    """
    line_number: int
    line_num: int = 0
    column: int = 0


@dataclass
class GosubStatementNode:
    """GOSUB statement - call subroutine at line number

    Syntax:
        GOSUB line_number
    """
    line_number: int
    line_num: int = 0
    column: int = 0


@dataclass
class ReturnStatementNode:
    """RETURN statement - return from GOSUB

    Syntax:
        RETURN
    """
    line_num: int = 0
    column: int = 0


@dataclass
class OnGotoStatementNode:
    """ON...GOTO statement - computed GOTO

    Syntax:
        ON expression GOTO line1, line2, ...
    """
    expression: 'ExpressionNode'
    line_numbers: List[int]
    line_num: int = 0
    column: int = 0


@dataclass
class OnGosubStatementNode:
    """ON...GOSUB statement - computed GOSUB

    Syntax:
        ON expression GOSUB line1, line2, ...
    """
    expression: 'ExpressionNode'
    line_numbers: List[int]
    line_num: int = 0
    column: int = 0


@dataclass
class DimStatementNode:
    """DIM statement - declare array dimensions

    Syntax:
        DIM array1(size), array2(rows, cols), ...
    """
    arrays: List['ArrayDeclNode']
    line_num: int = 0
    column: int = 0


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
    """Array declaration in DIM statement

    Example:
        A(10)         - One-dimensional array
        B(5, 10)      - Two-dimensional array
    """
    name: str
    dimensions: List['ExpressionNode']  # Must be constant expressions in compiled BASIC
    line_num: int = 0
    column: int = 0


@dataclass
class DefTypeStatementNode:
    """DEFINT/DEFSNG/DEFDBL/DEFSTR statement

    Syntax:
        DEFINT letter[-letter], ...
        DEFSNG letter[-letter], ...
        DEFDBL letter[-letter], ...
        DEFSTR letter[-letter], ...

    Defines default types for variables based on their first letter.
    Example: DEFINT I-K makes all variables starting with I, J, K default to INTEGER.
    """
    var_type: VarType  # Variable type (VarType.INTEGER, SINGLE, DOUBLE, or STRING)
    letters: Set[str]  # Set of lowercase letters affected by this declaration
    line_num: int = 0
    column: int = 0


@dataclass
class ReadStatementNode:
    """READ statement - read from DATA

    Syntax:
        READ variable1, variable2, ...
    """
    variables: List['VariableNode']
    line_num: int = 0
    column: int = 0


@dataclass
class DataStatementNode:
    """DATA statement - stores data values

    Syntax:
        DATA value1, value2, ...
    """
    values: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class RestoreStatementNode:
    """RESTORE statement - reset DATA pointer

    Syntax:
        RESTORE
        RESTORE line_number
    """
    line_number: Optional[int]
    line_num: int = 0
    column: int = 0


@dataclass
class OpenStatementNode:
    """OPEN statement - open file for I/O

    Syntax:
        OPEN mode, #filenum, filename$ [, reclen]
    """
    mode: str  # "I", "O", "R", "A"
    file_number: 'ExpressionNode'
    filename: 'ExpressionNode'
    record_length: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class CloseStatementNode:
    """CLOSE statement - close file(s)

    Syntax:
        CLOSE
        CLOSE #filenum1, #filenum2, ...
    """
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
    delete_range: Optional[Tuple[int, int]] = None  # (start_line_number, end_line_number) for DELETE option
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
    """END statement - terminate program

    Syntax:
        END
    """
    line_num: int = 0
    column: int = 0


@dataclass
class TronStatementNode:
    """TRON statement - enable execution trace (shows line numbers)

    Syntax:
        TRON
    """
    line_num: int = 0
    column: int = 0


@dataclass
class TroffStatementNode:
    """TROFF statement - disable execution trace

    Syntax:
        TROFF
    """
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


# NOTE: SetSettingStatementNode and ShowSettingsStatementNode are defined
# in the "Settings Commands" section later in this file (search for "Settings Commands").


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
    new_start: 'ExpressionNode' = None  # New starting line_number (None → default 10)
    old_start: 'ExpressionNode' = None  # First old line_number to renumber (None → default 0)
    increment: 'ExpressionNode' = None  # Increment (None → default 10)
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
    start: 'ExpressionNode' = None  # Start line_number (None = beginning)
    end: 'ExpressionNode' = None    # End line_number (None = end of program)
    single_line: bool = False       # True if listing single line (no dash)
    line_num: int = 0
    column: int = 0


@dataclass
class StopStatementNode:
    """STOP statement - pause program execution

    Syntax:
        STOP

    STOP pauses the program and returns to interactive mode.
    Variables, the program counter, and the call stack are preserved.
    Use CONT to resume execution from the statement after STOP.
    """
    line_num: int = 0
    column: int = 0


@dataclass
class ContStatementNode:
    """CONT statement - continue execution after STOP

    Syntax:
        CONT

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
    count: Optional[int] = None
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
    """REM/REMARK statement - comment

    Syntax:
        REM text
        REMARK text
        ' text

    The comment_type field preserves the original comment syntax used in source code.
    The parser sets this to "REM", "REMARK", or "APOSTROPHE" based on input, and the
    value determines which comment keyword appears when generating source text.
    """
    text: str
    comment_type: str = "REM"  # Original syntax: "REM", "REMARK", or "APOSTROPHE"
    line_num: int = 0
    column: int = 0


@dataclass
class SwapStatementNode:
    """SWAP statement - exchange values of two variables

    Syntax:
        SWAP variable1, variable2
    """
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
    """ON ERROR GOTO/GOSUB statement - error handling

    Syntax:
        ON ERROR GOTO line_number
        ON ERROR GOSUB line_number
        ON ERROR GOTO 0                - Disable error handling
    """
    line_number: int
    is_gosub: bool = False  # True for ON ERROR GOSUB, False for ON ERROR GOTO
    line_num: int = 0
    column: int = 0


@dataclass
class ResumeStatementNode:
    """RESUME statement - continue after error

    Syntax:
        RESUME                  - Retry statement that caused error
        RESUME NEXT             - Continue at next statement
        RESUME line_number      - Continue at specific line
    """
    line_number: Optional[int]  # None means RESUME, 0 means RESUME NEXT
    line_num: int = 0
    column: int = 0


@dataclass
class PokeStatementNode:
    """POKE statement - write to memory

    Syntax:
        POKE address, value
    """
    address: 'ExpressionNode'
    value: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class OutStatementNode:
    """OUT statement - write to I/O port

    Syntax:
        OUT port, value
    """
    port: 'ExpressionNode'
    value: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WaitStatementNode:
    """WAIT statement - wait for I/O port condition

    Syntax:
        WAIT port, mask [, select]

    Waits until (INP(port) XOR select) AND mask <> 0
    If select is omitted, waits until INP(port) AND mask <> 0
    """
    port: 'ExpressionNode'
    mask: 'ExpressionNode'
    select: Optional['ExpressionNode'] = None
    line_num: int = 0
    column: int = 0


@dataclass
class CallStatementNode:
    """CALL statement - call machine language routine (MBASIC 5.21)

    Standard MBASIC 5.21 Syntax:
        CALL address           - Call machine code at numeric address

    Extended Syntax (for compatibility with other BASIC dialects):
        CALL ROUTINE(X,Y)      - Call with arguments

    Examples:
        CALL 16384             - Call decimal address
        CALL &HC000            - Call hex address
        CALL A                 - Call address in variable
        CALL DIO+1             - Call computed address
        CALL MYSUB(X,Y)        - Call with arguments (extended syntax)

    Implementation Note: The 'arguments' field is populated when the target is parsed as
    a function call or array access with subscripts. For standard MBASIC 5.21 programs
    (which only use numeric addresses), this field will be empty.
    """
    target: 'ExpressionNode'  # Memory address or subroutine name
    arguments: List['ExpressionNode'] = field(default_factory=list)  # Arguments for extended syntax
    line_num: int = 0
    column: int = 0


@dataclass
class DefFnStatementNode:
    """DEF FN statement - define single-line function

    Syntax:
        DEF FNname(param1, param2, ...) = expression
    """
    name: str
    parameters: List['VariableNode']
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WidthStatementNode:
    """WIDTH statement - set output width

    Syntax:
        WIDTH width
        WIDTH width, device
    """
    width: 'ExpressionNode'
    device: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class ClearStatementNode:
    """CLEAR statement - clear variables and set memory

    Syntax:
        CLEAR
        CLEAR string_space
        CLEAR string_space, stack_space
    """
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
    """FIELD statement - define random-access file buffer

    Syntax:
        FIELD #filenum, width1 AS var1, width2 AS var2, ...
    """
    file_number: 'ExpressionNode'
    fields: List[tuple]  # List of (width, variable) tuples
    line_num: int = 0
    column: int = 0


@dataclass
class GetStatementNode:
    """GET statement - read record from random-access file

    Syntax:
        GET #filenum
        GET #filenum, record_number
    """
    file_number: 'ExpressionNode'
    record_number: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class PutStatementNode:
    """PUT statement - write record to random-access file

    Syntax:
        PUT #filenum
        PUT #filenum, record_number
    """
    file_number: 'ExpressionNode'
    record_number: Optional['ExpressionNode']
    line_num: int = 0
    column: int = 0


@dataclass
class LineInputStatementNode:
    """LINE INPUT statement - read entire line

    Syntax:
        LINE INPUT "prompt"; variable$
        LINE INPUT #filenum, variable$
    """
    file_number: Optional['ExpressionNode']
    prompt: Optional['ExpressionNode']
    variable: 'VariableNode'
    line_num: int = 0
    column: int = 0


@dataclass
class WriteStatementNode:
    """WRITE statement - formatted output

    Syntax:
        WRITE expr1, expr2, ...
        WRITE #filenum, expr1, expr2, ...
    """
    file_number: Optional['ExpressionNode']
    expressions: List['ExpressionNode']
    line_num: int = 0
    column: int = 0


# ============================================================================
# Expressions
# ============================================================================

@dataclass
class ExpressionNode:
    """Base class for all expressions

    Expressions evaluate to values and can be used in statements.
    Subclasses include NumberNode, StringNode, VariableNode, BinaryOpNode, etc.
    """
    pass


@dataclass
class NumberNode:
    """Numeric literal

    Examples:
        42          - Integer
        3.14        - Floating point
        &HFF        - Hexadecimal
        &O77        - Octal
        1.23E+5     - Scientific notation
    """
    value: float
    literal: str  # Original text representation
    line_num: int = 0
    column: int = 0


@dataclass
class StringNode:
    """String literal

    Example:
        "HELLO"     - String constant
    """
    value: str
    line_num: int = 0
    column: int = 0


@dataclass
class VariableNode:
    """Variable reference

    Type suffix handling:
    - type_suffix: The actual suffix character ($, %, !, #) when present
    - explicit_type_suffix: Boolean indicating the origin of type_suffix:
        * True: suffix appeared in source code (e.g., "X%" in "X% = 5")
        * False: suffix inferred from DEFINT/DEFSNG/DEFDBL/DEFSTR (e.g., "X" with DEFINT A-Z)

    Source code regeneration rules:
    - When explicit_type_suffix=True: suffix IS included in regenerated source (e.g., "X%")
    - When explicit_type_suffix=False: suffix is NOT included in regenerated source (e.g., "X")

    Important: Both fields are ALWAYS present together:
    - type_suffix may be non-None even when explicit_type_suffix=False (inferred from DEF statement)
    - explicit_type_suffix=True should only occur when type_suffix is also non-None (the suffix was written)
    - explicit_type_suffix=False + type_suffix=None means variable has default type (SINGLE) with no explicit suffix

    Example: In "DEFINT A-Z: X=5", variable X has type_suffix='%' and explicit_type_suffix=False.
    The suffix is tracked for type checking but not output when regenerating source code.

    Critical: Code must always check BOTH fields together:
    - For source regeneration: use explicit_type_suffix to decide whether to output the suffix
    - For type checking: use type_suffix to determine the variable's actual type
    """
    name: str  # Normalized lowercase name for lookups
    type_suffix: Optional[str] = None  # $, %, !, # - The actual suffix (see explicit_type_suffix for origin)
    subscripts: Optional[List['ExpressionNode']] = None  # For array access
    original_case: Optional[str] = None  # Original case as typed by user (for display)
    explicit_type_suffix: bool = False  # True if type_suffix was in original source, False if inferred from DEF
    line_num: int = 0
    column: int = 0


@dataclass
class BinaryOpNode:
    """Binary operation (arithmetic, relational, logical)

    Examples:
        A + B       - Addition
        X * Y       - Multiplication
        I < 10      - Comparison
        A$ = B$     - String comparison
        X AND Y     - Logical AND
    """
    operator: TokenType
    left: 'ExpressionNode'
    right: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class UnaryOpNode:
    """Unary operation (-, NOT, +)

    Examples:
        -X          - Negation
        NOT FLAG    - Logical NOT
        +Y          - Unary plus
    """
    operator: TokenType
    operand: 'ExpressionNode'
    line_num: int = 0
    column: int = 0


@dataclass
class FunctionCallNode:
    """Built-in or user-defined function call

    Examples:
        SIN(X)      - Built-in function
        FNcalc(A,B) - User-defined function (DEF FN)
        LEN(A$)     - String function
    """
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
        SET case_conflict first_wins
        SET auto_number true
        SET ui.font_size 14
    """
    setting_name: str  # Setting key (e.g., "case_conflict")
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
        HELP SET case_conflict
        HELP SET auto_number
    """
    setting_name: str  # Setting key to show help for
    line_num: int = 0
    column: int = 0


# ============================================================================

class TypeInfo:
    """Type information utilities for variables

    Provides convenience methods for working with VarType enum and converting
    between type suffixes, DEF statement tokens, and VarType enum values.

    This class serves two purposes:
    1. Static helper methods for type conversions (from_suffix, from_token, etc.)
    2. Compatibility layer: Class attributes (INTEGER, SINGLE, etc.) alias VarType
       enum values to support legacy code that used TypeInfo.INTEGER instead of
       VarType.INTEGER. This allows gradual migration without breaking existing code.
       Note: New code should use VarType enum directly.
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

        Examples:
            TypeInfo.from_suffix('%') → VarType.INTEGER
            TypeInfo.from_suffix('$') → VarType.STRING
            TypeInfo.from_suffix(None) → VarType.SINGLE (default)
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

        Examples:
            TypeInfo.from_def_statement(TokenType.DEFINT) → VarType.INTEGER
            TypeInfo.from_def_statement(TokenType.DEFSTR) → VarType.STRING
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
