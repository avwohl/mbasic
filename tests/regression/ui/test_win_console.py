"""Windows console behaviour, exercised on POSIX with injected fakes.

The msvcrt and kernel32 calls cannot run here, so the real ones are replaced:
a fake ``msvcrt`` module in sys.modules, and a fake kernel32 whose entry points
are already bound into win_console's ``_win_api`` cache.

sys.platform is NOT patched for the key-reading tests: win_read_key() has no
platform check of its own - the call sites decide - so it is directly callable
here. The ctypes path is reached by seeding _win_api instead, because
ctypes.WinDLL genuinely does not exist on POSIX and cannot be patched into
being. The call-site tests at the end DO patch sys.platform, since that is the
branch they exist to exercise.
"""

import os
import sys
import types
import unittest
from unittest import mock

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src import win_console  # noqa: E402


class FakeMsvcrt:
    """Stands in for msvcrt, modelling the UCRT's pushback buffer.

    A special key is queued as its prefix byte plus its scan code. getch()
    hands back the prefix from the console queue and the scan code from the
    pushback buffer, and kbhit() reports either - which is the behaviour that
    makes the kbhit()-gated second read safe.
    """

    def __init__(self, keys=b''):
        self.queue = list(keys)   # bytes still "in the console"
        self.pushback = []        # the CRT's getch pushback buffer
        self.blocked = False      # set if a blocking getch() had nothing to give

    def kbhit(self):
        return bool(self.pushback or self.queue)

    def getch(self):
        if self.pushback:
            return bytes([self.pushback.pop(0)])
        if not self.queue:
            # A real blocking getch() would wait here forever.
            self.blocked = True
            raise AssertionError("getch() blocked with an empty console queue")
        byte = self.queue.pop(0)
        if byte in (0x00, 0xE0) and self.queue:
            # Prefix consumed: the UCRT moves the scan code into the pushback
            # buffer, where kbhit() can see it.
            self.pushback.append(self.queue.pop(0))
        return bytes([byte])


def install(fake):
    win_console._win_pending.clear()
    return mock.patch.dict(sys.modules, {'msvcrt': fake})


def drain(fake, calls=12, blocking=False):
    """Call win_read_key() repeatedly and join what it returns."""
    with install(fake):
        return ''.join(win_console.win_read_key(blocking) for _ in range(calls))


class TestKeyReading(unittest.TestCase):

    def test_arrow_up_becomes_an_escape_sequence_one_char_at_a_time(self):
        fake = FakeMsvcrt(b'\xe0H')          # 0xE0 prefix, scan code 72
        with install(fake):
            got = [win_console.win_read_key(False) for _ in range(5)]
        self.assertEqual(got, ['\x1b', '[', 'A', '', ''])
        # The property that matters: never more than one character per call.
        self.assertTrue(all(len(c) <= 1 for c in got))

    def test_all_four_arrows(self):
        for scan, seq in ((72, '\x1b[A'), (80, '\x1b[B'),
                          (77, '\x1b[C'), (75, '\x1b[D')):
            self.assertEqual(drain(FakeMsvcrt(bytes([0xE0, scan]))), seq)

    def test_both_prefixes_produce_the_same_sequence(self):
        # 0xE0 = dedicated cursor cluster, 0x00 = numeric keypad, NumLock off.
        self.assertEqual(drain(FakeMsvcrt(b'\xe0H')), drain(FakeMsvcrt(b'\x00H')))

    def test_f_keys(self):
        self.assertEqual(drain(FakeMsvcrt(b'\x00\x3b')), '\x1bOP')        # F1
        self.assertEqual(drain(FakeMsvcrt(b'\x00\x44')), '\x1b[21~')      # F10
        self.assertEqual(drain(FakeMsvcrt(b'\xe0\x85')), '\x1b[23~')      # F11
        self.assertEqual(drain(FakeMsvcrt(b'\xe0\x86')), '\x1b[24~')      # F12

    def test_ordinary_letter_is_unchanged(self):
        self.assertEqual(drain(FakeMsvcrt(b'A')), 'A')

    def test_no_key_pending_returns_empty_without_blocking(self):
        fake = FakeMsvcrt(b'')
        with install(fake):
            self.assertEqual(win_console.win_read_key(False), "")
        self.assertFalse(fake.blocked)

    def test_high_byte_is_preserved_not_dropped(self):
        # The old code did b'\x81'.decode('utf-8', errors='ignore') -> ''.
        self.assertEqual(drain(FakeMsvcrt(b'\x81')), '\x81')

    def test_lone_0xe0_is_treated_as_a_character(self):
        # A literal 0xE0 byte with nothing buffered behind it is a character.
        # (With something behind it the two are indistinguishable - see the
        # DBCS note in win_console.py.)
        self.assertEqual(drain(FakeMsvcrt(b'\xe0')), '\xe0')

    def test_unmapped_scancode_is_handed_back_not_dropped(self):
        # Ctrl+Up is {0xE0, 141}: no terminal equivalent. Both bytes come back
        # rather than vanishing - losing input silently is worse than emitting
        # a byte the program may not recognise, and the same path carries
        # multi-byte character continuations on a DBCS console.
        fake = FakeMsvcrt(bytes([0xE0, 141]) + b'Z')
        with install(fake):
            got = [win_console.win_read_key(False) for _ in range(3)]
        self.assertEqual(got, ['\xe0', chr(141), 'Z'])

    def test_blocking_read_skips_past_an_unmapped_key(self):
        # A blocking read must not report "" for a key it cannot express - the
        # caller reads "" as "there is no console" and falls back to line input.
        fake = FakeMsvcrt(bytes([0xE0, 141]) + b'Z')
        with install(fake):
            self.assertNotEqual(win_console.win_read_key(True), "")

    def test_ctrl_pgup_collides_with_f12_and_that_is_documented(self):
        # (0xE0, 134) is BOTH F12 and Ctrl+PgUp in the UCRT tables, so they are
        # indistinguishable at the getch() API. Pinning the collision keeps the
        # comment honest.
        self.assertEqual(win_console._WIN_KEY_TO_ANSI[(0xE0, 134)], '\x1b[24~')

    def test_prefix_and_scancode_are_keyed_as_a_pair(self):
        # Scan code 72 is Up under either prefix, but F10 is (0x00, 68) only -
        # keying on the scan code alone would have decoded stray bytes as keys.
        self.assertEqual(win_console._WIN_KEY_TO_ANSI[(0x00, 72)], '\x1b[A')
        self.assertEqual(win_console._WIN_KEY_TO_ANSI[(0xE0, 72)], '\x1b[A')
        self.assertEqual(win_console._WIN_KEY_TO_ANSI[(0x00, 68)], '\x1b[21~')
        self.assertNotIn((0xE0, 68), win_console._WIN_KEY_TO_ANSI)

    def test_pending_can_be_flushed_between_programs(self):
        # A program that stops mid-sequence must not leak the rest into the
        # next one.
        fake = FakeMsvcrt(b'\xe0H')
        with install(fake):
            self.assertEqual(win_console.win_read_key(False), '\x1b')
            win_console.win_flush_pending()
            self.assertEqual(win_console.win_read_key(False), "")

    def test_typing_after_an_arrow_stays_in_order(self):
        self.assertEqual(drain(FakeMsvcrt(b'\xe0HZ')), '\x1b[AZ')

    def test_blocking_read_never_returns_more_than_one_char(self):
        fake = FakeMsvcrt(b'\xe0H')
        with install(fake):
            got = [win_console.win_read_key(True) for _ in range(3)]
        self.assertEqual(got, ['\x1b', '[', 'A'])
        self.assertFalse(fake.blocked)

    def test_no_console_returns_empty_instead_of_spinning(self):
        # pythonw.exe: kbhit() is 0 and getch() yields EOF truncated to 0xFF.
        class NoConsole(FakeMsvcrt):
            def kbhit(self):
                return False

            def getch(self):
                return b'\xff'
        with install(NoConsole()):
            self.assertEqual(win_console.win_read_key(True), "")

    def test_missing_msvcrt_is_not_fatal(self):
        win_console._win_pending.clear()
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            self.assertEqual(win_console.win_read_key(False), "")


class FakeKernel32:
    """Enough of kernel32 to drive the VT-enable path."""

    def __init__(self, mode=0, is_console=True, set_succeeds=True):
        self.mode = mode
        self.is_console = is_console
        self.set_succeeds = set_succeeds
        self.set_calls = []

    def GetStdHandle(self, which):
        return 7  # any non-null, non-INVALID_HANDLE_VALUE value

    def GetConsoleMode(self, handle, out_ptr):
        if not self.is_console:
            return 0                      # ERROR_INVALID_HANDLE on a pipe/file
        out_ptr._obj.value = self.mode
        return 1

    def SetConsoleMode(self, handle, mode):
        self.set_calls.append(mode)
        if not self.set_succeeds:
            return 0                      # pre-1511: ERROR_INVALID_PARAMETER
        self.mode = mode
        return 1


def install_kernel32(k32):
    """Seed win_console's api cache so no real WinDLL load is attempted."""
    import ctypes
    win_console._win_vt_state = None
    win_console._win_api = {
        'ctypes': ctypes,
        'DWORD': ctypes.c_uint32,
        'GetStdHandle': k32.GetStdHandle,
        'GetConsoleMode': k32.GetConsoleMode,
        'SetConsoleMode': k32.SetConsoleMode,
        'INVALID_HANDLE_VALUE': ctypes.c_void_p(-1).value,
    }


class TestLocate(unittest.TestCase):

    def tearDown(self):
        win_console._win_api = None
        win_console._win_vt_state = None

    def test_enables_vt_when_off_and_reports_success(self):
        k32 = FakeKernel32(mode=0x0003)
        install_kernel32(k32)
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            self.assertTrue(win_console.win_locate(5, 10))
        # Existing flags preserved, VT and PROCESSED_OUTPUT added.
        self.assertEqual(k32.set_calls, [0x0003 | 0x0004 | 0x0001])

    def test_already_enabled_does_not_touch_the_mode(self):
        k32 = FakeKernel32(mode=0x0007)   # ConPTY / VirtualTerminalLevel=1
        install_kernel32(k32)
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            self.assertTrue(win_console.win_locate(1, 1))
        self.assertEqual(k32.set_calls, [])

    def test_redirected_stdout_is_not_a_console(self):
        k32 = FakeKernel32(is_console=False)
        install_kernel32(k32)
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            self.assertFalse(win_console.win_locate(5, 10))
        self.assertEqual(k32.set_calls, [])

    def test_down_level_windows_degrades_to_false(self):
        k32 = FakeKernel32(mode=0x0003, set_succeeds=False)
        install_kernel32(k32)
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            self.assertFalse(win_console.win_locate(5, 10))

    def test_probe_is_cached(self):
        k32 = FakeKernel32(mode=0x0003)
        install_kernel32(k32)
        with mock.patch.dict(sys.modules, {'msvcrt': None}):
            for _ in range(5):
                win_console.win_locate(1, 1)
        self.assertEqual(len(k32.set_calls), 1)   # enabled once, not per call

    def test_module_is_import_safe_on_posix(self):
        # _load_win_api() must refuse to touch ctypes.WinDLL off Windows.
        win_console._win_api = None
        self.assertIsNone(win_console._load_win_api())


class TestLocateEmission(unittest.TestCase):
    """The console.py locate() body, transcribed, driven both ways."""

    def locate(self, row, col, platform, win_ok):
        out = []
        try:
            row = max(1, int(row))
            col = max(1, int(col))
        except (TypeError, ValueError):
            return ''
        if platform == 'win32':
            if not win_ok:
                return ''
        else:
            if not sys.stdout.isatty():
                return ''
        out.append(f'\033[{row};{col}H')
        return ''.join(out)

    def test_windows_console_emits_the_same_escape_as_posix(self):
        self.assertEqual(self.locate(5, 10, 'win32', True), '\033[5;10H')

    def test_windows_without_vt_emits_nothing(self):
        self.assertEqual(self.locate(5, 10, 'win32', False), '')

    def test_clamped_to_one_based(self):
        self.assertEqual(self.locate(0, -3, 'win32', True), '\033[1;1H')

    def test_non_numeric_is_inert(self):
        self.assertEqual(self.locate('x', 1, 'win32', True), '')

    def test_posix_redirected_emits_nothing(self):
        with mock.patch.object(sys, 'stdout') as fake_out:
            fake_out.isatty.return_value = False
            self.assertEqual(self.locate(5, 10, 'linux', None), '')


class TestByteFidelity(unittest.TestCase):
    def test_genuine_ff_keypress_survives_non_blocking(self):
        self.assertEqual(drain(FakeMsvcrt(b'\xff')), '\xff')

    def test_every_byte_round_trips_when_not_a_prefix(self):
        for b in range(256):
            if b in (0x00, 0xE0):
                continue
            got = drain(FakeMsvcrt(bytes([b])), calls=2)
            self.assertEqual(got, chr(b), "byte %#04x" % b)



class TestCallSites(unittest.TestCase):
    """The fix has to be WIRED IN, not merely available.

    Everything above tests win_console in isolation, which stays green even if
    somebody deletes the win_read_key() call from INKEY$ and restores the old
    decode('utf-8', errors='ignore'). These patch sys.platform so the
    `if sys.platform == 'win32'` branches at the three real call sites actually
    execute.
    """

    def _read_through(self, call, keys, count):
        fake = FakeMsvcrt(keys)
        win_console._win_pending.clear()
        with mock.patch.dict(sys.modules, {'msvcrt': fake}), \
                mock.patch.object(sys, 'platform', 'win32'):
            return [call() for _ in range(count)]

    def test_inkey_routes_through_win_read_key(self):
        from src.basic_builtins import BuiltinFunctions
        builtins_obj = BuiltinFunctions.__new__(BuiltinFunctions)
        got = self._read_through(
            lambda: BuiltinFunctions.INKEY(builtins_obj), b'\xe0H', 4)
        self.assertEqual(got, ['\x1b', '[', 'A', ''],
                         "INKEY$ must resolve the arrow key on Windows")

    def test_inkey_preserves_a_high_byte(self):
        # The exact byte the old decode('utf-8', errors='ignore') destroyed.
        from src.basic_builtins import BuiltinFunctions
        builtins_obj = BuiltinFunctions.__new__(BuiltinFunctions)
        got = self._read_through(
            lambda: BuiltinFunctions.INKEY(builtins_obj), b'\x81', 2)
        self.assertEqual(got, ['\x81', ''])

    def test_input_char_nonblocking_routes_through_win_read_key(self):
        from src.iohandler.console import ConsoleIOHandler
        handler = ConsoleIOHandler()
        got = self._read_through(
            lambda: handler.input_char(blocking=False), b'\xe0H', 4)
        self.assertEqual(got, ['\x1b', '[', 'A', ''])

    def test_input_char_blocking_routes_through_win_read_key(self):
        from src.iohandler.console import ConsoleIOHandler
        handler = ConsoleIOHandler()
        got = self._read_through(
            lambda: handler.input_char(blocking=True), b'\xe0H', 3)
        self.assertEqual(got, ['\x1b', '[', 'A'])

    def test_locate_writes_nothing_on_windows_without_a_console(self):
        import io
        from src.iohandler.console import ConsoleIOHandler
        handler = ConsoleIOHandler()
        buffer = io.StringIO()
        win_console._win_api = False        # force "no kernel32 available"
        win_console._win_vt_state = None
        try:
            with mock.patch.object(sys, 'platform', 'win32'), \
                    mock.patch.object(sys, 'stdout', buffer):
                handler.locate(5, 10)
        finally:
            win_console._win_api = None
            win_console._win_vt_state = None
        self.assertEqual(buffer.getvalue(), "",
                         "conhost would have shown this escape as literal text")

    def test_locate_writes_the_escape_on_a_posix_tty(self):
        from src.iohandler.console import ConsoleIOHandler
        handler = ConsoleIOHandler()

        class FakeTty:
            def __init__(self):
                self.written = []

            def isatty(self):
                return True

            def write(self, text):
                self.written.append(text)

            def flush(self):
                pass

        out = FakeTty()
        with mock.patch.object(sys, 'platform', 'linux'), \
                mock.patch.object(sys, 'stdout', out):
            handler.locate(5, 10)
        self.assertEqual(''.join(out.written), '\033[5;10H')

    def test_locate_writes_nothing_when_redirected_on_posix(self):
        import io
        from src.iohandler.console import ConsoleIOHandler
        handler = ConsoleIOHandler()
        buffer = io.StringIO()          # isatty() is False
        with mock.patch.object(sys, 'platform', 'linux'), \
                mock.patch.object(sys, 'stdout', buffer):
            handler.locate(5, 10)
        self.assertEqual(buffer.getvalue(), "")


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("\n" + "=" * 60)
    print(f"Results: {result.testsRun - len(result.failures) - len(result.errors)} "
          f"passed, {len(result.failures) + len(result.errors)} failed")
    if result.wasSuccessful():
        print("\u2705 All tests passed!")
        sys.exit(0)
    print("\u274c Some tests failed")
    sys.exit(1)

