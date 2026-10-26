"""Where MBASIC ends the line number of a typed or loaded line.

MBASIC reads the digits of a line number into a 16 bit value and stops
before a digit that would take the value above 65529: once the value is 6553
or more, the next digit is not part of the number.  So 65529 is a line
number, but 70000 is line 7000 followed by the text "0" (measured on MBASIC
5.21 under cpmemu; LINGET in the 5.21 source does the same test).
"""

import re

_DIGITS = re.compile(r'\d+')


def split_line_number(text: str):
    """Return (line_number, rest) for text that starts with digits, else None.

    rest is the text after the number.  The digits MBASIC does not take
    stay at the start of rest.
    """
    match = _DIGITS.match(text)
    if not match:
        return None
    value = 0
    taken = 0
    for ch in match.group(0):
        if value >= 6553:
            break
        value = value * 10 + int(ch)
        taken += 1
    return value, text[taken:]


def normalize_line_number(text: str) -> str:
    """Rewrite text so that its line number is the one MBASIC reads.

    "70000 PRINT 1" becomes "7000 0 PRINT 1".  Text that starts with no
    digit, or with a line number MBASIC reads whole, is returned unchanged.
    """
    split = split_line_number(text)
    if split is None:
        return text
    value, rest = split
    if not rest[:1].isdigit():
        return text
    return "%d %s" % (value, rest)
