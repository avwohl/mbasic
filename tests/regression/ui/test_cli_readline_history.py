#!/usr/bin/env python3
"""
Test CLI readline history setup against a readline that fails (GitHub PR #3).

macOS system Python links libedit, not GNU readline. libedit's read_history()
ends with `return (!(history_length > 0));` - a boolean "loaded nothing" flag -
and CPython's readline module assigns that return value to errno and raises
from it. So reading a perfectly normal 0600 ~/.mbasic_history that happens to
hold no entries surfaces as PermissionError [Errno 1] and crashed mbasic at
startup.

Nothing is macOS-specific once the exception exists, so these tests reproduce it
anywhere by installing a fake readline module in sys.modules (_setup_readline()
does a function-local `import readline`, which resolves through sys.modules at
call time).

Also guards what a careless "just catch it" fix would break: the exit-time save
must not raise, an unreadable history file must not be silently replaced with an
empty one, and tab completion plus the ^A EDIT-mode binding must still be
configured - in the right dialect for the readline library in use.
"""

import atexit
import os
import shutil
import sys
import tempfile
import types

# Add project root to path (3 levels up from tests/regression/*/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.interactive import InteractiveMode


class FakeReadline(types.ModuleType):
    """Stand-in for the readline C extension that records every call."""

    def __init__(self, read_exc=None, write_exc=None, backend=None, doc=None,
                 history_length=0):
        super().__init__('readline')
        self.calls = []
        self._read_exc = read_exc
        self._write_exc = write_exc
        self._history_length = history_length
        if backend is not None:
            self.backend = backend      # Python 3.13+ exposes this
        self.__doc__ = doc              # detection path for Python 3.8-3.12

    def read_history_file(self, path):
        self.calls.append(('read_history_file', path))
        if self._read_exc is not None:
            raise self._read_exc

    def write_history_file(self, path):
        self.calls.append(('write_history_file', path))
        if self._write_exc is not None:
            raise self._write_exc
        with open(path, 'w') as f:
            f.write('')

    def get_current_history_length(self):
        return self._history_length

    def set_history_length(self, n):
        self.calls.append(('set_history_length', n))

    def set_completer(self, fn):
        self.calls.append(('set_completer', fn))

    def parse_and_bind(self, spec):
        self.calls.append(('parse_and_bind', spec))

    def called(self, name):
        return any(call[0] == name for call in self.calls)

    def bindings(self):
        return [spec for name, spec in self.calls if name == 'parse_and_bind']


class StubInteractive:
    """Minimal stand-in for InteractiveMode - _setup_readline needs only this."""

    def _completer(self, text, state):
        return None


class Harness:
    """Swap in the fake readline, capture atexit hooks, point HOME at a tmpdir."""

    def __init__(self, fake, history_bytes=None):
        self.fake = fake
        self.history_bytes = history_bytes
        self.hooks = []

    def __enter__(self):
        self.saved_module = sys.modules.get('readline')
        self.saved_register = atexit.register
        self.saved_env = {name: os.environ.get(name)
                          for name in ('HOME', 'MBASIC_DEBUG')}
        self.home = None
        try:
            sys.modules['readline'] = self.fake
            atexit.register = self._fake_register
            self.home = tempfile.mkdtemp(prefix='mbasic_history_test_')
            os.environ['HOME'] = self.home
            os.environ.pop('MBASIC_DEBUG', None)  # keep debug_log off in tests
            self.history_file = os.path.join(self.home, '.mbasic_history')
            if self.history_bytes is not None:
                with open(self.history_file, 'wb') as f:
                    f.write(self.history_bytes)
        except BaseException:
            # Never leave a fake readline or a hijacked atexit behind.
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *exc_info):
        atexit.register = self.saved_register
        if self.saved_module is not None:
            sys.modules['readline'] = self.saved_module
        else:
            sys.modules.pop('readline', None)
        for name, value in self.saved_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        if self.home is not None:
            shutil.rmtree(self.home, ignore_errors=True)
        return False

    def _fake_register(self, func, *args, **kwargs):
        self.hooks.append((func, args, kwargs))
        return func

    def setup(self):
        """Run _setup_readline(); return the exception it raised, or None."""
        try:
            InteractiveMode._setup_readline(StubInteractive())
        except Exception as e:
            return e
        return None

    def run_exit_hooks(self):
        """Run what atexit would run; return the exception raised, or None."""
        try:
            for func, args, kwargs in self.hooks:
                func(*args, **kwargs)
        except Exception as e:
            return e
        return None


results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def test_read_failure_does_not_crash_startup():
    """A history file readline will not read must not stop the REPL starting."""
    print("\nRead failures must not propagate")
    print("-" * 60)
    cases = [
        (PermissionError(1, 'Operation not permitted'),
         'PermissionError [Errno 1] - macOS libedit, PR #3'),
        (PermissionError(13, 'Permission denied'),
         'PermissionError [Errno 13] - root-owned file from a sudo run'),
        (OSError(22, 'Invalid argument'),
         'OSError [Errno 22] - history path is a directory (GNU readline)'),
        (IsADirectoryError(21, 'Is a directory'),
         'IsADirectoryError'),
        (FileNotFoundError(2, 'No such file or directory'),
         'FileNotFoundError - first run, must stay tolerated'),
    ]
    for exc, label in cases:
        with Harness(FakeReadline(read_exc=exc), history_bytes=b'PRINT 1\n') as h:
            error = h.setup()
        detail = '' if error is None else f" -> raised {type(error).__name__}: {error}"
        check(error is None, f"_setup_readline survives {label}{detail}")


def test_exit_save_is_guarded():
    """write_history_file fails the same ways read_history_file does."""
    print("\nThe exit-time save must not dump a traceback")
    print("-" * 60)
    fake = FakeReadline(write_exc=PermissionError(13, 'Permission denied'),
                        history_length=3)
    with Harness(fake) as h:
        setup_error = h.setup()
        registered = len(h.hooks) > 0
        hook_error = h.run_exit_hooks()
        wrote = fake.called('write_history_file')
    check(setup_error is None, "setup completes")
    check(registered, "a history save is registered with atexit")
    check(wrote, "the atexit hook actually calls write_history_file")
    detail = '' if hook_error is None else f" -> raised {type(hook_error).__name__}"
    check(hook_error is None, f"the atexit hook swallows write errors{detail}")


def test_unreadable_history_is_not_replaced_with_nothing():
    """Swallowing the read must not turn into silently wiping the file."""
    print("\nAn unreadable history file must survive a session that adds nothing")
    print("-" * 60)
    original = b'PRINT "OLD HISTORY"\n'
    fake = FakeReadline(read_exc=PermissionError(1, 'Operation not permitted'),
                        history_length=0)
    with Harness(fake, history_bytes=original) as h:
        setup_error = h.setup()
        h.run_exit_hooks()
        wrote = fake.called('write_history_file')
        with open(h.history_file, 'rb') as f:
            content = f.read()
    check(setup_error is None, "setup completes")
    check(not wrote, "no save is attempted when nothing was read and nothing typed")
    check(content == original, "the old history file is still intact on disk")


def test_unreadable_history_self_heals_once_used():
    """If the session did record commands, saving them is worth the overwrite."""
    print("\nAn unreadable history file is replaced once there is history to save")
    print("-" * 60)
    fake = FakeReadline(read_exc=PermissionError(1, 'Operation not permitted'),
                        history_length=3)
    with Harness(fake, history_bytes=b'PRINT "OLD HISTORY"\n') as h:
        setup_error = h.setup()
        hook_error = h.run_exit_hooks()
        wrote = fake.called('write_history_file')
    check(setup_error is None and hook_error is None, "setup and exit both complete")
    check(wrote, "the session's own history is saved")


def test_first_run_saves_what_was_typed():
    """The no-history-file case must keep working - that is how history starts."""
    print("\nFirst run (no history file) saves the commands that were typed")
    print("-" * 60)
    fake = FakeReadline(read_exc=FileNotFoundError(2, 'No such file or directory'),
                        history_length=3)
    with Harness(fake) as h:
        setup_error = h.setup()
        hook_error = h.run_exit_hooks()
        wrote = fake.called('write_history_file')
    check(setup_error is None and hook_error is None, "setup and exit both complete")
    check(wrote, "a history file is created on the first run")


def test_empty_history_is_never_written():
    """An empty history file is the very thing that trips libedit next run."""
    print("\nA session that records nothing must not write an empty history file")
    print("-" * 60)
    fake = FakeReadline(read_exc=FileNotFoundError(2, 'No such file or directory'),
                        history_length=0)
    with Harness(fake) as h:
        setup_error = h.setup()
        hook_error = h.run_exit_hooks()
        wrote = fake.called('write_history_file')
        left_behind = os.path.exists(h.history_file)
    check(setup_error is None and hook_error is None, "setup and exit both complete")
    check(not wrote, "no save is attempted when there is no history to save")
    check(not left_behind, "no empty history file is left behind")


def test_gnu_readline_bindings():
    """The crash fix must not cost us completion or ^A EDIT mode."""
    print("\nGNU readline keybindings")
    print("-" * 60)
    fake = FakeReadline(backend='readline')
    with Harness(fake) as h:
        error = h.setup()
    binds = fake.bindings()
    check(error is None, "setup completes on GNU readline")
    check(fake.called('set_completer'), "completer is registered")
    check('tab: complete' in binds, "tab completion is bound")
    check('Control-a: self-insert' in binds,
          "^A is bound to self-insert for EDIT mode")
    # Selecting the keymap has to come first here too: a user with
    # "set editing-mode vi" in ~/.inputrc otherwise gets the bindings written
    # into the vi keymap and then switched away from, leaving Tab dead.
    check(bool(binds) and binds[0] == 'set editing-mode emacs',
          "emacs mode is set first, before the other binds")


def test_libedit_bindings():
    """libedit ignores GNU syntax silently, so the editrc dialect is required."""
    print("\nlibedit (editline) keybindings")
    print("-" * 60)
    backends = [
        ('backend attribute (Python 3.13+)', FakeReadline(backend='editline')),
        ('module docstring (Python 3.8-3.12)',
         FakeReadline(doc='Importing this module enables command line editing '
                          'using libedit readline.')),
    ]
    for label, fake in backends:
        with Harness(fake) as h:
            error = h.setup()
        binds = fake.bindings()
        check(error is None, f"setup completes, detected via {label}")
        check('bind ^I rl_complete' in binds,
              f"tab completion uses editrc syntax ({label})")
        check('bind ^A ed-insert' in binds,
              f"^A EDIT mode uses editrc syntax ({label})")
        check('tab: complete' not in binds and 'Control-a: self-insert' not in binds,
              f"GNU-only strings are not emitted ({label})")
        check(bool(binds) and binds[0] == 'bind -e',
              f"emacs mode is set first, before the other binds ({label})")


if __name__ == "__main__":
    print("CLI readline history setup (GitHub PR #3 regression)")
    print("=" * 60)

    test_read_failure_does_not_crash_startup()
    test_exit_save_is_guarded()
    test_unreadable_history_is_not_replaced_with_nothing()
    test_unreadable_history_self_heals_once_used()
    test_first_run_saves_what_was_typed()
    test_empty_history_is_never_written()
    test_gnu_readline_bindings()
    test_libedit_bindings()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
