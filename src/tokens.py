"""
Token definitions for MBASIC 5.21 (CP/M era Microsoft BASIC-80)
Based on BASIC-80 Reference Manual Version 5.21
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    # Literals
    NUMBER = auto()          # Integer, fixed-point, or floating-point
    STRING = auto()          # "string literal"

    # Identifiers
    IDENTIFIER = auto()      # Variables (with optional type suffix: $ % ! #)

    # Keywords - Program Control
    AUTO = auto()
    CONT = auto()
    DELETE = auto()
    EDIT = auto()
    LIST = auto()
    LLIST = auto()
    LOAD = auto()
    MERGE = auto()
    NEW = auto()
    RENUM = auto()
    RUN = auto()
    SAVE = auto()

    # Keywords - File Operations
    AS = auto()              # AS (used in OPEN and FIELD)
    CLOSE = auto()
    FIELD = auto()
    GET = auto()
    INPUT = auto()            # Also used for INPUT statement
    KILL = auto()
    LINE_INPUT = auto()       # LINE INPUT
    LSET = auto()
    NAME = auto()
    OPEN = auto()
    OUTPUT = auto()          # OUTPUT (used in OPEN FOR OUTPUT)
    PUT = auto()
    RESET = auto()           # RESET (close all files)
    RSET = auto()

    # Keywords - Control Flow
    CALL = auto()
    CHAIN = auto()
    ELSE = auto()
    END = auto()
    FOR = auto()
    GOSUB = auto()
    GOTO = auto()
    IF = auto()
    NEXT = auto()
    ON = auto()
    RESUME = auto()
    RETURN = auto()
    STEP = auto()
    STOP = auto()
    SYSTEM = auto()
    THEN = auto()
    TO = auto()
    WHILE = auto()
    WEND = auto()

    # Keywords - Data/Arrays
    CLEAR = auto()
    DATA = auto()
    DEF = auto()
    DEFINT = auto()
    DEFSNG = auto()
    DEFDBL = auto()
    DEFSTR = auto()
    DIM = auto()
    ERASE = auto()
    FN = auto()
    LET = auto()
    OPTION = auto()
    BASE = auto()
    READ = auto()
    RESTORE = auto()

    # Keywords - I/O
    PRINT = auto()
    LPRINT = auto()
    WRITE = auto()

    # Keywords - Other
    COMMON = auto()
    ERROR = auto()
    OUT = auto()
    POKE = auto()
    RANDOMIZE = auto()
    REM = auto()
    REMARK = auto()          # Synonym for REM
    SWAP = auto()
    WAIT = auto()
    WIDTH = auto()

    # Operators - Arithmetic
    PLUS = auto()            # +
    MINUS = auto()           # -
    MULTIPLY = auto()        # *
    DIVIDE = auto()          # /
    POWER = auto()           # ^
    BACKSLASH = auto()       # \ (integer division)
    AMPERSAND = auto()       # & (string concatenation or standalone)
    MOD = auto()             # MOD

    # Operators - Relational
    EQUAL = auto()           # =
    NOT_EQUAL = auto()       # <>
    LESS_THAN = auto()       # <
    GREATER_THAN = auto()    # >
    LESS_EQUAL = auto()      # <=
    GREATER_EQUAL = auto()   # >=

    # Operators - Logical
    NOT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    EQV = auto()
    IMP = auto()

    # Built-in Functions - Numeric
    ABS = auto()
    ATN = auto()
    CDBL = auto()
    CINT = auto()
    COS = auto()
    CSNG = auto()
    EXP = auto()
    FIX = auto()
    INT = auto()
    LOG = auto()
    RND = auto()
    SGN = auto()
    SIN = auto()
    SQR = auto()
    TAN = auto()

    # Built-in Functions - String (with $ in name)
    ASC = auto()
    CHR = auto()             # CHR$
    HEX = auto()             # HEX$
    INKEY = auto()           # INKEY$
    INPUT_FUNC = auto()      # INPUT$ (different from INPUT statement)
    INSTR = auto()
    LEFT = auto()            # LEFT$
    LEN = auto()
    MID = auto()             # MID$
    OCT = auto()             # OCT$
    RIGHT = auto()           # RIGHT$
    SPACE = auto()           # SPACE$
    STR = auto()             # STR$
    STRING_FUNC = auto()     # STRING$ function
    VAL = auto()

    # Built-in Functions - Other
    EOF_FUNC = auto()        # EOF
    INP = auto()
    PEEK = auto()
    POS = auto()
    USR = auto()

    # Delimiters
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    COMMA = auto()           # ,
    SEMICOLON = auto()       # ;
    COLON = auto()           # :
    HASH = auto()            # # (file number prefix)

    # Special
    NEWLINE = auto()
    LINE_NUMBER = auto()     # Line numbers at start of statement
    EOF = auto()
    QUESTION = auto()        # ? (shorthand for PRINT)
    APOSTROPHE = auto()      # ' (comment, like REM)


@dataclass
class Token:
    """Represents a single token in MBASIC source code"""
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# Keywords mapping (case-insensitive)
# String functions include $ as part of the name
KEYWORDS = {
    # Program control
    'AUTO': TokenType.AUTO,
    'CONT': TokenType.CONT,
    'DELETE': TokenType.DELETE,
    'EDIT': TokenType.EDIT,
    'LIST': TokenType.LIST,
    'LLIST': TokenType.LLIST,
    'LOAD': TokenType.LOAD,
    'MERGE': TokenType.MERGE,
    'NEW': TokenType.NEW,
    'RENUM': TokenType.RENUM,
    'RUN': TokenType.RUN,
    'SAVE': TokenType.SAVE,

    # File operations
    'AS': TokenType.AS,
    'CLOSE': TokenType.CLOSE,
    'FIELD': TokenType.FIELD,
    'GET': TokenType.GET,
    'INPUT': TokenType.INPUT,
    'KILL': TokenType.KILL,
    'LINE': TokenType.LINE_INPUT,  # Will need special handling for "LINE INPUT"
    'LSET': TokenType.LSET,
    'NAME': TokenType.NAME,
    'OPEN': TokenType.OPEN,
    'OUTPUT': TokenType.OUTPUT,
    'PUT': TokenType.PUT,
    'RESET': TokenType.RESET,
    'RSET': TokenType.RSET,

    # Control flow
    'CALL': TokenType.CALL,
    'CHAIN': TokenType.CHAIN,
    'ELSE': TokenType.ELSE,
    'END': TokenType.END,
    'FOR': TokenType.FOR,
    'GOSUB': TokenType.GOSUB,
    'GOTO': TokenType.GOTO,
    'IF': TokenType.IF,
    'NEXT': TokenType.NEXT,
    'ON': TokenType.ON,
    'RESUME': TokenType.RESUME,
    'RETURN': TokenType.RETURN,
    'STEP': TokenType.STEP,
    'STOP': TokenType.STOP,
    'SYSTEM': TokenType.SYSTEM,
    'THEN': TokenType.THEN,
    'TO': TokenType.TO,
    'WHILE': TokenType.WHILE,
    'WEND': TokenType.WEND,

    # Data/Arrays
    'BASE': TokenType.BASE,
    'CLEAR': TokenType.CLEAR,
    'COMMON': TokenType.COMMON,
    'DATA': TokenType.DATA,
    'DEF': TokenType.DEF,
    'DEFINT': TokenType.DEFINT,
    'DEFSNG': TokenType.DEFSNG,
    'DEFDBL': TokenType.DEFDBL,
    'DEFSTR': TokenType.DEFSTR,
    'DIM': TokenType.DIM,
    'ERASE': TokenType.ERASE,
    'FN': TokenType.FN,
    'LET': TokenType.LET,
    'OPTION': TokenType.OPTION,
    'READ': TokenType.READ,
    'RESTORE': TokenType.RESTORE,

    # I/O
    'PRINT': TokenType.PRINT,
    'LPRINT': TokenType.LPRINT,
    'WRITE': TokenType.WRITE,

    # Other
    'ERROR': TokenType.ERROR,
    'OUT': TokenType.OUT,
    'POKE': TokenType.POKE,
    'RANDOMIZE': TokenType.RANDOMIZE,
    'REM': TokenType.REM,
    'REMARK': TokenType.REMARK,
    'SWAP': TokenType.SWAP,
    'WAIT': TokenType.WAIT,
    'WIDTH': TokenType.WIDTH,

    # Operators
    'MOD': TokenType.MOD,
    'NOT': TokenType.NOT,
    'AND': TokenType.AND,
    'OR': TokenType.OR,
    'XOR': TokenType.XOR,
    'EQV': TokenType.EQV,
    'IMP': TokenType.IMP,

    # Numeric functions
    'ABS': TokenType.ABS,
    'ATN': TokenType.ATN,
    'CDBL': TokenType.CDBL,
    'CINT': TokenType.CINT,
    'COS': TokenType.COS,
    'CSNG': TokenType.CSNG,
    'EXP': TokenType.EXP,
    'FIX': TokenType.FIX,
    'INT': TokenType.INT,
    'LOG': TokenType.LOG,
    'RND': TokenType.RND,
    'SGN': TokenType.SGN,
    'SIN': TokenType.SIN,
    'SQR': TokenType.SQR,
    'TAN': TokenType.TAN,

    # String functions (with $ suffix)
    'ASC': TokenType.ASC,
    'CHR$': TokenType.CHR,
    'HEX$': TokenType.HEX,
    'INKEY$': TokenType.INKEY,
    'INPUT$': TokenType.INPUT_FUNC,
    'INSTR': TokenType.INSTR,
    'LEFT$': TokenType.LEFT,
    'LEN': TokenType.LEN,
    'MID$': TokenType.MID,
    'OCT$': TokenType.OCT,
    'RIGHT$': TokenType.RIGHT,
    'SPACE$': TokenType.SPACE,
    'STR$': TokenType.STR,
    'STRING$': TokenType.STRING_FUNC,
    'VAL': TokenType.VAL,

    # Other functions
    'EOF': TokenType.EOF_FUNC,
    'INP': TokenType.INP,
    'PEEK': TokenType.PEEK,
    'POS': TokenType.POS,
    'USR': TokenType.USR,
}
