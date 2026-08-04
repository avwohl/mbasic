#!/usr/bin/env python3
"""
Test two CLI input bugs found while triaging GitHub PR #3.

1. termios.error is not an OSError subclass.
   _read_char() and ConsoleIOHandler.input_char() put the terminal in raw mode
   and caught (AttributeError, OSError, ImportError) around it. On a non-tty
   stdin, termios.tcgetattr() raises termios.error, which none of those cover,
   so EDIT on piped input died with:
       ?error: (25, 'Inappropriate ioctl for device')

2. Program INPUT answers were recorded as commands.
   The INPUT statement read its answer with a bare input(), so readline filed
   the answer in the command history and then saved it to ~/.mbasic_history.
   Pressing Up at the "Ok" prompt scrolled back through whatever a program had
   asked the user to type.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import termios
import types

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

from src.interactive import InteractiveMode
from src.iohandler.console import ConsoleIOHandler

results = []


def get_input_without_history():
    """Fetch the helper, or None if this build predates it.

    Imported lazily rather than at module scope so that the termios half of
    this file still runs - and still reports its own verdict - against a tree
    where the INPUT-history fix is absent.
    """
    try:
        from src.iohandler.console import input_without_history
        return input_without_history
    except ImportError:
        return None


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


class NonTtyStdin:
    """A stdin with a real file descriptor that is not a terminal.

    A StringIO would raise io.UnsupportedOperation from fileno() (an OSError
    subclass, which the old code did catch). Only a genuine non-tty fd gets
    tcgetattr to raise termios.error, which is the bug.
    """

    def __init__(self, data):
        self.file = tempfile.TemporaryFile(mode='w+')
        self.file.write(data)
        self.file.seek(0)

    def __enter__(self):
        self.saved = sys.stdin
        sys.stdin = self.file
        return self

    def __exit__(self, *exc_info):
        sys.stdin = self.saved
        self.file.close()
        return False


def test_termios_error_is_not_an_oserror():
    """The premise of the bug - if this ever changes, the fix can be simplified."""
    print("\ntermios.error really is outside the OSError hierarchy")
    print("-" * 60)
    check(not issubclass(termios.error, OSError),
          "termios.error is not an OSError subclass (so it must be named)")


def test_read_char_on_non_tty():
    """_read_char must fall back to a cooked read instead of raising."""
    print("\n_read_char() survives a stdin that has no terminal")
    print("-" * 60)
    with NonTtyStdin('ABC') as stdin:
        # Confirm the harness really does reproduce the failing condition.
        try:
            termios.tcgetattr(stdin.file.fileno())
            reproduced = False
        except termios.error:
            reproduced = True
        except Exception:
            reproduced = False

        try:
            ch = InteractiveMode._read_char(None)
            error = None
        except Exception as e:
            ch, error = None, e

    check(reproduced, "the harness reproduces termios.error from tcgetattr")
    detail = '' if error is None else f" -> raised {type(error).__name__}: {error}"
    check(error is None, f"_read_char returns instead of raising{detail}")
    check(ch == 'A', f"_read_char returned the first character (got {ch!r})")


def test_input_char_on_non_tty():
    """ConsoleIOHandler.input_char had the same unguarded tcgetattr."""
    print("\nConsoleIOHandler.input_char() survives the same condition")
    print("-" * 60)
    handler = ConsoleIOHandler()
    with NonTtyStdin('XYZ'):
        try:
            ch = handler.input_char(blocking=True)
            error = None
        except Exception as e:
            ch, error = None, e
    detail = '' if error is None else f" -> raised {type(error).__name__}: {error}"
    check(error is None, f"input_char returns instead of raising{detail}")
    check(ch == 'X', f"input_char returned the first character (got {ch!r})")


class FilenoRaisesValueError:
    """A readable stdin whose fileno() raises ValueError.

    That is what a closed file does ("I/O operation on closed file"), and
    ValueError is neither an OSError nor a termios.error - so it is a third
    way for the raw-mode setup to fail. Reading still works here, which
    isolates the guard from the read.
    """

    def __init__(self, data):
        self.data = data

    def fileno(self):
        raise ValueError('I/O operation on closed file.')

    def read(self, size=-1):
        chunk = self.data[:size] if size and size > 0 else self.data
        self.data = self.data[len(chunk):]
        return chunk


def test_fileno_raising_value_error():
    """ValueError from fileno() must degrade to a cooked read, not escape."""
    print("\nValueError from fileno() is treated as 'no terminal here'")
    print("-" * 60)
    for label, call in (
        ('_read_char', lambda: InteractiveMode._read_char(None)),
        ('input_char', lambda: ConsoleIOHandler().input_char(blocking=True)),
    ):
        saved, sys.stdin = sys.stdin, FilenoRaisesValueError('AB')
        try:
            got = call()
        except Exception as e:
            got = f"<raised {type(e).__name__}: {e}>"
        finally:
            sys.stdin = saved
        check(got == 'A', f"{label} read the character anyway (got {got!r})")


def test_restore_failure_does_not_eat_a_second_character():
    """If only the terminal restore fails, the character already read stands."""
    print("\nA failing terminal restore must not consume another character")
    print("-" * 60)
    import tty
    saved = (termios.tcgetattr, termios.tcsetattr, tty.setraw)

    def boom(*args, **kwargs):
        raise termios.error(5, 'Input/output error')

    for label, call, want in (
        ('_read_char', lambda: InteractiveMode._read_char(None), 'A'),
        ('input_char', lambda: ConsoleIOHandler().input_char(blocking=True), 'A'),
    ):
        with NonTtyStdin('AB'):
            termios.tcgetattr = lambda fd: []
            tty.setraw = lambda fd, when=None: None
            termios.tcsetattr = boom       # the restore fails, nothing else
            try:
                got = call()
            except Exception as e:
                got = f"<raised {type(e).__name__}>"
            finally:
                termios.tcgetattr, termios.tcsetattr, tty.setraw = saved
        check(got == want,
              f"{label} returns the character it read, not the next one "
              f"(got {got!r}, want {want!r})")


def test_edit_on_piped_input_end_to_end():
    """The user-visible symptom: EDIT died on piped input."""
    print("\nEDIT on piped stdin does not report an ioctl error")
    print("-" * 60)
    env = dict(os.environ)
    env.pop('MBASIC_DEBUG', None)
    home = tempfile.mkdtemp(prefix='mbasic_edit_test_')
    env['HOME'] = home
    try:
        proc = subprocess.run(
            [sys.executable, 'mbasic', '--ui', 'cli'],
            input='10 PRINT "HI"\nEDIT 10\n\nSYSTEM\n',
            capture_output=True, text=True, cwd=PROJECT_ROOT, env=env, timeout=20)
    finally:
        shutil.rmtree(home, ignore_errors=True)
    output = proc.stdout + proc.stderr
    check('Inappropriate ioctl' not in output,
          "no 'Inappropriate ioctl for device' in the output")
    check('?error:' not in output, "no '?error:' in the output")
    check('PRINT "HI"' in output, "EDIT actually displayed the line")


class FakeReadline(types.ModuleType):
    """Records set_auto_history() calls."""

    def __init__(self, with_api=True):
        super().__init__('readline')
        self.calls = []
        if with_api:
            self.set_auto_history = self._set_auto_history

    def _set_auto_history(self, enabled):
        self.calls.append(enabled)


class FakeInput:
    """Swap in a fake readline and a scripted input()."""

    def __init__(self, fake, answer='42', raises=None):
        self.fake = fake
        self.answer = answer
        self.raises = raises
        self.input_calls = []

    def __enter__(self):
        import builtins
        self.builtins = builtins
        self.saved_module = sys.modules.get('readline')
        self.saved_input = builtins.input
        sys.modules['readline'] = self.fake
        builtins.input = self._input
        return self

    def __exit__(self, *exc_info):
        self.builtins.input = self.saved_input
        if self.saved_module is not None:
            sys.modules['readline'] = self.saved_module
        else:
            sys.modules.pop('readline', None)
        return False

    def _input(self, prompt=''):
        # Record the flag state at the moment the read happens - that is what
        # actually decides whether readline files the answer in history.
        self.input_calls.append(list(self.fake.calls))
        if self.raises is not None:
            raise self.raises
        return self.answer


def test_input_without_history_suppresses_and_restores():
    """Auto history must be off during the read and back on afterwards."""
    print("\ninput_without_history() suppresses history around the read")
    print("-" * 60)
    helper = get_input_without_history()
    if helper is None:
        check(False, "src.iohandler.console.input_without_history exists")
        return
    fake = FakeReadline()
    with FakeInput(fake) as h:
        value = helper()
    check(value == '42', "the typed value is returned unchanged")
    check(h.input_calls == [[False]],
          f"auto history was already off when input() ran (saw {h.input_calls})")
    check(fake.calls == [False, True],
          f"auto history is turned off then back on (saw {fake.calls})")


def test_input_without_history_restores_on_exception():
    """A Ctrl+C or EOF at the INPUT prompt must not leave history disabled."""
    print("\ninput_without_history() restores history when the read raises")
    print("-" * 60)
    helper = get_input_without_history()
    if helper is None:
        check(False, "src.iohandler.console.input_without_history exists")
        return
    for exc in (EOFError(), KeyboardInterrupt()):
        fake = FakeReadline()
        with FakeInput(fake, raises=exc):
            try:
                helper()
                raised = None
            except BaseException as e:
                raised = e
        check(type(raised) is type(exc),
              f"{type(exc).__name__} still propagates to the caller")
        check(fake.calls == [False, True],
              f"auto history restored after {type(exc).__name__} (saw {fake.calls})")


def test_input_without_history_without_readline_api():
    """Old or shimmed readline modules must not break INPUT."""
    print("\ninput_without_history() degrades when readline cannot suppress")
    print("-" * 60)
    helper = get_input_without_history()
    if helper is None:
        check(False, "src.iohandler.console.input_without_history exists")
        return
    fake = FakeReadline(with_api=False)
    with FakeInput(fake) as h:
        try:
            value = helper()
            error = None
        except Exception as e:
            value, error = None, e
    check(error is None, "no error when readline has no set_auto_history")
    check(value == '42', "the typed value is still returned")


def test_input_answer_stays_out_of_history_end_to_end():
    """The real thing, under a pty - readline only keeps history on a tty."""
    print("\nProgram INPUT answers are not written to ~/.mbasic_history")
    print("-" * 60)
    try:
        import pexpect
    except ImportError:
        print("SKIP: pexpect not installed (pip install \"mbasic[dev]\")")
        return

    import time
    home = tempfile.mkdtemp(prefix='mbasic_pty_test_')
    env = dict(os.environ, HOME=home, TERM='dumb')
    env.pop('MBASIC_DEBUG', None)
    try:
        child = pexpect.spawn(sys.executable, ['mbasic', '--ui', 'cli'],
                              cwd=PROJECT_ROOT, env=env, timeout=20,
                              encoding='utf-8')
        child.expect('Ready')
        for line in ['10 INPUT "AGE"; A', '20 PRINT A', 'RUN']:
            child.sendline(line)
            time.sleep(0.2)
        child.expect(r'AGE\?')
        child.sendline('SECRET42')      # the program INPUT answer
        time.sleep(0.5)
        child.sendline('SYSTEM')
        child.expect(pexpect.EOF)
        child.close()

        history_file = os.path.join(home, '.mbasic_history')
        history = ''
        if os.path.exists(history_file):
            with open(history_file) as f:
                history = f.read()
    finally:
        shutil.rmtree(home, ignore_errors=True)

    check('SECRET42' not in history,
          "the INPUT answer is not in the history file")
    check('RUN' in history,
          f"commands still are in the history file (got {history!r})")


if __name__ == "__main__":
    print("CLI input isolation (termios.error, INPUT history)")
    print("=" * 60)

    test_termios_error_is_not_an_oserror()
    test_read_char_on_non_tty()
    test_fileno_raising_value_error()
    test_restore_failure_does_not_eat_a_second_character()
    test_input_char_on_non_tty()
    test_edit_on_piped_input_end_to_end()
    test_input_without_history_suppresses_and_restores()
    test_input_without_history_restores_on_exception()
    test_input_without_history_without_readline_api()
    test_input_answer_stays_out_of_history_end_to_end()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
