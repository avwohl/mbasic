"""RENUM on the program text, the way MBASIC 5.21 does it.

Real MBASIC keeps a program as tokenised text.  When it tokenises a line it
turns the digits that follow certain keywords into a "line number constant".
RENUM then rewrites only those constants.  Every other byte of the line stays
as it was.  This module does the same on the source text of a line:

1. scan_line_references() finds the digits that MBASIC would tokenise as line
   numbers.  It follows the tokeniser (CRUNCH in bintrp.mac) closely, so it
   gives the same answer for GOTO10, ON ERROR GOTO 0, ERL=10, DATA and so on.
2. renumber_lines() maps old line numbers to new ones and replaces only those
   digits.  A reference to a line that does not exist stays as it is, and a
   message "Undefined line nnnnn in mmmmm" is returned for it.

The caller re-parses each changed line to get a new AST.  No code here
generates BASIC text from an AST.
"""

import re
from typing import Dict, List, NamedTuple, Optional, Tuple

MAX_LINE_NUMBER = 65529
DEFAULT_START = 10
DEFAULT_INCREMENT = 10


class RenumError(ValueError):
    """RENUM failed.  mbasic_code is the MBASIC error number (2 or 5)."""

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.mbasic_code = code


def _syntax_error() -> RenumError:
    return RenumError("Syntax error", 2)


def _illegal_function_call() -> RenumError:
    return RenumError("Illegal function call", 5)


# ---------------------------------------------------------------------------
# Scanning a line for line number constants
# ---------------------------------------------------------------------------

#: Keywords after which MBASIC reads digits as a line number (see CRUNCH).
LINE_NUMBER_KEYWORDS = frozenset([
    'RESTORE', 'AUTO', 'RENUM', 'DELETE', 'EDIT', 'RESUME', 'ERL', 'ELSE',
    'RUN', 'LIST', 'LLIST', 'GOTO', 'THEN', 'GOSUB',
])

#: Every other reserved word of MBASIC 5.21.  After one of these, digits are
#: ordinary numbers.  A word that is missing here is read as a variable name,
#: which has the same effect for RENUM.
OTHER_KEYWORDS = frozenset([
    'END', 'FOR', 'NEXT', 'DATA', 'INPUT', 'DIM', 'READ', 'LET', 'IF',
    'RETURN', 'REM', 'STOP', 'PRINT', 'CLEAR', 'NEW', 'ON', 'NULL', 'WAIT',
    'DEF', 'POKE', 'CONT', 'OUT', 'LPRINT', 'WIDTH', 'ERROR', 'OPEN', 'CLOSE',
    'FIELD', 'GET', 'PUT', 'LSET', 'RSET', 'NAME', 'FILES', 'KILL', 'SAVE',
    'LOAD', 'MERGE', 'SYSTEM', 'RANDOMIZE', 'CALL', 'ERASE', 'SWAP',
    'DEFSTR', 'DEFINT', 'DEFSNG', 'DEFDBL', 'TRON', 'TROFF', 'CHAIN',
    'COMMON', 'WRITE', 'WHILE', 'WEND', 'RESET', 'LINE', 'OPTION',
    'TO', 'USING', 'NOT', 'STEP', 'AND', 'OR', 'XOR', 'EQV', 'IMP', 'MOD',
    'AS', 'ERR', 'OUTPUT', 'SGN', 'INT', 'ABS', 'FRE', 'INP', 'POS', 'SQR',
    'RND', 'LOG', 'EXP', 'COS', 'SIN', 'TAN', 'ATN', 'PEEK', 'LEN', 'VAL',
    'ASC', 'CVI', 'CVS', 'CVD', 'EOF', 'LOC', 'LOF', 'CINT', 'CSNG', 'CDBL',
    'FIX', 'INSTR', 'VARPTR', 'LPOS',
    # reserved words that end in $ or ( - matched with that character
    'STR$', 'CHR$', 'LEFT$', 'RIGHT$', 'MID$', 'MKI$', 'MKS$', 'MKD$',
    'HEX$', 'OCT$', 'INKEY$', 'STRING$', 'SPACE$', 'INPUT$', 'TAB(', 'SPC(',
])

_NAME_RUN = re.compile(r'[A-Za-z][A-Za-z0-9.]*')
_GO_WORD = re.compile(r'[Gg][Oo] +(?:([Tt][Oo])|([Ss][Uu][Bb]))')
_FLOAT = re.compile(r'(?:\d+\.?\d*|\.\d+)(?:[EeDd][+-]?\d+)?[%!#]?')
_RADIX = re.compile(r'&(?:[Hh][0-9A-Fa-f]*|[Oo][0-7]*|[0-7]*)')


class Reference(NamedTuple):
    """One line number constant: text[start:end] holds the digits."""
    start: int
    end: int
    value: int
    skip: bool      # ON ERROR GOTO 0: RENUM leaves this 0 alone


def _read_line_number(text: str, pos: int) -> Tuple[int, int, int]:
    """Read a line number constant the way LINGET does.

    Spaces between digits belong to the number, spaces after the last digit do
    not.  Reading stops before a digit when the value so far is above 6552, so
    that 70000 is the two constants 7000 and 0.

    Returns (value, last_digit_end, next_pos_to_scan).
    """
    value = 0
    i = pos
    end = pos
    while True:
        if value > 6552:
            break
        value = value * 10 + int(text[i])
        i += 1
        end = i
        j = i
        while j < len(text) and text[j] in ' \t':
            j += 1
        if j < len(text) and text[j].isdigit():
            i = j
            continue
        break
    return value, end, end


def scan_line_references(text: str, start: int = 0) -> List[Reference]:
    """Find the line number constants in text[start:].

    text is a program line; start is the index just after the line number.
    """
    refs: List[Reference] = []
    events: List[str] = []      # keywords and 'x' for anything else, no spaces
    donum = 0                   # 0 numbers, 1 line numbers, -1 inside a name
    in_data = False
    n = len(text)
    i = start

    def keyword(word: str):
        nonlocal donum, in_data
        events.append(word)
        donum = 1 if word in LINE_NUMBER_KEYWORDS else 0

    while i < n:
        c = text[i]

        if c == '"':
            events.append('x')
            j = text.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == ' ':
            i += 1
            continue
        if in_data:
            if c == ':':
                in_data = False
                donum = 0
                events.append('x')
            i += 1
            continue
        if c == '?':
            keyword('PRINT')
            i += 1
            continue

        if c.isalpha():
            m = _GO_WORD.match(text, i)
            if m:
                keyword('GOTO' if m.group(1) else 'GOSUB')
                i = m.end()
                continue
            m = _NAME_RUN.match(text, i)
            run = m.group(0).upper()
            end = m.end()
            word = None
            if end < n and text[end] == '$' and run + '$' in OTHER_KEYWORDS:
                word, end = run + '$', end + 1
            elif end < n and text[end] == '(' and run + '(' in OTHER_KEYWORDS:
                word, end = run + '(', end + 1
            elif run in LINE_NUMBER_KEYWORDS or run in OTHER_KEYWORDS:
                word = run
            elif run.startswith('FN') or run.startswith('USR'):
                word = 'FN' if run.startswith('FN') else 'USR'
                end = i + len(word)
            if word is None:
                events.append('x')
                donum = -1
                i = end
                continue
            keyword(word)
            i = end
            if word == 'REM':
                break
            if word == 'DATA':
                in_data = True
                donum = 1
            continue

        if c == "'":
            break
        if c.isdigit() or c == '.':
            if donum < 0 or (c == '.' and donum > 0):
                events.append('x')
                i += 1
                continue
            if donum == 0:
                m = _FLOAT.match(text, i)
                events.append('x')
                i = m.end() if m else i + 1
                continue
            value, end, nxt = _read_line_number(text, i)
            skip = value == 0 and events[-2:] == ['ERROR', 'GOTO']
            refs.append(Reference(i, end, value, skip))
            events.append('x')
            i = nxt
            continue
        if c == '&':
            m = _RADIX.match(text, i)
            events.append('x')
            i = m.end()
            continue
        if c == ':':
            donum = 0
            events.append('x')
            i += 1
            continue
        # any other character: it ends a variable name, nothing else changes
        if donum < 0:
            donum = 0
        events.append('x')
        i += 1
    return refs


# ---------------------------------------------------------------------------
# RENUM arguments
# ---------------------------------------------------------------------------

def _get_line_number(args: str, i: int) -> Tuple[int, int]:
    """LINGET on the argument text.  No digits gives 0."""
    if i < len(args) and args[i].isdigit():
        value, _, i = _read_line_number(args, i)
        return value, i
    return 0, i


def _skip_spaces(args: str, i: int) -> int:
    while i < len(args) and args[i] in ' \t':
        i += 1
    return i


def _at_end(args: str, i: int) -> bool:
    return i >= len(args) or args[i] == ':'


def parse_renum_arguments(args: str) -> Tuple[int, int, int]:
    """Parse RENUM [new_start][,[old_start][,increment]] like MBASIC.

    Returns (new_start, old_start, increment).  Raises RenumError for
    "Syntax error" and for an increment of zero ("Illegal function call").
    """
    new_start, old_start, increment = DEFAULT_START, 0, DEFAULT_INCREMENT
    i = _skip_spaces(args, 0)
    if _at_end(args, i):
        return new_start, old_start, increment
    if args[i] != ',':
        new_start, i = _get_line_number(args, i)
        i = _skip_spaces(args, i)
        if _at_end(args, i):
            return new_start, old_start, increment
    if args[i] != ',':
        raise _syntax_error()
    old_start, i = _get_line_number(args, _skip_spaces(args, i + 1))
    i = _skip_spaces(args, i)
    if _at_end(args, i):
        return new_start, old_start, increment
    if args[i] != ',':
        raise _syntax_error()
    increment, i = _get_line_number(args, _skip_spaces(args, i + 1))
    if not _at_end(args, _skip_spaces(args, i)):
        raise _syntax_error()
    if increment == 0:
        raise _illegal_function_call()
    return new_start, old_start, increment


# ---------------------------------------------------------------------------
# Renumbering
# ---------------------------------------------------------------------------

def build_line_map(old_numbers: List[int], new_start: int, old_start: int,
                   increment: int) -> Dict[int, int]:
    """Old line number -> new line number, with MBASIC's checks.

    Lines below old_start keep their number.  Raises RenumError ("Illegal
    function call") when the new numbers would reach back to a line that stays
    or go above 65529.
    """
    numbers = sorted(old_numbers)
    first = next((k for k, num in enumerate(numbers) if num >= old_start),
                 len(numbers))
    first_new = next((k for k, num in enumerate(numbers) if num >= new_start),
                     len(numbers))
    if first_new < first:
        raise _illegal_function_call()
    mapping = {num: num for num in numbers[:first]}
    new = new_start
    for num in numbers[first:]:
        if new > MAX_LINE_NUMBER:
            raise _illegal_function_call()
        mapping[num] = new
        new += increment
    return mapping


_LINE_NUMBER = re.compile(r'\s*(\d+)')


def renumber_lines(lines: Dict[int, str], new_start: int = DEFAULT_START,
                   old_start: int = 0, increment: int = DEFAULT_INCREMENT
                   ) -> Tuple[Dict[int, str], Dict[int, int], List[str]]:
    """Renumber program text.

    lines maps line number to the full line text, line number included.
    Returns (new_lines, line_map, messages).  new_lines is keyed by the new
    line numbers.  messages holds "Undefined line n in m" for each reference
    to a line that does not exist; the reference is left as it is.  Nothing is
    changed when RenumError is raised.
    """
    line_map = build_line_map(list(lines), new_start, old_start, increment)
    new_lines: Dict[int, str] = {}
    messages: List[str] = []
    for old in sorted(lines):
        text = lines[old]
        m = _LINE_NUMBER.match(text)
        body_start = m.end() if m else 0
        pieces = []
        last = body_start
        for ref in scan_line_references(text, body_start):
            if ref.skip:
                continue
            if ref.value not in line_map:
                messages.append(f"Undefined line {ref.value} in {old}")
                continue
            pieces.append(text[last:ref.start])
            pieces.append(str(line_map[ref.value]))
            last = ref.end
        pieces.append(text[last:])
        body = ''.join(pieces)
        if m:
            prefix = text[:m.start(1)] + str(line_map[old])
        else:
            prefix = ''
        new_lines[line_map[old]] = prefix + body
    return new_lines, line_map, messages
