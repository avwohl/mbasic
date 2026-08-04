#!/usr/bin/env python3
"""
Test that mbasic imports and runs where the Windows standard library differs.

Three separate bugs made mbasic unimportable, all fixed:

1. src/basic_builtins.py imported tty and termios at module scope. Neither
   exists in the Windows stdlib, so src.basic_builtins - and by cascade
   src.interpreter, src.interactive, src.immediate_executor and src.ui - could
   not be imported at all.
2. src/iohandler/__init__.py imported curses through .curses_io, unconditionally.
3. src/ui/keybindings.py read curses_keybindings.json at module scope with no
   encoding=, so it decoded using the locale's codepage. That file ships UTF-8
   arrows (U+2191/U+2193), which raise UnicodeDecodeError on any Windows whose
   ANSI codepage is not UTF-8 - cp932, cp936, cp949, cp950, cp874. That is a
   ValueError, so it also escaped the (ImportError, OSError) guard in
   src/ui/__init__.py and took every UI backend down with it.

WHAT THIS TEST SIMULATES, AND WHAT IT DOES NOT
----------------------------------------------
Both failures were about the *environment*, not about Windows behavior, so both
reproduce here exactly:

  - missing modules: a sys.meta_path hook refuses the POSIX-only names and
    mbasic is run as a subprocess underneath it.
  - non-UTF-8 default encoding: LC_ALL=C with PYTHONUTF8=0 and
    PYTHONCOERCECLOCALE=0 makes open() default to ASCII, which fails on the
    same bytes cp932 fails on.

It does NOT simulate Windows itself. sys.platform stays 'linux', so every
`if sys.platform == 'win32'` branch - the msvcrt paths in INKEY$ and
input_char, the %APPDATA% settings path, `cls` in clear_screen - is never
executed here. msvcrt is in the blocked list so that this file is also
meaningful if it is ever run ON Windows, where msvcrt does exist; on POSIX,
blocking it is a no-op. Nothing here says anything about Windows runtime
behavior: console codes, path handling and key decoding are all untested.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

# Absent from the Windows standard library. readline is too, which is why the
# CLI already guards it - this keeps that guard honest as well.
BLOCKED = ['termios', 'tty', 'curses', 'fcntl', 'pty', 'grp', 'pwd',
           'resource', 'readline', 'msvcrt']

# Must import no matter what is missing. This is the anti-vacuity floor: the
# broad sweep below only reports failures, so on its own it would pass happily
# if it ever examined nothing at all.
MUST_IMPORT = [
    'src.basic_builtins', 'src.interpreter', 'src.interactive',
    'src.immediate_executor', 'src.iohandler', 'src.iohandler.console',
    'src.ui', 'src.ui.cli', 'src.ui.keybindings', 'src.ui.keybinding_loader',
    'src.lexer', 'src.parser', 'src.terminal_errors', 'src.win_console',
    'src.mbasic_main',
]

# Allowed to fail: genuinely requires a blocked module.
EXPECTED_UNIMPORTABLE = {'src.iohandler.curses_io'}

SITECUSTOMIZE = '''
import sys
BLOCKED = {blocked!r}

class _Blocker:
    """Refuse the POSIX-only modules the way a Windows interpreter would."""

    def find_module(self, name, path=None):
        return self.find_spec(name, path)

    def find_spec(self, name, path=None, target=None):
        if name.split('.')[0] in BLOCKED:
            # ModuleNotFoundError, not bare ImportError: that is what Python
            # raises for a missing module, and code that catches the narrower
            # type would behave differently under a less faithful blocker.
            raise ModuleNotFoundError(
                "No module named %r (simulated Windows)" % name, name=name)
        return None

sys.meta_path.insert(0, _Blocker())
for _name in list(sys.modules):
    if _name.split('.')[0] in BLOCKED:
        del sys.modules[_name]
'''

# Reports one line per failure: module|type|message|missing|origin-file.
# The origin file is what lets the parent tell "mbasic imports a POSIX module"
# apart from "an optional third-party package does".
PROBE = '''
import importlib, pkgutil, sys, traceback
sys.path.insert(0, {root!r})
import src
walked = 0
for module in pkgutil.walk_packages(src.__path__, prefix="src."):
    walked += 1
    try:
        importlib.import_module(module.name)
    except BaseException as exc:
        frames = traceback.extract_tb(sys.exc_info()[2])
        origin = frames[-1].filename if frames else "?"
        print("FAIL|%s|%s|%s|%s|%s" % (
            module.name, type(exc).__name__, str(exc).replace("|", "/"),
            getattr(exc, "name", None), origin))
print("WALKED|%d" % walked)
'''

IMPORT_EACH = '''
import importlib, sys
sys.path.insert(0, {root!r})
for name in {names!r}:
    try:
        importlib.import_module(name)
        print("OK|%s" % name)
    except BaseException as exc:
        print("FAIL|%s|%s: %s" % (name, type(exc).__name__, exc))
'''

results = []


def check(condition, label):
    """Record one check; print pass/fail immediately."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def mentions_blocked_module(text):
    """True if a blocked module is named as a whole word (not 'empty' -> 'pty')."""
    return bool(re.search(r'\b(' + '|'.join(BLOCKED) + r')\b', text))


class Sim:
    """A child environment with the POSIX modules hidden, ASCII default
    encoding, or both."""

    def __init__(self, block=True, ascii_locale=False):
        self.block = block
        self.ascii_locale = ascii_locale

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix='mbasic_winsim_')
        try:
            self.env = dict(os.environ)
            self.env.pop('MBASIC_DEBUG', None)
            self.env['HOME'] = self.dir
            if self.block:
                path = os.path.join(self.dir, 'sitecustomize.py')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(SITECUSTOMIZE.format(blocked=BLOCKED))
                existing = self.env.get('PYTHONPATH')
                self.env['PYTHONPATH'] = (f"{self.dir}{os.pathsep}{existing}"
                                          if existing else self.dir)
            if self.ascii_locale:
                # Make open() default to ASCII, the way a non-UTF-8 Windows
                # codepage does. Python would otherwise coerce C to C.UTF-8
                # (PEP 538) or enable UTF-8 mode (PEP 540).
                self.env['LC_ALL'] = 'C'
                self.env['LANG'] = 'C'
                self.env['PYTHONCOERCECLOCALE'] = '0'
                self.env['PYTHONUTF8'] = '0'
        except BaseException:
            shutil.rmtree(self.dir, ignore_errors=True)
            raise
        return self

    def __exit__(self, *exc_info):
        shutil.rmtree(self.dir, ignore_errors=True)
        return False

    def run(self, args, stdin=None, timeout=20):
        return subprocess.run([sys.executable] + args, input=stdin,
                              capture_output=True, text=True,
                              cwd=PROJECT_ROOT, env=self.env, timeout=timeout)


def test_the_simulation_actually_blocks():
    """Controls - without these, every check below could pass vacuously."""
    print("\nThe simulation really does hide the modules and change the encoding")
    print("-" * 60)
    with Sim() as sim:
        for name in ('termios', 'curses', 'readline'):
            proc = sim.run(['-c', f'import {name}'])
            check(proc.returncode != 0 and 'simulated Windows' in proc.stderr,
                  f"importing {name} fails under the simulation")

    with Sim(block=False, ascii_locale=True) as sim:
        proc = sim.run(['-c', 'import locale; print(locale.getpreferredencoding(False))'])
    encoding = proc.stdout.strip()
    normalized = encoding.lower().replace('-', '').replace('_', '')
    check(normalized in ('ansix3.41968', 'ascii', 'usascii', '646'),
          f"the ASCII-locale simulation really is non-UTF-8 (got {encoding!r})")


def test_core_modules_import():
    """Every module on the startup path, imported explicitly by name."""
    print("\nCore modules import with the POSIX-only stdlib missing")
    print("-" * 60)
    with Sim() as sim:
        proc = sim.run(['-c', IMPORT_EACH.format(root=PROJECT_ROOT,
                                                 names=MUST_IMPORT)], timeout=60)
    failures = [line for line in proc.stdout.splitlines() if line.startswith('FAIL|')]
    imported = [line for line in proc.stdout.splitlines() if line.startswith('OK|')]
    check(len(imported) + len(failures) == len(MUST_IMPORT),
          f"all {len(MUST_IMPORT)} core modules were actually tried "
          f"(saw {len(imported) + len(failures)})")
    check(not failures, "every core module imports" + (f" -> {failures}" if failures else ""))


def test_core_modules_import_in_ascii_locale():
    """The codepage half: shipped data files must not depend on the locale."""
    print("\nCore modules import with a non-UTF-8 default encoding")
    print("-" * 60)
    with Sim(block=False, ascii_locale=True) as sim:
        proc = sim.run(['-c', IMPORT_EACH.format(root=PROJECT_ROOT,
                                                 names=MUST_IMPORT)], timeout=60)
    failures = [line for line in proc.stdout.splitlines() if line.startswith('FAIL|')]
    check(not failures,
          "every core module imports under an ASCII locale"
          + (f" -> {failures}" if failures else ""))

    # And with both problems at once, which is the real Windows case.
    with Sim(block=True, ascii_locale=True) as sim:
        proc = sim.run(['-c', IMPORT_EACH.format(root=PROJECT_ROOT,
                                                 names=MUST_IMPORT)], timeout=60)
    failures = [line for line in proc.stdout.splitlines() if line.startswith('FAIL|')]
    check(not failures,
          "every core module imports with both problems at once"
          + (f" -> {failures}" if failures else ""))


def test_no_module_imports_a_posix_module():
    """Broad sweep over every module, classified by where the failure came from."""
    print("\nNo src module needs a POSIX-only module to import")
    print("-" * 60)
    with Sim() as sim:
        proc = sim.run(['-c', PROBE.format(root=PROJECT_ROOT)], timeout=60)

    walked = 0
    ours = []
    for line in proc.stdout.splitlines():
        if line.startswith('WALKED|'):
            walked = int(line.split('|')[1])
            continue
        if not line.startswith('FAIL|'):
            continue
        _, name, exc_type, message, missing, origin = line.split('|', 5)
        if name in EXPECTED_UNIMPORTABLE:
            continue
        # Only our own code counts. If the traceback ends inside a third-party
        # package, that package needs the POSIX module, not us - urwid and
        # pexpect both really do import termios and pty.
        if not os.path.abspath(origin).startswith(PROJECT_ROOT + os.sep):
            continue
        # Our file raised. It is a Windows problem only if a blocked module is
        # what went missing - by exception name, or named in a wrapped message.
        if missing in BLOCKED or mentions_blocked_module(message):
            ours.append(f"{name}: {exc_type}: {message} (at {origin})")

    check(walked >= 40, f"the sweep actually examined the tree ({walked} modules walked)")
    check(not ours,
          "no module of ours fails on a missing POSIX module"
          + (f" -> {ours}" if ours else ""))


def test_interpreter_runs():
    """The whole point: BASIC still executes in the degraded environment."""
    print("\nmbasic runs a program in the simulated environment")
    print("-" * 60)
    program = ('10 FOR I=1 TO 3\n'
               '20 PRINT "N=";I\n'
               '30 NEXT I\n'
               '40 A$=INKEY$\n'
               '50 PRINT "INKEY-OK";LEN(A$)\n'
               'RUN\n'
               'SYSTEM\n')
    for label, sim in (('POSIX modules missing', Sim()),
                       ('ASCII locale', Sim(block=False, ascii_locale=True)),
                       ('both', Sim(block=True, ascii_locale=True))):
        with sim:
            proc = sim.run(['mbasic', '--ui', 'cli'], stdin=program, timeout=30)
        output = proc.stdout + proc.stderr
        check(proc.returncode == 0, f"mbasic exits 0 ({label}, got {proc.returncode})")
        check('Traceback' not in output, f"no traceback ({label})")
        check('N= 1' in output and 'N= 3' in output, f"the FOR loop ran ({label})")
        # NOTE: stdin is a pipe here, so INKEY$ returns "" at its isatty()
        # check. This says INKEY$ is reachable and harmless, NOT that the
        # Windows msvcrt path works - that branch cannot run on this platform.
        check('INKEY-OK' in output, f"INKEY$ is reachable and returns ({label})")

    with Sim() as sim:
        proc = sim.run(['mbasic', '--ui', 'cli'], stdin='SYSTEM\n', timeout=30)
    check('readline not available' in (proc.stdout + proc.stderr),
          "a missing readline is reported rather than fatal")


def test_curses_handler_degrades_to_none():
    """Importing the package must work; the curses handler just is not there."""
    print("\nsrc.iohandler imports, with CursesIOHandler absent")
    print("-" * 60)
    probe = (f'import sys; sys.path.insert(0, {PROJECT_ROOT!r});'
             'import src.iohandler as m;'
             'print("handler:", m.CursesIOHandler);'
             'print("flag:", m._has_curses_io);'
             'print("console:", m.ConsoleIOHandler is not None)')
    with Sim() as sim:
        proc = sim.run(['-c', probe])
    output = proc.stdout
    check(proc.returncode == 0, f"src.iohandler imports (stderr: {proc.stderr[:200]})")
    check('handler: None' in output, "CursesIOHandler is None rather than missing")
    check('flag: False' in output, "_has_curses_io reports the degradation")
    check('console: True' in output, "ConsoleIOHandler is still exported")


def test_shipped_data_files_are_utf8():
    """The files we ship and read back must decode as UTF-8 explicitly."""
    print("\nShipped data files decode independently of the locale")
    print("-" * 60)
    keybindings = os.path.join(PROJECT_ROOT, 'src/ui/curses_keybindings.json')
    with open(keybindings, 'rb') as f:
        raw = f.read()
    check(any(b > 127 for b in raw),
          "the keybindings JSON really does contain non-ASCII (else this is vacuous)")
    try:
        raw.decode('utf-8')
        decoded = True
    except UnicodeDecodeError:
        decoded = False
    check(decoded, "the keybindings JSON is valid UTF-8")

    # The reader must name the encoding rather than trusting the locale.
    for path in ('src/ui/keybindings.py', 'src/ui/keybinding_loader.py'):
        with open(os.path.join(PROJECT_ROOT, path), encoding='utf-8') as f:
            source = f.read()
        opens = re.findall(r'open\([^)]*\)', source, re.S)
        unqualified = [o for o in opens if 'encoding=' not in o and "'w'" not in o]
        check(not unqualified,
              f"{path} names an encoding on every read"
              + (f" -> {unqualified}" if unqualified else ""))


def test_posix_behavior_is_unchanged():
    """No simulation - the real platform must be entirely unaffected."""
    print("\nThe normal POSIX path still behaves as before")
    print("-" * 60)
    env = dict(os.environ)
    env.pop('MBASIC_DEBUG', None)
    home = tempfile.mkdtemp(prefix='mbasic_posix_check_')
    env['HOME'] = home
    try:
        proc = subprocess.run(
            [sys.executable, 'mbasic', '--ui', 'cli'],
            input='10 PRINT "HI"\n40 A$=INKEY$\n50 PRINT "INKEY-OK";LEN(A$)\nRUN\nSYSTEM\n',
            capture_output=True, text=True, cwd=PROJECT_ROOT, env=env, timeout=20)
    finally:
        shutil.rmtree(home, ignore_errors=True)
    output = proc.stdout + proc.stderr
    check(proc.returncode == 0, "mbasic exits 0 on the real platform")
    check('INKEY-OK' in output, "INKEY$ still works on POSIX")
    check('Traceback' not in output, "no traceback on the real platform")


if __name__ == "__main__":
    print("Windows import compatibility (missing POSIX stdlib, non-UTF-8 locale)")
    print("=" * 60)

    test_the_simulation_actually_blocks()
    test_core_modules_import()
    test_core_modules_import_in_ascii_locale()
    test_no_module_imports_a_posix_module()
    test_interpreter_runs()
    test_curses_handler_degrades_to_none()
    test_shipped_data_files_are_utf8()
    test_posix_behavior_is_unchanged()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
