"""Cursor column rules shared by PRINT, POS and the output handlers.

Real MBASIC 5.21 counts the column of every character it sends to the
screen or to a file. PRINT uses that count for TAB, for the comma zones and
for the line wrap, and POS(0) reports it. The rules below were measured on
the real interpreter (see docs/dev/PRINT_COLUMNS.md).
"""

SCREEN_WIDTH = 80        # the console width MBASIC starts with
FILE_WIDTH = 255         # the width of a disk file
ZONE_WIDTH = 14          # comma zone width


def advance_column(col: int, text: str) -> int:
    """Return the column after sending text, starting at column col (0-based).

    A newline or a carriage return goes back to column 0. A tab moves to the
    next multiple of 8 and a backspace moves left one column. The other
    control characters do not move the cursor. The wrap at the line width is
    not done here: PRINT inserts the newline itself, so the text seen here
    already holds it.
    """
    for ch in text:
        if ch == '\n' or ch == '\r':
            col = 0
        elif ch == '\t':
            col = (col // 8 + 1) * 8
        elif ch == '\b':
            col = col - 1 if col > 0 else 0
        elif ch >= ' ':
            col += 1
    return col


def moves_cursor(ch: str) -> bool:
    """True when the character is printable, so it needs room on the line."""
    return ch >= ' '


def wrap_text(col: int, width: int, text: str, whole_item: bool = True):
    """Lay out text for a line of the given width, starting at column col.

    Returns (text_with_newlines_added, new_col). MBASIC wraps lazily: a line
    that is exactly full stays as it is until the next printable character
    arrives. With whole_item true, an item that does not fit in the rest of a
    line starts on a new line first (a PRINT item); SPC passes false and
    wraps one character at a time. An item longer than the width is split at
    the width.
    """
    out = []
    if whole_item and col > 0 and col + len(text) > width:
        out.append('\n')
        col = 0
    for ch in text:
        # The binary tests for equal, not for beyond: a width of 0 (which
        # WIDTH 0 sets) wraps only at column 0, once, before the first
        # character of a line.
        if moves_cursor(ch) and (col >= width if width else col == 0):
            out.append('\n')
            col = 0
        out.append(ch)
        col = advance_column(col, ch)
    return ''.join(out), col


INFINITE = 255           # a screen width of 255 never wraps; its column stops at 255


def screen_wrap_width(width: int) -> int:
    """The width the screen wraps at: a width of 255 is infinite (no wrap)."""
    return 1 << 30 if width >= INFINITE else width


def tab_target(n: int, width: int, infinite: bool = False) -> int:
    """The 0-based column TAB(n) goes to: n is 1-based and wraps at the width.

    On a screen of width 255 (infinite) the count is a byte: n modulo 256.
    """
    if width == 0 and not infinite:
        raise ZeroDivisionError("Division by zero")    # the binary divides by the width
    if n < 1:
        return 0
    return (n - 1) % (256 if infinite else width)


def spc_count(n: int, width: int, infinite: bool = False) -> int:
    """How many spaces SPC(n) prints: n modulo the width (modulo 256 when infinite)."""
    if width == 0 and not infinite:
        raise ZeroDivisionError("Division by zero")    # the binary divides by the width
    n = max(n, 0)
    return n % (256 if infinite else width)


def comma_step(col: int, width: int, infinite: bool = False):
    """What a comma does at column col: ('pad', spaces) or ('newline', 0).

    The next zone starts at the next multiple of 14. A zone that would not
    fit completely in the line is not used, so a comma in the last zone
    starts a new line. When the width is under 14 no zone fits and real MBASIC
    has no last-zone limit (the limit is a byte that wraps to 242): the comma
    pads to the next multiple of 14 and the spaces wrap.
    """
    zone = (col // ZONE_WIDTH + 1) * ZONE_WIDTH
    if infinite and col >= INFINITE:
        return ('pad', zone - col)    # the column stops at 255: no last-zone limit
    if width >= ZONE_WIDTH and zone + ZONE_WIDTH > width:
        return ('newline', 0)
    return ('pad', zone - col)
