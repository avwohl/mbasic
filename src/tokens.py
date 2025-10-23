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
    FILES = auto()
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
    ALL = auto()             # ALL (used in CHAIN)
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


# Keywords mapping (case-insensitive, use lowercase since lexer normalizes to lowercase)
# String functions include $ as part of the name
KEYWORDS = {
    # Program control
    'auto': TokenType.AUTO,
    'cont': TokenType.CONT,
    'delete': TokenType.DELETE,
    'edit': TokenType.EDIT,
    'files': TokenType.FILES,
    'list': TokenType.LIST,
    'llist': TokenType.LLIST,
    'load': TokenType.LOAD,
    'merge': TokenType.MERGE,
    'new': TokenType.NEW,
    'renum': TokenType.RENUM,
    'run': TokenType.RUN,
    'save': TokenType.SAVE,

    # File operations
    'as': TokenType.AS,
    'close': TokenType.CLOSE,
    'field': TokenType.FIELD,
    'get': TokenType.GET,
    'input': TokenType.INPUT,
    'kill': TokenType.KILL,
    'line': TokenType.LINE_INPUT,  # Will need special handling for "LINE INPUT"
    'lset': TokenType.LSET,
    'name': TokenType.NAME,
    'open': TokenType.OPEN,
    'output': TokenType.OUTPUT,
    'put': TokenType.PUT,
    'reset': TokenType.RESET,
    'rset': TokenType.RSET,

    # Control flow
    'all': TokenType.ALL,
    'call': TokenType.CALL,
    'chain': TokenType.CHAIN,
    'else': TokenType.ELSE,
    'end': TokenType.END,
    'for': TokenType.FOR,
    'gosub': TokenType.GOSUB,
    'goto': TokenType.GOTO,
    'if': TokenType.IF,
    'next': TokenType.NEXT,
    'on': TokenType.ON,
    'resume': TokenType.RESUME,
    'return': TokenType.RETURN,
    'step': TokenType.STEP,
    'stop': TokenType.STOP,
    'system': TokenType.SYSTEM,
    'then': TokenType.THEN,
    'to': TokenType.TO,
    'while': TokenType.WHILE,
    'wend': TokenType.WEND,

    # Data/Arrays
    'base': TokenType.BASE,
    'clear': TokenType.CLEAR,
    'common': TokenType.COMMON,
    'data': TokenType.DATA,
    'def': TokenType.DEF,
    'defint': TokenType.DEFINT,
    'defsng': TokenType.DEFSNG,
    'defdbl': TokenType.DEFDBL,
    'defstr': TokenType.DEFSTR,
    'dim': TokenType.DIM,
    'erase': TokenType.ERASE,
    'fn': TokenType.FN,
    'let': TokenType.LET,
    'option': TokenType.OPTION,
    'read': TokenType.READ,
    'restore': TokenType.RESTORE,

    # I/O
    'print': TokenType.PRINT,
    'lprint': TokenType.LPRINT,
    'write': TokenType.WRITE,

    # Other
    'error': TokenType.ERROR,
    'out': TokenType.OUT,
    'poke': TokenType.POKE,
    'randomize': TokenType.RANDOMIZE,
    'rem': TokenType.REM,
    'remark': TokenType.REMARK,
    'swap': TokenType.SWAP,
    'wait': TokenType.WAIT,
    'width': TokenType.WIDTH,

    # Operators
    'mod': TokenType.MOD,
    'not': TokenType.NOT,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'xor': TokenType.XOR,
    'eqv': TokenType.EQV,
    'imp': TokenType.IMP,

    # Numeric functions
    'abs': TokenType.ABS,
    'atn': TokenType.ATN,
    'cdbl': TokenType.CDBL,
    'cint': TokenType.CINT,
    'cos': TokenType.COS,
    'csng': TokenType.CSNG,
    'exp': TokenType.EXP,
    'fix': TokenType.FIX,
    'int': TokenType.INT,
    'log': TokenType.LOG,
    'rnd': TokenType.RND,
    'sgn': TokenType.SGN,
    'sin': TokenType.SIN,
    'sqr': TokenType.SQR,
    'tan': TokenType.TAN,

    # String functions (with $ suffix)
    'asc': TokenType.ASC,
    'chr$': TokenType.CHR,
    'hex$': TokenType.HEX,
    'inkey$': TokenType.INKEY,
    'input$': TokenType.INPUT_FUNC,
    'instr': TokenType.INSTR,
    'left$': TokenType.LEFT,
    'len': TokenType.LEN,
    'mid$': TokenType.MID,
    'oct$': TokenType.OCT,
    'right$': TokenType.RIGHT,
    'space$': TokenType.SPACE,
    'str$': TokenType.STR,
    'string$': TokenType.STRING_FUNC,
    'val': TokenType.VAL,

    # Other functions
    'eof': TokenType.EOF_FUNC,
    'inp': TokenType.INP,
    'peek': TokenType.PEEK,
    'pos': TokenType.POS,
    'usr': TokenType.USR,
}
