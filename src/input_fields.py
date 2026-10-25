"""Field parsing for INPUT and INPUT #, as MBASIC 5.21 does it.

Every rule here was checked against the real MBASIC 5.21 binary under cpmemu.
The keyboard rules match the JavaScript runtime in codegen_js_backend.py
(_input_fields, _input_number); the file rules are the ones real MBASIC uses
for INPUT #, which differ from the keyboard rules (see read_file_field).
"""

import re

# MBASIC's largest number. Anything beyond it is "Overflow" for single and double alike.
MAX_FLOAT = 1.7014118346046923e38

_NUMBER = re.compile(r'^([+-]?)(\d*\.?\d*)(?:[EeDd]([+-]?\d*))?[%!#]?$')
_PREFIX = re.compile(r'^([+-]?)(\d*\.?\d*)(?:[EeDd]([+-]?\d+))?')


def split_keyboard_fields(line):
    """Split an INPUT answer at commas.

    A field may be "quoted" and then holds commas; the closing quote may be
    missing. Blanks around a field are dropped. Returns a list of
    (text, was_quoted), or None when text follows a closing quote, which makes
    MBASIC print "?Redo from start".
    """
    fields = []
    n = len(line)
    i = 0
    while True:
        while i < n and line[i] in ' \t':
            i += 1
        quoted = False
        if i < n and line[i] == '"':
            quoted = True
            i += 1
            j = line.find('"', i)
            if j < 0:
                text, i = line[i:], n
            else:
                text, i = line[i:j], j + 1
            while i < n and line[i] in ' \t':
                i += 1
            if i < n and line[i] != ',':
                return None
        else:
            j = line.find(',', i)
            if j < 0:
                j = n
            text = line[i:j].rstrip(' \t')
            i = j
        fields.append((text, quoted))
        if i >= n:
            return fields
        i += 1  # the comma


def _radix_value(text):
    """Value of &H.. or &O.. text as MBASIC's signed 16-bit word, or None if malformed.

    More than 16 bits raises OverflowError (measured: "Overflow in 10", no Redo).
    """
    base = 16 if text[1] in 'Hh' else 8
    digits = text[2:]
    if digits == '':
        return 0
    try:
        value = int(digits, base)
    except ValueError:
        return None
    if value > 65535:
        raise OverflowError("Overflow")  # real MBASIC stops with an error, it does not ask again
    return value - 65536 if value >= 32768 else value


def keyboard_number(text):
    """Convert one INPUT field to a number, or None for "?Redo from start".

    Blanks inside the number are ignored ("1 2" is 12), an empty field is 0,
    &H and &O numbers are accepted. The caller rounds and range-checks.
    """
    s = re.sub(r'[ \t]', '', text)
    if s == '':
        return 0
    if len(s) >= 2 and s[0] == '&' and s[1] in 'HhOo':
        return _radix_value(s)
    m = _NUMBER.match(s)
    if not m:
        return None
    digits = '' if m.group(2) == '.' else m.group(2)
    exp = m.group(3)
    if exp in (None, '', '+', '-'):
        exp = '0'
    try:
        return float(m.group(1) + (digits or '0') + 'e' + exp)
    except OverflowError:
        return None


def val_number(text):
    """MBASIC's VAL rule, used for numbers read from a file: leading blanks,
    then the longest number at the start; anything else gives 0.
    """
    s = text.strip(' \t')
    if len(s) >= 2 and s[0] == '&' and s[1] in 'HhOo':
        base = 16 if s[1] in 'Hh' else 8
        allowed = '0123456789ABCDEFabcdef' if base == 16 else '01234567'
        k = 2
        while k < len(s) and s[k] in allowed:
            k += 1
        if k == 2:
            return 0
        value = int(s[2:k], base) & 0xFFFF
        return value - 65536 if value >= 32768 else value
    m = _PREFIX.match(s)
    if not m or (m.group(2) in ('', '.')):
        return 0
    digits = m.group(2)
    exp = m.group(3) or '0'
    try:
        return float(m.group(1) + digits + 'e' + exp)
    except OverflowError:
        return MAX_FLOAT if m.group(1) != '-' else -MAX_FLOAT


def read_file_field(read_byte, unread_byte, numeric):
    """Read the next INPUT # field from a stream.

    read_byte() returns one byte value or None at end of file (or ^Z);
    unread_byte() puts the last byte back.

    Rules measured on MBASIC 5.21 (they differ from keyboard INPUT):
    - A line end is a plain terminator: a blank line gives an empty field.
    - A "quoted" string runs to the closing quote, across line ends, and the
      closing quote may be missing. Text after the closing quote starts the
      next field.
    - Any other string ends at a comma or line end; trailing blanks go.
    - A number ends at a blank, a comma or a line end, so "1 2" is two numbers.
    - A number is read with the VAL rule: a bad one is 0, not an error.
    Returns (text, was_quoted) or None when no byte is left at all.
    """
    b = read_byte()
    while b is not None and b in (32, 9):
        b = read_byte()
    if b is None:
        return None
    out = bytearray()
    quoted = False
    if b == 34:
        quoted = True
        b = read_byte()
        while b is not None and b != 34:
            out.append(b)
            b = read_byte()
        b = read_byte()
        while b is not None and b in (32, 9):
            b = read_byte()
    else:
        stops = (44, 10, 13, 32, 9) if numeric else (44, 10, 13)
        while b is not None and b not in stops:
            out.append(b)
            b = read_byte()
        if numeric:
            while b is not None and b in (32, 9):
                b = read_byte()
    # b is now the first byte after the field (and its blanks)
    if b == 44:
        pass
    elif b == 13:
        nxt = read_byte()
        if nxt is not None and nxt != 10:
            unread_byte()
    elif b == 10 or b is None:
        pass
    else:
        unread_byte()
    text = out.decode('latin-1')
    if not quoted:
        text = text.rstrip(' \t')
    return text, quoted
