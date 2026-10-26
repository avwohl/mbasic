"""Field parsing for INPUT and INPUT #, as MBASIC 5.21 does it.

Every rule here was checked against the real MBASIC 5.21 binary under cpmemu.
The keyboard rules match the JavaScript runtime in codegen_js_backend.py
(_input_fields, _input_number); the file rules are the ones real MBASIC uses
for INPUT #, which differ from the keyboard rules (see read_file_field).
"""

import re

from src.number_format import MBF_INFINITY_DOUBLE

# MBASIC's largest number. Anything beyond it is "Overflow" for single and double alike.
MAX_FLOAT = 1.7014118346046923e38

# A suffix (% ! #) is allowed only after a number without an exponent part.
_NUMBER = re.compile(r'^([+-]?)(\d*\.?\d*)(?:[EeDd]([+-]?\d*)|([%!#]))?$')
_PREFIX = re.compile(r'^([+-]?)(\d*\.?\d*)(?:[EeDd]([+-]?\d+))?')


def _round_percent(value):
    """A number typed with a % suffix becomes an integer, halves away from zero.

    Real MBASIC raises Overflow when the result is outside 16 bits.
    """
    value = float(int(value + 0.5)) if value >= 0 else -float(int(-value + 0.5))
    if value > 32767 or value < -32768:
        raise OverflowError("Overflow")
    return value


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


def _word(value):
    """The signed 16-bit word for an &H or &O value; more than 16 bits is an Overflow error."""
    if value > 65535:
        raise OverflowError("Overflow")  # real MBASIC stops with an error, it does not ask again
    return value - 65536 if value >= 32768 else value


def _keyboard_radix(s):
    """Value of an &... answer (no outer blanks), or None for Redo.

    &H takes hex digits and no blanks. &O, and & alone, take octal digits and
    blanks are ignored. A digit 8 or 9 in an octal number is a Syntax error,
    not a Redo. Any other bad character is a Redo. Bare &, &H and &O are 0.
    """
    if s[1:2] in ('H', 'h'):
        digits = s[2:]
        if not re.match(r'^[0-9A-Fa-f]*$', digits):
            return None
        return _word(int(digits, 16)) if digits else 0
    digits = re.sub(r'[ \t]', '', s[2:] if s[1:2] in ('O', 'o') else s[1:])
    lead = re.match(r'[0-9]*', digits).group(0)
    if '8' in lead or '9' in lead:
        raise RuntimeError("Syntax error")
    if lead != digits:
        return None
    return _word(int(digits, 8)) if digits else 0


def keyboard_number(text):
    """Convert one INPUT field to a number, or None for "?Redo from start".

    Blanks inside the number are ignored ("1 2" is 12), an empty field is 0,
    &H and &O numbers are accepted. A % suffix rounds to an integer.
    The caller rounds for integer variables and range-checks floats.
    """
    stripped = text.strip(' \t')
    if stripped[:1] == '&':
        return _keyboard_radix(stripped)
    s = re.sub(r'[ \t]', '', text)
    if s == '':
        return 0
    m = _NUMBER.match(s)
    if not m:
        return None
    digits = '' if m.group(2) == '.' else m.group(2)
    exp = m.group(3)
    if exp in (None, '', '+', '-'):
        exp = '0'
    try:
        value = float(m.group(1) + (digits or '0') + 'e' + exp)
    except OverflowError:
        return None
    if m.group(4) == '%':
        value = _round_percent(value)
    return value


_VAL_MANTISSA = re.compile(r'([+-]?)(\d*)(\.?)(\d*)')
_VAL_EXPONENT = re.compile(r'[EeDd]([+-]?)(\d*)')


def _val_radix(s):
    """VAL of text that starts with & (leading blanks already gone).

    &H takes hex digits and no blanks after the H; &O, and & with an octal
    digit, take octal digits with blanks between them. More than four hex
    digits (leading zeros count), or an octal number above 65535, is Overflow;
    an 8 or 9 in an octal number is a Syntax error. The value is a signed
    16-bit word. Anything else after the & is 0.
    """
    i = 1
    while i < len(s) and s[i] in ' \t':
        i += 1
    kind = s[i:i + 1].upper()
    if kind == 'H':
        digits = re.match(r'[0-9A-Fa-f]*', s[i + 1:]).group(0)
        if len(digits) > 4:
            raise OverflowError("Overflow")
        return _word(int(digits, 16)) if digits else 0
    if kind == 'O':
        i += 1
    elif not kind.isdigit():
        return 0
    run = ''
    for ch in s[i:]:
        if ch in ' \t':
            continue
        if not ch.isdigit():
            break
        run += ch
    if '8' in run or '9' in run:
        raise RuntimeError("Syntax error")
    return _word(int(run, 8)) if run else 0


def val_text(text):
    """MBASIC's VAL: the number at the start of the text, 0 if there is none.

    Spaces, tabs and line feeds are skipped everywhere in a decimal number ("1 2" is 12,
    "- 5" is -5, "1 E 2" is 100). The exponent letter is E or D in either
    case, and with no digits after it the exponent is 0. The number ends at
    the second point, at a second E, and at any other character. A % right
    after a number with no exponent rounds it to a 16-bit integer.
    &H, &O and & constants are signed 16-bit words (_val_radix).
    Everything above was checked against MBASIC 5.21 under cpmemu.
    A number too big for a double comes back as infinity; the interpreter
    turns that into Overflow.
    """
    s = text.lstrip(' \t\n')
    if s[:1] == '&':
        return _val_radix(s)
    s = s.replace(' ', '').replace('\t', '').replace('\n', '')
    m = _VAL_MANTISSA.match(s)
    if not m.group(2) and not m.group(4):
        return 0
    rest = s[m.end():]
    exponent = '0'
    has_exponent = False
    e = _VAL_EXPONENT.match(rest)
    if e:
        has_exponent = True
        if e.group(2):
            exponent = e.group(1) + e.group(2)
        rest = rest[e.end():]
    value = float(f"{m.group(1)}{m.group(2) or '0'}.{m.group(4) or '0'}e{exponent}")
    if not has_exponent and rest[:1] == '%':
        value = _round_percent(value)
    # An MBF number stops at 1.70141E+38 (beyond: Overflow) and at 2^-129 (below: 0), measured
    if abs(value) > MBF_INFINITY_DOUBLE:
        return float('-inf') if value < 0 else float('inf')
    if abs(value) < 2.0 ** -129:
        return 0.0
    return value


def val_number(text):
    """MBASIC's VAL rule, used for numbers read from a file: leading blanks,
    then the longest number at the start; anything else gives 0.
    &H takes hex digits, & and &O take octal digits. A % right after a number
    without an exponent rounds it to an integer (Overflow beyond 16 bits).
    Measured on MBASIC 5.21: &O/&H/& forms, 1.5%, 40000%, 1e5%.
    """
    s = text.strip(' \t')
    if s[:1] == '&':
        base = 16 if s[1:2] in ('H', 'h') else 8
        allowed = '0123456789ABCDEFabcdef' if base == 16 else '01234567'
        start = 2 if s[1:2] in ('H', 'h', 'O', 'o') else 1
        k = start
        while k < len(s) and s[k] in allowed:
            k += 1
        if k == start:
            return 0
        return _word(int(s[start:k], base) & 0xFFFF)
    m = _PREFIX.match(s)
    if not m or (m.group(2) in ('', '.')):
        return 0
    digits = m.group(2)
    exp = m.group(3) or '0'
    try:
        value = float(m.group(1) + digits + 'e' + exp)
    except OverflowError:
        return MAX_FLOAT if m.group(1) != '-' else -MAX_FLOAT
    if m.group(3) is None and s[m.end():m.end() + 1] == '%':
        value = _round_percent(value)
    return value


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
      A quote is no quote for a number: "5" is 0 and the field ends at the
      next blank, comma or line end.
    Returns (text, was_quoted) or None when no byte is left at all.
    """
    b = read_byte()
    while b is not None and b in (32, 9):
        b = read_byte()
    if b is None:
        return None
    out = bytearray()
    quoted = False
    if b == 34 and not numeric:
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
