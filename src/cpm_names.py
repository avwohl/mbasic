"""CP/M file names as MBASIC 5.21 under cpmemu accepts them.

MBASIC turns the string of an OPEN, KILL, NAME, LOAD or SAVE into a CP/M file
control block (namfil in dcpm.mac). The routine has two kinds of failure, and
a third comes from the CP/M system underneath:

    64  Bad file name   The string itself cannot be a name: it is empty, the
                        drive letter is not a letter, nothing follows the
                        drive colon, no name stands before the dot, or a second
                        dot comes after the extension has begun
                        (ABCDEFGHI.DAT, A.B.C, .DAT, 1:X, A:).
    67  Too many files  A statement that makes a file (OPEN "O", OPEN "R",
                        SAVE) and a name with a character that the file system
                        refuses: control characters, and  % ( ) * , / : ; < =
                        > [ \\ ] ^ |  and a dot (the bytes 128 and up count as
                        the same byte without bit 7).
    53  File not found  The same name for a statement that reads a file.

All of this was measured on the binary. A name is cut, not refused, when it is
too long: the first 8 characters before the dot are the name and 3 after it
are the type, and a name without a dot may hold 11 characters.

Host names such as inputfile.txt break these rules, so the interpreter applies
them only while the setting cpm_file_names is on. It also lets a name with a
slash or backslash pass, as a host path (the binary gives Too many files).
"""

from typing import Optional

BAD_FILE_NAME = 64
TOO_MANY_FILES = 67
FILE_NOT_FOUND = 53

#: Characters (bit 7 clear) that the file system under MBASIC refuses in a name.
_REFUSED = frozenset('%()*,/:;<=>[\\]^|.')


def _fcb_name(name: str) -> Optional[str]:
    """The 11 characters that namfil puts in the control block.

    Returns None where namfil gives Bad file name. A character that does not
    fit in a byte cannot be in a CP/M name, so it counts as Bad file name too.
    """
    if not name:
        return None
    try:
        name.encode('latin-1')
    except UnicodeEncodeError:
        return None
    rest = name
    if len(name) >= 2 and name[1] == ':':
        # The drive letter, made upper case by clearing bit 5, must come out
        # between '@' (the current drive) and 'Z'.
        if not 0 <= (ord(name[0]) & 0xDF) - 0x40 <= 26:
            return None
        rest = name[2:]
        if not rest:
            return None
    field = []
    left = 11                       # characters still free in name and type
    for ch in rest:
        if ch == '.':
            if left == 11 or left < 3:
                return None         # no name before the dot, or a second dot
            field.extend(' ' * (left - 3))
            left = 3
            continue
        field.append(ch)
        left -= 1
        if left == 0:
            break                   # the rest of the string is ignored
    field.extend(' ' * left)
    return ''.join(field)


def cpm_name_error(name: str, creates: bool = False) -> Optional[int]:
    """The MBASIC error number the binary gives for this file name, or None.

    creates: the statement makes the file (OPEN "O", OPEN "R", SAVE). A name
    with a refused character is then Too many files; for a statement that
    only reads, the same name is File not found.
    """
    field = _fcb_name(name)
    if field is None:
        return BAD_FILE_NAME
    if not field.strip(' '):
        # An all-blank name is refused by the file system like a bad character.
        return TOO_MANY_FILES if creates else FILE_NOT_FOUND
    if set(field[:8].strip(' ')) == {'?'}:
        # A name part of only question marks is refused as well.
        return TOO_MANY_FILES if creates else FILE_NOT_FOUND
    for ch in field:
        code = ord(ch) & 0x7F
        if code < 32 or code == 127 or chr(code) in _REFUSED:
            return TOO_MANY_FILES if creates else FILE_NOT_FOUND
    return None


def _drive(name: str) -> int:
    """The drive of a name: 0 for none or "@:", 1 for A to 26 for Z."""
    if len(name) >= 2 and name[1] == ':':
        return (ord(name[0]) & 0xDF) - 0x40
    return 0


def cpm_new_name_error(name: str, old_name: str = '') -> Optional[int]:
    """The error for the new name of NAME ... AS, or None.

    Measured: a malformed name is Bad file name, as for any other statement;
    a drive that differs from the drive of the old name is Illegal function
    call, because the rename would cross drives. No drive and the current
    drive "@:" count as the same drive. Refused characters such as * are not
    an error.
    """
    if _fcb_name(name) is None:
        return BAD_FILE_NAME
    if _drive(name) != _drive(old_name):
        return 5
    return None
