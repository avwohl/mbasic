"""Windows console support for key reading and cursor positioning.

Two things live here, both Windows-only, both kept out of the modules that use
them so the ctypes and msvcrt details stay in one place:

* ``win_read_key`` - INKEY$ / input_char() on Windows.
* ``win_locate``   - LOCATE on Windows.

This module is import-safe on POSIX. Every ctypes and msvcrt reference is
inside a function, because ``ctypes.WinDLL`` and ``ctypes.windll`` are defined
only under ``if os.name == "nt"`` in ctypes/__init__.py and would raise
AttributeError at import time here otherwise.
"""

import sys

# ---------------------------------------------------------------------------
# Key reading (INKEY$, input_char)
# ---------------------------------------------------------------------------

# Windows reports arrows/F-keys/Home/End/... as a scan code behind a prefix
# byte, not as characters. MBASIC 5.21 has no such concept: a CP/M console is a
# byte stream from a serial terminal, and an arrow key is whatever escape
# sequence that terminal transmits. So translate the scan code into the same
# escape sequence a Linux terminal sends, and hand it back one character per
# call - which is all INKEY$ can physically return (bistrs.mac hardcodes the
# length: "strin1: mvi a,1 ;make one char string (chr$, inkey$)").
#
# Keyed on the (prefix, scan code) PAIR, not the scan code alone. The two
# number spaces are not disjoint: from the UCRT dispatch tables, Ctrl+PgUp is
# (0xE0, 134) and F12 is also (0xE0, 134) - genuinely indistinguishable at the
# getch() API, so F12 wins and Ctrl+PgUp is reported as F12. Keying on the scan
# code alone would additionally have conflated (0x00, 132) - numpad Ctrl+PgUp -
# with nothing at all, and would have decoded stray bytes as navigation keys.
#
# 0xE0 leads the dedicated cursor cluster plus F11/F12; 0x00 leads F1-F10 and
# the numeric keypad with NumLock off. Both spellings of a nav key are listed
# because both reach the program depending on which physical key was pressed.
_WIN_KEY_TO_ANSI = {
    (0x00, 59): '\x1bOP',     # F1
    (0x00, 60): '\x1bOQ',     # F2
    (0x00, 61): '\x1bOR',     # F3
    (0x00, 62): '\x1bOS',     # F4
    (0x00, 63): '\x1b[15~',   # F5
    (0x00, 64): '\x1b[17~',   # F6
    (0x00, 65): '\x1b[18~',   # F7
    (0x00, 66): '\x1b[19~',   # F8
    (0x00, 67): '\x1b[20~',   # F9
    (0x00, 68): '\x1b[21~',   # F10
    (0xE0, 133): '\x1b[23~',  # F11
    (0xE0, 134): '\x1b[24~',  # F12  (also Ctrl+PgUp - see above)
}
# The navigation cluster, reachable under either prefix with the same number.
for _prefix in (0x00, 0xE0):
    _WIN_KEY_TO_ANSI.update({
        (_prefix, 71): '\x1b[H',    # Home
        (_prefix, 72): '\x1b[A',    # Up
        (_prefix, 73): '\x1b[5~',   # PgUp
        (_prefix, 75): '\x1b[D',    # Left
        (_prefix, 77): '\x1b[C',    # Right
        (_prefix, 79): '\x1b[F',    # End
        (_prefix, 80): '\x1b[B',    # Down
        (_prefix, 81): '\x1b[6~',   # PgDn
        (_prefix, 82): '\x1b[2~',   # Ins
        (_prefix, 83): '\x1b[3~',   # Del
    })
del _prefix

# Characters decoded but not yet handed to the program. One physical keypress
# can expand to several characters and INKEY$ returns at most one, so the
# remainder waits here for the next call. Module-level on purpose: there is one
# console, and INKEY$ and input_char() must not each hold half of a sequence.
_win_pending = []


def win_flush_pending() -> None:
    """Drop any half-delivered escape sequence.

    Call this when a program starts or stops. A program that reads INKEY$ until
    it sees something interesting and then exits leaves the rest of the
    sequence here - "10 A$=INKEY$: IF A$=\"\" THEN 10" takes the ESC of an
    arrow key and stops - and without this the next program's first INKEY$
    calls would return "[" and "A" with no key touched. POSIX has no
    equivalent problem: leftover bytes stay in the tty queue, where the next
    line-input read consumes and echoes them.
    """
    _win_pending.clear()


def win_read_key(blocking: bool = False) -> str:
    """Read one character from the Windows console. "" if nothing is waiting.

    Never returns more than one character, so LEN(INKEY$) stays 0 or 1 exactly
    as on CP/M. A special key arrives over several successive calls, the same
    way an arrow key does through a POSIX terminal.
    """
    if _win_pending:
        return _win_pending.pop(0)

    try:
        import msvcrt
    except ImportError:
        return ""

    # A blocking read loops, because consuming a key we cannot express (Ctrl+Up
    # and friends) is not the same as having no key to read. Returning "" for
    # both would make a caller that treats "" as "no console" - which
    # ConsoleIOHandler.input_char does - silently downgrade to line input the
    # first time somebody pressed Ctrl+Left.
    while True:
        if not blocking and not msvcrt.kbhit():
            return ""

        first = msvcrt.getch()  # always exactly one byte, never b''

        if blocking and first == b'\xff' and not msvcrt.kbhit():
            # No console at all (pythonw.exe, a detached process): CONIN$
            # cannot be opened, kbhit() reports 0 and getch() hands back EOF
            # truncated to a byte. This is the ONLY way a blocking read returns
            # "", so the caller can read it as "there is no console".
            # Not checked when non-blocking: the kbhit() gate above has already
            # returned "" in that situation, so a 0xFF here is a real keypress.
            return ""

        if first in (b'\x00', b'\xe0') and msvcrt.kbhit():
            # Prefix byte. The scan code is already in the CRT's pushback
            # buffer, and _kbhit_nolock() opens by checking that very buffer
            # ("if (peek_next_getch_pushback_buffer() != EOF) return TRUE;"),
            # so a true kbhit() here guarantees the next getch() returns
            # without touching the console. That keeps a non-blocking INKEY$
            # non-blocking.
            #
            # Do NOT rewrite this using msvcrt.getwch(). Its pushback is a
            # separate "static wint_t wchbuf" in ucrt/conio/getwch.cpp that
            # _kbhit() never looks at, so kbhit() would read False with a scan
            # code still pending and that scan code would leak out of the next
            # call - exactly the desync being fixed here.
            #
            # kbhit() is not proof of a prefix, though: the same pushback
            # buffer also carries bytes 2..n of a multi-byte character, so on a
            # DBCS or UTF-8 console a lead byte of 0x00/0xE0 looks identical to
            # a prefix. That ambiguity is unfixable at the getch() API and
            # needs ReadConsoleInputW; see docs/dev/WINDOWS_CONSOLE_KEYS.md.
            second = msvcrt.getch()[0]
            seq = _WIN_KEY_TO_ANSI.get((first[0], second))
            if seq is None:
                # Either a key with no terminal equivalent (Ctrl+Up, Alt+Home)
                # or a continuation byte. Hand back both bytes rather than
                # dropping them: losing input silently is worse than emitting a
                # byte the program may not understand, and it keeps this
                # byte-transparent like the POSIX side.
                _win_pending.append(chr(second))
                return chr(first[0])
            _win_pending.extend(seq)
            return _win_pending.pop(0)

        # Not a prefix (or nothing was buffered behind it), so this is a real
        # character whose byte value happens to be 0x00 or 0xE0.
        break

    # Byte-transparent, matching the POSIX side: INKEY$ yields one character
    # whose ordinal is the byte the console produced, so ASC() means the same
    # thing on both platforms. Decoding against the OEM codepage instead would
    # not survive chcp 65001, where one keypress spans up to four getch() calls.
    return chr(first[0])


# ---------------------------------------------------------------------------
# Cursor positioning (LOCATE)
# ---------------------------------------------------------------------------

_ENABLE_PROCESSED_OUTPUT = 0x0001
_ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

# STD_OUTPUT_HANDLE is ((DWORD)-11). Microsoft documents the unsigned spelling
# for languages that do not parse the C headers.
_STD_OUTPUT_HANDLE = 0xFFFFFFF5

_win_api = None       # bound entry points, or False once we have given up
_win_vt_state = None  # None = not probed yet


def _load_win_api():
    """Bind the kernel32 calls we need, or return None if unavailable."""
    global _win_api
    if _win_api is not None:
        return _win_api or None
    _win_api = False
    if sys.platform != 'win32':
        return None
    try:
        import ctypes

        # A private kernel32 handle rather than ctypes.windll. windll is a
        # process-wide singleton that caches each function object on itself, so
        # setting .argtypes there mutates state shared with every other library
        # in the process - the collision behind prompt_toolkit's
        # ArgumentError("argument 2: <class 'TypeError'>: wrong type").
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        handle_t = ctypes.c_void_p
        dword_t = ctypes.c_uint32
        bool_t = ctypes.c_int32

        k32.GetStdHandle.argtypes = [dword_t]
        k32.GetStdHandle.restype = handle_t
        k32.GetConsoleMode.argtypes = [handle_t, ctypes.POINTER(dword_t)]
        k32.GetConsoleMode.restype = bool_t
        k32.SetConsoleMode.argtypes = [handle_t, dword_t]
        k32.SetConsoleMode.restype = bool_t

        _win_api = {
            'ctypes': ctypes,
            'DWORD': dword_t,
            'GetStdHandle': k32.GetStdHandle,
            'GetConsoleMode': k32.GetConsoleMode,
            'SetConsoleMode': k32.SetConsoleMode,
            # ((HANDLE)(LONG_PTR)-1) is pointer-width, so compute it rather
            # than hardcoding a 32- or 64-bit literal.
            'INVALID_HANDLE_VALUE': ctypes.c_void_p(-1).value,
        }
    except (AttributeError, ImportError, OSError, ValueError):
        _win_api = False
    return _win_api or None


def _win_console_mode():
    """Return (handle, mode) when stdout is a real console, else None."""
    api = _load_win_api()
    if api is None:
        return None

    # Ask what is behind the object we are about to write to, so an in-process
    # reassignment of sys.stdout or of fd 1 is respected. GetStdHandle only
    # knows about the process handle table, which can disagree.
    handle = None
    try:
        import msvcrt
        handle = msvcrt.get_osfhandle(sys.stdout.fileno())
    except (ImportError, AttributeError, OSError, ValueError):
        handle = None
    if handle is None:
        handle = api['GetStdHandle'](_STD_OUTPUT_HANDLE)
    if not handle or handle == api['INVALID_HANDLE_VALUE']:
        return None

    # GetConsoleMode succeeding is the console test; it fails with
    # ERROR_INVALID_HANDLE on a file or a pipe. isatty() cannot be used for this
    # on Windows - the CRT reports any character device as a tty, so
    # "mbasic > NUL" and "mbasic > COM1" both answer True.
    mode = api['DWORD'](0)
    if not api['GetConsoleMode'](handle, api['ctypes'].byref(mode)):
        return None
    return handle, mode.value


def _win_enable_vt(handle, mode):
    """Turn on ANSI interpretation for the console. Cached; done at most once."""
    global _win_vt_state
    if _win_vt_state is not None:
        return _win_vt_state
    api = _load_win_api()
    _win_vt_state = False
    if api is None:
        return False
    # Frequently already on: inside ConPTY (Windows Terminal, VS Code, OpenSSH)
    # since Windows 10 20H2, or when HKCU\\Console\\VirtualTerminalLevel is 1.
    if mode & _ENABLE_VIRTUAL_TERMINAL_PROCESSING:
        _win_vt_state = True
        return True
    # Build on the existing mode so other flags survive. Fails with
    # ERROR_INVALID_PARAMETER on Windows 8 and on Windows 10 before 1511, which
    # is Microsoft's documented way of detecting a down-level system.
    wanted = mode | _ENABLE_VIRTUAL_TERMINAL_PROCESSING | _ENABLE_PROCESSED_OUTPUT
    if not api['SetConsoleMode'](handle, wanted):
        return False
    # Confirm the bit stuck rather than trusting the return value.
    check = api['DWORD'](0)
    if api['GetConsoleMode'](handle, api['ctypes'].byref(check)):
        _win_vt_state = bool(check.value & _ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    return _win_vt_state


def win_locate(row: int, col: int) -> bool:
    """Prepare the Windows console for a CUP escape.

    True  - stdout is a console with ANSI processing on; caller writes the
            escape exactly as it does on POSIX.
    False - not a console, or ANSI could not be enabled; caller writes nothing.

    Only ever touches the *output* handle's mode. Do not add
    ENABLE_VIRTUAL_TERMINAL_INPUT to the input handle to go with it: msvcrt
    would then deliver escape sequences instead of the prefix+scan-code pairs
    win_read_key() is built around, and INKEY$ would quietly stop working.
    """
    probe = _win_console_mode()
    if probe is None:
        return False
    return _win_enable_vt(*probe)
