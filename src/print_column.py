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
        if moves_cursor(ch) and col >= width:
            out.append('\n')
            col = 0
        out.append(ch)
        col = advance_column(col, ch)
    return ''.join(out), col


def tab_target(n: int, width: int) -> int:
    """The 0-based column TAB(n) goes to: n is 1-based and wraps at the width."""
    if n < 1:
        return 0
    return (n - 1) % width


def comma_step(col: int, width: int):
    """What a comma does at column col: ('pad', spaces) or ('newline', 0).

    The next zone starts at the next multiple of 14. A zone that would not
    fit completely in the line is not used, so a comma in the last zone
    starts a new line.
    """
    zone = (col // ZONE_WIDTH + 1) * ZONE_WIDTH
    if zone + ZONE_WIDTH > width:
        return ('newline', 0)
    return ('pad', zone - col)
