"""
Token definitions for MBASIC 5.21 (CP/M era MBASIC-80)
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
    LIMITS = auto()
    SHOWSETTINGS = auto()
    SETSETTING = auto()

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
    CLS = auto()
    PRINT = auto()
    LPRINT = auto()
    WRITE = auto()

    # Keywords - Other
    COMMON = auto()
    ERROR = auto()
    ERR = auto()
    ERL = auto()
    HELP = auto()
    OUT = auto()
    POKE = auto()
    RANDOMIZE = auto()
    REM = auto()
    REMARK = auto()          # Synonym for REM
    SET = auto()             # SET (for settings, not same as LET)
    SETTINGS = auto()        # SETTINGS (used in SHOW SETTINGS)
    SHOW = auto()            # SHOW (for SHOW SETTINGS)
    SWAP = auto()
    TRON = auto()
    TROFF = auto()
    USING = auto()
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
    CVD = auto()             # CVD (convert string to double)
    CVI = auto()             # CVI (convert string to integer)
    CVS = auto()             # CVS (convert string to single)
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
    MKD = auto()             # MKD$ (convert double to string)
    MKI = auto()             # MKI$ (convert integer to string)
    MKS = auto()             # MKS$ (convert single to string)
    OCT = auto()             # OCT$
    RIGHT = auto()           # RIGHT$
    SPACE = auto()           # SPACE$
    STR = auto()             # STR$
    STRING_FUNC = auto()     # STRING$ function
    VAL = auto()

    # Built-in Functions - Other
    EOF_FUNC = auto()        # EOF
    INP = auto()
    LOC = auto()             # LOC
    LOF = auto()             # LOF
    PEEK = auto()
    POS = auto()
    SPC = auto()             # SPC (print spacing function)
    TAB = auto()             # TAB (print tab function)
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
    """Represents a single token in MBASIC source code.

    Attributes:
        type: Token type (keyword, identifier, number, etc.)
        value: Normalized value (lowercase for identifiers/keywords)
        line: Line number where token appears
        column: Column number where token starts
        original_case: Original case for user-defined identifiers (variable names) before normalization.
                      Only set for IDENTIFIER tokens. Example: "myVar" stored here, "myvar" in value.
        original_case_keyword: Original case for keywords, determined by keyword case policy.
                              Only set for keyword tokens (PRINT, IF, GOTO, etc.). Used by serializer
                              to output keywords with consistent or preserved case style.

    Note: These fields serve different purposes and should be mutually exclusive
    (identifiers use original_case, keywords use original_case_keyword):
    - original_case: For identifiers (user variables) - preserves what user typed
    - original_case_keyword: For keywords - stores policy-determined display case
    The dataclass doesn't enforce this exclusivity, but code should maintain it.
    """
    type: TokenType
    value: Any  # Normalized value (lowercase for identifiers and keywords)
    line: int
    column: int
    original_case: Any = None  # Original case for user identifiers (variables only, not keywords)
    original_case_keyword: str = None  # Display case for keywords (policy-determined, not identifiers)

    def __repr__(self):
        # Show both original cases if available
        extras = []
        if self.original_case and self.original_case != self.value:
            extras.append(f"id:{self.original_case!r}")
        if self.original_case_keyword and self.original_case_keyword != self.value:
            extras.append(f"kw:{self.original_case_keyword!r}")

        if extras:
            return f"Token({self.type.name}, {self.value!r} [{', '.join(extras)}], {self.line}:{self.column})"
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
    'limits': TokenType.LIMITS,
    'showsettings': TokenType.SHOWSETTINGS,
    'setsetting': TokenType.SETSETTING,

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
    'cls': TokenType.CLS,
    'print': TokenType.PRINT,
    'lprint': TokenType.LPRINT,
    'write': TokenType.WRITE,

    # Other
    'error': TokenType.ERROR,
    'err': TokenType.ERR,
    'erl': TokenType.ERL,
    'help': TokenType.HELP,
    'out': TokenType.OUT,
    'poke': TokenType.POKE,
    'randomize': TokenType.RANDOMIZE,
    'rem': TokenType.REM,
    'remark': TokenType.REMARK,
    'set': TokenType.SET,
    'settings': TokenType.SETTINGS,
    'show': TokenType.SHOW,
    'swap': TokenType.SWAP,
    'tron': TokenType.TRON,
    'troff': TokenType.TROFF,
    'using': TokenType.USING,
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
    'cvd': TokenType.CVD,
    'cvi': TokenType.CVI,
    'cvs': TokenType.CVS,
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
    'mkd$': TokenType.MKD,
    'mki$': TokenType.MKI,
    'mks$': TokenType.MKS,
    'oct$': TokenType.OCT,
    'right$': TokenType.RIGHT,
    'space$': TokenType.SPACE,
    'str$': TokenType.STR,
    'string$': TokenType.STRING_FUNC,
    'val': TokenType.VAL,

    # Other functions
    'eof': TokenType.EOF_FUNC,
    'inp': TokenType.INP,
    'loc': TokenType.LOC,
    'lof': TokenType.LOF,
    'peek': TokenType.PEEK,
    'pos': TokenType.POS,
    'spc': TokenType.SPC,
    'tab': TokenType.TAB,
    'usr': TokenType.USR,
}
