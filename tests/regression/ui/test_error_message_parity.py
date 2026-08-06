#!/usr/bin/env python3
"""Every UI reports an error in MBASIC's words, not Python's.

docs/user/UI_FEATURE_COMPARISON.md promises "Standard MBASIC errors" in all
four UIs. It was true of none of them: each backend built its own string out of
the Python exception, so the same failure read

    CLI      ?RuntimeError in 20: Cannot open NOSUCH.XYZ: Cannot open NOSUCH.XYZ: No such file or directory
                20 OPEN "I",1,"NOSUCH.XYZ"
    curses   | Error: Cannot open NOSUCH.XYZ: Cannot open NOSUCH.XYZ: No such file or directory
    Tk       --- Error at line 20: Cannot open NOSUCH.XYZ: ... ---
    web      --- Error: Cannot open NOSUCH.XYZ: ... ---

where the real binary says, simply, `File not found in 20`.

The rendering now lives in one place - ErrorInfo.message(), on top of
src/error_codes.py - and each UI keeps its own presentation around it. The
curses box still draws its box and shows the offending source line, because
that is a deliberate IDE affordance and the curses UI is documented as an IDE;
what it must not do is invent the wording.

This test pins the *text*. It does not pin the chrome.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


#: (name, program, the message the binary gives). Line 20 is the failing one
#: in each, so the CLI's rendering is "<message> in 20".
CASES = [
    ('file not found',
     '10 PRINT "before"\n20 OPEN "I",1,"NOSUCH.XYZ"\n30 PRINT "after"',
     'File not found'),
    ('subscript out of range',
     '10 DIM Q(3)\n20 Q(9) = 1\n30 PRINT "after"',
     'Subscript out of range'),
    ('type mismatch',
     '10 A = 1\n20 A$ = 5\n30 PRINT "after"',
     'Type mismatch'),
    ('undefined line number',
     '10 PRINT "before"\n20 GOTO 9999\n30 PRINT "after"',
     'Undefined line number'),
]

CHROME = ('MBASIC-', '100%', '(Tip:', 'Type HELP')

#: Typed at the Ok prompt, against what the binary answers. Measured under
#: cpmemu on com/mbasic.com - see tests/HOW_TO_RUN_REAL_MBASIC.md. Each of
#: these produces exactly one line, so the two lists zip.
COMMANDS = [
    ('LOAD "NOSUCH.BAS"', 'File not found'),
    ('MERGE "NOSUCH.BAS"', 'File not found'),
    ('SAVE ""', 'Bad file name'),
    ('LOAD ""', 'Bad file name'),
    ('MERGE ""', 'Bad file name'),
    ('CHAIN ""', 'Bad file name'),
    ('SAVE', 'Missing operand'),
    ('EDIT 500', 'Undefined line number'),
    ('DELETE 99-1', 'Illegal function call'),
    ('AUTO X', 'Syntax error'),
    ('RUN 9999', 'Undefined line number'),
    ('CONT', "Can't continue"),
    ('ZZZ 1', 'Syntax error'),
    ('PRINT SQR(-1)', 'Illegal function call'),
]

#: Where 5.21 draws the line between "an operand never arrived" and "this is
#: simply wrong". Measured the same way. The split falls exactly on one of our
#: parser's messages - "Unexpected token in expression: EOF" - and on nothing
#: else, which is what error_code_for() keys on. Testing for "EOF" anywhere in
#: the text instead got the whole second group wrong, because there EOF is the
#: token a bracket was wanted before, or the name of the EOF function.
OPERANDS = [
    ('PRINT 1 +', 'Missing operand'),
    ('PRINT EOF(', 'Missing operand'),
    ('FOR I = 1 TO', 'Missing operand'),
    ('LET X =', 'Missing operand'),
    ('DIM A(', 'Missing operand'),
    ('PRINT #', 'Missing operand'),
    ('OPEN "I",1,', 'Missing operand'),
    ('PRINT MID$(', 'Missing operand'),
    ('PRINT EOF', 'Syntax error'),
    ('PRINT EOF)', 'Syntax error'),
    ('X = EOF(1', 'Syntax error'),
    ('PRINT (1', 'Syntax error'),
    ('GOTO', 'Syntax error'),
    ('ON 1 GOTO', 'Syntax error'),
    ('PRINT LEFT$("a"', 'Syntax error'),
]


#: Statement names that collide with the fragments error_code_for() searches
#: for. An unknown statement is a syntax error whatever it is called, so these
#: must not be read as the error they happen to spell. Measured; all three are
#: `Syntax error` on the binary.
COLLISIONS = [
    ('OVERFLOW 1', 'Syntax error'),
    ('TYPE MISMATCH', 'Syntax error'),
    ('SYNTAX 1', 'Syntax error'),
]


def cli_commands(commands):
    """Type these at the Ok prompt, and give back what came out."""
    with tempfile.TemporaryDirectory(prefix='mbasic-uiparity-') as tmp:
        done = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / 'mbasic'), '--ui', 'cli'],
            input=''.join(c + '\n' for c in commands) + 'SYSTEM\n',
            capture_output=True, text=True, cwd=tmp, timeout=120)
    return [l for l in done.stdout.split('\n')
            if not l.startswith(CHROME) and l not in ('Ready', 'Goodbye', '')]


def cli_output(program):
    with tempfile.TemporaryDirectory(prefix='mbasic-uiparity-') as tmp:
        source = Path(tmp) / 'case.bas'
        source.write_text(program + '\n')
        done = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / 'mbasic'), '--ui', 'cli', str(source)],
            input='RUN\nSYSTEM\n', capture_output=True, text=True,
            cwd=tmp, timeout=60)
    return [l for l in done.stdout.split('\n')
            if not l.startswith(CHROME) and l not in ('Ready', 'Goodbye', '')]


def curses_output(program):
    """Drive the curses backend without a terminal, as its own tests do."""
    from src.ui.curses_ui import CursesBackend
    from src.iohandler.console import ConsoleIOHandler
    from src.editing import ProgramManager
    from src.parser import TypeInfo

    def_types = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    backend = CursesBackend(ConsoleIOHandler(debug_enabled=False),
                            ProgramManager(def_types))
    backend._create_ui()
    backend.editor.set_edit_text(program)
    backend._run_program()
    return list(backend.output_buffer)


def test_the_cli_says_what_the_binary_says():
    print("CLI")
    print("-" * 60)
    for name, program, message in CASES:
        got = cli_output(program)
        want = ['before' if 'before' in program else None]
        expected = f'{message} in 20'
        ok = expected in got
        # and nothing of Python's is left in it
        clean = not any(bad in line for line in got
                        for bad in ('Error:', 'RuntimeError', 'ValueError',
                                    'OSError', 'Errno', 'Traceback', '?'))
        check(ok and clean, f"{name:26} -> {got}"
              + ("" if ok and clean else f"   (want {expected!r} and no Python detail)"))


def test_curses_says_the_same_thing():
    print("\ncurses")
    print("-" * 60)
    for name, program, message in CASES:
        got = curses_output(program)
        # The box shows the line separately, so the message stands alone.
        ok = any(line.strip() == f'│ Error: {message}' for line in got)
        clean = not any(bad in line for line in got
                        for bad in ('RuntimeError', 'ValueError', 'OSError',
                                    'Errno', 'Traceback'))
        shown = [l for l in got if 'Error' in l]
        check(ok and clean, f"{name:26} -> {shown}"
              + ("" if ok and clean else f"   (want '│ Error: {message}')"))


def test_the_rendering_lives_in_one_place():
    """ErrorInfo.message() is what every backend should be calling."""
    print("\nOne renderer, not six")
    print("-" * 60)
    from src.interpreter import ErrorInfo
    from src.pc import PC

    info = ErrorInfo(53, PC.running_at(50, 0), 'Cannot open X: No such file or directory')
    check(info.message() == 'File not found in 50',
          f"with the line   -> {info.message()!r}")
    check(info.message(with_line=False) == 'File not found',
          f"without it      -> {info.message(with_line=False)!r}")

    # No backend should be reaching for the Python text any more.
    offenders = []
    for name in ('src/ui/curses_ui.py', 'src/ui/tk_ui.py',
                 'src/ui/web/nicegui_backend.py'):
        text = (PROJECT_ROOT / name).read_text()
        if 'error_info.error_message' in text:
            offenders.append(name)
    check(not offenders,
          f"no backend reads error_info.error_message ({offenders or 'none'})")


def test_direct_commands_match_the_binary():
    """LOAD, SAVE, MERGE, CHAIN, EDIT, DELETE, AUTO, RUN, CONT at the prompt."""
    print("\nDirect commands")
    print("-" * 60)
    got = cli_commands([c for c, _ in COMMANDS])
    for (command, want), line in zip(COMMANDS, got + [''] * len(COMMANDS)):
        check(line == want, f"{command:20} -> {line!r}"
              + ("" if line == want else f"   (binary says {want!r})"))


def test_missing_operand_is_told_from_syntax_error():
    """A parse failure is only "Missing operand" when an operand ran out."""
    print("\nMissing operand vs Syntax error")
    print("-" * 60)
    got = cli_commands([c for c, _ in OPERANDS])
    for (source, want), line in zip(OPERANDS, got + [''] * len(OPERANDS)):
        check(line == want, f"{source:20} -> {line!r}"
              + ("" if line == want else f"   (binary says {want!r})"))

    # A statement whose name spells one of the fragments is still just unknown.
    got = cli_commands([c for c, _ in COLLISIONS])
    for (source, want), line in zip(COLLISIONS, got + [''] * len(COLLISIONS)):
        check(line == want, f"{source:20} -> {line!r}"
              + ("" if line == want else f"   (binary says {want!r})"))


def test_a_parse_error_is_worded_once():
    """ProgramManager writes the prefix; a backend must not write it again."""
    print("\nSaid once, not twice")
    print("-" * 60)
    from src.ui.curses_ui import CursesBackend
    from src.iohandler.console import ConsoleIOHandler
    from src.editing import ProgramManager
    from src.parser import TypeInfo

    def_types = {letter: TypeInfo.SINGLE for letter in 'abcdefghijklmnopqrstuvwxyz'}
    with tempfile.TemporaryDirectory(prefix='mbasic-uiparity-') as tmp:
        source = Path(tmp) / 'bad.bas'
        source.write_text('10 PRINT "ok"\n20 ZZZ 1\n')

        manager = ProgramManager(def_types)
        backend = CursesBackend(ConsoleIOHandler(debug_enabled=False), manager)
        backend._create_ui()
        backend.cmd_merge(str(source))
        shown = [l for l in backend.output_buffer if 'error' in l.lower()]

    check(len(shown) == 1 and shown[0].count('Syntax error') == 1
          and shown[0].startswith('Syntax error in 20:'),
          f"curses MERGE of a bad line -> {shown}")

    # And a missing file is MBASIC's message, not the OSError.
    backend.output_buffer.clear()
    backend.cmd_load('NOSUCH.BAS')
    got = list(backend.output_buffer)
    check(got == ['File not found'], f"curses LOAD of a missing file -> {got}")


if __name__ == "__main__":
    print("Error message parity across the UIs")
    print("=" * 60)

    test_the_cli_says_what_the_binary_says()
    test_curses_says_the_same_thing()
    test_direct_commands_match_the_binary()
    test_missing_operand_is_told_from_syntax_error()
    test_a_parse_error_is_worded_once()
    test_the_rendering_lives_in_one_place()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")

    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    print("✅ All tests passed!")
    sys.exit(0)
